import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent.parent / "artifacts" / "request-login-smoke.json"

prd_text = (ROOT / "prd/login-smoke.md").read_text(encoding="utf-8")

cases = [
    {
        "id": "G1",
        "label": "good",
        "requirement_ids": ["FR-ACC-04"],
        "scenario": (
            "Verify that logging in with a registered email and its correct password "
            "logs the user in."
        ),
        "preconditions": [
            "A registered account exists whose email and password are known.",
            "User is a guest on /login.",
        ],
        "steps": [
            {
                "index": 1,
                "action": (
                    "In the 'Login to your account' block enter the registered Email "
                    "Address and its correct Password."
                ),
                "expected_result": (
                    "The entered values are shown in the Email Address and Password fields."
                ),
            },
            {
                "index": 2,
                "action": "Click 'Login'.",
                "expected_result": (
                    "The user is logged in: the header shows 'Logged in as <name>' together "
                    "with 'Logout' and 'Delete Account', and no error message is displayed."
                ),
            },
        ],
    },
    {
        "id": "G2",
        "label": "good",
        "requirement_ids": ["FR-ACC-04"],
        "scenario": (
            "Verify that logging in with incorrect credentials shows the error and keeps "
            "the user on /login as a guest."
        ),
        "preconditions": [
            "A registered account exists and its correct password is known.",
            "User is a guest on /login.",
        ],
        "steps": [
            {
                "index": 1,
                "action": (
                    "In the 'Login to your account' block enter the registered Email "
                    "Address with an incorrect Password."
                ),
                "expected_result": (
                    "The entered email and incorrect password are shown in their fields."
                ),
            },
            {
                "index": 2,
                "action": "Click 'Login'.",
                "expected_result": (
                    "The error 'Your email or password is incorrect!' is displayed, the "
                    "user remains on /login with 'Login to your account' and 'New User "
                    "Signup!' still visible, and the header still shows 'Signup / Login' "
                    "(guest, not logged in)."
                ),
            },
        ],
    },
    {
        "id": "B1",
        "label": "bad",
        "tests": "nonexistent control",
        "requirement_ids": ["FR-ACC-04"],
        "scenario": "Verify that a registered user can log in.",
        "preconditions": ["User is a guest on /login."],
        "steps": [
            {
                "index": 1,
                "action": (
                    "On /login click 'Forgot Password' and enter the registered Email and "
                    "correct Password there."
                ),
                "expected_result": (
                    "The entered values are shown in the Email Address and Password fields."
                ),
            },
            {
                "index": 2,
                "action": "Click 'Login'.",
                "expected_result": (
                    "The user is logged in: the header shows 'Logged in as <name>'."
                ),
            },
        ],
    },
    {
        "id": "B2",
        "label": "bad",
        "tests": "vague expected result",
        "requirement_ids": ["FR-ACC-04"],
        "scenario": "Verify that a registered user can log in.",
        "preconditions": ["User is a guest on /login."],
        "steps": [
            {
                "index": 1,
                "action": (
                    "Enter the registered Email Address and correct Password in the "
                    "'Login to your account' block."
                ),
                "expected_result": "The values are entered.",
            },
            {
                "index": 2,
                "action": "Click 'Login'.",
                "expected_result": "Login works.",
            },
        ],
    },
    {
        "id": "B3",
        "label": "bad",
        "tests": "contradicts the AC",
        "requirement_ids": ["FR-ACC-04"],
        "scenario": "Verify that a registered user can log in with an incorrect password.",
        "preconditions": ["User is a guest on /login."],
        "steps": [
            {
                "index": 1,
                "action": (
                    "Enter the registered Email Address with an incorrect Password in the "
                    "'Login to your account' block."
                ),
                "expected_result": (
                    "The entered email and password are shown in their fields."
                ),
            },
            {
                "index": 2,
                "action": "Click 'Login'.",
                "expected_result": (
                    "The user is logged in: the header shows 'Logged in as <name>' with "
                    "'Logout' and 'Delete Account'."
                ),
            },
        ],
    },
    {
        "id": "B4",
        "label": "bad",
        "tests": "skipped required data entry",
        "requirement_ids": ["FR-ACC-04"],
        "scenario": "Verify that a registered user can log in.",
        "preconditions": ["User is a guest on /login."],
        "steps": [
            {
                "index": 1,
                "action": "Open /login and click 'Login' without entering Email or Password.",
                "expected_result": (
                    "The user is logged in: the header shows 'Logged in as <name>'."
                ),
            },
            {
                "index": 2,
                "action": "Verify the header.",
                "expected_result": (
                    "The header shows 'Logged in as <name>' with 'Logout' and 'Delete Account'."
                ),
            },
        ],
    },
]

