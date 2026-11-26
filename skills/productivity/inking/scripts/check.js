// The two halves of ink.py check that run in the browser.

// On the page: wrap the labels so that a view can hide or recolour them, and
// list each one with its box in CSS pixels.
function inkLabels() {
  const labels = [], seen = new Set(), nodes = [];
  const walker = document.createTreeWalker(document.querySelector('.page'), NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    const parent = node.parentElement;
    if (!node.data.trim() || parent.closest('style, script, title, desc, defs, symbol, .ink-echo')) continue;
    let el = parent.closest('svg text');
    if (el) {
      if (seen.has(el)) continue;
      seen.add(el);
    } else {
      el = document.createElement('span');
      el.className = 'ink-label';
      node.replaceWith(el);
      el.append(node);
    }
    const frame = el.closest('svg text, foreignObject'), m = frame ? frame.getScreenCTM() : new DOMMatrix();
    const em = parseFloat(getComputedStyle(el).fontSize) * Math.sqrt(Math.abs(m.a * m.d - m.b * m.c));
    const box = el.getBoundingClientRect();
    if (box.width && box.height)
      labels.push({ text: el.textContent.trim().replace(/\s+/g, ' '), em, x: box.x, y: box.y, w: box.width, h: box.height });
  }
  return labels;
}

// Over three views of the page: "letters" (labels alone, magenta), "drawing"
// (everything but labels and grounds) and "stacked" (the page, labels
// magenta). One label colour in both views gives one antialiasing.
function inkCompare(labels, page, images, scale, slackMm) {
  const mm = (96 / 25.4) * scale, pixels = {}, findings = [];
  let W, H;
  for (const name in images) {
    const canvas = document.createElement('canvas');
    W = canvas.width = images[name].naturalWidth;
    H = canvas.height = images[name].naturalHeight;
    const pen = canvas.getContext('2d');
    pen.drawImage(images[name], 0, 0);
    pixels[name] = pen.getImageData(0, 0, W, H).data;
  }
  const rgb = (name, x, y) => [...pixels[name].subarray((y * W + x) * 4, (y * W + x) * 4 + 3)];
  const place = (x, y) => `${(x / mm).toFixed(0)} mm from the left, ${(y / mm).toFixed(0)} mm from the top`;

  // Grow or shrink a mask by r, one axis at a time.
  function spread(mask, w, h, r, grow) {
    for (const [step, length, lines, across] of [[1, w, h, w], [w, h, w, 1]]) {
      const out = new Uint8Array(mask.length);
      for (let l = 0; l < lines; l++)
        for (let i = 0; i < length; i++) {
          let v = !grow;
          for (let k = Math.max(0, i - r); k <= Math.min(length - 1, i + r) && v !== grow; k++)
            if (!!mask[l * across + k * step] === grow) v = grow;
          out[l * across + i * step] = v;
        }
      mask = out;
    }
    return mask;
  }

  // Marks and labels stay inside the safe margins; the slack allows for a soft edge.
  const { left, top, right, bottom } = page.margins_mm, slack = slackMm * mm, over = { left: 0, top: 0, right: 0, bottom: 0 };
  const safe = { left: left * mm, top: top * mm, right: (page.width_mm - right) * mm, bottom: (page.height_mm - bottom) * mm };
  for (let y = 0; y < H; y++)
    for (let x = 0; x < W; x++) {
      const past = { left: safe.left - x, top: safe.top - y, right: x + 1 - safe.right, bottom: y + 1 - safe.bottom };
      if (Math.max(past.left, past.top, past.right, past.bottom) <= slack) continue;
      if (Math.min(...rgb('drawing', x, y), ...rgb('letters', x, y)) >= 245) continue;
      for (const side in over) over[side] = Math.max(over[side], past[side]);
    }
  for (const side in over)
    if (over[side] > slack) findings.push(`a mark runs ${(over[side] / mm).toFixed(1)} mm into the ${side} margin`);

  for (const label of labels) {
    const points = (label.em / 96) * 72;
    if (points < 7.95) findings.push(`"${label.text}" prints at ${points.toFixed(1)} pt, and 8 pt is the least`);
    // The label's own area: its letters, the gaps between them closed, and 0.3 mm around.
    const gap = Math.max(2, Math.round(0.18 * label.em * scale)), pad = Math.round(0.3 * mm), edge = gap + pad;
    const bx0 = Math.floor(label.x * scale), bx1 = Math.ceil((label.x + label.w) * scale);
    const by0 = Math.floor(label.y * scale), by1 = Math.ceil((label.y + label.h) * scale);
    const x0 = Math.max(0, bx0 - edge), x1 = Math.min(W, bx1 + edge), y0 = Math.max(0, by0 - edge), y1 = Math.min(H, by1 + edge);
    const w = x1 - x0, h = y1 - y0;
    let area = new Uint8Array(Math.max(0, w) * Math.max(0, h)), letters = 0, buried = 0;
    for (let y = Math.max(0, by0); y < Math.min(H, by1); y++)
      for (let x = Math.max(0, bx0); x < Math.min(W, bx1); x++) {
        const paper = rgb('letters', x, y)[1]; // green: 255 on bare paper, 0 under a letter
        if (paper < 128) area[(y - y0) * w + x - x0] = 1;
        if (paper > 40) continue;
        const [r, g, b] = rgb('stacked', x, y);
        letters++;
        if (r < 160 || g > 96 || b < 160) buried++;
      }
    if (!letters) continue;
    area = spread(spread(area, w, h, edge, true), w, h, gap, false);

    // Its ground is the colour most of that area has; any other colour there is ink.
    const tally = new Map(), inside = [];
    for (let y = 0; y < h; y++)
      for (let x = 0; x < w; x++)
        if (area[y * w + x]) {
          const color = rgb('drawing', x + x0, y + y0), key = color.map((v) => v >> 4).join();
          const entry = tally.get(key) || { count: 0, color };
          entry.count++;
          tally.set(key, entry);
          inside.push({ x: x + x0, y: y + y0, color });
        }
    const ground = [...tally.values()].sort((a, b) => b.count - a.count)[0].color;
    const ink = inside.filter((p) => p.color.some((v, i) => Math.abs(v - ground[i]) > 48));
    if (ink.length >= 6) {
      const middle = (axis) => ink.reduce((sum, p) => sum + p[axis], 0) / ink.length;
      findings.push(`ink crosses "${label.text}" at ${place(middle('x'), middle('y'))}`);
    } else if (buried / letters > 0.05)
      findings.push(`a drawing covers "${label.text}" at ${place((bx0 + bx1) / 2, (by0 + by1) / 2)}`);
  }
  return findings;
}
