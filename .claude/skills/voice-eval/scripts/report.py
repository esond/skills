"""Summarize scored voice-eval rounds.

usage: python report.py <round_dir> [<round_dir> ...]

One round: means by arm, by arm and channel, by tag value, plus every item
scored 1-2 or carrying a note. Several rounds: also a by-arm trend table.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, pstdev


def load_round(d):
    d = Path(d).expanduser().resolve()
    items = json.loads((d / "items.json").read_text(encoding="utf-8"))["items"]
    scores = {}
    sp = d / "scores.jsonl"
    if sp.exists():
        for line in sp.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                scores[rec["id"]] = rec  # last write wins
    for it in items:
        rec = scores.get(it["id"], {})
        it["score"] = rec.get("score")
        it["note"] = rec.get("note", "")
    return d.name, items


def stat(vals):
    if not vals:
        return "  -"
    return f"{mean(vals):.2f} sd {pstdev(vals):.2f} (n={len(vals)})"


def group(items, key):
    g = defaultdict(list)
    for it in items:
        if it["score"] is not None:
            for k in key(it):
                g[k].append(it["score"])
    return g


def report(name, items):
    scored = [it for it in items if it["score"] is not None]
    print(f"# {name}: {len(scored)}/{len(items)} scored\n")

    print("## By arm")
    for arm, vals in sorted(group(items, lambda it: [it["arm"]]).items()):
        print(f"- {arm}: {stat(vals)}")
    for arm in ("control", "anchor"):
        vals = [it["score"] for it in scored if it["arm"] == arm]
        if vals and mean(vals) < 4:
            print(f"- WARNING: {arm} items average {mean(vals):.2f}, expected 4+; "
                  "the scale has drifted or the context display is off.")

    print("\n## By arm and channel")
    for k, vals in sorted(group(items, lambda it: [(it["arm"], it["context"].get("channel", "?"))]).items()):
        print(f"- {k[0]} / {k[1]}: {stat(vals)}")

    tags = group(items, lambda it: it.get("tags", []))
    if tags:
        print("\n## By tag")
        for tag, vals in sorted(tags.items()):
            print(f"- {tag}: {stat(vals)}")

    flagged = [it for it in scored if it["score"] <= 2 or it["note"]]
    flagged += [it for it in items if it["score"] is None and it["note"]]
    if flagged:
        print("\n## Low scores and notes")
        for it in sorted(flagged, key=lambda it: (it["score"] or 0)):
            print(f"\n### {it['id']} [{it['arm']}] score={it['score']} tags={','.join(it.get('tags', []))}")
            c = it["context"]
            print(f"context: {c.get('channel')} / to {c.get('to')} / {c.get('situation')}")
            if it["note"]:
                print(f"NOTE: {it['note']}")
            print("> " + it["text"].replace("\n", "\n> "))
    print()


def main(dirs):
    if not dirs:
        sys.exit(__doc__)
    rounds = [load_round(d) for d in dirs]
    for name, items in rounds:
        report(name, items)
    if len(rounds) > 1:
        print("# Trend by arm")
        for name, items in rounds:
            arms = group(items, lambda it: [it["arm"]])
            print(f"- {name}: " + "; ".join(f"{a} {mean(v):.2f}" for a, v in sorted(arms.items())))


if __name__ == "__main__":
    main(sys.argv[1:])
