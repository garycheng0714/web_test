# 兩階段對稱：都在 CI、同一個 app 身分、run-scoped 分支

## Context

ADR-0006 把 Gate 改成「merge 新增 `test-case/<prd-stem>.md` 的 PR」，並讓 automation 由該 merge
觸發；但第一階段的 `plan` 仍被描述成「可在本地跑」，且只帶 `--base-url`。實作後兩階段開始漂移：

1. **身分不同**：automation 改用 GitHub App token，plan 若在本地跑則用個人身分，PR 的 CI 也會
   因身分而卡在 `action_required`。
2. **觸發不同**：automation 是 merge 觸發，plan 是手動執行；PRD 的變更沒有版本控管的觸發點。
3. **分支命名不同**：automation 固定 `automation/<id>`（重跑會撞），plan 用時間戳；同一條規則
   被寫了兩次。
4. **base URL 來源不同**：plan 從命令列參數拿，CI 沒有這個參數。

## Decision

- **兩階段都是 merge 觸發的 CI workflow**：新增 `prd/**` 的 PR 被 merge → `plan.yml`；新增
  `test-case/**` 的 PR 被 merge → `automate.yml`。兩者都只認**恰好一個新增**的檔案。
- **同一個 app 身分**：兩個 workflow 都以 `actions/create-github-app-token` mint
  `web-test-qa-flow` 的 installation token，供 checkout 與 `gh` 使用；workflow 自身權限降為
  `contents: read`，寫入全由 app token 執行。
- **分支命名共用一條規則**：`<kind>/<id>-<run_id>-<run_attempt>`；無 run 資訊（本地執行）時
  退回 UTC 時間戳。重跑不會在 push 時碰撞。
- **plan 的 base URL 來自 repository variable**：`WEB_TEST_BASE_URL`，未設定即明確失敗；不再有
  本地的 `--base-url` 作為 CI 路徑。
- **Gate 不變**：merge **test-case PR** 才是人工審核點。merge PRD PR 只是 plan 的觸發，不是
  Gate——它不核准任何測試案例。

## Considered Options

- **只有 automation 在 CI**：少一個 workflow、PRD 仍可本地產生；但身分、觸發、分支命名會繼續
  各走各的，且 plan 的產出沒有 PR 可審。
- **兩階段都在 CI（採納）**：對稱、可重跑、PRD 與 test-case 的變更都走 GitHub 原生流程；代價是
  多一個 workflow，且 workflow 改動要落在 `main` 才生效。

## Consequences

- **換得**：兩個階段的身分、觸發、分支命名與 CI 檢查一致；PRD 變更可追溯；PR 的 CI 真的執行
  （不再有 app 身分造成的 approval 停滯）；重跑安全。
- **代價**：plan 不能只靠本地命令列完成（需 push 與 `gh`）；PRD 的修改本身不會觸發 plan（只認
  **新增**），需要新的 PRD 檔名或另訂規則。
- **Supersede**：spec 的「`plan` may run locally」與「plan 的 CI 改寫尚未實作」、票 13 的
  「local first / no CI workflow for plan」。ADR-0006／0007 的 Gate 與 artifact 決策不變。
