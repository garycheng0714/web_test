# 案例生成要「收斂」——覆蓋率不是越多越好，未定義行為是 open question

拿一份 6 條需求的 PRD（Register / Login）餵 designer，第一版產出 **26 個案例**。逐一盤點後
發現三個病：

1. **臆測當案例**——約半數案例來自 PRD **未定義**的行為（驗證訊息、大小寫、session 持續、
   權限轉址、刪除確認…），卻寫成有明確 expected result 的案例。這種對真系統幾乎必紅。
2. **去重不足**——端到端重跑、訊息總表、header/角色檢查，只是**重述**其他案例。
3. **把 grounding 觀察當案例**——下拉選項範圍、預設值、disabled 欄位等，是「**供自動化定位**」的
   觀察，不是需求。

收斂成三條政策，寫進 skill：**每需求一個 happy，至多一個 negative/validation；boundary 只在
PRD 明述限制、且 happy path 未涵蓋時才加；PRD 未定義的行為升級成 `open_questions`（cases 之外的
一等公民），永不當成案例。** 設計 agent 的輸出因此改為 `DesignOutput(cases, open_questions)`，
文件尾部渲染一段 `## Open Questions`。

結果：**26 → 12 → 7 個案例**（＋ 11 個 open questions），檔案 **683 → 202 行**；最終每條 FR
對得上一個可追溯的案例，自動化階段的紅燈面大幅縮小。

## Evidence

- 產物：`test-case/test-case-register-login.md`（一 PRD 一檔；7 例＋11 open questions）。
- 政策：`.agents/libraries/test_case_designer/qa-test-case-generation/SKILL.md` 的
  Coverage / Boundary / Deduplication / Output 四段。
- 型別與渲染：`web_test/planning/schema.py` 的 `DesignOutput`；
  `web_test/planning/cases_writer.py` 的 `render_document(..., open_questions)` 與 `## Open Questions`。
- 迭代數字：26（+14 open）→ 12（+14）→ 7（+11）。

## Implications

- **覆蓋率 ≠ 案例數**：案例必須 grounded；把「猜的 expected result」寫成案例，只會在自動化階段紅。
- **「未定義」要有出口**：沒有 `open_questions` 這種一等公民，模型就會用臆測把缺口填滿。
- **grounding 觀察 ≠ 需求**：happy path 已成功用過的控件（選項集合、預設、disabled）不需再細測。
- **診斷法**：把候選案例逐一分類成 stated／inferred／overlap → 三個病一目了然。

## 面試 STAR

**S — Situation**
我做一個「PRD → 測試案例」的 agent，用一份 6 條需求的 PRD 當起點；第一版產出 26 個案例，但品質沒保障。

**T — Task**
讓產出的案例**可信、可自動化**：不能混入「猜出來的行為」，否則自動化階段會整批紅（一 PRD 一檔、一次實作、全有全無）。

**A — Action**
把 26 例逐一分類 → 約 9 條有 PRD 依據、13 條屬 PRD 未定義的推論、4 條與其他案例重疊。據此定三條生成政策並寫進 skill：① 每需求 happy ＋至多一 negative/validation，boundary 只在 PRD 明述且 happy path 未涵蓋；② PRD 未定義的行為升級成**一等公民 `open_questions`**，不當案例；③ 禁止把 grounding 觀察（選項範圍、預設、disabled）當案例。並把 designer 輸出改成 `DesignOutput(cases, open_questions)`。

**R — Result**
26 → 12 → 7 個案例（＋11 open questions），檔案 683 → 202 行；每條 FR 對應一個可追溯案例，自動化紅燈面大幅縮小。可複用原則：覆蓋率 ≠ 案例數；「未定義」要有出口；grounding ≠ 需求。

**可能被追問**
- *為什麼敢刪那些案例？* → 它們沒有 PRD 依據、expected result 是猜的，對真系統必紅，留著只會拖垮整批。
- *怎麼知道收斂夠了？* → 每條 FR 都有一個 grounded 的 happy 案例（＋明列的 negative），缺口改用 open questions 明示，而非用臆測填空。
