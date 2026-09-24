# NOTES

## 學習偏好
- 語言：繁體中文
- 完全新手；偏好先用一句話定義術語，再放進流程
- 邊做邊學：課程要能立刻套用到「Agent 閱讀 PRD 產生測試案例然後建立自動化測試」這個真實功能
- 喜歡 leading-word 寫法（一個詞承載一組行為），不喜歡長串說明
- 不排斥被連續提問（grill）來收斂想法

## 教學模式：使用者寫、agent grill（重要）
使用者要親自練習「計劃專案」，所以：
- **使用者負責寫計畫**（PRD / spec 草稿），agent 只提問與挑漏洞。
- agent **不主動給建議答案**：連 `grilling` 的 `➡️ 建議` 也省略，除非使用者明確要求。
- agent 可以補**事實**（查檔案、看程式），但**決策留給使用者**。
- 目的：把 planning 的主導權留在使用者身上，避免 agent 主導整個設計。

## 工作筆記
- 本工作區是 `teach` skill 的 stateful 教學工作區，根目錄 `learn/`，納入版控。
- 對應的實作 repo 是上層的 `web_test`（Python/uv + playwright-cli + Pydantic AI）。
- `GLOSSARY.md` 依規範 lazy 建立：等你「能正確使用」某術語才收錄，不是先寫字典。
- `learning-records/` 也 lazy：只在出現非顯而易見的洞見、先備知識或觀念修正時才寫。

## 已知缺失 (gaps)
- `ask-matt` SKILL.md 內引用的 smart zone 連結
  `https://www.aihero.dev/ai-coding-dictionary/smart-zone` 目前回 404。
  已改用字典首頁與 GitHub 版（見 `RESOURCES.md`）。
