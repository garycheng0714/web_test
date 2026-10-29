#!/usr/bin/env python3
"""Toy restaurant reservation pipeline.

Reads tuples.json, writes traces.jsonl and answer-key.json.
Stdlib only. Run from anywhere:

    python3 learn/evals/toy/pipeline.py
"""

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FULL = {("週六", "20:00"), ("母親節", "19:00"), ("情人節", "19:00")}
INTENTS = {"booking", "modify", "cancel", "question", "out_of_scope"}
CLARITIES = {"clear", "ambiguous", "special_request"}

SPECIAL_ACK = {
    "窗邊": "我會幫您備註希望靠窗。",
    "生日": "我會幫您備註慶生，可以協助準備小蛋糕。",
    "花生過敏": "我會幫您備註花生過敏，並提醒廚房。",
    "兒童椅": "我會幫您準備兒童椅。",
    "無障礙": "我會幫您安排無障礙座位。",
}

TIME = re.compile(r"\d{2}:\d{2}")


def load_tuples():
    path = HERE / "tuples.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        sys.exit(f"tuples.json 不是合法 JSON：{exc}")
    if not isinstance(data, list):
        sys.exit("tuples.json 必須是陣列")
    validate(data)
    return data


def validate(tuples):
    seen = set()
    for i, t in enumerate(tuples, 1):
        where = f"第 {i} 個 tuple"
        if not isinstance(t, dict):
            sys.exit(f"{where} 必須是物件")
        tid = t.get("id")
        if not isinstance(tid, str) or not tid:
            sys.exit(f"{where} 缺少 id")
        if tid in seen:
            sys.exit(f"id 重複：{tid}")
        seen.add(tid)

        if t.get("intent") not in INTENTS:
            sys.exit(f"{tid}: intent 必須是 {sorted(INTENTS)}")
        if t.get("clarity") not in CLARITIES:
            sys.exit(f"{tid}: clarity 必須是 {sorted(CLARITIES)}")
        if not isinstance(t.get("party"), int) or not 1 <= t["party"] <= 20:
            sys.exit(f"{tid}: party 必須是 1–20 的整數")

        if t["intent"] == "out_of_scope":
            if t.get("day") or t.get("time"):
                sys.exit(f"{tid}: out_of_scope 不該有 day/time")
            continue

        if not isinstance(t.get("day"), str) or not t["day"]:
            sys.exit(f"{tid}: 缺少 day")

        if t["intent"] != "booking" or t["clarity"] != "ambiguous":
            if not isinstance(t.get("time"), str) or not TIME.fullmatch(t["time"]):
                sys.exit(f"{tid}: time 必須是 HH:MM")

        if t["intent"] == "modify":
            if not isinstance(t.get("new_time"), str) or not TIME.fullmatch(t["new_time"]):
                sys.exit(f"{tid}: modify 需要 new_time（HH:MM）")
            if t["new_time"] == t["time"]:
                sys.exit(f"{tid}: new_time 不能等於 time")

        if t["clarity"] == "special_request":
            if t.get("special") not in {*SPECIAL_ACK, "包場"}:
                sys.exit(f"{tid}: special 必須是 {sorted({*SPECIAL_ACK, '包場'})}")
        elif t.get("special"):
            sys.exit(f"{tid}: 只有 special_request 可以有 special")


def render_query(t, variant):
    party = f"{t['party']} 位"
    if t["intent"] == "out_of_scope":
        return "請問你們有外送嗎？" if variant == "a" else "你們有做外送嗎？"
    if t["intent"] == "cancel":
        return (
            f"我想取消{t['day']} {t['time']} 的{t['party']} 人訂位。"
            if variant == "a"
            else f"幫我取消{t['day']} {t['time']}，{party}。"
        )
    if t["intent"] == "modify":
        return (
            f"我原本訂{t['day']} {t['time']}，想改成 {t['new_time']}，{party}。"
            if variant == "a"
            else f"我想把{t['day']} {t['time']} 的{t['party']} 人訂位改到 {t['new_time']}。"
        )
    if t["intent"] == "question":
        need = ""
        if t["clarity"] == "special_request":
            need = (
                "需要無障礙座位。"
                if t["special"] == "無障礙"
                else f"另外，{t['special']}。"
            )
        return (
            f"請問{t['day']} {t['time']} 還有{party}的位子嗎？{need}"
            if variant == "a"
            else f"{t['day']} {t['time']} 還有{party}的位子嗎？{need}"
        )
    if t["clarity"] == "ambiguous":
        return (
            f"你好，我想訂{t['day']}晚上，{party}。"
            if variant == "a"
            else f"我想訂{t['day']}晚上，{party}，時間都可以。"
        )
    if t["clarity"] == "special_request":
        return (
            f"你好，我想訂{t['day']} {t['time']}，{party}，{t['special']}。"
            if variant == "a"
            else f"{t['day']} {t['time']}，{party}，{t['special']}，可以嗎？"
        )
    return (
        f"你好，我想訂{t['day']} {t['time']}，{party}。"
        if variant == "a"
        else f"請問{t['day']} {t['time']} 可以訂{party}嗎？"
    )


