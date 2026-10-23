# 人工裁決流程：approve 之後 check 怎麼變綠

日期：2026-10-23
狀態：設計說明，尚未實作。對應票 [`24b`](../../.scratch/prd-to-tests/issues/24b-adjudication-and-required-check.md)；
契約見 [`19`](../../.scratch/prd-to-tests/issues/19-define-test-case-verification-contract.md)。

這份筆記只回答一件事：**有人在 Test Case PR 按下 approving review 之後，`verify-test-case`
這個 check 要怎麼從紅變綠，而且不會把不該放行的東西放行。**

不是整個 verification 流程，也不是 branch protection 的設定（那是 24b-2）。

## 先定義四個詞

- **head SHA**：PR 目前最新 commit 的識別碼，例如 `H1`。
- **`review.commit_id`**：這則 review 是按在哪一個 commit 上。它不一定等於最新的 head。
- **verdict**：Jev 對這份 Test Case 的判定：`PASS` / `NEEDS_REVIEW` / `FAIL` / `BLOCKED`。
- **override**：人工裁決，把 `NEEDS_REVIEW` 或 `BLOCKED` 改成「可合併」，但保留原本的
  verdict、理由，以及它套用的 head SHA。

## 用一個例子走一次

```text
PR head = H1
  │
  ▼
verify publishes NEEDS_REVIEW (p=0.75)
  │
  ▼
human submits an approving review with a reason
  │
  ▼
GitHub emits pull_request_review:
  review.state     = approved
  review.body      = reason
  review.commit_id = H1
  PR head SHA      = H1
```

工作流收到事件後：

```text
review.state == approved and reason is not empty?
  ├─ no  ──> ignore this review
  └─ yes ──> review.commit_id == PR head SHA?
                ├─ no  ──> ignore; the current head keeps its verdict
                └─ yes ──> original verdict?
                             ├─ PASS or FAIL ──> publish the original verdict
                             └─ NEEDS_REVIEW or BLOCKED
                                    │
                                    ▼
                              publish success
                              summary records:
                                original verdict, reason, head SHA
```

## 三個容易卡住的點

### 1. 為什麼要比 `review.commit_id` 和 head SHA？

因為核准是針對「某一個版本的程式」。如果人類在 `H1` 核准後又 push 了 `H2`，這則 review
仍然掛在 `H1` 上；`H2` 必須重新產生 verdict，不能繼承 `H1` 的核准。這就是
「a new head voids the override」。

```text
H1: NEEDS_REVIEW ──> approve(reason) ──> H1 becomes success
  │
  └── push H2
        │
        ▼
      the approval still points at H1
      H2 commit_id mismatch ──> approval does not apply
      H2 runs verify again and gets its own verdict
```

`H1` 上的 success check 仍然存在，但它不是 `H2` 的 required check。Branch protection 只看
目前 head 上的 `verify-test-case`。

### 2. 為什麼要 restore cached verdict，不是直接重跑 Jev？

因為 Jev 是機率模型。同一個內容重跑，可能從 `NEEDS_REVIEW` 漂成 `FAIL`；人類看到的是
`p=0.75` 才決定核准，重跑卻可能變成 `p=0.4`，系統就會拒絕一個本來合理的核准。還原 cache
裡「人類當時看到的那個 verdict」比較一致。

`BLOCKED` 是例外：[`24a-6`](../../.scratch/prd-to-tests/issues/24a-6-verdict-cache.md) 的設計
本來就不把 `BLOCKED` 寫進 cache，所以沒有東西可還原，只能重跑 Jev。重跑後：

- 還是 `BLOCKED` 或變成 `NEEDS_REVIEW`：套用人工核准。
- 變成 `FAIL`：不覆寫，照 `FAIL` 發佈。
- 變成 `PASS`：本來就是 success，不需要 override。

這也是為什麼「原 verdict 從哪裡來」是一個需要明確定下來的設計點；目前 cache 只存
`CheckPayload`，verdict 只出現在 title/summary 字串裡，沒有結構化欄位。

### 3. 為什麼 `FAIL` 不能覆寫？

`FAIL` 代表問題大到需要改 Test Case 或問題集，不是「人工覺得可以就好」。24b 的合約只讓
`NEEDS_REVIEW`（分數在灰色地帶）和 `BLOCKED`（系統無法判斷）走人工裁決。`FAIL` 只能靠
admin break-glass；那是 24b-2 的文件政策，不是這個流程的一部分。

## 實作前的程式缺口

以 2026-10-23 的 `main`（`9e55fc4`）為準：

- `.github/workflows/verify.yml` 只聽 `pull_request` 的 `opened` / `synchronize` /
  `reopened`，沒有 `pull_request_review`。
