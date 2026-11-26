"""Tests for the inking skill's command line, through a real headless browser.
Usage: python scripts/test_inking.py   (needs Chrome or Edge; the assemble
tests are skipped without pypdf and pymupdf)
"""
import importlib.util
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent / "skills" / "productivity" / "inking"
INK = SKILL / "scripts" / "ink.py"

STYLE, A4 = (json.loads((SKILL / "example" / name).read_text(encoding="utf-8")) for name in ("style.json", "print.json"))

# A rain gauge on a 186 x 273 board: one label, and a free place for a stroke.
PAGE = """<svg class="board" viewBox="0 0 186 273">
<text class="title" x="20" y="40" font-size="22">Rain gauge</text>
<rect class="ink shadow" data-cue="water" x="40" y="150" width="50" height="80"/>
<text id="label" x="40" y="120" font-size="8">Read the water level</text>
%s
</svg>"""


PDF_PACKAGES = all(importlib.util.find_spec(name) for name in ("pypdf", "pymupdf"))


def png_size(path):
    return struct.unpack(">II", Path(path).read_bytes()[16:24])


class Inking(unittest.TestCase):
    def setUp(self):
        # A space in the folder name: the plugin's users have them.
        self.dir = Path(tempfile.mkdtemp(prefix="ink test "))
        self.addCleanup(shutil.rmtree, self.dir, True)

    def write(self, name, data):
        path = self.dir / name
        path.write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
        return path

    def ink(self, *args, **env):
        return subprocess.run([sys.executable, str(INK), *map(str, args)], text=True,
                              encoding="utf-8", capture_output=True, env={**os.environ, **env})

    def render(self, marks="", style=STYLE, print_=A4, orientation="portrait", name="page-1", **env):
        src = self.write(name + ".src.html", PAGE % marks)
        run = self.ink("render", src, "--style", self.write("style.json", style),
                       "--print", self.write("print.json", print_), "--orientation", orientation, **env)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        return self.dir / (name + ".html")

    def test_render_writes_a_self_contained_page_and_a_150_dpi_png(self):
        page = self.render()
        w, h = png_size(page.with_suffix(".png"))
        self.assertLessEqual(abs(w - 1240), 2)
        self.assertLessEqual(abs(h - 1754), 2)
        self.assertIn("data:font/ttf;base64,", page.read_text(encoding="utf-8"))
        self.assertNotIn("inking", page.read_text(encoding="utf-8"))

    def test_orientation_turns_the_paper(self):
        w, h = png_size(self.render(orientation="landscape").with_suffix(".png"))
        self.assertLessEqual(abs(w - 1754), 2)
        self.assertLessEqual(abs(h - 1240), 2)

    def test_a_board_that_does_not_fit_the_safe_area_is_named_with_its_scale(self):
        src = self.write("page-1.src.html", PAGE % "")
        rules = ("--style", self.write("style.json", STYLE), "--print", self.write("print.json", A4))
        self.assertNotIn("note:", self.ink("render", src, *rules, "--orientation", "portrait").stdout)
        # 186 mm of height for a 273-unit board
        self.assertIn("1 unit prints as 0.68 mm", self.ink("render", src, *rules, "--orientation", "landscape").stdout)

    def test_paper_dimensions_set_the_png_size(self):
        small = {"paper": {"width_mm": 105, "height_mm": 148},
                 "margins_mm": {"top": 5, "right": 5, "bottom": 5, "left": 5}}
        w, h = png_size(self.render(print_=small).with_suffix(".png"))
        self.assertLessEqual(abs(w - 620), 2)
        self.assertLessEqual(abs(h - 874), 2)

    def test_the_same_inputs_draw_the_same_page_and_a_style_change_draws_another(self):
        first = self.render().with_suffix(".png").read_bytes()
        self.assertEqual(first, self.render().with_suffix(".png").read_bytes())
        for part, change in {"ink": {"wobble_mm": 1}, "shadow": {"dx_mm": -3},
                             "lettering": {"label_font": "National Park"},
                             "hatch": {"spacing_mm": 2}, "cues": {"water": {"color": "#f2c14e", "treatment": "hatch"}}}.items():
            with self.subTest(part):
                style = {**STYLE, part: {**STYLE[part], **change}}
                self.assertNotEqual(first, self.render(style=style).with_suffix(".png").read_bytes())

    def test_a_page_embeds_the_title_face_its_style_names(self):
        for face in ("Londrina Solid", "Cabin Sketch"):
            with self.subTest(face):
                style = {**STYLE, "lettering": {**STYLE["lettering"], "title_font": face, "title_fill": "solid"}}
                self.assertIn(f"@font-face{{font-family:'{face}'", self.render(style=style).read_text(encoding="utf-8"))

    def test_each_new_title_face_renders_and_checks_clear_in_every_fill(self):
        for face in ("Titan One", "Sniglet", "Knewave"):
            for fill in ("solid", "hatched", "outline"):
                with self.subTest(f"{face} {fill}"):
                    style = {**STYLE, "lettering": {**STYLE["lettering"], "title_font": face, "title_fill": fill}}
                    page = self.render(style=style)
                    self.assertIn(f"@font-face{{font-family:'{face}'", page.read_text(encoding="utf-8"))
                    run = self.ink("check", page)
                    self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_rules_that_are_incomplete_or_misspelled_stop_the_render(self):
        src = self.write("page-1.src.html", PAGE % "")
        for style, named in (({k: v for k, v in STYLE.items() if k != "arrow"}, "style.arrow: missing"),
                             ({**STYLE, "ink": {**STYLE["ink"], "colour": "#000000"}}, "style.ink.colour: unknown key"),
                             ({**STYLE, "cues": {}}, "water")):
            with self.subTest(named):
                run = self.ink("render", src, "--style", self.write("style.json", style), "--print",
                               self.write("print.json", A4), "--orientation", "portrait")
                self.assertEqual(run.returncode, 2)
                self.assertIn(named, run.stderr)

    def test_a_missing_browser_stops_with_what_to_install(self):
        self.render()
        # Windows refills PROGRAMFILES in a new process, so empty the environment inside it.
        bare = ("import os, runpy, sys; os.environ.clear(); os.environ['PATH'] = os.getcwd(); sys.platform = 'linux'; "
                "sys.argv = sys.argv[1:]; runpy.run_path(sys.argv[0], run_name='__main__')")
        run = subprocess.run([sys.executable, "-c", bare, str(INK), "pdf", "page-1.html", "part.pdf"], text=True,
                             capture_output=True, cwd=self.dir)
        self.assertEqual(run.returncode, 2)
        self.assertIn("Install Google Chrome or Microsoft Edge", run.stderr)

    def test_a_browser_is_discovered_and_a_named_one_is_used_instead(self):
        page = self.render(INK_BROWSER="")
        run = self.ink("pdf", page, self.dir / "part.pdf", INK_BROWSER=str(self.dir / "nowhere"))
        self.assertEqual(run.returncode, 2)
        self.assertIn("nowhere", run.stderr)

    def test_an_8_pt_label_is_clear_in_every_label_face_and_a_smaller_one_is_found(self):
        for face in ("Patrick Hand", "Itim", "National Park", "Architects Daughter", "Short Stack", "Comic Neue"):
            style = {**STYLE, "lettering": {**STYLE["lettering"], "label_font": face}}
            for weight in (400, 700):
                with self.subTest(f"{face} {weight}"):
                    code, said = self.check(f'<text x="110" y="200" font-size="2.9" font-weight="{weight}">Every drop '
                                            'counts</text><rect class="ink shadow" x="108" y="210" width="50" height="20"/>'
                                            f'<text x="112" y="220" font-size="3.2" font-weight="{weight}">In a box</text>',
                                            style=style)
                    self.assertEqual(code, 0, said)
        code, said = self.check('<text x="110" y="200" font-size="2">Too small</text>')
        self.assertEqual(code, 1, said)
        self.assertIn('"Too small" prints at 5.7 pt', said)

    def check(self, marks, **kw):
        run = self.ink("check", self.render(marks, **kw))
        return run.returncode, run.stdout + run.stderr

    def test_a_stroke_through_a_label_is_found_and_moving_only_the_stroke_clears_it(self):
        code, said = self.check('<path class="ink" d="M30 117 L120 119"/>')
        self.assertEqual(code, 1, said)
        self.assertIn('ink crosses "Read the water level"', said)
        code, said = self.check('<path class="ink" d="M30 127 L120 129"/>')
        self.assertEqual(code, 0, said)

    CROSSED = {
        "a hairline": '<line x1="30" y1="117" x2="120" y2="118" stroke="#1a1a1a" stroke-width="0.15"/>',
        "a line between two words": '<line class="ink" x1="56.6" y1="105" x2="56.6" y2="130"/>',
        "a stroke over a ground": '<rect class="ground" x="112" y="156" width="20" height="10" fill="#f2c14e"/>'
                                  '<text x="116" y="165" font-size="8">Wet weather</text>'
                                  '<path class="ink" d="M105 161 L165 163"/>',
        "a rotated label": '<text transform="rotate(-90 120 200)" x="120" y="200" font-size="8">Pour it out</text>'
                           '<path class="ink" d="M100 180 L150 182"/>',
        "a wrapped label": '<foreignObject x="110" y="150" width="50" height="30"><p style="margin:0;font-size:8px">'
                           'Empty it every <b>morning</b></p></foreignObject><path class="ink" d="M105 154 L165 155"/>',
        "ink of the label's own colour on a fill": '<rect class="ink" data-cue="water" x="112" y="60" width="70" height="30"/>'
                           '<text x="118" y="78" font-size="8">Rain falls</text><path class="ink" d="M116 75 L150 76"/>',
    }
    CLEAR = {
        "a label on a filled panel": '<rect class="ink shadow" data-cue="water" x="110" y="150" width="60" height="24"/>'
                                     '<text x="116" y="165" font-size="8">Wet weather</text>',
        "a white label on a dark fill": '<rect x="110" y="150" width="60" height="24" fill="#222222"/>'
                                        '<text x="116" y="165" font-size="8" fill="#ffffff">Night rain</text>',
        "a highlight behind part of a label": '<rect class="ground" x="112" y="156" width="20" height="10" fill="#f2c14e"/>'
                                                '<text x="116" y="165" font-size="8">Wet weather</text>',
        "a hatched title with a shadow": '<text class="title shadow" x="20" y="90" font-size="18">Water</text>',
        "a reused icon with its own label": '<defs><symbol id="drop" viewBox="0 0 20 30"><path class="ink" '
            'd="M10 2 C2 14 2 26 10 27 C18 26 18 14 10 2 Z"/><text x="7" y="22" font-size="8">1</text></symbol></defs>'
            '<use href="#drop" x="110" y="200" width="40" height="60"/>',
    }

    def test_ink_is_found_across_a_label(self):
        for name, marks in self.CROSSED.items():
            with self.subTest(name):
                code, said = self.check(marks)
                self.assertEqual(code, 1, said)
                self.assertEqual(said.count("ink crosses"), 1, said)

    def test_a_label_clear_of_ink_passes(self):
        for name, marks in self.CLEAR.items():
            with self.subTest(name):
                code, said = self.check(marks)
                self.assertEqual(code, 0, said)

    def test_a_drawing_that_hides_part_of_a_label_is_found(self):
        code, said = self.check('<rect x="35" y="105" width="30" height="25" fill="#ffffff"/>')
        self.assertEqual(code, 1, said)
        self.assertIn('covers "Read the water level"', said)

    def test_a_mark_outside_the_safe_margins_is_found_and_a_ground_may_run_to_the_edge(self):
        code, said = self.check('<path class="ink" d="M-6 200 L20 200"/>')
        self.assertEqual(code, 1, said)
        self.assertIn("left margin", said)
        code, said = self.check('<rect class="ground" x="-12" y="240" width="210" height="60" fill="#dddddd"/>')
        self.assertEqual(code, 0, said)

    def test_a_page_prints_to_pdf_at_its_paper_size(self):
        out = self.dir / "part.pdf"
        run = self.ink("pdf", self.render(orientation="landscape"), out)
        self.assertEqual(run.returncode, 0, run.stderr)
        boxes = re.findall(rb"/MediaBox \[0 0 ([\d.]+) ([\d.]+)\]", out.read_bytes())
        self.assertEqual(len(boxes), 1)
        self.assertLessEqual(abs(float(boxes[0][0]) - 841.89), 1)
        self.assertLessEqual(abs(float(boxes[0][1]) - 595.28), 1)

    def approved_set(self, name, style, marks=""):
        """A set folder as older runs saved it: no approved-sample.md."""
        page = self.render(marks, style=style, name="sample-" + name)
        folder = self.dir / "sketchnotes" / name
        folder.mkdir(parents=True)
        shutil.copy(page, folder / "approved-sample.html")
        shutil.copy(page.with_suffix(".png"), folder / "approved-sample.png")
        (folder / "style.json").write_text(json.dumps(style), encoding="utf-8")
        return folder

    def house_style(self, style):
        return self.write("mine.md", "# House style: mine\n\n## Principles\n\n- **Ink:** firm\n\n"
                          "## Style rules\n\n```json\n%s\n```\n" % json.dumps(style, indent=2))

    def earlier(self, page, *earlier, fixed=()):
        return self.looks(page, "--earlier", *earlier, fixed=fixed)

    def test_a_page_too_like_an_approved_sample_is_named_and_rules_come_from_the_page_too(self):
        wider = {**STYLE, "ink": {**STYLE["ink"], "width_mm": STYLE["ink"]["width_mm"] + 0.3}}
        folder = self.approved_set("rain", STYLE)
        page = self.render(style=wider, name="new")  # same title and main colour, wider ink
        for missing in (None, "style.json"):
            if missing:
                (folder / missing).unlink()
            code, said = self.earlier(page, folder)
            self.assertEqual(code, 1, said)
            self.assertIn("differs in ink width; alike in main colour, title treatment", said)
            self.assertIn("2 of main colour, title treatment, ink width must differ", said)
        code, said = self.earlier(page, folder, fixed=("title", "main-colour"))
        self.assertEqual(code, 0, said)
        code, said = self.earlier(page, folder, fixed=("ink",))
        self.assertEqual(code, 1, said)

    def test_a_house_style_is_compared_on_title_and_ink_and_a_fixed_one_leaves_colour_to_the_eye(self):
        other = {**STYLE, "ink": {**STYLE["ink"], "width_mm": STYLE["ink"]["width_mm"] + 0.2},
                 "lettering": {**STYLE["lettering"], "title_font": "Knewave", "title_fill": "solid"}}
        page = self.render(style=other, name="new")
        code, said = self.earlier(page, self.house_style(STYLE))
        self.assertEqual(code, 0, said)
        self.assertNotIn("note:", said)
        code, said = self.earlier(page, self.house_style(other))
        self.assertEqual(code, 1, said)
        code, said = self.earlier(page, self.house_style(STYLE), fixed=("title",))
        self.assertEqual(code, 0, said)
        self.assertIn("compare main colour by eye; 1 must differ", said)

    def test_a_set_with_only_an_image_is_compared_on_colour_and_the_rest_left_to_the_eye(self):
        folder = self.approved_set("old", STYLE)
        (folder / "style.json").unlink()
        (folder / "approved-sample.html").write_text("<html><body>hand-drawn</body></html>", encoding="utf-8")
        code, said = self.earlier(self.render(name="new"), folder)
        self.assertEqual(code, 1, said)
        self.assertIn("compare title treatment, ink width by eye; 1 must differ", said)
        code, said = self.earlier(self.render(name="other"), self.dir / "nowhere")
        self.assertEqual(code, 2, said)

    def looks(self, *pages, fixed=()):
        run = self.ink("looks", *pages, *(["--fixed", *fixed] if fixed else []))
        return run.returncode, run.stdout + run.stderr

    def test_looks_names_the_main_colour_by_its_area_on_the_page_panel_tints_included(self):
        # A pale cream panel outweighs the 50 x 80 mm pale blue water cue; black and white never count.
        panel = '<rect x="10" y="60" width="160" height="200" fill="#fff8e1"/>'
        code, said = self.looks(self.render(panel, name="cream"))
        self.assertIn("cream.html: main colour yellow", said)
        code, said = self.looks(self.render(name="water"))
        self.assertIn("water.html: main colour blue", said)

    def test_two_looks_too_alike_are_named_and_a_fixed_choice_is_exempt(self):
        two_cues = '<circle class="ink" data-cue="leak" cx="140" cy="190" r="10"/>'
        cues = {"water": {"color": "#a9d8ea", "treatment": "fill"}, "leak": {"color": "#c0392b", "treatment": "fill"}}
        first = self.render(two_cues, style={**STYLE, "cues": cues}, name="a")
        near = {**STYLE, "ink": {**STYLE["ink"], "width_mm": 0.65},
                "cues": {"water": {"color": "#5b9bd5", "treatment": "fill"}, "leak": {"color": "#a93226", "treatment": "outline"}}}
        second = self.render(two_cues, style=near, name="b")
        code, said = self.looks(first, second)
        self.assertEqual(code, 1, said)
        for fault in ("the same title treatment, Londrina Solid hatched", "ink 0.5 and 0.65 mm, under 0.2 mm apart",
                      "the same main colour, blue", "2 cue colours shared, blue, red"):
            self.assertIn(fault, said)
        code, said = self.looks(first, second, fixed=("title", "ink", "main-colour", "cues"))
        self.assertEqual(code, 0, said)
        far = {**near, "ink": {**STYLE["ink"], "width_mm": 0.7},
               "lettering": {**STYLE["lettering"], "title_font": "Titan One", "title_fill": "solid"},
               "cues": {"water": {"color": "#f2c14e", "treatment": "fill"}, "leak": {"color": "#c0392b", "treatment": "fill"}}}
        code, said = self.looks(first, self.render(two_cues, style=far, name="c"))
        self.assertEqual(code, 0, said)

    def test_two_palettes_share_cue_colours_whether_or_not_a_page_uses_them(self):
        cues = {"water": {"color": "#a9d8ea", "treatment": "fill"}, "leak": {"color": "#c0392b", "treatment": "fill"}}
        pages = [self.render(style={**STYLE, "cues": cues, "ink": {**STYLE["ink"], "width_mm": width}}, name=name)
                 for name, width in (("a", 0.5), ("b", 1))]
        code, said = self.looks(*pages, fixed=("title", "main-colour"))
        self.assertEqual(code, 1, said)
        self.assertIn("2 cue colours shared, blue, red", said)

    def test_colours_lists_a_pictures_exact_colours_by_area_each_with_its_grey(self):
        drawing = ('<rect fill="#b4605a" x="0" y="0" width="100" height="100"/>'
                   '<rect fill="#4f8a5b" x="100" y="0" width="60" height="100"/>')
        picture = self.render(drawing, name="picture").with_suffix(".png")
        run = self.ink("colours", picture)
        self.assertEqual(0, run.returncode, run.stderr)
        listed = [line.split(",")[0] for line in run.stdout.splitlines()]
        self.assertEqual(["#ffffff neutral", "#b4605a red", "#4f8a5b green"], listed[:3])
        self.assertIn("grey 120", run.stdout)
        self.assertEqual(2, self.ink("colours", picture.with_suffix(".html")).returncode)

    def test_cues_too_close_in_grey_and_coloured_paper_are_named(self):
        close = {**STYLE, "cues": {"water": {"color": "#a9d8ea", "treatment": "fill"},
                                   "leak": {"color": "#b8d4a0", "treatment": "fill"}}}
        page = self.render('<circle class="ink" data-cue="leak" cx="140" cy="190" r="10"/>', style=close, name="close")
        code, said = self.looks(page)
        self.assertEqual(code, 1, said)
        self.assertRegex(said, r"cues (leak and water|water and leak) print \d+ grey levels apart, under 30")
        paper = self.render('<rect class="ground" x="-12" y="-12" width="210" height="297" fill="#fdf1d8"/>', name="paper")
        code, said = self.looks(paper)
        self.assertRegex(said, r"paper.html: coloured paper, #[0-9a-f]{6} at the corners")
        code, said = self.looks(paper, "--coloured-paper")
        self.assertEqual(code, 0, said)


    def rounds(self, name, text):
        run = self.ink("rounds", self.write(name, text))
        return run.returncode, run.stdout + run.stderr

    def test_rounds_with_both_replies_pass_whatever_headings_the_replies_hold(self):
        for name, first, second in (("checks.md", "Reader", "Inspector"), ("icons.md", "Cold read", "Judge")):
            with self.subTest(name):
                text = (f"# Record\n\n## Round 1\n\n{first}:\n\n1. A gauge.\n\n{second}:\n\n## 1. Details\n\nkept\n"
                        f"\n## Round 2 (redraw)\n{first}: a gauge\n{second}: hit\n")
                code, said = self.rounds(name, text)
                self.assertEqual(code, 0, said)

    def test_a_round_without_one_of_its_replies_is_named(self):
        whole = "## Round 1\nReader:\na\nInspector:\nb\n"
        for text, named in ((whole + "## Round 2\nReader:\na\n", "round 2: no reply under a 'Inspector:' line"),
                            ("## Round 1\nReader:\n\nInspector:\nb\n", "round 1: no reply under a 'Reader:' line"),
                            (whole + "## Round 3\nReader:\na\nInspector:\nb\n", "rounds run 1, 3"),
                            ("# Checks\n", "no '## Round <n>' heading")):
            with self.subTest(named):
                code, said = self.rounds("checks.md", text)
                self.assertEqual(code, 1, said)
                self.assertIn(named, said)

    def page_of_a_set(self, folder, marks="", orientation="portrait"):
        (self.dir / folder).mkdir()
        return self.render(marks, orientation=orientation, name=f"{folder}/page-1")

    def assemble(self, *pages, print_=A4, out="set.pdf"):
        run = self.ink("assemble", *pages, "--print", self.write("approved.json", print_),
                       "--out", self.dir / out, "--renders", self.dir / "renders")
        return run.returncode, run.stdout + run.stderr

    @unittest.skipUnless(PDF_PACKAGES, "needs pypdf and pymupdf")
    def test_assemble_merges_pages_in_order_each_in_its_orientation(self):
        pages = [self.page_of_a_set("01-wide", orientation="landscape"), self.page_of_a_set("02-tall")]
        code, said = self.assemble(*pages)
        self.assertEqual(code, 0, said)
        sizes = [png_size(self.dir / "renders" / f"pdf-{n}.png") for n in (1, 2)]
        self.assertGreater(sizes[0][0], sizes[0][1])
        self.assertLess(sizes[1][0], sizes[1][1])
        boxes = re.findall(rb"/MediaBox \[\s*0 0 ([\d.]+) ([\d.]+)\s*\]", (self.dir / "set.pdf").read_bytes())
        self.assertEqual([float(w) > float(h) for w, h in boxes], [True, False])

    @unittest.skipUnless(PDF_PACKAGES, "needs pypdf and pymupdf")
    def test_assemble_writes_no_pdf_for_a_faulty_page_list(self):
        first, second = self.page_of_a_set("01-a"), self.page_of_a_set("02-b")
        for pages, named in (((first,), "missing from the page list"), ((first, second, first), "listed twice"),
                             ((first, second, self.dir / "02-b" / "page-9.html"), "no such page")):
            with self.subTest(named):
                code, said = self.assemble(*pages)
                self.assertEqual(code, 1, said)
                self.assertIn(named, said)
                self.assertFalse((self.dir / "set.pdf").exists())

    @unittest.skipUnless(PDF_PACKAGES, "needs pypdf and pymupdf")
    def test_a_left_out_page_is_found_wherever_the_pdf_goes(self):
        first = self.page_of_a_set("01-a")
        self.page_of_a_set("02-b")
        code, said = self.assemble(first, out="elsewhere/set.pdf")
        self.assertEqual(code, 1, said)
        self.assertIn("missing from the page list", said)

    @unittest.skipUnless(PDF_PACKAGES, "needs pypdf and pymupdf")
    def test_assemble_measures_the_margins_of_a_page_it_did_not_render(self):
        sheet = ('<style>@page { size: 210mm 297mm; margin: 0 } body { margin: 0 }</style>'
                 '<div style="position:absolute; left:%smm; top:40mm; width:60mm; height:20mm; background:#000; '
                 '-webkit-print-color-adjust:exact"></div>')
        code, said = self.assemble(self.write("old.html", sheet % 3))
        self.assertEqual(code, 1, said)
        self.assertIn("left margin", said)
        code, said = self.assemble(self.write("old.html", sheet % 30))
        self.assertEqual(code, 0, said)

    @unittest.skipUnless(PDF_PACKAGES, "needs pypdf and pymupdf")
    def test_assemble_holds_the_pages_to_the_approved_print_rules_and_margins(self):
        page = self.page_of_a_set("01-a", '<path class="ink" d="M-6 200 L20 200"/>')
        code, said = self.assemble(page)
        self.assertEqual(code, 1, said)
        self.assertIn("left margin", said)
        wider = {**A4, "margins_mm": {**A4["margins_mm"], "top": 20}}
        code, said = self.assemble(page, print_=wider)
        self.assertIn("other paper or margins", said)
        self.assertFalse((self.dir / "set.pdf").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
