import base64
import errno
import html
import json
import math
import os
from pathlib import Path
import pty
import select
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent.parent
NOTES = json.loads((ROOT / "tools" / "study_notes.json").read_text(encoding="utf-8"))
GREEN = "#1d4938"
INK = "#223b30"
MUTED = "#647569"


def quoted(text):
    return "'" + text.replace("\\", "\\\\").replace("'", "\\'") + "'"


class Drawing:
    def __init__(self, width, height, title, background="#ffffff"):
        self.width = width
        self.height = height
        self.svg = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
            f"<title>{html.escape(title)}</title>",
        ]
        self.mvg = [f"viewbox 0 0 {width} {height}"]
        self.rectangle(0, 0, width, height, background)

    def rectangle(self, left, top, width, height, fill, stroke="none", radius=0, stroke_width=2):
        self.svg.append(
            f'<rect x="{left}" y="{top}" width="{width}" height="{height}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>'
        )
        self.mvg.extend([
            f"fill '{fill}' stroke '{stroke}' stroke-width {stroke_width}",
            f"roundrectangle {left},{top} {left + width},{top + height} {radius},{radius}",
        ])

    def polygon(self, points, fill, stroke="none", stroke_width=2):
        coordinates = " ".join(f"{horizontal},{vertical}" for horizontal, vertical in points)
        self.svg.append(f'<polygon points="{coordinates}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>')
        self.mvg.extend([f"fill '{fill}' stroke '{stroke}' stroke-width {stroke_width}", f"polygon {coordinates}"])

    def polyline(self, points, color=MUTED, stroke_width=2.5):
        coordinates = " ".join(f"{horizontal},{vertical}" for horizontal, vertical in points)
        self.svg.append(f'<polyline points="{coordinates}" fill="none" stroke="{color}" stroke-width="{stroke_width}" stroke-linejoin="round"/>')
        self.mvg.extend([f"fill none stroke '{color}' stroke-width {stroke_width}", f"polyline {coordinates}"])

    def text(self, horizontal, vertical, content, size=18, color=INK, anchor="start", bold=False, mono=False):
        family = "DejaVu Sans Mono" if mono else "DejaVu Sans"
        font_name = "DejaVu-Sans-Mono" if mono else "DejaVu-Sans"
        if bold:
            font_name += "-Bold"
        weight = "700" if bold else "400"
        self.svg.append(
            f'<text x="{horizontal}" y="{vertical}" fill="{color}" font-family="{family}, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{html.escape(content)}</text>'
        )
        self.mvg.extend([
            f"fill '{color}' stroke none font '{font_name}' font-size {size} text-anchor {anchor}",
            f"text {horizontal},{vertical} {quoted(content)}",
        ])

    def lines(self, horizontal, center, lines, size=18, color=INK, bold=False):
        line_height = size * 1.36
        first_baseline = center - (len(lines) - 1) * line_height / 2 + size * 0.34
        for line_index, content in enumerate(lines):
            self.text(horizontal, first_baseline + line_index * line_height, content, size, color, "middle", bold)

    def arrow(self, points, label="", label_position=None):
        self.polyline(points)
        previous_horizontal, previous_vertical = points[-2]
        end_horizontal, end_vertical = points[-1]
        delta_horizontal = end_horizontal - previous_horizontal
        delta_vertical = end_vertical - previous_vertical
        distance = math.hypot(delta_horizontal, delta_vertical)
        unit_horizontal = delta_horizontal / distance
        unit_vertical = delta_vertical / distance
        base_horizontal = end_horizontal - unit_horizontal * 10
        base_vertical = end_vertical - unit_vertical * 10
        self.polygon([
            (end_horizontal, end_vertical),
            (base_horizontal - unit_vertical * 5, base_vertical + unit_horizontal * 5),
            (base_horizontal + unit_vertical * 5, base_vertical - unit_horizontal * 5),
        ], MUTED)
        if label:
            label_horizontal, label_vertical = label_position
            self.rectangle(label_horizontal - 5, label_vertical - 17, len(label) * 10 + 10, 23, "#ffffff", radius=4)
            self.text(label_horizontal, label_vertical, label, 15, GREEN, bold=True)

    def save(self, svg_path, png_path):
        svg_path.write_text("\n".join(self.svg + ["</svg>"]) + "\n", encoding="utf-8")
        with tempfile.TemporaryDirectory(prefix="python-activity-") as temporary:
            mvg_path = Path(temporary) / "drawing.mvg"
            mvg_path.write_text("\n".join(self.mvg) + "\n", encoding="utf-8")
            subprocess.run(
                ["convert", f"mvg:{mvg_path}", "-depth", "8", str(png_path)],
                check=True,
                capture_output=True,
                timeout=45,
            )


