# 產生的測試用 Python，而非 TypeScript

## Context

`playwright-cli` 的每個動作輸出的是 **TypeScript**，測試 repo 若用 TypeScript 可直接
重用這些程式碼；但建構者對 Python 較熟悉。

## Decision

產生的自動化測試用 **Python（pytest ＋ Playwright）**，接受 playwright-cli 吐出的
TypeScript 只當**參考素材**、需要時再翻譯成 Python。

## Consequences

- 換得：建構者的熟悉度與可維護性。
- 代價：多一層 TS→Python 的轉譯（多一個出錯點）；不需要 Node 工作區，改走 uv／pytest。
