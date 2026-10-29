# Evals 基礎完成：從 traces 到校正後的通過率

2026-10-27 完成七課 + capstone。使用者能從 traces 收斂 failure modes、選 code vs judge、
寫 binary judge、用 TPR/TNR 與 CI 校準，並 audit 一份 pipeline。最關鍵的非顯而易見洞見：
a/b diff 是便宜的 oracle；judge 的邊界由定義與 few-shot 的一致性決定；5/5 不是 validation；
CI 的寬度由分母與 J 決定。

## Evidence

- `lessons/0001`–`0007` 完成；`audit.md` 有 6 個 findings。
- `toy/checks.py` 的 party/special checks；`judge_tone.md` 與
  `tone_lite_metrics.md`（toy rehearsal 32/32，CI [0.806, 1.000]）。
- 修正過的誤解：a/b 對調、N 變小不會讓 CI 變窄、Area+Status 不是 finding。

## Implications

- 下一步若接真實專案，需要放寬 MISSION 的「無真實 traces／無 API」constraint。
- 真實 validation 需要可重現 runner、~50／50 labels、第二 annotator；
  toy 的 32／32 不能當 production evidence。
- 可延伸：CI 的兩個噪聲來源、full bootstrap、RAG evals。
