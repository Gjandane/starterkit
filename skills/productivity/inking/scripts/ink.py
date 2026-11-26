#!/usr/bin/env python3
"""Draw a page source in a set of drawing rules, print it and check its labels.

  ink.py render <page>.src.html --style S.json --print P.json --orientation portrait|landscape
      writes <page>.html (self-contained) and <page>.png (150 dpi) beside the source
  ink.py check <page>.html [...]     exit 1 and list each label or margin at fault
  ink.py pdf <page>.html <out>.pdf   print one page at its paper size
  ink.py assemble <page>.html [...] --print P.json --out <set>.pdf --renders <folder>
      checks the pages, merges them in the order given and renders each merged page
  ink.py rounds <record>.md [...]    exit 1 and list each check round that lacks a reply
  ink.py looks <page>.html [...] [--earlier <set folder or House style .md> ...]
      [--fixed title ink main-colour cues] [--coloured-paper]
      measure each page's Look; exit 1 and list each pair too alike for a fresh round
  ink.py colours <image>             list a picture's main colours, greys included, each with its grey

Drawing commands find Chrome or Edge. INK_BROWSER names an executable to use instead.
Python 3.8 or later. Only assemble needs packages: pypdf and pymupdf.
"""
import argparse
import base64
import html
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / "fonts"
FACES = {  # family: [(weight, file)]
    "Patrick Hand": [(400, "PatrickHand-Regular.ttf")],
    "National Park": [(400, "NationalPark-Regular.ttf"), (700, "NationalPark-Bold.ttf")],
    "Londrina Solid": [(900, "LondrinaSolid-Black.ttf")],
    "Itim": [(400, "Itim-Regular.ttf")],
    "Cabin Sketch": [(700, "CabinSketch-Bold.ttf")],
    "Architects Daughter": [(400, "ArchitectsDaughter-Regular.ttf")],
    "Short Stack": [(400, "ShortStack-Regular.ttf")],
    "Comic Neue": [(400, "ComicNeue-Regular.ttf"), (700, "ComicNeue-Bold.ttf")],
    "Titan One": [(400, "TitanOne-Regular.ttf")],
    "Sniglet": [(800, "Sniglet-ExtraBold.ttf")],
    "Knewave": [(400, "Knewave-Regular.ttf")],
}
PX_PER_MM = 96 / 25.4
PNG_SCALE = 150 / 96
CHECK_SCALE = 2
SLACK_MM = 0.25  # how far a soft edge may pass a safe margin
RENDER_DPI = 150
RECORDS = {"checks.md": ("Reader", "Inspector"), "icons.md": ("Cold read", "Judge")}
VIEWS = {  # what the checker looks at: CSS laid over the page
    "letters": """* { visibility: hidden !important }
        html, body, .page { background: #fff !important }
        .ink-label, svg text:not(.ink-echo), svg text:not(.ink-echo) * { visibility: visible !important;
          fill: #f0f !important; color: #f0f !important; -webkit-text-fill-color: #f0f !important;
          stroke: none !important; text-shadow: none !important; background: none !important }""",
    "drawing": ".ink-label, svg text, svg text *, .ground, .ground * { visibility: hidden !important }",
    "stacked": """.ink-label, svg text:not(.ink-echo), svg text:not(.ink-echo) * {
          fill: #f0f !important; color: #f0f !important; -webkit-text-fill-color: #f0f !important;
          stroke: none !important; text-shadow: none !important; opacity: 1 !important }""",
}


class Stop(Exception):
    """A problem the caller can fix; the message says how."""


# ---- inputs ---------------------------------------------------------------

def number(low, high):
    def test(v):
        ok = isinstance(v, (int, float)) and not isinstance(v, bool) and low <= v <= high
        return None if ok else f"a number from {low} to {high}"
    return test


def one_of(*names):
    return lambda v: None if v in names else "one of " + ", ".join(names)


def colour(v):
    return None if isinstance(v, str) and re.fullmatch(r"#[0-9a-fA-F]{6}", v) else "a #rrggbb colour"


