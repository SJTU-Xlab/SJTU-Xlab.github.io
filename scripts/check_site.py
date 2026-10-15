"""Validate the publishable static site using only the Python standard library."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import json
import math
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []
links = []
scripts = []

class PageParser(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.inline = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for name in ("href", "src"):
            if name in attrs:
                links.append((self.path, attrs[name]))
        if tag == "script" and "src" not in attrs:
            self.inline = []

    def handle_data(self, data):
        if self.inline is not None:
            self.inline.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.inline is not None:
            scripts.append((self.path.name, "".join(self.inline)))
            self.inline = None

def check_local(source, url):
    if url.startswith(("#", "//")):
        return
    parts = urlsplit(url)
    if parts.scheme or not parts.path:
        return
    target = ROOT / unquote(parts.path.lstrip("/")) if parts.path.startswith("/") else source.parent / unquote(parts.path)
    if target.is_dir():
        target = target / "index.html"
    try:
        relative = target.resolve().relative_to(ROOT)
    except ValueError:
        errors.append(f"{source.name}: link escapes site: {url}")
        return
    current = ROOT
    for piece in relative.parts:
        if not current.is_dir() or piece not in {entry.name for entry in current.iterdir()}:
            errors.append(f"{source.name}: missing/case-mismatched target: {url}")
            return
        current /= piece

pages = sorted(ROOT.glob("*.html"))
for page in pages:
    text = page.read_text(encoding="utf-8")
    parser = PageParser(page)
    parser.feed(text)
    for pattern in (r"jquery", r"\$\.ajax", r"\$\.each", r"[\"'](?:/|\./)api/", r"/static(?:Mdui|Main|Drone|Commu)/", r"http://apps\.bdimg"):
        if re.search(pattern, text, re.I):
            errors.append(f"{page.name}: legacy dependency: {pattern}")
    for url in re.findall(r"[\"'](\./static/[^\"']+)[\"']", text):
        links.append((page, url))
for css in (ROOT / "static").rglob("*.css"):
    for url in re.findall(r"url\(\s*['\"]?([^)'\"\s]+)", css.read_text(encoding="utf-8")):
        links.append((css, url))
for source, url in links:
    check_local(source, url)

counts = {}
for name, fields in (("sigs", ["Lat", "Lng", "Amp"]), ("sigsmutils", ["Lat", "Lng", "Time"] + [f"F{i}" for i in range(20, 41)])):
    rows = json.loads((ROOT / "data" / (name + ".json")).read_text(encoding="utf-8"))
    counts[name] = len(rows)
    if not isinstance(rows, list) or not rows:
        errors.append(f"{name}: expected a non-empty array")
    for index, row in enumerate(rows):
        if set(row) != set(fields):
            errors.append(f"{name}[{index}]: unexpected fields")
        for field in fields:
            value = row.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                errors.append(f"{name}[{index}].{field}: invalid numeric value")
        if not -90 <= row.get("Lat", 999) <= 90 or not -180 <= row.get("Lng", 999) <= 180:
            errors.append(f"{name}[{index}]: invalid coordinates")
        if "Time" in row and int(row["Time"]) != row["Time"]:
            errors.append(f"{name}[{index}]: Time must be an integer")

node = shutil.which("node")
if node:
    scripts.extend((str(js.relative_to(ROOT)), js.read_text(encoding="utf-8")) for js in (ROOT / "static/js").glob("*.js"))
    for label, script in scripts:
        result = subprocess.run([node, "--check", "-"], input=script, text=True, encoding="utf-8", capture_output=True)
        if result.returncode:
            errors.append(label + ": " + result.stderr)
else:
    print("Node.js not installed; JavaScript syntax check skipped.")
if errors:
    print("\n".join(errors))
    sys.exit(1)
print(f"PASS: {len(pages)} HTML pages, {len(links)} local/external resource references, data={counts}, {len(scripts)} scripts checked")