def make_flowchart(study, directory):
    graph = study["flow"]
    maximum_row = max(node[1] for node in graph["nodes"])
    width = 1280
    height = 235 + maximum_row * 150
    drawing = Drawing(width, height, f"Case {study['number']}: {study['title']} — flowchart")
    drawing.text(52, 41, f"CASE {study['number']}  /  ALGORITHM FLOW", 17, GREEN, bold=True)
    drawing.text(52, 70, study["title"], 22, INK, bold=True)
    nodes = {}
    for identifier, row, kind, label in graph["nodes"]:
        horizontal = 1010 if kind == "side" else 425
        vertical = 130 + row * 150
        node_width = 330 if kind == "side" else 540
        node_height = 90
        if kind == "decision":
            node_width = 510
            node_height = 126
        elif kind == "start":
            node_width = 210
            node_height = 52
        nodes[identifier] = {
            "horizontal": horizontal,
            "vertical": vertical,
            "width": node_width,
            "height": node_height,
            "kind": kind,
            "label": label.replace("\\n", "\n"),
        }
    for edge in graph["edges"]:
        source_id, target_id = edge[:2]
        label = edge[2] if len(edge) >= 3 else ""
        route = edge[3] if len(edge) >= 4 else "down"
        source = nodes[source_id]
        target = nodes[target_id]
        source_left = source["horizontal"] - source["width"] / 2
        source_right = source["horizontal"] + source["width"] / 2
        source_bottom = source["vertical"] + source["height"] / 2
        source_top = source["vertical"] - source["height"] / 2
        target_left = target["horizontal"] - target["width"] / 2
        target_right = target["horizontal"] + target["width"] / 2
        target_top = target["vertical"] - target["height"] / 2
        if route == "down":
            points = [(source["horizontal"], source_bottom), (target["horizontal"], target_top)]
            label_position = (source["horizontal"] + 12, (source_bottom + target_top) / 2 + 5)
        elif route in ("loop", "inner_loop"):
            gutter = 62 if route == "loop" else 108
            points = [
                (source_left, source["vertical"]), (gutter, source["vertical"]),
                (gutter, target["vertical"]), (target_left, target["vertical"]),
            ]
            label_position = (gutter + 15, source["vertical"] - 10)
        elif route == "side":
            midpoint = 775
            points = [
                (source_right, source["vertical"]), (midpoint, source["vertical"]),
                (midpoint, target["vertical"]), (target_left, target["vertical"]),
            ]
            points = [point for point_index, point in enumerate(points) if point_index == 0 or point != points[point_index - 1]]
            label_position = (source_right + 22, source["vertical"] - 12)
        elif route == "retry":
            points = [
                (source["horizontal"], source_top), (source["horizontal"], target["vertical"]),
                (target_right, target["vertical"]),
            ]
            label_position = (source["horizontal"] + 12, source_top - 14)
        else:
            points = [
                (source["horizontal"], source_bottom), (source["horizontal"], target["vertical"]),
                (target_right, target["vertical"]),
            ]
            label_position = (source["horizontal"] + 12, source_bottom + 20)
        drawing.arrow(points, label, label_position)
    for node in nodes.values():
        horizontal = node["horizontal"]
        vertical = node["vertical"]
        node_width = node["width"]
        node_height = node["height"]
        left = horizontal - node_width / 2
        top = vertical - node_height / 2
        kind = node["kind"]
        if kind == "decision":
            drawing.polygon([
                (horizontal, top), (left + node_width, vertical),
                (horizontal, top + node_height), (left, vertical),
            ], "#fff3d9", "#baa66b")
        elif kind == "input":
            drawing.polygon([
                (left + 22, top), (left + node_width, top),
                (left + node_width - 22, top + node_height), (left, top + node_height),
            ], "#edf4ed", "#91ad98")
        elif kind == "start":
            drawing.rectangle(left, top, node_width, node_height, GREEN, radius=26)
        else:
            fill = "#fff0e7" if kind == "side" else "#ffffff"
            drawing.rectangle(left, top, node_width, node_height, fill, "#b5c5b8", radius=8)
        text_lines = node["label"].splitlines()
        text_size = 17 if max(map(len, text_lines)) > 39 else 18
        drawing.lines(horizontal, vertical, text_lines, text_size, "#ffffff" if kind == "start" else INK, kind == "start")
    drawing.text(52, height - 25, "Rounded: start / stop     Parallelogram: input / output     Diamond: decision     Rectangle: process", 15, MUTED)
    drawing.save(directory / "assets" / "flowchart.svg", directory / "assets" / "flowchart.png")
    mermaid = ["flowchart TD"]
    for identifier, row, kind, label in graph["nodes"]:
        safe_label = html.escape(label.replace("\\n", "<br/>"), quote=True).replace("&lt;br/&gt;", "<br/>")
        if kind == "decision":
            notation = '{"' + safe_label + '"}'
        elif kind == "start":
            notation = '(["' + safe_label + '"])'
        elif kind == "input":
            notation = '[/"' + safe_label + '"/]'
        else:
            notation = '["' + safe_label + '"]'
        mermaid.append(f"    {identifier}{notation}")
    for edge in graph["edges"]:
        label = f"|{edge[2]}|" if len(edge) >= 3 and edge[2] else ""
        mermaid.append(f"    {edge[0]} -->{label} {edge[1]}")
    (directory / "flowchart.mmd").write_text("\n".join(mermaid) + "\n", encoding="utf-8")


def capture_terminal(directory, sample_input):
    master_descriptor, slave_descriptor = pty.openpty()
    process = subprocess.Popen(
        [sys.executable, "-B", "program.py"],
        cwd=directory,
        stdin=slave_descriptor,
        stdout=slave_descriptor,
        stderr=slave_descriptor,
        close_fds=True,
    )
    os.close(slave_descriptor)
    answers = sample_input.splitlines()
    answer_index = 0
    transcript = bytearray()
    deadline = time.monotonic() + 10
    try:
        while time.monotonic() < deadline:
            readable, _, _ = select.select([master_descriptor], [], [], 0.2)
            if not readable:
                if process.poll() is not None:
                    break
                continue
            try:
                chunk = os.read(master_descriptor, 65536)
            except OSError as error:
                if error.errno == errno.EIO:
                    break
                raise
            if not chunk:
                break
            transcript.extend(chunk)
            if transcript.endswith(b": ") and answer_index < len(answers):
                os.write(master_descriptor, (answers[answer_index] + "\n").encode("utf-8"))
                answer_index += 1
        else:
            raise RuntimeError(f"Terminal capture timed out for {directory.name}")
        return_code = process.wait(timeout=2)
        if return_code != 0 or answer_index != len(answers):
            raise RuntimeError(f"Incomplete terminal capture for {directory.name}: exit {return_code}, inputs {answer_index}/{len(answers)}")
    finally:
        os.close(master_descriptor)
        if process.poll() is None:
            process.kill()
            process.wait()
    return "$ python3 -B program.py\n" + transcript.decode("utf-8").replace("\r\n", "\n").replace("\r", "")


def make_output_image(study, directory, transcript):
    lines = transcript.rstrip("\n").splitlines()
    maximum_length = max(map(len, lines))
    width = max(1000, math.ceil(maximum_length * 10.85 + 76))
    height = 117 + 25 * len(lines)
    drawing = Drawing(width, height, f"Case {study['number']}: actual executed sample output", "#132b23")
    drawing.rectangle(0, 0, width, 60, "#1d3b30")
    drawing.text(30, 38, f"CASE {study['number']}  /  PYTHON TERMINAL", 16, "#dbe8db", bold=True)
    drawing.text(width - 29, 38, "EXECUTED SAMPLE", 13, "#a8d0ab", "end", True)
    for line_index, line in enumerate(lines):
        color = "#dce9dc"
        if line.startswith("$"):
            color = "#f2cf88"
        elif line.startswith(("ERROR", "REJECTED", "  -", "CONFLICT:", "UNAVAILABLE:")):
            color = "#f1b8a0"
        elif line.startswith(("Total", "Final", "Highest", "Accepted:", "Top", "Inventory value:", "Water balance:", "Reconciliation:")):
            color = "#b9dfb3"
        drawing.text(30, 91 + line_index * 25, line, 18, color, mono=True)
    drawing.text(30, height - 17, "Source: output.txt  |  Input: sample_input.txt  |  Fictional classroom data", 12, "#9bb4a0")
    drawing.save(directory / "assets" / "output.svg", directory / "assets" / "output.png")


