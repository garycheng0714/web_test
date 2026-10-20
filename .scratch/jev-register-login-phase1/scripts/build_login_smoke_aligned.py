import json
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"
base = ARTIFACTS / "request-login-smoke.json"
out = ARTIFACTS / "request-login-smoke-aligned.json"
payload = json.loads(base.read_text(encoding="utf-8"))

cases = {case["id"]: case for case in payload["state"]["cases"]}

cases["G1"]["steps"][0]["expected_result"] = (
    "The Email Address and Password fields contain the entered values."
)
cases["G1"]["steps"][1]["expected_result"] = (
    "The header shows 'Logged in as <name>'."
)
cases["G2"]["steps"][0]["expected_result"] = (
    "The Email Address and Password fields contain the entered values."
)
cases["G2"]["steps"][1]["expected_result"] = (
    "The error 'Your email or password is incorrect!' is displayed and the user "
    "remains on /login."
)

payload["state"]["source_notes"] = (
    "This experiment uses only prd/login-smoke.md. The good cases were rewritten to "
    "assert only what that PRD states; no screenshots or screen descriptions are supplied."
)

out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out}")
print("G1:", [s["expected_result"] for s in cases["G1"]["steps"]])
print("G2:", [s["expected_result"] for s in cases["G2"]["steps"]])
