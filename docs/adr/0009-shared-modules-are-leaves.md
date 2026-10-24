# 共用模組是 leaf，依賴方向由 contract 強制

## Context

`web_test.planning.schema` 被 planning 與 automation 共用；`web_test.publishing` 被 plan 與
automate 共用。共用點只有在「不反過來依賴任何 use case」時才穩定。

這不是抽象風險：`web_test.planning.review.service` 已經 import `web_test.planning.schema`，
所以 schema 一旦 import review 就形成 cycle。即使沒有成環，schema 依賴 review 也會把 review 的
依賴（pydantic_ai、Jev client）帶進 automation 的測試與啟動路徑。ticket 12 只寫了兩條
contract，其餘方向仍靠慣例。

## Decision

- 共用模組是 leaf：`web_test.planning.schema` 與 `web_test.publishing` 不得 import
  `web_test.planning`、`web_test.automation` 或其他 use case。
- 依賴箭頭一律從 entrypoint/use case 指向共用模組，不反向。
- 以 `uv run lint-imports` 的 forbidden contracts 強制（ticket 19）。
- 要放寬任何 contract，先更新本 ADR 並說明新的依賴方向；不要用 `ignore_imports` 靜默繞過。

## Considered Options

- 只靠慣例與 code review：成本最低，但依賴會慢慢腐化，cycle 與依賴膨脹在幾週後才浮現。
- 允許方便的 import，等成環再拆：短期快，長期要解開已擴散的依賴。
- leaf + contract：多幾行 TOML，換得 PR 當下就擋下錯誤方向。

## Consequences

- 換得：不會有 import cycle / order-dependent failure；automation 不會間接依賴 review；
  schema 與 publishing 可被單獨 import、測試與重用；改動漣漪被限制在單一 stage。
- 代價：新增 contract 可能擋下「其實很方便」的 import；架構變更要同步改 ADR/contract。
  `web_test.planning.**` 會自動涵蓋新子模組，因此不需要手動維護清單。
