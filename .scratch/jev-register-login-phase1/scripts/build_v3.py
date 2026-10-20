import json
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"
base = ARTIFACTS / "request-v2.json"
out = ARTIFACTS / "request-v3.json"
payload = json.loads(base.read_text(encoding="utf-8"))

questions = payload["questions"]
questions.pop("step_B4_1_reachable", None)
questions.pop("step_B4_2_reachable", None)

for n in (1, 2):
    questions[f"step_B4_{n}_complete"] = {
        "type": "noul",
        "instructions": (
            f"Does step {n} of case B4 include every action required to produce its "
            "expected result, including required data entry?"
        ),
        "criteria": {
            "true": (
                "The step includes all required actions and inputs; nothing needed for "
                "the expected result is missing."
            ),
            "false": (
                "A required action or input is missing, so the step as written cannot "
                "produce the expected result."
            ),
        },
    }

payload["state"]["review_rules"]["step_complete"] = (
    "Judge whether a step is complete: it must include every action and input needed "
    "to produce its expected result, not merely a control that exists."
)

out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out}")
print(f"questions={len(payload['questions'])}")
