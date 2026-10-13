# 以 PR merge 為 Gate，測試案例一 case 一檔

## Context

ADR-0002 定「兩階段（設計／自動化）＋人工關卡」，關卡以 Test Case 文件的 front-matter
`approval`（`draft` → `approved`）表示；ADR-0005 定第一階段輸出單一 qa 表格文件，並移除 `base_url`。
實際運作後想把「人工審核」改用 GitHub 原生的 PR review，並讓每個測試案例可獨立追溯與觸發。

## Decision

- **artifact 改為一 case 一檔**：`test-case/test-case-<id>.md`。機器可讀欄位放在 **YAML front-matter**：
  必填 `id`、`base_url`；選填 `requirement_ids`、`priority`、`test_type`。
- **Gate ＝ PR merge**：`plan` agent 開 PR 新增該檔，人工 review 後 merge 即代表核准。不再有
  front-matter `approval` 狀態，執行期也不自查「是否核准」。
- **自動化由 merge 觸發**：`.github/workflows/automate.yml` 於 `pull_request: [closed]` 且
  `merged == true`、且變更 `test-case/**` 時執行；取出本次**新增**的檔（恰好一個，多於一個即失敗），
  交給 coding agent 實作，綠燈才由 publisher 開 PR。編輯既有檔不觸發。
- **PR CI**：`.github/workflows/ci.yml` 於每個 PR 跑 pytest，作為 agent 測試 PR 的檢查。

## Considered Options

- 維持 front-matter `approval` 狀態（原 ADR-0002）：關卡在檔案內、執行期可自查；但要靠本地流程與
  自律，CI 無法原生把關。
- 以 PR merge 為關卡：用 GitHub 的 review／merge 與 branch protection；代價是執行期不能再自查。

## Consequences

- 換得：審核走 GitHub 原生流程；一 case 一檔、可獨立追溯與觸發；CI 可在 PR 上把關。
- 代價：`is_approved`／`ApprovedDocumentError` 與 qa 大表退役；`base_url` 回到 artifact；
  觸發的邊界（多檔／編輯／重跑）需要規則；`plan` → per-case PR 的改寫尚未完成，其輸出必須遵守
  同一份 front-matter schema。
- 本 ADR **supersede ADR-0002**（關卡媒介）與 **ADR-0005**（artifact 形狀）。
