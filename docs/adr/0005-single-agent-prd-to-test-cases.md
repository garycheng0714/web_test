# PRD → 測試案例：單一 agent＋qa skill

## Context

第一階段（設計）原本拆成「PRD 解析模組（`PRD{base_url, requirements}`）」→「Test Case
designer」兩個 agent，並有 base URL 欄位。後來評估過以 ralph skill 產出 `prd.json` 再轉測試案例。
但需求文件是 markdown/文字，測試案例設計本來就是一次性的推理工作。

## Decision

第一階段改成**單一 agent**：把 PRD 文字直接交給一個 Pydantic AI agent，載入
`qa-test-case-generation` skill（透過 harness `Skills`），輸出**結構化的 `QaReport`**，再由程式
render 成 qa 表格的 markdown 文件。

- 不再有獨立的 PRD 解析模組、`PRD` 模型與 `base_url` 欄位。
- `QaReport` 的每個測試案例帶 `requirement_ids`，保留對 PRD 需求 id 的追溯。
- 文件 front-matter 帶 `approval: draft|approved`，作為人工審核（Gate）狀態。

## Considered Options

- 兩段（解析 PRD → 設計）：seam 清楚，但多一個 agent／模型與一份中介產物。
- ralph `prd.json` 中介：適合自主建置迴圈，但與測試案例設計的目的不同（會重編號、塞入
  建置用 AC）。
- 單一 agent：活動部件最少、全域去重與覆蓋最自然。

## Consequences

- 換得：一個 seam（`design_test_cases`）、結構化輸出可測、全域去重；qa 詞彙保留。
- 代價：**移除 base_url**，之後自動化階段需另尋來源（例如 CLI 參數）；qa 的 `references/`
  在 harness `Skills` 下不會被載入，故需**裁切版 house `SKILL.md`（內嵌規則）**。
- ADR-0002（兩階段＋人工關卡）不變；本 ADR 只改第一階段的內部形狀。