def availability(t, special=True):
    ack = SPECIAL_ACK.get(t.get("special"), "") if special else ""
    if (t["day"], t["time"]) in FULL:
        tail = f"若改到 18:00，{ack}" if ack else ""
        return (
            f"抱歉，{t['day']} {t['time']} 已經客滿。"
            f"當天 18:00 或 21:00 還有位子，{tail}需要幫您保留嗎？"
        )
    reply = f"有的，{t['day']} {t['time']} 目前還有 {t['party']} 人的位子。需要我幫您保留嗎？"
    return f"{reply} {ack}".strip()


def booking_reply(t, special=True, force_available=False):
    if t.get("special") == "包場" and special:
        return (
            f"{t['day']} {t['time']} 的包場需要專人報價，我會請業務與您聯繫。"
            "請問方便留下聯絡方式嗎？"
        )
    if not force_available and (t["day"], t["time"]) in FULL:
        ack = SPECIAL_ACK.get(t.get("special"), "") if special else ""
        tail = f"若改到 18:00，{ack}" if ack else ""
        return (
            f"抱歉，{t['day']} {t['time']} 已經客滿。"
            f"當天 18:00 或 21:00 還有位子，{tail}需要幫您保留嗎？"
        )
    ack = SPECIAL_ACK.get(t.get("special"), "") if special else ""
    return (
        f"好的，已為您保留{t['day']} {t['time']} 的 {t['party']} 人桌。"
        f"{ack}請問需要留下聯絡電話嗎？"
    )


def clean_reply(t, special=True):
    if t["intent"] == "out_of_scope":
        return "我們目前只有內用，沒有外送服務。請問需要幫您訂位嗎？"
    if t["intent"] == "cancel":
        return (
            f"好的，已為您取消{t['day']} {t['time']} 的 {t['party']} 人訂位。"
            "請問還有其他需要嗎？"
        )
    if t["intent"] == "question":
        return availability(t, special=special)
    if t["intent"] == "modify":
        return (
            f"好的，我幫您把{t['day']} {t['time']} 的 {t['party']} 人訂位改到 "
            f"{t['new_time']}。請問這樣正確嗎？"
        )
    if t["clarity"] == "ambiguous":
        return (
            f"沒問題。請問您想訂{t['day']}的幾點？"
            f"{t['party']} 人的位子我先幫您留意。"
        )
    return booking_reply(t, special=special)


# ---------------------------------------------------------------------------
# SPOILER: 以下到 inject() 結束是 Lesson 0003 的答案。做完那個 lesson 再讀。
# ---------------------------------------------------------------------------

WRONG_DAY = {
    "週五": "週六",
    "週六": "週日",
    "週日": "下週二",
    "下週二": "週三",
    "週三": "週五",
}
WRONG_TIME = {
    "19:00": "19:15",
    "20:00": "20:30",
    "12:00": "12:30",
    "18:30": "19:00",
    "13:00": "13:30",
    "18:00": "18:30",
    "21:00": "21:30",
}
TONE = {
    "booking": " 記得準時到嘿。",
    "modify": " 就這樣，別再改囉。",
    "cancel": " 好喔，取消囉。",
    "question": " 要訂就快喔。",
    "out_of_scope": " 我們只做內用啦。",
}


