# 產品不得依賴 eval harness

## Context

`evals/designer` 是 dev-only 的評測 harness：它 import `web_test`（PRD 解析、schema、paths），
並且依賴 Phoenix client 與 judge 模型。反方向若成立，`web_test` 會把 eval 的依賴帶進
production 的啟動與測試路徑。

原本的 `.importlinter` 只把 `web_test` 當 root，`evals` 不在圖裡，所以這條方向沒有任何檢查。

```text
evals/designer  ──>  web_test  ──>  (never back to evals)
```

## Decision

- `web_test` 不得 import `evals`。
- `evals.designer.designer_eval` 不得 import `evals.designer` 底下的 CLI 腳本；腳本 import
  套件，套件不回頭 import 腳本。
- 為此 lint-imports 的 root 改為 `root_packages = ["web_test", "evals"]`。
- 要放寬這兩條，先更新本 ADR；不要用 `ignore_imports` 靜默繞過。

## Considered Options

- 只靠慣例：成本最低，但錯誤的 import 只會在依賴清單或 runtime 才浮現。
- `include_external_packages = true`：能檢查 `web_test -> evals`，但會把外部套件一起拉進圖
  （80 檔／266 依賴），且無法以 `evals` 為 source 寫 contract。
- `root_packages` 多一個 root：70 檔／180 依賴，兩個方向都能寫。

## Consequences

- 換得：產品與評測的依賴方向在 PR 當下被擋下；eval 可以放心 import 產品的 schema 與 parser。
- 代價：`evals` 成為 lint-imports 的 root，未來 evals 內部若成環或命名衝突，分析輸出會變多
  （毫秒級）。eval 套件內部的層次（哪個模組可以 import 哪個）仍靠慣例，不寫成 contract。
