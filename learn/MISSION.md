# Mission: 用 Matt Pocock 工程流程開發一個功能

## Why
你是這套流程的完全新手。你要用它從頭到尾做出一個真實功能——經你自己主導的 grilling
收斂後，目前方向是「以蘇格拉底式提問，協助熟練測試工程師從 PRD 設計測試項目」的教練
（確切範圍由你的 `learn/plans/0001-prd-to-tests.md` 定義）——藉此把流程的每一步變成
肌肉記憶，而不是只讀文件。

## Success looks like
- 自己主導一次規劃：用 grilling 把一個模糊想法收斂成可寫的計畫
- 不看筆記能畫出 idea → ship 主流程，並說出每個階段該用哪個 skill
- 用 `setup-matt-pocock-skills` 正確配置本 repo（local markdown tracker、`docs/agents/*`、AGENTS.md 區塊）
- 用 `to-spec` 產出 spec、用 `to-tickets` 拆出帶 blocking edges 的票
- 至少獨立完成一張票的 `implement`（tdd 紅→綠）並 commit
- 能分辨何時走哪條 on-ramp（`triage` / `diagnosing-bugs` / `wayfinder`）

## Constraints
- 完全新手：術語先定義再用，第一課只教一件事
- 一次只跑一個真實功能；用本 repo 的 local markdown tracker
- 學習與實作交錯（邊做邊學），不先上一堆理論

## Out of scope
- 精通 `grilling` 訪談技巧
- 撰寫新 skill / `writing-for-agents` 的深水區
- `wayfinder`、`improve-codebase-architecture` 等高階流程（先知道存在即可）