rules = {
    "ac_alignment": (
        "Judge whether the case's scenario, preconditions, steps, and expected results "
        "are required or permitted by the PRD requirement text and acceptance criteria. "
        "A precondition is acceptable when the PRD leaves the data source undefined. "
        "A setup step is permitted when it is necessary to reach an AC."
    ),
    "step_reasonable": (
        "Judge whether the step names a concrete action and target that exists in the "
        "supplied PRD text and is consistent with the PRD flow. Do not require a step to "
        "be explicitly written in the PRD when it is a normal part of the described flow."
    ),
    "step_reachable": (
        "Judge whether the step can be performed at this point in the flow: the case's "
        "preconditions and preceding steps must establish everything the step needs."
    ),
    "step_complete": (
        "Judge whether a step is complete: it must include every action and input needed "
        "to produce its expected result, not merely a control that exists."
    ),
    "observable": (
        "Judge whether the expected result is a specific outcome a manual tester could "
        "observe in the PRD text or its verbatim messages. A vague restatement such as "
        "'it works' is not observable."
    ),
}

state = {
    "goal": (
        "Review test-case artifacts for the Automation Exercise login flow using only "
        "the sparse PRD text. No screenshots, screen descriptions, or live page "
        "observations are supplied."
    ),
    "prd_text": prd_text,
    "source_notes": (
        "This experiment uses only prd/login-smoke.md. It has no screenshot appendix and "
        "no screen descriptions."
    ),
    "cases": cases,
    "review_rules": rules,
}

questions = {}
for case in cases:
    cid = case["id"]
    questions[f"ac_{cid}"] = {
        "type": "noul",
        "instructions": (
            f"Is case {cid} directly supported by the PRD requirement text and acceptance "
            "criteria? Judge the scenario, preconditions, all steps, and all expected "
            "results together. A setup step needed to reach an AC is permitted."
        ),
        "criteria": {
            "true": (
                "Every step and expected result is required or permitted by the PRD "
                "requirement text and AC, and no behaviour is invented or contradicted."
            ),
            "false": (
                "At least one step or expected result is unsupported by the PRD requirement "
                "text or AC, contradicts it, or invents behaviour."
            ),
        },
    }
    for step in case["steps"]:
        n = step["index"]
        questions[f"step_{cid}_{n}_reasonable"] = {
            "type": "noul",
            "instructions": (
                f"Does step {n} of case {cid} name a concrete action and target that exists "
                "in the supplied PRD text and is consistent with the PRD flow?"
            ),
            "criteria": {
                "true": (
                    "The action and target are concrete and appear in, or follow directly "
                    "from, the supplied PRD text and flow."
                ),
                "false": (
                    "The action or target is absent from the PRD text, contradicts it, or "
                    "skips a necessary part of the flow."
                ),
            },
        }
        questions[f"step_{cid}_{n}_reachable"] = {
            "type": "noul",
            "instructions": (
                f"Given the case's preconditions and the preceding steps, can step {n} of "
                f"case {cid} be performed as written at this point in the flow?"
            ),
            "criteria": {
                "true": (
                    "The preconditions and preceding steps establish everything this step "
                    "needs, and the step can be performed as written."
                ),
                "false": (
                    "A precondition or preceding step is missing, so the step cannot be "
                    "performed as written or would be invalid at this point."
                ),
            },
        }
        questions[f"step_{cid}_{n}_complete"] = {
            "type": "noul",
            "instructions": (
                f"Does step {n} of case {cid} include every action required to produce its "
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
        questions[f"step_{cid}_{n}_observable"] = {
            "type": "noul",
            "instructions": (
                f"Is the expected result of step {n} of case {cid} a specific, observable "
                "outcome that a manual tester could verify from the PRD text or its "
                "verbatim messages?"
            ),
            "criteria": {
                "true": (
                    "The expected result names a specific visible page, field, text, or state "
                    "that the supplied PRD text describes."
                ),
                "false": (
                    "The expected result is vague, unstated, or not something the supplied "
                    "PRD text lets a tester observe."
                ),
            },
        }

payload = {
    "model": "typesafe/jev-1.13",
    "state": state,
    "questions": questions,
}

OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
print(f"cases={len(cases)} steps={sum(len(c['steps']) for c in cases)} questions={len(questions)}")
