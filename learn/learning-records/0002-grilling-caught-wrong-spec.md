# grilling 抓出了錯誤的 spec 前提

使用者對已發佈的 spec 執行 grilling 後，主動指出前提有誤：原 spec 只涵蓋「自然語言任務
→ 單一 Playwright 測試」，真正的意圖是「讀 PRD → 以 QA 職能產出測試項目 → 轉成自動化
測試」的三段式管線。這是主流程「先 grill 再 to-spec」順序的活生生證明——我們當時跳過了
grill，直接把窄化的理解寫成了 spec。

影響後續 session：之後每個功能都應在 to-spec 前先 grill（或至少在下票前確認前提），
不要等到 to-tickets 才發現方向錯。本 repo 的 `prd-to-tests` spec 已為此重寫。