STYLE = {
    "ink": {"color": colour, "width_mm": number(0.1, 3), "wobble_mm": number(0, 3),
            "unevenness": number(0, 1)},
    "lettering": {"label_font": one_of(*FACES), "title_font": one_of(*FACES),
                  "title_fill": one_of("solid", "hatched", "outline"),
                  "title_outline_mm": number(0, 2)},
    "hatch": {"angle_deg": number(-90, 90), "spacing_mm": number(0.3, 10), "width_mm": number(0.05, 5)},
    "shadow": {"dx_mm": number(-10, 10), "dy_mm": number(-10, 10), "color": colour},
    "arrow": {"head": one_of("open", "filled", "none"), "length_mm": number(0.5, 20),
              "angle_deg": number(10, 60), "weight": number(0.2, 5)},
    "cues": {"*": {"color": colour, "treatment": one_of("fill", "hatch", "outline")}},
}
PRINT = {
    "paper": {"width_mm": number(50, 1000), "height_mm": number(50, 1000)},
    "margins_mm": {side: number(0, 100) for side in ("top", "right", "bottom", "left")},
}


def problems(data, shape, where):
    """Every way data differs from shape, as 'key: what it must be' lines."""
    if callable(shape):
        wanted = shape(data)
        return [f"{where}: must be {wanted}"] if wanted else []
    if not isinstance(data, dict):
        return [f"{where}: must be an object"]
    keys = {k: shape["*"] for k in data} if "*" in shape else shape
    found = [f"{where}.{k}: unknown key" for k in data if k not in keys]
    for key, inner in keys.items():
        found += problems(data[key], inner, f"{where}.{key}") if key in data else [f"{where}.{key}: missing"]
    return found


def read(path):
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as err:
        raise Stop(f"cannot read {path}: {err}")


def load(path, shape, name):
    try:
        data = json.loads(read(path))
    except ValueError as err:
        raise Stop(f"{path} is not JSON: {err}")
    found = problems(data, shape, name)
    if found:
        raise Stop(f"{path}:\n  " + "\n  ".join(found))
    return data


def layout(rules, orientation):
    """The page as it will be read: paper turned to the orientation, and its safe area."""
    short, long = sorted(rules["paper"].values())
    w, h = (short, long) if orientation == "portrait" else (long, short)
    m = rules["margins_mm"]
    page = {"width_mm": w, "height_mm": h, "margins_mm": m,
            "safe_width_mm": w - m["left"] - m["right"], "safe_height_mm": h - m["top"] - m["bottom"]}
    if page["safe_width_mm"] <= 0 or page["safe_height_mm"] <= 0:
        raise Stop("the margins leave no safe area on this paper")
    return page


# ---- browser --------------------------------------------------------------

