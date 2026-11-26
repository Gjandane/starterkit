// Redraws a page source's marked shapes in the page's drawing rules.
// Every uneven line is seeded by its own shape, so a re-render repeats it and
// moving one shape leaves the others as they were.
(function () {
  const style = JSON.parse(document.getElementById('ink-style').textContent);
  const NS = 'http://www.w3.org/2000/svg';
  const CSS_PX_PER_MM = 96 / 25.4;
  const STEP_MM = 0.7;

  const make = (name, attrs) => {
    const el = document.createElementNS(NS, name);
    for (const k in attrs) el.setAttribute(k, attrs[k]);
    return el;
  };
  const num = (n) => n.toFixed(3);
  const apart = (a, b) => Math.hypot(a[0] - b[0], a[1] - b[1]);

  // ---- noise ----
  function hash(text) {
    let h = 2166136261;
    for (let i = 0; i < text.length; i++) h = Math.imul(h ^ text.charCodeAt(i), 16777619);
    h ^= h >>> 15;
    h = Math.imul(h, 2246822507);
    return (h ^ (h >>> 13)) >>> 0;
  }
  function noise(seed, x) {
    const at = (i) => (hash(seed + ':' + i) % 2000) / 1000 - 1;
    const i = Math.floor(x), t = x - i, s = t * t * (3 - 2 * t);
    return at(i) * (1 - s) + at(i + 1) * s;
  }

  // ---- geometry ----
  // The shape as subpaths of evenly spaced points, with its corners kept.
  function trace(shape, step) {
    const total = shape.getTotalLength();
    const at = (s) => { const p = shape.getPointAtLength(s); return [p.x, p.y]; };
    const n = Math.max(2, Math.ceil(total / step)), gap = total / n;
    const subpaths = [[at(0)]];
    for (let i = 1; i <= n; i++) {
      const s = i * gap, p = at(s);
      let last = subpaths[subpaths.length - 1];
      const before = at(s - gap), straight = apart(before, p);
      let lo = s - gap, hi = s;
      if (straight > gap * 1.5) {
        // A jump is a new subpath: close in on both sides of the break.
        for (let k = 0; k < 20; k++) {
          const mid = (lo + hi) / 2;
          if (apart(before, at(mid)) > gap * 1.2) hi = mid; else lo = mid;
        }
        last.push(at(lo));
        last = [at(hi)];
        subpaths.push(last);
      } else if (straight < gap * 0.98) {
        // A short cut means a corner inside the step: find it.
        for (let k = 0; k < 20; k++) {
          const a = lo + (hi - lo) / 3, b = hi - (hi - lo) / 3;
          const round = (t) => apart(before, at(t)) + apart(at(t), p);
          if (round(a) > round(b)) hi = b; else lo = a;
        }
        last.push(at((lo + hi) / 2));
      }
      last.push(p);
    }
    return subpaths;
  }

  const isClosed = (points, reach) => points.length > 3 && apart(points[0], points[points.length - 1]) < reach;

  function jitter(points, seed, wobble, unit) {
    const along = [0];
    for (let i = 1; i < points.length; i++) along.push(along[i - 1] + apart(points[i - 1], points[i]) / unit);
    const total = along[along.length - 1], closed = isClosed(points, 0.1 * unit);
    const blend = Math.min(10, total / 3);
    const shake = (axis, mm) => 0.75 * noise(seed + axis, mm / 9) + 0.25 * noise(seed + 'f' + axis, mm / 3);
    return points.map((p, i) => [0, 1].map((axis) => {
      const mm = along[i];
      let shift = shake(axis, mm);
      if (closed && mm > total - blend) {
        // The end of a closed line eases back to where it started.
        const k = (mm - total + blend) / blend;
        shift = shift * (1 - k) + shake(axis, mm - total) * k;
      }
      return p[axis] + wobble * unit * shift;
    }));
  }

  const outline = (points, closed) => 'M' + points.map((p) => p.map(num).join(' ')).join('L') + (closed ? 'Z' : '');

  // A pen line of uneven weight: one quad per step and a dot at each joint, all
  // wound the same way so that overlaps stay filled.
  function pen(points, seed, width, uneven, unit, dashed) {
    let d = '', s = 0;
    const half = (at) => (width / 2) * (1 + 0.6 * uneven * noise(seed + 'w', at / unit / 4));
    const dot = (p, r) => outline([...Array(8).keys()].map((k) =>
      [p[0] + r * Math.cos((k * Math.PI) / 4), p[1] + r * Math.sin((k * Math.PI) / 4)]), true);
    for (let i = 1; i < points.length; i++) {
      const a = points[i - 1], b = points[i], len = apart(a, b);
      const ha = half(s), hb = half(s + len), inked = !dashed || (s / unit) % 4 < 2.4;
      s += len;
      if (!len || !inked) continue;
      const nx = (b[1] - a[1]) / len, ny = -(b[0] - a[0]) / len;
      d += outline([[a[0] + nx * ha, a[1] + ny * ha], [b[0] + nx * hb, b[1] + ny * hb],
        [b[0] - nx * hb, b[1] - ny * hb], [a[0] - nx * ha, a[1] - ny * ha]], true) + dot(a, ha) + dot(b, hb);
    }
    return d;
  }

  // ---- marks ----
  // User units in one printed mm.
  function unitOf(el) {
    const m = el.getScreenCTM();
    return CSS_PX_PER_MM / Math.sqrt(Math.abs(m.a * m.d - m.b * m.c));
  }

  let patterns = 0;
  function hatch(el, color, unit) {
    const { angle_deg, spacing_mm, width_mm } = style.hatch, id = 'ink-hatch-' + ++patterns;
    const size = spacing_mm * unit;
    const pattern = make('pattern', { id, width: size, height: size, patternUnits: 'userSpaceOnUse',
      patternTransform: `rotate(${90 + angle_deg})` });
    pattern.append(make('rect', { width: width_mm * unit, height: size, fill: color }));
    const defs = make('defs', {});
    defs.append(pattern);
    el.ownerSVGElement.prepend(defs);
    return `url(#${id})`;
  }

  function arrowhead(points, color, seed, unit, width) {
    const { head, length_mm, angle_deg, weight } = style.arrow;
    if (head === 'none') return [];
    const tip = points[points.length - 1], length = length_mm * unit;
    const base = [...points].reverse().find((p) => apart(p, tip) > length * 0.8) || points[0];
    const back = Math.atan2(base[1] - tip[1], base[0] - tip[0]), half = (angle_deg * Math.PI) / 180;
    const barb = (angle) => [tip[0] + length * Math.cos(angle), tip[1] + length * Math.sin(angle)];
    const a = barb(back - half), b = barb(back + half);
    const marks = [make('path', { fill: color,
      d: pen(head === 'filled' ? [a, tip, b, a] : [a, tip, b], seed + 'h', width * weight, 0, unit) })];
    if (head === 'filled') marks.push(make('path', { d: outline([a, tip, b], true), fill: color }));
    return marks;
  }

  function draw(shape) {
    const unit = unitOf(shape), has = (name) => shape.classList.contains(name);
    const seed = shape.tagName + [...shape.attributes]
      .filter((a) => /^(x|y|x1|x2|y1|y2|cx|cy|r|rx|ry|width|height|points|d)$/.test(a.name))
      .map((a) => a.name + a.value).join();
    const cue = style.cues[shape.dataset.cue];
    const color = cue && cue.treatment === 'outline' ? cue.color : shape.getAttribute('stroke') || style.ink.color;
    const width = style.ink.width_mm * unit * (parseFloat(shape.dataset.weight) || 1);
    const lines = trace(shape, STEP_MM * unit).map((points, i) => jitter(points, seed + i, style.ink.wobble_mm, unit));
    const strokes = lines.map((points, i) => pen(points, seed + i, width, style.ink.unevenness, unit, has('dashed'))).join('');
    const encloses = !/^(line|polyline)$/.test(shape.tagName) && !has('arrow') && !has('arrow-both');
    const area = lines.map((points) => outline(points, true)).join('');

    const group = make('g', {});
    for (const name of ['id', 'transform', 'opacity', 'clip-path'])
      if (shape.hasAttribute(name)) group.setAttribute(name, shape.getAttribute(name));
    if (has('ground')) group.classList.add('ground');
    const layer = (attrs) => group.append(make('path', attrs));

    let fill = encloses ? shape.getAttribute('fill') || 'none' : 'none';
    const rule = { 'fill-rule': shape.getAttribute('fill-rule') || 'nonzero' };
    if (has('shadow')) {
      const shadow = { fill: style.shadow.color,
        transform: `translate(${style.shadow.dx_mm * unit} ${style.shadow.dy_mm * unit})` };
      layer({ ...shadow, d: strokes });
      if (encloses) {
        layer({ ...shadow, ...rule, d: area });
        if (fill === 'none') fill = '#ffffff';
      }
    }
    if (encloses && cue && cue.treatment === 'fill') fill = cue.color;
    if (fill !== 'none') layer({ ...rule, d: area, fill });
    const cueHatch = cue && cue.treatment === 'hatch';
    if (encloses && (cueHatch || has('hatch')))
      layer({ ...rule, d: area, fill: hatch(shape, cueHatch ? cue.color : style.ink.color, unit) });
    layer({ d: strokes, fill: color });
    if (has('arrow') || has('arrow-both')) group.append(...arrowhead(lines[lines.length - 1], color, seed, unit, width));
    if (has('arrow-both')) group.append(...arrowhead([...lines[0]].reverse(), color, seed + 's', unit, width));
    shape.replaceWith(group);
  }

  // A copy of a label that only draws: the checker reads the original.
  function echo(text) {
    const copy = text.cloneNode(true);
    copy.removeAttribute('id');
    copy.classList.add('ink-echo');
    copy.setAttribute('aria-hidden', 'true');
    return copy;
  }

  function letter(text) {
    const unit = unitOf(text), { title_fill, title_outline_mm } = style.lettering;
    if (text.classList.contains('shadow')) {
      const copy = echo(text), { dx_mm, dy_mm, color } = style.shadow;
      copy.style.fill = copy.style.stroke = color;
      copy.style.strokeWidth = text.classList.contains('title') ? title_outline_mm * unit : 0;
      const group = make('g', { transform: `translate(${dx_mm * unit} ${dy_mm * unit})` });
      group.append(copy);
      text.before(group);
    }
    if (!text.classList.contains('title') || title_fill === 'solid') {
      if (!text.classList.contains('shadow')) return;
      // Solid letters over their own shadow: a white rim keeps the two apart.
      text.style.stroke = '#ffffff';
      text.style.strokeWidth = Math.max(0.5, 2 * title_outline_mm) * unit;
      text.style.strokeLinejoin = 'round';
      text.style.paintOrder = 'stroke';
      return;
    }
    text.style.stroke = style.ink.color;
    text.style.strokeWidth = title_outline_mm * unit;
    text.style.fill = '#ffffff';
    if (title_fill !== 'hatched') return;
    text.before(echo(text)); // white ground, so that a shadow stays behind the hatching
    text.style.fill = hatch(text, style.ink.color, unit);
  }

  // A reused icon becomes its own copy, so that its shapes take ink at their final size.
  function expand(use) {
    const icon = document.querySelector(use.getAttribute('href') || 'missing');
    if (!icon) return;
    const at = (name) => parseFloat(use.getAttribute(name)) || 0;
    const group = make('g', { transform: `${use.getAttribute('transform') || ''} translate(${at('x')} ${at('y')})` });
    let holder = group;
    if (icon.hasAttribute('viewBox')) {
      const [, , w, h] = icon.getAttribute('viewBox').split(/[\s,]+/).map(Number);
      holder = make('svg', { viewBox: icon.getAttribute('viewBox'), width: at('width') || w,
        height: at('height') || h, overflow: 'visible' });
      group.append(holder);
    }
    const copies = icon.tagName === 'symbol' ? [...icon.children] : [icon];
    for (const child of copies) {
      const copy = child.cloneNode(true);
      copy.removeAttribute('id');
      holder.append(copy);
    }
    use.replaceWith(group);
  }

  const drawn = (selector) => [...document.querySelectorAll(selector)].filter((el) => !el.closest('defs, symbol'));
  drawn('svg use').forEach(expand);
  drawn('svg :is(path, rect, circle, ellipse, line, polyline, polygon).ink').forEach(draw);
  drawn('svg text').forEach(letter);
})();
