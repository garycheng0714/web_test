# 自建 agent harness，不委派給 coding agent

## Context

這個 agent 要在測試 repo 上讀檔、寫測試程式、跑測試——本質是一個窄化的 coding agent。
另一條路是讓它當「大腦」，把改 code 委派給現成的 coding agent（透過 CLI 或 MCP）。

## Decision

自建 harness：用 Pydantic AI 自己提供檔案工具（read／write／glob／grep／run）與瀏覽器
工具，並以 write guard 限制寫入。

## Considered Options

- 委派給 coding agent（OpenCode／Claude Code）：省 harness，但要設計跨 agent 介面與權限。
- MCP 拼裝現成 server：快，但彈性受限。

## Consequences

- 換得：完整控制、可單元測試的 seam、可產品化成 CLI，以及「學會建 agent」這個專案目的。
- 代價：要自己處理工具、context 檢索、錯誤處理與安全，不能直接借用成熟 harness。