def browser():
    chosen = os.environ.get("INK_BROWSER")
    if chosen:
        if not Path(chosen).is_file():
            raise Stop(f"INK_BROWSER names no file: {chosen}")
        return chosen
    known = []
    if sys.platform == "win32":
        roots = [os.environ.get(k) for k in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA")]
        known = [Path(root, tail) for tail in ("Google/Chrome/Application/chrome.exe",
                                               "Microsoft/Edge/Application/msedge.exe") for root in roots if root]
    elif sys.platform == "darwin":
        known = [Path(root, app) for app in ("Google Chrome.app/Contents/MacOS/Google Chrome",
                                             "Microsoft Edge.app/Contents/MacOS/Microsoft Edge")
                 for root in ("/Applications", Path.home() / "Applications")]
    for path in known:
        if path.is_file():
            return str(path)
    for name in ("google-chrome", "google-chrome-stable", "chrome", "microsoft-edge",
                 "microsoft-edge-stable", "msedge", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    raise Stop("no Chrome or Edge found. Install Google Chrome or Microsoft Edge, "
               "or set INK_BROWSER to its executable.")


def run_browser(page, *flags, output=None):
    """Open a page file in a fresh headless profile. Returns the DOM, or waits for the output file."""
    command = [browser(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--no-first-run",
               "--no-default-browser-check", "--virtual-time-budget=10000", *flags]
    profile = tempfile.mkdtemp(prefix="inking-")
    try:
        if output and Path(output).exists():
            Path(output).unlink()
        try:
            run = subprocess.run([*command, f"--user-data-dir={profile}", Path(page).resolve().as_uri()],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
        except subprocess.TimeoutExpired:
            raise Stop(f"{command[0]} did not finish {page} in 90 seconds")
        if not output:
            return run.stdout.decode("utf-8", "replace")
        for _ in range(50):  # Edge can return before its file is written
            if Path(output).exists() and Path(output).stat().st_size:
                return None
            time.sleep(0.1)
        raise Stop(f"{command[0]} wrote no {output}:\n" + run.stderr.decode("utf-8", "replace")[-800:])
    finally:
        shutil.rmtree(profile, ignore_errors=True)


def window_flags(page, scale):
    w, h = (round(page[k] * PX_PER_MM) for k in ("width_mm", "height_mm"))
    return [f"--window-size={w},{h}", f"--force-device-scale-factor={scale}"]


def screenshot(source, page, scale, png):
    """Screenshot a page file and confirm the PNG has the paper's pixel size."""
    run_browser(source, *window_flags(page, scale), f"--screenshot={Path(png).resolve()}", output=png)
    got = struct.unpack(">II", Path(png).read_bytes()[16:24])
    want = [page[k] * PX_PER_MM * scale for k in ("width_mm", "height_mm")]
    if any(abs(g - w) > 2 for g, w in zip(got, want)):
        raise Stop(f"{png} is {got[0]} x {got[1]} px; the paper is {want[0]:.0f} x {want[1]:.0f} px")
    return got


# ---- commands -------------------------------------------------------------

def font_faces(style):
    css = []
    for family in sorted({style["lettering"]["label_font"], style["lettering"]["title_font"]}):
        for weight, name in FACES[family]:
            data = base64.b64encode((FONTS / name).read_bytes()).decode()
            css.append(f"@font-face{{font-family:'{family}';font-weight:{weight};"
                       f"src:url(data:font/ttf;base64,{data}) format('truetype')}}")
    return "\n".join(css)


def embed(data):
    return json.dumps(data).replace("</", "<\\/")


def build(source, style, page, title):
    m, let, ink = page["margins_mm"], style["lettering"], style["ink"]["color"]
    title_weight = max(weight for weight, _ in FACES[let["title_font"]])
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>{html.escape(title)}</title>
<script type="application/json" id="ink-page">{embed(page)}</script>
<script type="application/json" id="ink-style">{embed(style)}</script>
<style>
@page {{ size: {page["width_mm"]}mm {page["height_mm"]}mm; margin: 0 }}
html, body {{ margin: 0; background: #fff }}
* {{ print-color-adjust: exact; -webkit-print-color-adjust: exact }}
.page {{ position: relative; overflow: hidden; width: {page["width_mm"]}mm; height: {page["height_mm"]}mm;
  color: {ink}; fill: {ink}; font-family: '{let["label_font"]}' }}
.safe {{ position: absolute; left: {m["left"]}mm; top: {m["top"]}mm;
  width: {page["safe_width_mm"]}mm; height: {page["safe_height_mm"]}mm }}
svg.board {{ display: block; width: 100%; height: 100%; overflow: visible }}
.title {{ font-family: '{let["title_font"]}'; font-weight: {title_weight} }}
</style>
<style>
{font_faces(style)}
</style></head>
<body><div class="page"><div class="safe">
{source}
</div></div>
<script>
{read(HERE / "ink.js")}
</script></body></html>
"""


def render(args):
    source = Path(args.source)
    if not source.name.endswith(".src.html"):
        raise Stop(f"{source}: name a page source <page>.src.html")
    text = read(source)
    if re.search(r"<(html|head|body)\b", text, re.I):
        raise Stop(f"{source}: a page source is a fragment, without <html>, <head> or <body>")
    style = load(args.style, STYLE, "style")
    unknown = set(re.findall(r"""data-cue=["']([^"']*)["']""", text)) - set(style["cues"])
    if unknown:
        raise Stop(f"{source}: cues the style does not define: {', '.join(sorted(unknown))}")
    page = layout(load(args.print, PRINT, "print"), args.orientation)
    out = source.with_name(source.name[:-len(".src.html")] + ".html")
    out.write_text(build(text, style, page, out.stem), encoding="utf-8", newline="\n")
    png = out.with_suffix(".png")
    w, h = screenshot(out, page, PNG_SCALE, png)
    print(f"{out}: {page['width_mm']:g} x {page['height_mm']:g} mm, "
          f"safe area {page['safe_width_mm']:g} x {page['safe_height_mm']:g} mm")
    print(f"{png}: {w} x {h} px at 150 dpi")
    board = re.search(r"""viewBox=["']\s*\S+\s+\S+\s+([\d.]+)\s+([\d.]+)""",
                      "".join(re.findall(r"""<svg\b[^>]*\bclass=["'][^"']*\bboard\b[^>]*>""", text)[:1]))
    if board:
        width, height = map(float, board.groups())
        unit = min(page["safe_width_mm"] / width, page["safe_height_mm"] / height)
        if abs(width - page["safe_width_mm"]) > 0.5 or abs(height - page["safe_height_mm"]) > 0.5:
            print(f"note: the board is {width:g} x {height:g}, so 1 unit prints as {unit:.2f} mm")


def answer(dom, path):
    """The JSON a page left in its #ink-out."""
    found = re.search(r'<pre id="ink-out">(.*?)</pre>', dom, re.S)
    if not found:
        raise Stop(f"the browser could not read {path}:\n{dom[-400:]}")
    return json.loads(html.unescape(found.group(1)))


ANSWER = """{ const out = document.createElement('pre'); out.id = 'ink-out';
  out.textContent = JSON.stringify(%s); document.body.append(out); }"""


def page_meta(text):
    """The paper and margins ink.py rendered a page with; None for any other page."""
    meta = re.search(r'<script type="application/json" id="ink-page">(.*?)</script>', text)
    return json.loads(meta.group(1)) if meta else None


def check_page(path, folder):
    """The findings on a rendered page, and how many labels were read."""
    text = read(path)
    page = page_meta(text)
    if not page:
        raise Stop(f"{path}: not a page that ink.py rendered")
    script = read(HERE / "check.js")
    base = Path(path).resolve().parent.as_uri()
    def view(name):
        file, head, tail = Path(folder, f"{name}.html"), VIEWS.get(name, ""), "inkLabels();"
        if name == "labels":
            tail = ANSWER % "inkLabels()"
        file.write_bytes(text.replace("</head>", f'<base href="{base}/"><style>{head}</style></head>', 1)
                         .replace("</body></html>", f"<script>{script}\n{tail}</script></body></html>").encode("utf-8"))
        if name == "labels":
            return answer(run_browser(file, *window_flags(page, 1), "--dump-dom"), path)
        png = Path(folder, f"{name}.png")
        screenshot(file, page, CHECK_SCALE, png)
        return base64.b64encode(png.read_bytes()).decode()

    with ThreadPoolExecutor(4) as pool:
        labels, *shots = pool.map(view, ["labels", *VIEWS])
    images = "".join(f'<img id="{name}" src="data:image/png;base64,{shot}">' for name, shot in zip(VIEWS, shots))
    sheet = Path(folder, "compare.html")
    compare = f"inkCompare({embed(labels)}, {embed(page)}, Object.fromEntries([...document.images].map((i) => [i.id, i])), {CHECK_SCALE}, {SLACK_MM})"
    sheet.write_text(f'<!doctype html><meta charset="utf-8"><body>{images}<script>{script}\n'
                     f"window.onload = () => {ANSWER % compare};</script></body>", encoding="utf-8")
    return answer(run_browser(sheet, "--dump-dom"), path), len(labels)


def check(args):
    code = 0
    for path in args.pages:
        with tempfile.TemporaryDirectory(prefix="inking-") as folder:
            findings, labels = check_page(path, folder)
        for finding in findings:
            print(f"{path}: {finding}")
        if findings:
            code = 1
        else:
            print(f"{path}: {labels} labels clear of ink, 8 pt or more and inside the safe margins")
    return code


NEUTRAL_CHROMA = 12  # channels closer than this are black, white or a grey between, never a colour
HUES = ((15, "red"), (40, "orange"), (70, "yellow"), (160, "green"), (195, "teal"),
        (250, "blue"), (290, "purple"), (345, "pink"), (361, "red"))
FIXABLE = ("title", "ink", "main-colour", "cues")
PIXELS_JS = """(() => { const img = document.images[0], c = document.createElement('canvas');
  c.width = img.naturalWidth; c.height = img.naturalHeight;
  const g = c.getContext('2d'); g.drawImage(img, 0, 0);
  const d = g.getImageData(0, 0, c.width, c.height).data, counts = {};
  for (let p = 0; p < d.length; p += 4) {
    const key = (d[p] >> 3) << 10 | (d[p + 1] >> 3) << 5 | d[p + 2] >> 3; counts[key] = (counts[key] || 0) + 1 }
  const at = (x, y) => [...d.slice((y * c.width + x) * 4, (y * c.width + x) * 4 + 3)];
  return { counts, corners: [at(0, 0), at(c.width - 1, 0), at(0, c.height - 1), at(c.width - 1, c.height - 1)] } })()"""


def colour_name(rgb):
    """The colour's everyday name, or None for black, white and grey."""
    r, g, b = rgb
    top, spread = max(rgb), max(rgb) - min(rgb)
    if spread < NEUTRAL_CHROMA:
        return None
    if top == r:
        hue = 60 * (g - b) / spread % 360
    elif top == g:
        hue = 60 * (b - r) / spread + 120
    else:
        hue = 60 * (r - g) / spread + 240
    if 15 <= hue < 50 and top < 160:
        return "brown"
    return next(name for edge, name in HUES if hue < edge)


def hex_of(rgb):
    return "#%02x%02x%02x" % tuple(rgb)


def grey(rgb):
    r, g, b = rgb
    return round(0.299 * r + 0.587 * g + 0.114 * b)


def main_colour(png):
    """The colour covering the most of a PNG (None when it holds none), that colour's share of
    the coloured area, and the first corner that is not white."""
    if not png.is_file():
        raise Stop(f"no image {png}")
    with tempfile.TemporaryDirectory(prefix="inking-") as folder:
        sheet = Path(folder, "count.html")
        sheet.write_text(f'<!doctype html><meta charset="utf-8"><body>'
                         f'<img src="data:image/png;base64,{base64.b64encode(png.read_bytes()).decode()}">'
                         f"<script>window.onload = () => {ANSWER % PIXELS_JS};</script></body>", encoding="utf-8")
        pixels = answer(run_browser(sheet, "--dump-dom"), png)
    area = {}
    for key, count in pixels["counts"].items():
        key = int(key)
        name = colour_name([(key >> shift & 31) * 8 + 4 for shift in (10, 5, 0)])
        if name:
            area[name] = area.get(name, 0) + count
    return (max(area, key=area.get) if area else None, max(area.values(), default=0) / max(sum(area.values()), 1),
            next((c for c in pixels["corners"] if min(c) < 250), None))


def title_treatment(style):
    return f'{style["lettering"]["title_font"]} {style["lettering"]["title_fill"]}'


def look_of(path):
    """What a rendered page shows of its Look: its style, the cues it uses and its pixels' colours."""
    text = read(path)
    style = re.search(r'<script type="application/json" id="ink-style">(.*?)</script>', text)
    png = Path(path).with_suffix(".png")
    if not style or not png.is_file():
        raise Stop(f"{path}: not a page that ink.py rendered beside its PNG")
    style = json.loads(style.group(1))
    source = text.split('<div class="safe">', 1)[-1].rsplit("<script>", 1)[0]
    used = sorted(set(re.findall(r"""data-cue=["']([^"']*)["']""", source)) & set(style["cues"]))
    main, share, paper = main_colour(png)
    palette = {name: [int(cue["color"][i:i + 2], 16) for i in (1, 3, 5)] for name, cue in style["cues"].items()}
    return {"main": main, "share": share, "title": title_treatment(style), "ink": style["ink"]["width_mm"],
            "palette": palette, "cues": {name: palette[name] for name in used}, "paper": paper}


def saved_rules(path):
    """The title treatment and ink width an earlier Look's saved rules state, or nothing."""
    block = None
    if path.is_dir():
        file = path / "style.json"
        if not file.is_file():
            file = path / "approved-sample.html"
            block = r'<script type="application/json" id="ink-style">(.*?)</script>'
    else:
        file, block = path, r"(?ms)^## Style rules\s.*?^```json\s*$(.*?)^```"
    if not file.is_file():
        return {}
    text = read(file)
    if block:
        found = re.search(block, text)
        text = found.group(1) if found else ""
    try:
        style = json.loads(text)
        return {"title": title_treatment(style), "ink": float(style["ink"]["width_mm"])}
    except (ValueError, KeyError, TypeError):
        return {}


def earlier_look(path):
    """What an approved set folder or a House style file shows of its Look. A value it does not
    show is left out: a House style has no page, so no main colour."""
    path = Path(path)
    if not path.exists():
        raise Stop(f"{path}: no such set folder or House style file")
    look = saved_rules(path)
    if path.is_dir():
        look["main"] = main_colour(path / "approved-sample.png")[0]
    return look


def look_faults(looks, fixed, coloured_paper):
    """What keeps a fresh round's Looks from being three different ones, each fault with its pages."""
    found = []
    for path, look in looks.items():
        greys = sorted((grey(rgb), name) for name, rgb in look["cues"].items())
        found += [f"{path}: cues {a} and {b} print {gb - ga} grey levels apart, under 30"
                  for (ga, a), (gb, b) in zip(greys, greys[1:]) if gb - ga < 30]
        if look["paper"] and not coloured_paper:
            found.append(f"{path}: coloured paper, {hex_of(look['paper'])} at the corners")
    pages = list(looks.items())
    for i, (one, a) in enumerate(pages):
        for two, b in pages[i + 1:]:
            pair = f"{one} and {two}"
            if "title" not in fixed and a["title"] == b["title"]:
                found.append(f"{pair}: the same title treatment, {a['title']}")
            if "ink" not in fixed and round(abs(a["ink"] - b["ink"]), 3) < 0.2:
                found.append(f"{pair}: ink {a['ink']:g} and {b['ink']:g} mm, under 0.2 mm apart")
            if "main-colour" not in fixed and a["main"] and a["main"] == b["main"]:
                found.append(f"{pair}: the same main colour, {a['main']}")
            shared = sorted({colour_name(c) for c in a["palette"].values()} & {colour_name(c) for c in b["palette"].values()} - {None})
            if "cues" not in fixed and len(shared) > 1:
                found.append(f"{pair}: {len(shared)} cue colours shared, {', '.join(shared)}")
    return found


COMPARED = {"main-colour": ("main", "main colour"), "title": ("title", "title treatment"),
            "ink": ("ink", "ink width")}


def apart(key, a, b):
    return round(abs(a - b), 3) >= 0.2 if key == "ink" else a != b


def named(choices):
    return ", ".join(COMPARED[choice][1] for choice in choices) or "nothing"


def against_earlier(pages, earlier, fixed):
    """Each page against each earlier Look: a line saying where they differ, the faults, and
    the comparisons left to the eye because the earlier Look does not show enough."""
    lines, faults, notes = [], [], []
    free = [choice for choice in COMPARED if choice not in fixed]
    needed = min(2, len(free))
    for one, a in pages.items():
        for two, b in earlier.items():
            shown = [choice for choice in free if COMPARED[choice][0] in b]
            differ = [c for c in shown if apart(c, a[COMPARED[c][0]], b[COMPARED[c][0]])]
            same = [choice for choice in shown if choice not in differ]
            lines.append(f"{one} against {two}: differs in {named(differ)}; alike in {named(same)}")
            due = min(needed, len(shown))
            if len(differ) < due:
                faults.append(f"{one} and {two}: too alike in {named(same)}; "
                              f"{due} of {named(shown)} must differ")
            if due < needed:
                unshown = [choice for choice in free if choice not in shown]
                notes.append(f"note: {one} and {two}: compare {named(unshown)} by eye; "
                             f"{needed - due} must differ")
    return lines, faults, notes


def looks(args):
    found = {path: look_of(path) for path in args.pages}
    for path, look in found.items():
        cues = "; ".join(f"{name} {hex_of(rgb)} ({colour_name(rgb) or 'neutral'}, grey {grey(rgb)})"
                         for name, rgb in look["cues"].items()) or "none in use"
        print(f"{path}: main colour {look['main'] or 'none'} ({look['share']:.0%} of the coloured area), "
              f"title {look['title']}, ink {look['ink']:g} mm, cues {cues}")
    faults = look_faults(found, set(args.fixed), args.coloured_paper)
    earlier = {path: earlier_look(path) for path in args.earlier}
    for path, look in earlier.items():
        main = f"main colour {look['main'] or 'none'}" if "main" in look else "main colour not shown"
        rules = f"title {look['title']}, ink {look['ink']:g} mm" if "title" in look else "title and ink not shown"
        print(f"{path}: earlier Look, {main}, {rules}")
    lines, too_alike, notes = against_earlier(found, earlier, set(args.fixed))
    faults += too_alike
    for line in [*lines, *notes, *faults]:
        print(line)
    if not faults:
        print("the Looks differ as a fresh round needs")
    return 1 if faults else 0


COLOURS_JS = """(() => { const img = document.images[0], c = document.createElement('canvas');
  c.width = img.naturalWidth; c.height = img.naturalHeight;
  const g = c.getContext('2d'); g.fillStyle = '#fff'; g.fillRect(0, 0, c.width, c.height); g.drawImage(img, 0, 0);
  const d = g.getImageData(0, 0, c.width, c.height).data, exact = new Map(), near = {};
  for (let p = 0; p < d.length; p += 4) {
    const key = d[p] << 16 | d[p + 1] << 8 | d[p + 2]; exact.set(key, (exact.get(key) || 0) + 1) }
  for (const [key, n] of exact) {
    const bucket = key >> 19 << 10 | (key >> 11 & 31) << 5 | key >> 3 & 31;
    const e = near[bucket] || (near[bucket] = [0, 0, 0]); e[0] += n; if (n > e[1]) { e[1] = n; e[2] = key } }
  return { total: d.length / 4, found: Object.values(near).map(e => [e[0], e[2]]) } })()"""
IMAGE_TYPES = {".png": "png", ".jpg": "jpeg", ".jpeg": "jpeg", ".webp": "webp", ".gif": "gif"}
SAME_COLOUR = 16  # channels this close are one colour with its soft edges
LEAST_SHARE = 0.003
MOST_COLOURS = 20


def colours(args):
    path = Path(args.image)
    kind = IMAGE_TYPES.get(path.suffix.lower())
    if not kind or not path.is_file():
        raise Stop(f"{path}: name a picture, {', '.join(IMAGE_TYPES)}")
    with tempfile.TemporaryDirectory(prefix="inking-") as folder:
        sheet = Path(folder, "colours.html")
        sheet.write_text(f'<!doctype html><meta charset="utf-8"><body>'
                         f'<img src="data:image/{kind};base64,{base64.b64encode(path.read_bytes()).decode()}">'
                         f"<script>window.onload = () => {ANSWER % COLOURS_JS};</script></body>", encoding="utf-8")
        pixels = answer(run_browser(sheet, "--dump-dom"), path)
    merged = []  # [pixels, rgb], each group named by its commonest colour
    for count, key in sorted(pixels["found"], reverse=True):
        rgb = [key >> shift & 255 for shift in (16, 8, 0)]
        for group in merged:
            if max(abs(a - b) for a, b in zip(rgb, group[1])) <= SAME_COLOUR:
                group[0] += count
                break
        else:
            merged.append([count, rgb])
    shown = [group for group in sorted(merged, key=lambda g: -g[0]) if group[0] >= LEAST_SHARE * pixels["total"]]
    for count, rgb in shown[:MOST_COLOURS]:
        print(f"{hex_of(rgb)} {colour_name(rgb) or 'neutral'}, grey {grey(rgb)}, {count / pixels['total']:.1%}")


def print_pdf(page, out):
    run_browser(page, "--no-pdf-header-footer", f"--print-to-pdf={Path(out).resolve()}", output=out)


def ink_box_faults(image, margins):
    """The margins a grey render's ink enters, for a page that carries no layout to check."""
    dark = bytes(1 if value < 245 else 0 for value in range(256))
    rows = [image.samples[y * image.stride:y * image.stride + image.width].translate(dark)
            for y in range(image.height)]
    inked = [y for y, row in enumerate(rows) if 1 in row]
    if not inked:
        return []
    mm = 25.4 / RENDER_DPI
    clear = {"left": min(rows[y].find(1) for y in inked), "top": inked[0],
             "right": min(image.width - 1 - rows[y].rfind(1) for y in inked),
             "bottom": image.height - 1 - inked[-1]}
    return [f"a mark runs {margins[side] - pixels * mm:.1f} mm into the {side} margin"
            for side, pixels in clear.items() if margins[side] - pixels * mm > SLACK_MM]


def page_list_faults(pages):
    """What is wrong with the page list itself, against the files in the pages' set folder."""
    found, listed = [], set()
    for path in pages:
        if not path.is_file():
            found.append(f"{path}: no such page")
        if path.resolve() in listed:
            found.append(f"{path}: listed twice")
        listed.add(path.resolve())
    # A set's pages sit in <set folder>/<NN>-<slug>/.
    sets = sorted({page.parent.parent for page in listed if re.fullmatch(r"\d\d-.+", page.parent.name)})
    if len(sets) > 1:
        found.append("the pages come from more than one set folder: " + ", ".join(map(str, sets)))
    for set_folder in sets:
        for path in sorted(set_folder.glob("[0-9][0-9]-*/page-*.html")):
            if re.fullmatch(r"page-\d+\.html", path.name) and path.resolve() not in listed:
                found.append(f"{path}: in the set folder and missing from the page list")
    return found


def assemble(args):
    try:
        import pymupdf
        from pypdf import PdfReader, PdfWriter
    except ImportError as err:
        raise Stop(f"assemble needs pypdf and pymupdf ({err}). Run: python -m pip install pypdf pymupdf")
    rules = load(args.print, PRINT, "print")
    paper = sorted(rules["paper"].values())
    pages = [Path(page) for page in args.pages]
    out, renders = Path(args.out).resolve(), Path(args.renders).resolve()
    faults = page_list_faults(pages)
    if not faults:
        renders.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="inking-") as folder:
            parts = []
            for index, path in enumerate(pages, 1):
                meta = page_meta(read(path))
                if meta:
                    if (sorted((meta["width_mm"], meta["height_mm"])) != paper
                            or meta["margins_mm"] != rules["margins_mm"]):
                        faults.append(f"{path}: rendered with other paper or margins than {args.print}")
                    with tempfile.TemporaryDirectory(prefix="inking-") as views:
                        faults += [f"{path}: {finding}" for finding in check_page(path, views)[0]]
                part = Path(folder, f"part-{index}.pdf")
                print_pdf(path, part)
                sheets = PdfReader(str(part)).pages
                if len(sheets) != 1:
                    faults.append(f"{path}: prints on {len(sheets)} pages, so it spills")
                    continue
                size = [float(sheets[0].mediabox.width), float(sheets[0].mediabox.height)]
                # A rendered page names its orientation; any other page may take either.
                got, want = (size, [meta["width_mm"], meta["height_mm"]]) if meta else (sorted(size), paper)
                if any(abs(g - w * 72 / 25.4) > 1 for g, w in zip(got, want)):
                    faults.append(f"{path}: prints at {size[0]:.0f} x {size[1]:.0f} pt, "
                                  f"not {want[0]:g} x {want[1]:g} mm")
                document = pymupdf.open(str(part))
                try:
                    document[0].get_pixmap(dpi=RENDER_DPI).save(str(renders / f"pdf-{index}.png"))
                    if not meta:
                        grey = document[0].get_pixmap(dpi=RENDER_DPI, colorspace=pymupdf.csGRAY)
                        faults += [f"{path}: {fault}" for fault in ink_box_faults(grey, rules["margins_mm"])]
                finally:
                    document.close()
                parts.append(str(part))
            if not faults:
                merged = PdfWriter()
                for part in parts:
                    merged.append(part)
                out.parent.mkdir(parents=True, exist_ok=True)
                with open(out, "wb") as file:
                    merged.write(file)
                merged.close()
    for fault in faults:
        print(fault)
    if faults:
        print(f"{out}: not written")
        return 1
    for index, path in enumerate(pages, 1):
        print(f"{renders / f'pdf-{index}.png'}: page {index}, from {path.resolve()}")
    print(f"{out}: {len(pages)} pages")
    return 0


def round_faults(path):
    """Every way a record's rounds fall short: numbered from 1, each with both replies."""
    wanted = RECORDS.get(Path(path).name)
    if not wanted:
        raise Stop(f"{path}: name a record {' or '.join(RECORDS)}")
    parts = re.split(r"(?m)^## Round (\d+)\b.*$", read(path))
    numbers, bodies = [int(n) for n in parts[1::2]], parts[2::2]
    if not numbers:
        return ["no '## Round <n>' heading"]
    found = []
    if numbers != list(range(1, len(numbers) + 1)):
        found.append(f"rounds run {', '.join(map(str, numbers))}; number them from 1, one heading each")
    marker = r"(?m)^(" + "|".join(wanted) + r"):"
    for number_, body in zip(numbers, bodies):
        pieces = re.split(marker, body)
        replied = {name for name, text in zip(pieces[1::2], pieces[2::2]) if text.strip()}
        found += [f"round {number_}: no reply under a '{name}:' line" for name in wanted if name not in replied]
    return found


def rounds(args):
    code = 0
    for path in args.records:
        found = round_faults(path)
        for fault in found:
            print(f"{path}: {fault}")
        if found:
            code = 1
        else:
            print(f"{path}: every round has both replies")
    return code


def main():
    for stream in (sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("render")
    command.add_argument("source")
    command.add_argument("--style", required=True)
    command.add_argument("--print", required=True)
    command.add_argument("--orientation", required=True, choices=("portrait", "landscape"))
    command.set_defaults(run=render)
    command = commands.add_parser("check")
    command.add_argument("pages", nargs="+")
    command.set_defaults(run=check)
    command = commands.add_parser("pdf")
    command.add_argument("page")
    command.add_argument("out")
    command.set_defaults(run=lambda args: print_pdf(args.page, args.out))
    command = commands.add_parser("assemble")
    command.add_argument("pages", nargs="+")
    command.add_argument("--print", required=True)
    command.add_argument("--out", required=True)
    command.add_argument("--renders", required=True)
    command.set_defaults(run=assemble)
    command = commands.add_parser("rounds")
    command.add_argument("records", nargs="+")
    command.set_defaults(run=rounds)
    command = commands.add_parser("looks")
    command.add_argument("pages", nargs="+")
    command.add_argument("--earlier", nargs="+", default=[])
    command.add_argument("--fixed", nargs="+", default=[], choices=FIXABLE)
    command.add_argument("--coloured-paper", action="store_true")
    command.set_defaults(run=looks)
    command = commands.add_parser("colours")
    command.add_argument("image")
    command.set_defaults(run=colours)
    args = parser.parse_args()
    try:
        return args.run(args) or 0
    except Stop as stop:
        print(f"ink.py: {stop}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
