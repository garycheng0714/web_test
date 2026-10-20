import json
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"
base = ARTIFACTS / "request-v3.json"
out = ARTIFACTS / "request-v4b.json"
payload = json.loads(base.read_text(encoding="utf-8"))

state = payload["state"]
state.pop("screen_descriptions", None)
state["source_notes"] = (
    "This variant uses only the PRD text as evidence. No screen descriptions, "
    "screenshot images, or live page observations are supplied."
)

def rewrite(value):
    if isinstance(value, str):
        return (
            value.replace("the supplied screen descriptions or the PRD's verbatim messages", "the PRD text or its verbatim messages")
            .replace("the supplied screen descriptions and PRD flow", "the supplied PRD text and PRD flow")
            .replace("the supplied screen descriptions", "the supplied PRD text")
            .replace("screen descriptions", "PRD text")
        )
    if isinstance(value, list):
        return [rewrite(item) for item in value]
    if isinstance(value, dict):
        return {key: rewrite(item) for key, item in value.items()}
    return value

payload = rewrite(payload)

out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out}")
print(f"state keys={list(payload['state'])}")
print(f"questions={len(payload['questions'])}")