def markdown_list(items, ordered=False):
    return "\n".join(f"{index + 1}. {item}" if ordered else f"- {item}" for index, item in enumerate(items))


def case_markdown(study, directory, tests, transcript):
    source = (directory / "program.py").read_text(encoding="utf-8").rstrip()
    table_rows = []
    for case in tests:
        expected = case["expected"].replace("|", "\\|")
        table_rows.append(
            f"| `{case['id']}` | {case['kind']} | {expected} | PASS · [raw stdout](test_outputs/{case['id']}.txt) |"
        )
    sections = [
        f"# Case {study['number']}: {study['title']}",
        "[← Portfolio index](../README.md) · [Complete report](../REPORT.html)",
        "## Problem statement\n\n" + study["statement"],
        "## Objectives\n\n" + markdown_list(study["objectives"]),
        "## Assumptions and policy\n\n" + markdown_list(study["assumptions"]),
        "## Input and output\n\n**Input:** " + study["input"] + "\n\n**Output:** " + study["output"],
        "## Computational thinking\n\n" + markdown_list(study["thinking"]),
        "## Algorithm\n\n" + markdown_list(study["algorithm"], True),
        "## Flowchart\n\n![Algorithm flowchart](assets/flowchart.png)\n\n[Scalable SVG](assets/flowchart.svg) · [Mermaid source](flowchart.mmd)",
        "## Pseudocode\n\n```text\n" + study["pseudocode"] + "\n```",
        f"## Python source code\n\n[Runnable source](program.py). From the repository root:\n\n```bash\npython3 {study['folder']}/program.py\n```\n\n```python\n{source}\n```",
        "## Test cases\n\nSix automated fixtures cover normal, boundary, and validation behavior. Full stdin and assertions are in [tests.json](tests.json).\n\n| Test | Type | Expected result | Actual result |\n|---|---|---|---|\n" + "\n".join(table_rows),
        "## Output screenshot\n\nThe image is a rendered capture of the actual pseudo-terminal execution of test `01_normal`. Typed sample inputs are visible in the transcript. Every sample is fictional.\n\n![Executed Python output](assets/output.png)\n\n[Full terminal transcript](output.txt) · [Exact sample input](sample_input.txt) · [Scalable output image](assets/output.svg)\n\n```text\n" + transcript.rstrip() + "\n```",
        "## Conclusion\n\n" + study["conclusion"],
    ]
    return "\n\n".join(sections) + "\n"


def as_html_list(items, ordered=False):
    tag = "ol" if ordered else "ul"
    return "<" + tag + ">" + "".join("<li>" + html.escape(item) + "</li>" for item in items) + "</" + tag + ">"


def image_data(path, mime_type):
    return f"data:{mime_type};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def case_html(study, directory, tests, transcript, ordinal):
    escaped = html.escape
    source = (directory / "program.py").read_text(encoding="utf-8")
    test_rows = []
    for case in tests:
        raw_output = (directory / "test_outputs" / f"{case['id']}.txt").read_text(encoding="utf-8")
        test_rows.append(
            '<tr><td><span class="test-id">' + escaped(case["id"]) + '</span><span class="test-kind">' + escaped(case["kind"]) + '</span></td>'
            '<td><strong>' + escaped(case["purpose"]) + "</strong><p>" + escaped(case["expected"]) + "</p>"
            '<details class="test-detail"><summary>Input &amp; captured stdout</summary>'
            '<h5>Standard input</h5><pre>' + escaped(case["input"]) + "</pre>"
            '<h5>Actual stdout · piped test run</h5><pre>' + escaped(raw_output) + "</pre></details></td>"
            '<td><span class="pass">PASS</span></td></tr>'
        )
    flow_data = image_data(directory / "assets" / "flowchart.svg", "image/svg+xml")
    output_data = image_data(directory / "assets" / "output.png", "image/png")
    return f"""
<article class="study" id="case-{study['number']}">
  <header class="study-header">
    <div class="section-kicker">STUDY {ordinal:02d} / 10 <span>BRIEF CASE {study['number']}</span></div>
    <h2>{escaped(study['title'])}</h2>
    <div class="study-meta"><span>{escaped(study['focus'])}</span><span class="pass">6 / 6 TESTS PASSED</span></div>
  </header>
  <section class="content-block"><h3>01 <span>Problem statement</span></h3><p class="lead">{escaped(study['statement'])}</p></section>
  <div class="two-column">
    <section class="content-block"><h3>02 <span>Objectives</span></h3>{as_html_list(study['objectives'])}</section>
    <section class="content-block thought"><h3>Computational thinking</h3>{as_html_list(study['thinking'])}</section>
  </div>
  <section class="content-block policy"><h3>03 <span>Assumptions &amp; policy</span></h3>{as_html_list(study['assumptions'])}</section>
  <div class="io-grid"><div><h4>INPUT CONTRACT</h4><p>{escaped(study['input'])}</p></div><div><h4>PROGRAM OUTPUT</h4><p>{escaped(study['output'])}</p></div></div>
  <section class="content-block"><h3>04 <span>Algorithm</span></h3>{as_html_list(study['algorithm'], True)}</section>
  <section class="content-block"><h3>05 <span>Flowchart</span></h3><figure class="flow-figure"><img class="flow-image" src="{flow_data}" alt="Flowchart for {escaped(study['title'])}" loading="lazy"><figcaption>Input, validation, decisions, iteration, and output. SVG and PNG copies are included in the case folder.</figcaption></figure></section>
  <section class="content-block"><h3>06 <span>Pseudocode</span></h3><pre class="pseudocode">{escaped(study['pseudocode'])}</pre></section>
  <section class="content-block"><h3>07 <span>Python source</span></h3><div class="run-command"><span>RUN FROM REPOSITORY ROOT</span><code>python3 {study['folder']}/program.py</code></div>
    <details class="source-detail"><summary>Read the complete program <span>{len(source.splitlines())} lines · no imports</span></summary><pre><code>{escaped(source)}</code></pre></details>
  </section>
  <section class="content-block"><h3>08 <span>Test cases</span></h3><p>Each expected result is checked against a separate execution of the program. Inputs, assertions, and raw stdout are included in the repository.</p>
    <div class="table-scroll"><table class="test-table"><thead><tr><th>Test</th><th>Purpose &amp; expected result</th><th>Actual</th></tr></thead><tbody>{''.join(test_rows)}</tbody></table></div>
  </section>
  <section class="content-block"><h3>09 <span>Output screenshot</span></h3><figure class="output-figure"><img src="{output_data}" alt="Actual executed sample terminal output for {escaped(study['title'])}" loading="lazy"><figcaption>Rendered from the actual pseudo-terminal run of <code>01_normal</code>. The exact input and full transcript are preserved in the case folder.</figcaption></figure>
    <details><summary>Accessible text transcript</summary><pre>{escaped(transcript)}</pre></details>
  </section>
  <section class="content-block conclusion"><h3>10 <span>Conclusion</span></h3><p>{escaped(study['conclusion'])}</p></section>
  <a class="back-link" href="#overview">Back to portfolio overview ↑</a>
</article>"""


