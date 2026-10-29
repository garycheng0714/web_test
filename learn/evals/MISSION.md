# Mission: 學會 LLM evals 的基礎

## Why
你是 QA 背景的工程師，想學會「怎麼知道一個 LLM 功能到底好不好」。目標不是背指標，
而是能對一個 LLM 產品從零建一套可信的評測：找出真實 failure modes、選對 evaluator、
驗證它跟人類判斷一致，並回報帶不確定性的數字。

## Success looks like
- 能解釋為什麼 error analysis 必須先於 evaluator
- 能從 traces 收斂出可命名的 failure modes
- 能判斷一個 failure mode 該用 code evaluator 還是 LLM judge
- 能寫出 binary Pass/Fail judge 的四要素
- 能用 TPR/TNR 校準 judge，並用 Rogan-Gladen 修正成功率
- 能 audit 一份 eval pipeline，依 impact 排出修正順序

## Constraints
- 完全新手；術語先一句話定義再用
- 邊做邊學；用虛構的「餐廳訂位助理」當玩具領域
- 無真實 traces 與 API；用離線合成資料與模擬 judge
- 一次一課，20–30 分鐘；每課一個可檢查產出
- 繁中講解；程式與既有英文文獻保持原文

## Out of scope
- 接 production 監控、CI gate、dashboard
- RAG 專項評測
- 特定 eval 框架或供應商的 API 操作（僅約束本課程；專案探索見 `.scratch/designer-evals/`）
- 統計理論推導（會用公式，但不證明）

## Status
- 2026-10-27：七課 + capstone 完成。
- Evidence：`lessons/0001`–`0007`、`audit.md`、`toy/tone_lite_metrics.md`（toy rehearsal）。
- 2026-10-29：課程維持完成狀態；真實專案 follow-up 已移到 `.scratch/designer-evals/`
  （designer coverage/traceability、semantic judge、Phoenix spike）。本課程仍只涵蓋 toy/離線。
