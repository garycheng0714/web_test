# grilling 把產品從「自動化管線」翻轉成「蘇格拉底式教練」

使用者第一次自己主導 grilling，逐步推翻了先前由 agent 主導寫成的 spec。原本方向是
「agent 產生測試項目、再把測試項目轉成自動化測試」；經數輪拷問後收斂成：**人做全部
有技能的思考與實作，agent 在事後以蘇格拉底式提問協助，v1 不產出任何交付檔案**。

關鍵轉折是使用者自己提出的擔憂——「怕工程師變成 agent 的監控者、技能會退化」——
這是 agent 版 spec 完全沒有的一條。它也意外呼應了自動化去技能化的實證文獻
（Bainbridge 1983、HICSS 2018、AI Magazine 2026）。

影響後續 session：
- 讓使用者先寫計畫、agent 只 grill、**不要再用「➡️ 建議」主導**。
- 產品範圍已與 `.scratch/prd-to-tests/spec.md`（agent 主導版）嚴重脫節，該 spec 需重寫。
- 未決：技能的直接觀察指標（Q18 待補）、review 對象與介面（Q24/Q21 剛定）、
  以及「獨立 CLI」vs「用 OpenCode 本身當教練」的分岔。
