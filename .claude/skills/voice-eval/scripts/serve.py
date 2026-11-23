"""Serve one voice-eval round for keyboard scoring.

usage: python serve.py <round_dir> [--port N] [--no-open]

Reads <round_dir>/items.json, serves the scorer UI, and appends every score to
<round_dir>/scores.jsonl as it happens, so a round can be stopped and resumed.
The UI never sees an item's arm or tags. Exits when the UI posts /api/done.
"""

import argparse
import json
import sys
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HTML = Path(__file__).with_name("scorer.html")


def load_scores(path):
    scores = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                scores[rec["id"]] = {"score": rec.get("score"), "note": rec.get("note", "")}
    return scores


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("round_dir")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    round_dir = Path(args.round_dir).expanduser().resolve()
    round_data = json.loads((round_dir / "items.json").read_text(encoding="utf-8"))
    scores_path = round_dir / "scores.jsonl"
    public_items = [
        {"id": it["id"], "context": it["context"], "text": it["text"]}
        for it in round_data["items"]
    ]
    lock = threading.Lock()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def send(self, code, body, ctype="application/json"):
            data = body.encode("utf-8") if isinstance(body, str) else body
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/":
                self.send(200, HTML.read_bytes(), "text/html; charset=utf-8")
            elif self.path == "/api/round":
                payload = {
                    "round": round_dir.name,
                    "items": public_items,
                    "scores": load_scores(scores_path),
                }
                self.send(200, json.dumps(payload))
            else:
                self.send(404, "{}")

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0)
            if self.path == "/api/score":
                rec = json.loads(body)
                rec = {
                    "id": rec["id"],
                    "score": rec.get("score"),
                    "note": rec.get("note", ""),
                    "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
                with lock, scores_path.open("a", encoding="utf-8") as f:
                    f.write(json.dumps(rec) + "\n")
                self.send(200, "{}")
            elif self.path == "/api/done":
                self.send(200, "{}")
                threading.Thread(target=server.shutdown, daemon=True).start()
            else:
                self.send(404, "{}")

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"Scoring {round_dir.name} ({len(public_items)} items) at {url}", flush=True)
    if not args.no_open:
        webbrowser.open(url)
    server.serve_forever()
    scored = sum(1 for s in load_scores(scores_path).values() if s["score"] is not None)
    print(f"Round {round_dir.name} closed: {scored}/{len(public_items)} scored.")


if __name__ == "__main__":
    sys.exit(main())