STYLE = """
:root{--paper:#f7f6f0;--white:#fff;--ink:#20382e;--muted:#69776b;--line:#dbe1d5;--green:#214a37;--pale:#e9efdf;--gold:#d5b479;--mono:"DejaVu Sans Mono","Cascadia Code",Consolas,monospace}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:32px}body{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,"Segoe UI",Arial,sans-serif;font-size:15px;line-height:1.7}
a{color:var(--green);text-underline-offset:4px}button{font:inherit;cursor:pointer}a:focus-visible,button:focus-visible,summary:focus-visible{outline:3px solid #b98d42;outline-offset:4px}
.sidebar{position:fixed;inset:0 auto 0 0;width:252px;background:#eff1e7;border-right:1px solid var(--line);padding:35px 23px;display:flex;flex-direction:column;z-index:5;overflow-y:auto}
.brand{display:flex;align-items:center;gap:12px;text-decoration:none;font-weight:750;line-height:1.2;font-size:15px;letter-spacing:-.3px}.brand-mark{display:grid;place-items:center;background:var(--green);color:white;width:41px;height:41px;border-radius:11px;font-family:var(--mono);font-size:18px;flex-shrink:0}.brand small{display:block;font-size:10px;letter-spacing:1.8px;margin-top:7px;font-weight:500;color:var(--muted)}
.nav-label{font-size:10px;letter-spacing:1.6px;color:var(--muted);font-weight:700;margin:43px 0 14px 8px}.sidebar nav{display:grid;gap:5px}.nav-link{display:flex;align-items:center;gap:11px;color:#51634f;text-decoration:none;padding:10px 9px;border-radius:7px;line-height:1.4;font-size:12px}.nav-link:hover,.nav-link.active{background:#dfe8d6;color:#203e2c}.nav-link.active{font-weight:700}.nav-number{font-family:var(--mono);font-size:11px;opacity:.7}
.sidebar-bottom{margin-top:auto;padding:30px 8px 0;font-size:11px;color:var(--muted)}.sidebar-bottom strong{display:block;color:var(--green);font-weight:600}.sidebar-bottom .small-rule{width:28px;height:2px;background:var(--gold);margin-bottom:15px}
main{margin-left:252px;max-width:1500px}.page-shell{padding:0 58px 70px;max-width:1240px;margin:0 auto}.topbar{height:88px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);font-size:10px;letter-spacing:1.7px;color:var(--muted)}.topbar strong{color:var(--ink);font-weight:600}.print-button{background:transparent;border:1px solid #c4cebd;border-radius:5px;padding:8px 12px;color:var(--green);font-size:11px;letter-spacing:.2px}
.hero{padding:64px 0 44px;display:grid;grid-template-columns:1fr 235px;gap:35px;align-items:center}.eyebrow{font-size:10px;font-weight:700;letter-spacing:2px;color:var(--green);margin:0 0 22px}.hero h1{font-family:Georgia,"Times New Roman",serif;font-size:clamp(40px,4.5vw,67px);font-weight:400;letter-spacing:-2.7px;line-height:1.05;margin:0 0 24px}.hero h1 em{font-style:italic;color:#5d7954}.hero p{max-width:580px;color:var(--muted);font-size:15px;line-height:1.8;margin:0}.hero-card{background:var(--green);color:#e7efdc;padding:29px 26px;border-radius:4px;min-height:259px;position:relative;overflow:hidden}.hero-card:after{content:"";position:absolute;width:180px;height:180px;border:1px solid #526c4c;border-radius:50%;right:-75px;top:50px}.hero-card .big-number{font-family:Georgia,serif;line-height:1.1;font-size:91px;letter-spacing:-5px;color:#e8d4a5}.hero-card .card-label{font-size:10px;letter-spacing:2px;line-height:1.8;margin-top:8px}.hero-card .card-footer{margin-top:28px;border-top:1px solid #527052;padding-top:13px;font-size:11px;color:#c7d7bd}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:24px 0;margin:0 0 50px}.metric{padding:0 22px;border-right:1px solid var(--line)}.metric:first-child{padding-left:0}.metric:last-child{border:0}.metric strong{font-family:Georgia,serif;font-size:30px;line-height:1.3;font-weight:400}.metric span{display:block;font-size:10px;letter-spacing:1.1px;color:var(--muted);margin-top:4px;text-transform:uppercase}
.intro-head{display:flex;justify-content:space-between;align-items:baseline;gap:20px;margin-bottom:14px}.intro-head h2{font-family:Georgia,serif;font-size:28px;font-weight:400;letter-spacing:-.4px;margin:0}.small-label{font-size:10px;letter-spacing:1px;color:var(--muted)}.overview-table{width:100%;border-collapse:collapse;font-size:13px}.overview-table th{text-align:left;font-size:10px;color:var(--muted);letter-spacing:1.2px;font-weight:600;padding:10px 12px;border-bottom:1px solid #bfcab9}.overview-table td{padding:15px 12px;border-bottom:1px solid var(--line);vertical-align:top}.overview-table td:first-child{width:70px;font-family:var(--mono);color:#6a795c}.overview-table a{text-decoration:none;font-weight:600}.overview-table a:hover{text-decoration:underline}.overview-table .focus{font-size:11px;color:var(--muted)}
.assumption-note{padding:22px 25px;background:#eeeade;border-left:3px solid var(--gold);margin:32px 0;color:#5e654f;font-size:13px}.assumption-note strong{color:#3b4d36}.getting-started{display:grid;grid-template-columns:1fr 1fr;gap:30px;margin:34px 0 64px}.getting-started h3{font-size:13px;margin:0 0 9px}.getting-started p{font-size:13px;color:var(--muted);margin:0 0 12px}.getting-started pre{font-size:11px}
.study{border-top:2px solid var(--green);padding:40px 0 60px;scroll-margin-top:25px}.study-header{padding-bottom:24px;border-bottom:1px solid var(--line);margin-bottom:30px}.section-kicker{font-size:10px;letter-spacing:1.8px;color:var(--green);font-weight:700;display:flex;justify-content:space-between}.section-kicker span{color:var(--muted);font-weight:400}.study h2{font-family:Georgia,"Times New Roman",serif;font-size:36px;font-weight:400;letter-spacing:-.8px;line-height:1.18;margin:18px 0}.study-meta{display:flex;flex-wrap:wrap;justify-content:space-between;gap:12px;color:var(--muted);font-size:12px}.pass{display:inline-block;color:#37623c;background:#e6efdd;font-family:var(--mono);font-size:10px;padding:3px 8px;border-radius:3px;white-space:nowrap;line-height:1.5;font-weight:500}
.content-block{margin:30px 0}.content-block h3{font-size:11px;color:#88917a;font-weight:500;display:flex;align-items:baseline;gap:12px;margin:0 0 14px;letter-spacing:.6px}.content-block h3 span{font-size:17px;font-weight:650;color:var(--ink);letter-spacing:-.2px}.lead{font-size:16px;line-height:1.8}.two-column{display:grid;grid-template-columns:1fr 1fr;gap:32px}.two-column .content-block{margin-top:0}.thought{border-left:1px solid var(--line);padding-left:28px}.thought h3{font-size:12px;color:var(--green);font-weight:650}.thought li{font-size:13px;color:var(--muted)}ul,ol{padding-left:23px;margin:0}li{margin:8px 0;padding-left:4px}li::marker{color:#638253}.policy{background:var(--pale);padding:25px 28px;border-radius:4px}.policy li{font-size:13px}.io-grid{display:grid;grid-template-columns:1fr 1fr;gap:30px;border-top:1px solid var(--line);border-bottom:1px solid var(--line);padding:23px 0}.io-grid h4{font-size:9px;letter-spacing:1.7px;font-weight:650;margin:0 0 9px;color:#728365}.io-grid p{font-size:12px;margin:0;color:var(--muted)}
figure{margin:0}.flow-figure{background:white;border:1px solid var(--line);padding:13px;border-radius:4px}.flow-image{display:block;width:100%;height:auto;max-width:920px;margin:0 auto}.output-figure img{display:block;width:100%;height:auto;border-radius:5px}.output-figure{margin-top:12px}figcaption{font-size:11px;color:var(--muted);padding:13px 8px 6px;line-height:1.6}
pre{background:#edf0e6;border:1px solid #dde3d5;border-radius:5px;padding:20px 22px;overflow-x:auto;font-family:var(--mono);font-size:11px;line-height:1.75;tab-size:4;margin:12px 0;color:#294135;white-space:pre}code{font-family:var(--mono);font-size:.9em}.pseudocode{background:#f0f1e9;border-left:3px solid #8fa47e}.run-command{background:#203e30;border-radius:5px 5px 0 0;padding:17px 20px;color:#e0ebd8;overflow-x:auto}.run-command>span{display:block;font-size:8px;letter-spacing:1.4px;color:#b5c6a9;margin-bottom:6px}.run-command code{font-size:11px;white-space:nowrap}details{margin:12px 0}summary{cursor:pointer;font-size:12px;color:var(--green);padding:12px 0;font-weight:600}.source-detail{margin-top:0;border:1px solid var(--line);border-radius:0 0 5px 5px;background:#fff}.source-detail summary{padding:15px 19px}.source-detail summary span{font-size:10px;color:var(--muted);font-weight:400;margin-left:15px}.source-detail pre{margin:0;border:0;border-top:1px solid var(--line);border-radius:0 0 4px 4px;background:#fff;font-size:10px}
.table-scroll{overflow-x:auto}.test-table{width:100%;border-collapse:collapse;font-size:12px}.test-table th{font-size:9px;letter-spacing:1.3px;color:var(--muted);text-align:left;border-bottom:1px solid #bfcab9;padding:12px 9px}.test-table td{border-bottom:1px solid var(--line);padding:16px 9px;vertical-align:top}.test-table td:first-child{width:26%}.test-table td:last-child{width:60px}.test-id{font-family:var(--mono);font-size:10px;overflow-wrap:anywhere}.test-kind{display:block;font-size:10px;color:var(--muted);margin-top:4px}.test-table strong{font-weight:600;line-height:1.6;display:block}.test-table p{font-size:11px;color:var(--muted);margin:7px 0 0}.test-detail{margin:5px 0 0}.test-detail summary{font-size:10px;padding:5px 0}.test-detail h5{font-size:10px;margin:12px 0 0}.test-detail pre{font-size:9px;padding:12px;max-width:510px}.conclusion{background:#fff;border:1px solid var(--line);padding:24px 27px;border-radius:4px}.conclusion p{font-size:14px;margin:0}.back-link{font-size:11px;text-decoration:none;color:var(--muted)}
.submission{background:var(--green);color:#dfead5;padding:32px 35px;border-radius:5px}.submission h2{font-family:Georgia,serif;font-weight:400;font-size:29px;margin:0 0 15px;color:#f3f0dd}.submission p,.submission li{font-size:13px}.submission li::marker{color:#d5b479}.submission code{color:#f1dfb5}.footer{padding-top:30px;display:flex;justify-content:space-between;gap:20px;font-size:10px;color:var(--muted)}
@media(min-width:1700px){.page-shell{padding-left:75px;padding-right:75px}}
@media(max-width:1100px){.sidebar{width:218px;padding:28px 16px}main{margin-left:218px}.page-shell{padding-left:35px;padding-right:35px}.hero{grid-template-columns:1fr 190px;gap:22px}.hero-card{padding:24px 20px}.hero h1{font-size:49px}.two-column{gap:22px}.overview-table .focus{display:none}}
@media(max-width:800px){.sidebar{position:static;width:auto;padding:20px 24px;border-right:0;border-bottom:1px solid var(--line)}.sidebar nav{display:flex;gap:5px;overflow:auto;padding-top:17px}.nav-link{white-space:nowrap;font-size:11px;flex-shrink:0}.nav-label,.sidebar-bottom{display:none}.brand small{font-size:9px}.brand{font-size:14px}.brand-mark{width:35px;height:35px}.sidebar nav .nav-link:first-child{display:none}main{margin-left:0}.page-shell{padding:0 24px 40px}.topbar{height:64px}.hero{padding-top:40px}.hero h1{font-size:47px}.hero-card{min-height:230px}.metrics{margin-bottom:35px}.study h2{font-size:31px}.flow-figure{padding:4px}.test-detail pre{max-width:400px}}
@media(max-width:540px){.hero{grid-template-columns:1fr}.hero h1{font-size:48px}.hero-card{display:none}.hero p{font-size:14px}.metrics{grid-template-columns:1fr 1fr;gap:20px;padding:22px 0}.metric:nth-child(odd){padding-left:0}.metric:nth-child(even){border:0}.metric strong{font-size:28px}.metric span{font-size:9px}.topbar{font-size:8px;letter-spacing:1px}.print-button{font-size:9px}.two-column,.io-grid,.getting-started{grid-template-columns:1fr;gap:8px}.thought{padding-left:0;border-left:0}.policy{padding:20px}.section-kicker{font-size:8px}.overview-table td,.overview-table th{padding-left:5px;padding-right:5px}.overview-table{font-size:12px}.overview-table td:first-child{width:36px}.overview-table .pass{font-size:8px}.study h2{font-size:29px}.test-table{min-width:450px}.test-detail pre{max-width:260px}.footer{display:block}.source-detail summary span{display:block;margin-left:15px}.submission{padding:24px}.getting-started{margin-bottom:42px}}
@media print{@page{size:A4;margin:17mm}body{background:#fff;font-size:10pt;color:#17251c;line-height:1.5}.sidebar,.print-button,.back-link{display:none!important}main{margin:0;max-width:none}.page-shell{padding:0;max-width:none}.topbar{height:35px}.hero{padding:26px 0;grid-template-columns:1fr 160px;gap:20px}.hero h1{font-size:40px}.hero-card{min-height:0;padding:18px}.hero-card .big-number{font-size:60px}.hero-card .card-footer{margin-top:15px}.hero p{font-size:11px}.metrics{margin-bottom:24px;padding:15px 0}.metric strong{font-size:24px}.getting-started{margin-bottom:30px}.study{break-before:page;padding-top:24px}.study-header{break-inside:avoid}.study h2{font-size:29px}.content-block{margin:21px 0}.content-block h3,.content-block h3 span{break-after:avoid}.policy{background:#f1f3eb;break-inside:auto}.policy li{font-size:10px}.lead{font-size:12px}.thought li,.io-grid p,.conclusion p{font-size:10px}.two-column{gap:22px}.flow-image{max-height:235mm;object-fit:contain;width:100%}.flow-figure,.output-figure{break-inside:avoid}.output-figure img{max-height:235mm;object-fit:contain}.source-detail{break-inside:auto}details{display:block}details>summary{list-style:none}details>*{display:block}summary{break-after:avoid}pre,.source-detail pre{white-space:pre-wrap;overflow-wrap:anywhere;overflow:visible;font-size:8px;line-height:1.5;padding:12px}.test-detail pre{max-width:none;font-size:7px}.table-scroll{overflow:visible}.test-table{min-width:0;font-size:9px}.test-table td{padding:10px 6px}.test-table p,.test-id{font-size:8px}.test-table tr{break-inside:avoid}.test-table thead{display:table-header-group}.test-detail summary{font-size:8px}.submission{break-before:page;color:#17251c;background:#f0f3e8}.submission h2{color:#17251c}.submission code{color:#17251c}.submission li,.submission p{font-size:11px}a{color:inherit;text-decoration:none}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}}
"""


