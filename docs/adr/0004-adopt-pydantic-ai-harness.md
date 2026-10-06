# 以 Pydantic AI Harness 為骨、允許委派

## Context

ADR-0001 決定「自建 agent harness，不委派給 coding agent」，用自製檔案／瀏覽器工具與 write
guard 限制寫入。但 Pydantic AI 官方推出了 `pydantic-ai-harness`：一套可組合的 capability
函式庫（`Skills`、`FileSystem`、`Shell`、`Planning`、`Memory`、`Subagents`、`PlaywrightBrowser`
…），在 Pydantic AI 上提供檔案、命令、瀏覽、記憶、委派、context 管理與 durable execution。

## Decision

改以 **Pydantic AI Harness 的 capability 為骨架**，並**允許委派**（不再自限「不委派」）。需要
檔案、命令、瀏覽、記憶、多代理等能力時，優先採用 harness 既有的 capability，而不是自製。

## Considered Options

- 維持 ADR-0001 自建：控制最大，但要重造輪子（檔案守門、context 管理、記憶、委派）。
- 採用 harness：站在官方維護的 capability 上，迭代快、觀測性佳；代價是 0.x alpha 與版本綁定。

## Consequences

- 換得：少寫基礎設施；`Skills` 讓 agent 能直接吃 `.agents/skills/` 的 `SKILL.md`；`FileSystem`
  的 containment／pattern 與 `Shell` 的 allow/deny 取代多數自製守門；OTel/Logfire 一體。
- 代價：harness 為 **0.x alpha**，minor 之間 API 可能破壞性變更；會**硬綁 pydantic-ai 版本**
  （例如 harness 0.54.0 需要 `pydantic-ai-slim==2.54.0`）。
- 本 ADR **supersede ADR-0001**。write guard 等自製設計改為 harness 提供（或在其上加一層）。
