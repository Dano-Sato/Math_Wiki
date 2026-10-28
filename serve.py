"""Serve the wiki viewer locally.

    python serve.py              # http://127.0.0.1:8770 and open a browser
    python serve.py --port 9000 --no-browser
"""

import argparse
import json
import re
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
# Files shown first inside a conjecture folder; the rest follow alphabetically.
PRIMARY = ["conjectures.md", "discussion.md", "score.json"]
TEXT = "text/plain; charset=utf-8"
# Scorers recorded in score.json; the catalog averages whichever are present.
SCORERS = ["claude", "chatgpt"]
META_ROWS = {"버전": "version", "상태": "status", "분야": "field", "깊이": "depth"}


def plain(text):
    return re.sub(r"\*\*|`|\$", "", text).strip()


def parse_meta(text):
    """Title, tagline and header-table rows from a conjectures.md."""
    meta = {}
    title = re.search(r"^#\s+(.+)$", text, re.M)
    meta["title"] = re.sub(r"^\d+\s*·\s*", "", title.group(1)).strip() if title else ""
    tagline = re.search(r"^>\s*(.+)$", text, re.M)
    meta["tagline"] = plain(tagline.group(1)) if tagline else ""
    for key, field in META_ROWS.items():
        row = re.search(rf"^\|\s*{key}\s*\|\s*(.+?)\s*\|\s*$", text, re.M)
        meta[field] = plain(row.group(1)) if row else ""
    return meta


def read_score_data(folder):
    try:
        data = json.loads((folder / "score.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    return data if isinstance(data, dict) else {}


def read_scores(folder, data=None):
    if data is None:
        data = read_score_data(folder)
    scores = {}
    for name in SCORERS:
        entry = data.get(name)
        if isinstance(entry, dict) and isinstance(entry.get("score"), (int, float)):
            scores[name] = entry
    return scores


def target_ids(value, fallback):
    if value is None:
        return list(fallback)
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        return []
    return sorted(set(value))


def score_assessment(number, data, scores):
    """Keep old assessments visible, but average only the current target set."""
    declared = data.get("assessment")
    declared = declared if isinstance(declared, dict) else {}
    targets = target_ids(declared.get("targets"), [number])
    scopes = {name: target_ids(entry.get("targets"), [number])
              for name, entry in scores.items()}
    eligible = [name for name in scores if targets and scopes[name] == targets]
    values = [scores[name]["score"] for name in eligible]
    label = declared.get("label")
    if not isinstance(label, str) or not label.strip():
        label = " · ".join(targets) if targets else "평가 대상 확인 필요"
    return {
        "assessment": {"targets": targets, "label": label},
        "score_targets": scopes,
        "eligible_scorers": eligible,
        "average": sum(values) / len(values) if values else None,
    }


def tree():
    conjectures = []
    base = ROOT / "conjectures"
    for folder in sorted(p for p in base.iterdir() if p.is_dir()) if base.exists() else []:
        files = sorted(
            (f.name for f in folder.iterdir() if f.is_file()),
            key=lambda name: (PRIMARY.index(name) if name in PRIMARY else len(PRIMARY), name),
        )
        number, _, slug = folder.name.partition("-")
        try:
            meta = parse_meta((folder / "conjectures.md").read_text(encoding="utf-8"))
        except OSError:
            meta = parse_meta("")
        score_data = read_score_data(folder)
        scores = read_scores(folder, score_data)
        conjectures.append({
            "id": number,
            "slug": slug,
            "dir": f"conjectures/{folder.name}",
            "files": files,
            **meta,
            "scores": scores,
            **score_assessment(number, score_data, scores),
        })
    return {"readme": "README.md", "scorers": SCORERS, "conjectures": conjectures}


class Handler(SimpleHTTPRequestHandler):
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".md": "text/markdown; charset=utf-8",
        ".json": "application/json; charset=utf-8",
        ".py": TEXT,
        ".go": TEXT,
        ".txt": TEXT,
        ".html": "text/html; charset=utf-8",
        ".js": "text/javascript; charset=utf-8",
        ".css": "text/css; charset=utf-8",
    }

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/api/tree":
            body = json.dumps(tree(), ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/":
            self.path = "/viewer/index.html"
        super().do_GET()

    def end_headers(self):
        # Edits to the wiki should show up on reload.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(ROOT)))
    url = f"http://127.0.0.1:{args.port}/"
    print(f"위키 뷰어: {url}  (Ctrl+C로 종료)")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