def write_report(contents, verification):
    escaped = html.escape
    repository_path = ROOT / "repository.json"
    if repository_path.exists():
        repository = json.loads(repository_path.read_text(encoding="utf-8"))
        repository_url = escaped(repository["html_url"], quote=True)
        repository_label = escaped(repository["owner"] + "/" + repository["name"])
        visibility = "Private" if repository["private"] else "Public"
        access_note = ""
        if repository["private"]:
            access_note = "<li>Give your faculty access to this private repository before submitting its link, or change its visibility if required.</li>"
        submission = (
            '<section class="submission" id="submission"><h2>Your project repository.</h2>'
            f'<p><a href="{repository_url}" style="color:inherit;overflow-wrap:anywhere">{repository_label}</a></p>'
            f"<p>Visibility: {visibility}. The repository contains the complete project and its verification results.</p>"
            "<ol><li>Review the solutions and assumptions; add your student details to the README if required.</li>"
            + access_note
            + "<li>Submit the repository URL according to your faculty's instructions.</li></ol></section>"
        )
    else:
        submission = (
            '<section class="submission" id="submission"><h2>Ready for your repository.</h2>'
            "<p>The materials are prepared locally. Publishing to your own account and submitting its URL are the remaining submission steps.</p>"
            "<ol><li>Review the solutions and the policy assumptions; add your student details to the repository README if required.</li>"
            "<li>Create your own repository named <code>Python-Activity-Based-Learning</code>.</li>"
            "<li>Upload the extracted repository contents, keeping the case folders and assets together.</li>"
            "<li>Open the case READMEs and image links in your repository, then submit its actual URL according to the faculty instructions.</li></ol></section>"
        )
    navigation = ['<a class="nav-link active" href="#overview"><span class="nav-number">00</span>Portfolio overview</a>']
    rows = []
    for study in NOTES:
        navigation.append(f'<a class="nav-link" href="#case-{study["number"]}"><span class="nav-number">{study["number"]}</span>{escaped(study["short"])}</a>')
        rows.append(
            f'<tr><td>{study["number"]}</td><td><a href="#case-{study["number"]}">{escaped(study["title"])}</a>'
            f'<div class="focus">{escaped(study["focus"])}</div></td><td><span class="pass">6 / 6 PASS</span></td></tr>'
        )
    report = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Ten complete Python activity case studies with algorithms, flowcharts, source code, tests, and captured output.">
