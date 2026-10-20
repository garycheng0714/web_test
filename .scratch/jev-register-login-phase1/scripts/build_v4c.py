import json
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"
base = ARTIFACTS / "request-v4b.json"
out = ARTIFACTS / "request-v4c.json"
payload = json.loads(base.read_text(encoding="utf-8"))

state = payload["state"]
text = state["prd_text"]
start = text.index("## 附錄 A：截圖")
end = text.index("## 附錄 B")
state["prd_text"] = text[:start] + text[end:]
state["source_notes"] = (
    "This variant removes Appendix A (the screenshot index) from the PRD text. "
    "No screen descriptions, screenshot images, or live page observations are supplied. "
    "Appendix B remains."
)

out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out}")
print("has Appendix A:", "附錄 A" in state["prd_text"])
print("has Appendix B:", "附錄 B" in state["prd_text"])
print("prd chars:", len(state["prd_text"]))
