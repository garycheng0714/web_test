# 一 PRD 一檔（artifact 形狀）

## Context

ADR-0006 定「**一 case 一檔**」`test-case/test-case-<id>.md`，讓每個測試案例可獨立追溯與觸發。
實作後發現兩個問題：

1. **數量暴增**：單一 PRD 會被 designer 展開成大量案例（6 個 FR 可達 ~30 筆），導致檔案、PR 與
   自動化 run 的數量一起放大。
2. **page object 重複**：每個 case 各跑一次獨立的自動化 run（各自 checkout main），共享同一頁的
   case 會各自建立/修改 page object，跨 PR 重複甚至衝突。

另有一個資料問題：**「module」不是一等公民**——`module_feature` 是自由文字（模型每次寫法不同），
只有 requirement id 的前綴（`FR-<MODULE>-`）隱含 module。而目前的 PRD 又都是單模組。

## Decision

- artifact 改為 **一 PRD 一檔**：`test-case/test-case-<prd-stem>.md`（例：`test-case/test-case-register-login.md`）。
- **front-matter**：`id`（＝prd stem）、`base_url`。per-case 的機器可讀欄位不再放頂層。
- **body**：PRD 層級標題（由 prd stem 美化，`register-login` → `Register Login`）＋每個 case 一個
  區段；每個區段帶一小塊 ```yaml（`requirement_ids`/`priority`/`test_type`）＋人可讀的
  Preconditions/Test Steps/Notes，兼顧人工審閱（Gate）與工具解析。
- **同名再 plan 覆寫** `test-case/test-case-<prd-stem>.md`。
- `CaseFile.from_path` 的驗證**不變**（`test-case/test-case-<prd-stem>.md` 仍符合原本的
  `test-case-*` 檢查）。

## Considered Options

- **一 case 一檔**（原 ADR-0006）：追溯最細、blast radius 最小；代價是檔/PR/run 數暴增與 page
  object 重複。
- **一 module 一檔**：折衷；但要先定義 module（目前無受控詞彙），且跨模組案例（端到端/權限/
  持久性）歸屬難定。
- **一 PRD 一檔**：最單純、免定義 module；代價是單次範圍較大。

## Consequences

- **換得**：檔案、PR、自動化 run 數大幅下降；同一次 run 內可重用同一組 page object；branch 碰撞
  機會降低。
- **代價**：單次自動化範圍變大；紅燈影響整檔（all-or-nothing）。
- **未決（後續票）**：①自動化單位（整檔一次實作 vs 檔內逐 case 選擇）；②紅燈政策（全有全無 vs
  允許部分＋fixme）；③**複寫與 merge 觸發偵測的衝突**——`automate.yml` 以
  `git diff --diff-filter=A`（僅新增）找檔，ADR-0006 也定「編輯既有檔不觸發」；同名複寫對既有檔是
  **modified**，不會觸發，需另行決定。
- 本 ADR **取代 ADR-0006 的 artifact 段**；ADR-0006 的其餘決策（PR merge 為 Gate、審核走 GitHub
  review/merge、一 PR 一 merge 觸發）不變。