<title>Python Activity-Based Learning | Ten Case Studies</title>
<style>{STYLE}</style></head>
<body>
<aside class="sidebar"><a class="brand" href="#overview"><span class="brand-mark">py</span><span>Python Field Notes<small>ACTIVITY-BASED LEARNING</small></span></a>
<div class="nav-label">THE CASE STUDIES</div><nav aria-label="Case study navigation">{''.join(navigation)}</nav>
<div class="sidebar-bottom"><div class="small-rule"></div><strong>From problem to program.</strong>Ten practical studies.<br>One foundation in Python.</div></aside>
<main><div class="page-shell">
<div class="topbar"><span><strong>PROGRAMMING LAB</strong> &nbsp; / &nbsp; ACTIVITY 01</span><button class="print-button" type="button" onclick="window.print()">Print / Save PDF ↗</button></div>
<section id="overview">
<div class="hero"><div><div class="eyebrow">COMPUTATIONAL THINKING, IN PRACTICE</div><h1>Ten cases.<br><em>One Python<br>foundation.</em></h1>
<p>A complete learning portfolio, from a problem statement to a working program. Each study includes its assumptions, algorithm, flowchart, pseudocode, source, verified tests, and executed sample output.</p></div>
<div class="hero-card"><div class="big-number">10</div><div class="card-label">SELECTED CASE STUDIES<br>FROM THE ASSIGNED BRIEF</div><div class="card-footer">Loops. Strings. Lists. Tuples.<br>Practical problems, clearly solved.</div></div></div>
<div class="metrics"><div class="metric"><strong>10</strong><span>Complete programs</span></div><div class="metric"><strong>{verification['passed']}/{verification['total']}</strong><span>Tests passed</span></div><div class="metric"><strong>10</strong><span>Flowcharts &amp; captures</span></div><div class="metric"><strong>0</strong><span>External runtime libraries</span></div></div>
<div class="intro-head"><h2>The portfolio</h2><span class="small-label">SELECT A STUDY TO EXPLORE</span></div>
<table class="overview-table"><thead><tr><th>CASE</th><th>PROBLEM &amp; CORE CONCEPTS</th><th>VERIFICATION</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<div class="assumption-note"><strong>Read the policies first.</strong> The uploaded brief, <em>Python Activity1 case studies.pdf</em>, allows any ten cases and does not supply numeric policies. Every rate, threshold, limit, and example here is an explicit classroom assumption. Replace a policy if your faculty provides a different one.</div>
<div class="getting-started"><div><h3>Run a study</h3><p>Use Python 3.8 or later. Run from the repository root and enter values at the prompts. The ten programs use only the assigned introductory constructs.</p><pre>python3 02_electricity_billing/program.py</pre></div>
<div><h3>Reproduce the checks</h3><p>Each study includes six fixtures and their actual stdout. The optional verification tool uses the standard library and checks syllabus restrictions in the student programs.</p><pre>python3 tools/run_checks.py</pre></div></div>
</section>
{''.join(contents)}
{submission}
<footer class="footer"><span>PYTHON ACTIVITY-BASED LEARNING · TEN SELECTED STUDIES</span><span>Verified with Python {escaped(verification['python_version'])} · {verification['passed']} passing fixtures</span></footer>
</div></main>
<script>
const navigationLinks = [...document.querySelectorAll('.nav-link')];
const observedSections = [...document.querySelectorAll('#overview, .study')];
const sectionObserver = new IntersectionObserver(entries => {{
  for (const entry of entries) {{
    if (entry.isIntersecting) {{
      for (const link of navigationLinks) {{
        const active = link.getAttribute('href') === '#' + entry.target.id;
        link.classList.toggle('active', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      }}
    }}
  }}
}}, {{rootMargin: '-5% 0px -75% 0px', threshold: 0}});
for (const section of observedSections) sectionObserver.observe(section);
let previouslyClosed = [];
window.addEventListener('beforeprint', () => {{
  previouslyClosed = [...document.querySelectorAll('details:not([open])')];
  for (const detail of previouslyClosed) detail.open = true;
}});
window.addEventListener('afterprint', () => {{
  for (const detail of previouslyClosed) detail.open = false;
}});
</script></body></html>
"""
    (ROOT / "REPORT.html").write_text(report, encoding="utf-8")


def write_root_documents(verification):
    repository_path = ROOT / "repository.json"
    if repository_path.exists():
        repository = json.loads(repository_path.read_text(encoding="utf-8"))
        visibility = "Private" if repository["private"] else "Public"
        access_note = ""
        if repository["private"]:
            access_note = "\n\nGive your faculty access to this private repository before submitting its link, or change its visibility if required."
        submission = (
            "## Repository\n\n"
            f"[{repository['owner']}/{repository['name']}]({repository['html_url']})\n\n"
            f"**Visibility:** {visibility}."
            + access_note
            + "\n\nReview and understand the solutions, add your student name, roll number, and section if required, and submit the repository URL according to your faculty's instructions."
        )
    else:
        submission = """## Submit to your own repository

1. Review and understand the solutions, and add your student name, roll number, and section here if your faculty requires them.
2. Create a repository in your own account named **Python-Activity-Based-Learning**.
3. Extract the archive and upload the contents of this directory, keeping its folders intact.
4. Open the case READMEs and verify their image links in the repository.
5. Submit the actual repository URL according to the faculty's instructions.

These materials are prepared locally; no repository has been created or published by the preparation scripts."""
    rows = [
        f"| {study['number']} | [{study['title']}]({study['folder']}/README.md) | {study['focus']} | 6/6 PASS |"
        for study in NOTES
    ]
    readme = f"""# Python Activity-Based Learning

Ten complete solutions selected from **Python Activity1 case studies.pdf**. The brief permits any ten case studies; this selection spans arithmetic, conditions, loops, strings, pattern generation, lists, nested lists, tuples, and unpacking.

**Verification:** {verification['passed']}/{verification['total']} automated fixtures pass on Python {verification['python_version']}. All ten student programs pass the included syntax-based syllabus checks.

## Start here

- Open [REPORT.html](REPORT.html) locally for the complete illustrated portfolio. It is self-contained, with all diagrams, source code, tests, and output images embedded. Use **Print / Save PDF** for a printable copy.
- On a repository website, use the case-study README links below. Each README contains all ten mandatory deliverables.
- All numeric policies and sample records are explicitly declared classroom assumptions because the supplied brief does not provide rates or thresholds.

## Selected case studies

| Brief case | Study and complete documentation | Main concepts | Tests |
|---|---|---|---|
{chr(10).join(rows)}

## Run a program

Requires **Python 3.8 or later**, with no packages to install. From this repository directory:

```bash
python3 02_electricity_billing/program.py
```

Enter the requested values. Each study documents its input contract, retry behavior, and rejection policy. On systems where the executable is named `python`, substitute that command.

Run the included sample without interactive entry:

```bash
python3 02_electricity_billing/program.py < 02_electricity_billing/sample_input.txt
```

Run all verification fixtures:

```bash
python3 tools/run_checks.py
```

The checker validates expected output, rejects unexpected stderr or nonzero exits, enforces a per-test timeout, and checks the student source for out-of-syllabus constructs. It records actual stdout in each case's `test_outputs` folder and writes `verification.json`.

## Mandatory deliverables

Every case directory contains:

| Required material | Location |
|---|---|
| Problem statement, objectives, assumptions | `README.md` |
| Algorithm and computational thinking | `README.md` |
| Flowchart | `assets/flowchart.png`, `assets/flowchart.svg`, `flowchart.mmd` |
| Pseudocode | `README.md` |
| Python source code | `program.py`, also printed in `README.md` |
| Test cases and actual results | `tests.json`, `README.md`, `test_outputs/*.txt` |
| Output screenshot | `assets/output.png` |
| Reproducible sample input and output | `sample_input.txt`, `output.txt` |
| Conclusion | `README.md` |

The output images are rendered PNG captures of actual pseudo-terminal executions of each normal fixture. The plain-text transcripts include the typed fictional inputs. The test stdout files come from separate piped executions, so input text is not echoed in those files.

## Syllabus boundaries

The ten `program.py` files use procedural statements, variables, arithmetic, booleans, conditions, loops, basic input/output and conversions, string operations, lists, nested lists, tuples, and unpacking. They contain no imports, user-defined functions, classes, dictionaries, sets, comprehensions, exception handling, or third-party libraries.

The optional scripts under `tools/` are maintenance utilities, separate from the ten student solutions. They use standard-library features to run tests and generate documents. Rebuilding images also needs ImageMagick and DejaVu fonts; simply running the solutions or reading the finished materials does not.

## Policy and data notes

- The rates and cutoffs are assumed for these classroom exercises, not supplied institutional or commercial policies.
- Codes, transactions, student marks, schedules, and password samples are fictional.
- Each case states whether a malformed record is retried or counted as a rejected attempt.
- Some audit cases reserve a valid identifier before later field validation. This deliberately prevents repeated identifiers from being processed again; the relevant case documents and tests specify the rule.
- The numeric inputs model ordinary classroom-sized records. Scripts expect a complete input sequence; end-of-file recovery is outside the assigned syllabus.

{submission}

## Verification details

See [TEST_REPORT.md](TEST_REPORT.md) for all fixture outcomes and [verification.json](verification.json) for machine-readable results.
"""
    (ROOT / "README.md").write_text(readme, encoding="utf-8")
    report_lines = [
        "# Verification report",
        "",
        f"- Python: {verification['python_version']}",
        f"- Studies: {verification['studies']}",
        f"- Executed fixtures: {verification['total']}",
        f"- Passed: {verification['passed']}",
        f"- Failed: {verification['total'] - verification['passed']}",
        f"- Syllabus issues: {len(verification['syllabus_issues'])}",
        "",
        "The fixtures exercise normal input, invalid input, exact thresholds, ties, empty accepted-record sets where applicable, and arithmetic edge cases. These results cover the declared test cases; they do not claim exhaustive verification of every possible input.",
        "",
        "| Case | Fixture | Result | Evidence |",
        "|---|---|---|---|",
    ]
    for result in verification["results"]:
        report_lines.append(
            f"| {result['study']} | `{result['test']}` | {result['status']} | [Actual stdout]({result['study']}/test_outputs/{result['test']}.txt) |"
        )
    (ROOT / "TEST_REPORT.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")
    tools_readme = """# Optional maintenance utilities

These utilities are separate from the ten introductory student programs.

## Verify solutions

From the repository root:

```bash
python3 tools/run_checks.py
```

Only the Python standard library is needed. The checker executes all 60 input fixtures, compares the expected result strings, checks for unwanted output, and validates syllabus restrictions in the ten `program.py` files.

## Rebuild documents and images

```bash
python3 tools/build_materials.py
```

Run verification first. Rebuilding uses `study_notes.json`, each program, its fixtures, and the verification results. It requires a Unix-like system with Python, pseudo-terminal support, the ImageMagick `convert` command, and the DejaVu Sans / Sans Mono fonts. It captures a normal run of every program, renders the flowcharts and transcript images, and generates the case READMEs, root README, test report, and self-contained HTML report.

Generated documentation is derived from `study_notes.json` and the current source files. Update those inputs and rerun the tools when changing a policy.
"""
    (ROOT / "tools" / "README.md").write_text(tools_readme, encoding="utf-8")


def main():
    if shutil.which("convert") is None:
        raise RuntimeError("ImageMagick convert is required to rebuild image assets.")
    verification_path = ROOT / "verification.json"
    if not verification_path.exists():
        raise RuntimeError("Run tools/run_checks.py before building materials.")
    verification = json.loads(verification_path.read_text(encoding="utf-8"))
    if verification["passed"] != verification["total"] or verification["syllabus_issues"]:
        raise RuntimeError("Resolve verification failures before building materials.")
    contents = []
    for ordinal, study in enumerate(NOTES, 1):
        directory = ROOT / study["folder"]
        (directory / "assets").mkdir(exist_ok=True)
        tests = json.loads((directory / "tests.json").read_text(encoding="utf-8"))
        sample = tests[0]
        (directory / "sample_input.txt").write_text(sample["input"], encoding="utf-8")
        transcript = capture_terminal(directory, sample["input"])
        for expected in sample["contains"]:
            if expected not in transcript:
                raise RuntimeError(f"Terminal capture differs from verified sample for {directory.name}: {expected!r}")
        (directory / "output.txt").write_text(transcript, encoding="utf-8")
        make_flowchart(study, directory)
        make_output_image(study, directory, transcript)
        (directory / "README.md").write_text(case_markdown(study, directory, tests, transcript), encoding="utf-8")
        contents.append(case_html(study, directory, tests, transcript, ordinal))
        print(f"Built case {study['number']}: flowchart, output capture, documentation", flush=True)
    write_root_documents(verification)
    write_report(contents, verification)
    print(f"Complete report: {ROOT / 'REPORT.html'}")


if __name__ == "__main__":
    main()