- `web_test/planning/verify/run.py` 的 `run()` 沒有 approval 輸入。
- `CheckPayload` 只有 title 與 summary；verdict 沒有結構化欄位。
- `web_test/planning/review/verification.py` 已有 `Override(original, reason, head_sha)`，
  但沒有任何地方填入它。
- `publish_check()` 已經用 `PATCH` 更新同一個 head SHA 上同名的 check run，所以重跑會更新
  同一個結果，不會新增第二個 check。

## 實作後（2026-10-23）

- `Approval` 是 `input.py` 的 Pydantic 邊界模型；只有 `state == approved`、reason 非空、且
  `head_sha` 等於本次 head 時才套用。
- 原 verdict 用 `cache.py` 的 `CachedVerdict(status, payload)`；cache 永遠存原始 verdict，
  adjudicated success 不進 cache。
- `run(..., approval=...)` 只在 `NEEDS_REVIEW` / `BLOCKED` 時把 payload 改成 success；`FAIL`
  保留 failure，並在 summary 記下 approval ignored。
- Workflow 拆成三個檔：`verify.yml` 是 `pull_request` caller，`adjudicate.yml` 是
  `pull_request_review` caller 並負責 approval 政策，`verify-shared.yml` 是可重用的
  `workflow_call` 執行路徑。兩個 caller 共用同一個 App token、check 名稱與 cache key；
  `adjudicate.yml` 只接受 `OWNER` / `MEMBER` / `COLLABORATOR` 的 approving review。
- `pull_request_review` 的 `GITHUB_REF` 也是 `refs/pull/<n>/merge`，與 `pull_request` 相同，
  所以 shared workflow 可以 restore `pull_request` run 寫入的 cache，不會因為 event 不同而 miss。
- Workflow cache key 加上 `v2` 前綴，避免舊格式 cache 被永久 restore 卻又無法載入。
- 驗證：`215 passed, 1 skipped`；basedpyright、lint-imports、ruff F401、actionlint 都綠。
- `24b-1` 已實作；`24b-2` 的 branch protection 與 live PR 仍待人工完成。

## 與 24b-2 的界線

- **24b-1**：上面的裁決行為、workflow 觸發、override 記錄、測試。
- **24b-2**：把 `verify-test-case` 設成 branch protection 的 required check；shadow → required
  的 rollout、break-glass 政策、live Test Case PR。這需要 repo admin，不能由 agent 獨立完成。

## 已定案（2026-10-23）

- **原 verdict 的來源**：同一個 cache key 的既有 verdict。cache 從只存 `CheckPayload` 改成
  `CachedVerdict(status, payload)`；cache miss（包括不進 cache 的 `BLOCKED`）才重跑 Jev。
- **override 的位置**：只放在 check summary，不發 PR comment，因此沒有 comment dedupe。
- **票的形狀**：`24b` 改成 umbrella，拆成 `24b-1`（裁決程式）與 `24b-2`（required check，
  需要 repo admin）。
- **live 驗證的 artifact**：`test-case/test-case-register-login.md` 留在工作區，給 `24b-2`
  的 live PR 使用。
- **reviewer 權限**：只接受 `OWNER` / `MEMBER` / `COLLABORATOR` 的 approving review。GitHub
  本身已限制 approving 權限，這是防禦性檢查。
- **不在 v1**：重跑原本的 `pull_request` workflow（不是新的 review 事件）不會重新讀取既有
  核准；契約只描述「review 觸發一次重跑」。

## 相關檔案

- 契約：[`19-define-test-case-verification-contract.md`](../../.scratch/prd-to-tests/issues/19-define-test-case-verification-contract.md)
- Shadow check：[`24a-shadow-verification-check.md`](../../.scratch/prd-to-tests/issues/24a-shadow-verification-check.md)
- Verdict cache：[`24a-6-verdict-cache.md`](../../.scratch/prd-to-tests/issues/24a-6-verdict-cache.md)
- 裁決與 required check（umbrella）：[`24b-adjudication-and-required-check.md`](../../.scratch/prd-to-tests/issues/24b-adjudication-and-required-check.md)
- 裁決程式：[`24b-1-adjudication.md`](../../.scratch/prd-to-tests/issues/24b-1-adjudication.md)
- Required check：[`24b-2-required-check.md`](../../.scratch/prd-to-tests/issues/24b-2-required-check.md)
- 程式：`web_test/planning/verify/`、`web_test/planning/review/verification.py`、`web_test/publishing/github.py`
- Workflows：`.github/workflows/verify.yml`、`.github/workflows/adjudicate.yml`、`.github/workflows/verify-shared.yml`
