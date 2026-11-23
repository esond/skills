"""Generate one voice-eval arm with a local model served by Ollama.

usage: python ollama_arm.py <round_dir> <model> <prompt_file> <arm>

Sends each scenario in <round_dir>/scenarios.json to the writer-ollama
container on http://localhost:11435 as its own chat, with <prompt_file> as
the system prompt, and writes <round_dir>/out-<arm>.json in the same shape
the subagent arms write.
"""

import json
import re
import sys
import urllib.request
from pathlib import Path

INSTRUCTION = (
    "Write exactly the message the user will send under their own name, given "
    "this context and their ask. Output only the message: no commentary, no "
    "options, no placeholders.\n\n"
)


def main(round_dir, model, prompt_file, arm):
    d = Path(round_dir).expanduser().resolve()
    system = Path(prompt_file).expanduser().read_text(encoding="utf-8")
    out = []
    for sc in json.loads((d / "scenarios.json").read_text(encoding="utf-8")):
        body = {
            "model": model,
            "stream": False,
            "options": {"num_ctx": 8192},
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": INSTRUCTION + json.dumps(
                    {"context": sc["context"], "ask": sc["ask"]}, indent=2)},
            ],
        }
        req = urllib.request.Request(
            "http://localhost:11435/api/chat",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=600) as r:
            text = json.load(r)["message"]["content"]
        # Reasoning models (qwen3, deepseek-r1) prepend their thinking.
        text = re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()
        out.append({"scenario": sc["id"], "text": text})
        print(f"{sc['id']} done", file=sys.stderr)
    (d / f"out-{arm}.json").write_text(json.dumps(out, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main(*sys.argv[1:])
