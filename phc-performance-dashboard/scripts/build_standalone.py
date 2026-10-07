"""Bundle index.html and its data into one file that opens offline.

    python scripts/build_standalone.py

Writes PHC_Performance_Dashboard.html next to index.html. Share or download
that single file; it needs no server, internet connection or other files.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAG = '<script src="data/phc_2026_deidentified.js"></script>'

html = (ROOT / "index.html").read_text(encoding="utf-8")
data = (ROOT / "data" / "phc_2026_deidentified.js").read_text(encoding="utf-8")
assert html.count(TAG) == 1, "data script tag not found in index.html"
out = html.replace(TAG, "<script>\n" + data.replace("</", "<\\/") + "</script>")
dest = ROOT / "PHC_Performance_Dashboard.html"
dest.write_text(out, encoding="utf-8")
print(f"wrote {dest.name} ({dest.stat().st_size / 1024:.0f} KB)")
