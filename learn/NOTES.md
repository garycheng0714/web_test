# NOTES

## 學習偏好
- 語言：繁體中文
- 完全新手；偏好先用一句話定義術語，再放進流程
- 邊做邊學：課程要能立刻套用到「Agent 閱讀 PRD 產生測試案例然後建立自動化測試」這個真實功能
- 喜歡 leading-word 寫法（一個詞承載一組行為），不喜歡長串說明
- 不排斥被連續提問（grill）來收斂想法

## 教學模式：使用者寫、agent grill（重要）
使用者要親自練習「計劃專案」，所以：
- **使用者負責寫計畫**（PRD / spec 草稿）與做決定，agent 不寫使用者的計畫。
- agent 只提問、挑戰、補事實；**只有出現具體 tradeoff/risk 時才主動給建議**，並標明是建議、附一行理由。
- 沒有具體取捨時，只提問，不出現 `➡️ 建議`。
- 你明確要求建議時，agent 可以回答，但要標明這是回答，並說明是否基於具體 tradeoff/risk。
- 「具體 tradeoff/risk」例如：資料遺失、安全、相容性、成本/效能、不可逆遷移、兩個設計有不同失敗模式；單純風格偏好不算。
- `grilling` 的 `➡️` 只在形成建議時出現；不需要每題都有。
- 決策留給使用者；目的仍是把 planning 的主導權留在使用者身上。

## 工作筆記
- 本工作區是 `teach` skill 的 stateful 教學工作區，根目錄 `learn/`，納入版控。
- 對應的實作 repo 是上層的 `web_test`（Python/uv + playwright-cli + Pydantic AI）。
- `GLOSSARY.md` 依規範 lazy 建立：等你「能正確使用」某術語才收錄，不是先寫字典。
- `learning-records/` 也 lazy：只在出現非顯而易見的洞見、先備知識或觀念修正時才寫。
- Lesson 0003 起加入 Pydantic AI Harness 線（課 + `reference/harness-capabilities.html`）。
  教學以 harness **0.54.0**（`uv.lock` 鎖定）為準；harness 是 0.x，minor 版之間 API 可能
  改名／改預設，升級後要重讀對應 capability 的 README。新增可重用元件：
  `assets/style.css` 的 `details.reveal`（步驟揭曉）。
- 2026-10-19：研究 pstack `0.15.28`，筆記在 `reference/pstack.md`。目前學習焦點是
  **產出可信度**；優先序、本地證據與待答問題見
  `learning-records/0009-pstack-learning-priorities.md`。

## 已知缺失 (gaps)
- `ask-matt` SKILL.md 內引用的 smart zone 連結
  `https://www.aihero.dev/ai-coding-dictionary/smart-zone` 目前回 404。
  已改用字典首頁與 GitHub 版（見 `RESOURCES.md`）。