PLAN = {
    "t-001": ["time_hallucination", None],
    "t-002": [None, "false_availability"],
    "t-003": ["day_mismatch", None],
    "t-004": ["party_mismatch", "missing_confirmation"],
    "t-005": ["dropped_special", "tone_mismatch"],
    "t-006": ["false_availability", "day_mismatch"],
    "t-007": [None, "party_mismatch"],
    "t-008": ["time_hallucination", None],
    "t-009": ["assumed_time", None],
    "t-010": [None, "assumed_time"],
    "t-011": ["party_mismatch", None],
    "t-012": [None, "missing_confirmation"],
    "t-013": ["time_hallucination", None],
    "t-014": [None, "day_mismatch"],
    "t-015": ["party_mismatch", None],
    "t-016": [None, "tone_mismatch"],
    "t-017": ["party_mismatch", None],
    "t-018": ["dropped_special", None],
    "t-019": ["false_promise", None],
    "t-020": ["dropped_special", None],
    "t-021": ["false_availability", None],
    "t-022": [None, "dropped_special"],
}


def applicable(t, defect):
    if defect == "false_availability":
        return (t.get("day"), t.get("time")) in FULL and t["intent"] in ("booking", "question")
    if defect == "false_promise":
        return t["intent"] == "out_of_scope"
    if defect == "assumed_time":
        return t["intent"] == "booking" and t["clarity"] == "ambiguous"
    if defect == "party_mismatch":
        return (
            t["intent"] != "out_of_scope"
            and t.get("special") != "包場"
            and not ((t.get("day"), t.get("time")) in FULL and t["intent"] in ("booking", "question"))
        )
    if defect == "day_mismatch":
        return t["intent"] != "out_of_scope"
    if defect == "time_hallucination":
        return (
            t["intent"] in ("booking", "modify", "question")
            and t["clarity"] != "ambiguous"
            and (t.get("day"), t.get("time")) not in FULL
        )
    if defect == "dropped_special":
        return t["clarity"] == "special_request"
    return defect in ("missing_confirmation", "tone_mismatch")


def defect_for(t, variant):
    defect = PLAN.get(t["id"], [None, None])[0 if variant == "a" else 1]
    return defect if defect and applicable(t, defect) else None


def inject(t, defect, variant):
    if defect is None:
        return clean_reply(t)
    if defect == "party_mismatch":
        wrong = t["party"] + 1 if t["party"] < 8 else t["party"] - 2
        return (
            clean_reply(t)
            .replace(f"{t['party']} 人", f"{wrong} 人")
            .replace(f"{t['party']} 位", f"{wrong} 位")
        )
    if defect == "day_mismatch":
        return clean_reply(t).replace(t["day"], WRONG_DAY.get(t["day"], "下週三"))
    if defect == "time_hallucination":
        target = t.get("new_time") if t["intent"] == "modify" else t["time"]
        wrong = WRONG_TIME.get(target)
        return clean_reply(t).replace(target, wrong) if wrong else clean_reply(t)
    if defect == "dropped_special":
        return clean_reply(t, special=False)
    if defect == "missing_confirmation":
        return "好的，沒問題！" if variant == "a" else "收到，已處理。"
    if defect == "tone_mismatch":
        return clean_reply(t) + TONE[t["intent"]]
    if defect == "assumed_time":
        return booking_reply(dict(t, time="19:00"))
    if defect == "false_availability":
        return booking_reply(t, force_available=True)
    if defect == "false_promise":
        return "有的，我們有外送服務，滿 500 元免運。"
    raise ValueError(defect)


def main():
    traces = []
    key = {}
    for t in load_tuples():
        for variant in ("a", "b"):
            rid = f"{t['id']}-{variant}"
            defect = defect_for(t, variant)
            traces.append(
                {
                    "id": rid,
                    "tuple_id": t["id"],
                    "turns": [
                        {"role": "user", "content": render_query(t, variant)},
                        {"role": "assistant", "content": inject(t, defect, variant)},
                    ],
                    "meta": {
                        "intent": t["intent"],
                        "clarity": t["clarity"],
                        "party": t["party"],
                        "day": t.get("day"),
                        "time": t.get("time"),
                        "language": "zh-TW",
                    },
                }
            )
            key[rid] = {
                "tuple_id": t["id"],
                "defect": defect,
                "expected": {
                    k: t[k]
                    for k in ("intent", "party", "clarity", "day", "time", "new_time", "special")
                    if k in t
                },
            }

    (HERE / "traces.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in traces),
        encoding="utf-8",
    )
    (HERE / "answer-key.json").write_text(
        json.dumps(
            {"_warning": "Spoiler: 完成 Lesson 0003 再打開。", **key},
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(traces)} traces -> toy/traces.jsonl")
    print("answer key -> toy/answer-key.json (spoiler: finish Lesson 0003 first)")


if __name__ == "__main__":
    main()
