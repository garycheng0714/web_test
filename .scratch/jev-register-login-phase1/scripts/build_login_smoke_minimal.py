import json
from pathlib import Path

ARTIFACTS = Path(__file__).resolve().parent.parent / "artifacts"
base = ARTIFACTS / "request-login-smoke-aligned.json"
out = ARTIFACTS / "request-login-smoke-minimal.json"
payload = json.loads(base.read_text(encoding="utf-8"))
cases = {case["id"]: case for case in payload["state"]["cases"]}

cases["G1"]["steps"] = [
    {
        "index": 1,
        "action": "Open /login.",
        "expected_result": (
            "The 'Login to your account' block is displayed with Email Address, "
            "Password, and a 'Login' button."
        ),
    },
    {
        "index": 2,
        "action": (
            "Enter the registered Email Address and correct Password, then click 'Login'."
        ),
        "expected_result": "The header shows 'Logged in as <name>'.",
    },
]

cases["G2"]["steps"] = [
    {
        "index": 1,
        "action": "Open /login.",
        "expected_result": (
            "The 'Login to your account' block is displayed with Email Address, "
            "Password, and a 'Login' button."
        ),
    },
    {
        "index": 2,
        "action": (
            "Enter the registered Email Address with an incorrect Password, then click "
            "'Login'."
        ),
        "expected_result": (
            "The error 'Your email or password is incorrect!' is displayed and the user "
            "remains on /login."
        ),
    },
]

payload["state"]["source_notes"] = (
    "This experiment uses only prd/login-smoke.md. The good cases were reduced to "
    "expectations stated verbatim by that PRD; no screenshots or descriptions are supplied."
)

out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {out}")
