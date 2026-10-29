#!/usr/bin/env python3
"""One code evaluator per failure mode.

    python3 learn/evals/toy/checks.py

Worked example: party mismatch. Add your own check below and register it in CHECKS.
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
TRACES = HERE / "traces.jsonl"

PARTY = re.compile(r"(\d+)\s*(?:位|人)")


@dataclass
class Result:
    trace_id: str
    passed: bool
    reason: str


def first_party(text):
    match = PARTY.search(text)
    return int(match.group(1)) if match else None


def check_party_mismatch(trace):
    user, assistant = (turn["content"] for turn in trace["turns"])
    wanted = first_party(user)
    got = first_party(assistant)
    if wanted is None or got is None:
        return Result(trace["id"], True, "no party size in both turns")
    if wanted != got:
        return Result(trace["id"], False, f"user asked {wanted}, reply says {got}")
    return Result(trace["id"], True, f"party size matches ({wanted})")


SPECIAL_EVENTS = {
    "window": ["靠窗", "窗邊"],
    "accessibility": ["無障礙"],
    "birthday": ["生日", "慶生"],
    "allergy": ["花生過敏"],
    "children": ["兒童椅"],
}


def check_special_omitted(trace):
    user, assistant = (turn["content"] for turn in trace["turns"])
    mentioned = [
        key
        for key, synonyms in SPECIAL_EVENTS.items()
        if any(synonym in user for synonym in synonyms)
    ]
    if not mentioned:
        return Result(trace["id"], True, "no special request")

    omitted = [
        key
        for key in mentioned
        if not any(synonym in assistant for synonym in SPECIAL_EVENTS[key])
    ]
    if omitted:
        return Result(trace["id"], False, f"special not mentioned: {', '.join(omitted)}")
    return Result(trace["id"], True, f"special mentioned: {', '.join(mentioned)}")


CHECKS = {
    "party_mismatch": check_party_mismatch,
    "special_omitted": check_special_omitted,
}


def load_traces():
    return [
        json.loads(line)
        for line in TRACES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def self_check():
    traces = {trace["id"]: trace for trace in load_traces()}

    assert not check_special_omitted(traces["t-005-a"]).passed
    assert check_special_omitted(traces["t-006-b"]).passed

    two_specials = {
        "id": "synthetic-two-specials",
        "turns": [
            {"role": "user", "content": "我想訂週五 19:00，4 位，窗邊，生日。"},
            {
                "role": "assistant",
                "content": "好的，已為您保留週五 19:00 的 4 人桌。我會幫您備註希望靠窗。",
            },
        ],
    }
    assert not check_special_omitted(two_specials).passed

    negative_mention = {
        "id": "synthetic-negative-mention",
        "turns": [
            {"role": "user", "content": "我想訂週五 19:00，4 位，窗邊。"},
            {"role": "assistant", "content": "抱歉，我們沒有窗邊座位。"},
        ],
    }
    # mention-only proxy: passes even though the request is not fulfilled
    assert check_special_omitted(negative_mention).passed

    print("self-check ok")


def main():
    self_check()
    traces = load_traces()
    for name, check in CHECKS.items():
        results = [check(trace) for trace in traces]
        failures = [result for result in results if not result.passed]
        print(f"\n{name}: {len(failures)} fail / {len(results)}")
        for result in failures:
            print(f"  {result.trace_id}: {result.reason}")


if __name__ == "__main__":
    main()
