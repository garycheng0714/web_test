# pstack 的學習優先序：先處理產出可信度

日期：2026-10-19  
背景：讀完 pstack `0.15.28` 後，對照本 repo 現況，判斷哪些部分現在值得學。  
完整研究見 [`learn/reference/pstack.md`](../reference/pstack.md)。

## 目前專案在哪裡

- 兩階段管線已完成：PRD merge 觸發 plan，test-case PR merge 觸發 automate；兩邊都在 CI、同一個 GitHub App 身分、run-scoped 分支（`docs/adr/0008`）。
- 人工 Gate 是刻意設計：test-case PR 被 merge 才算審核通過（`CONTEXT.md:51-54`）。
- 下一個已知工作是 G2：把 account fixtures 預先建好，讓 agent 消費而不是每次重造（`.scratch/agent-in-ci/optimization-runs.md:185`）。
- 目前 automation 的成功判準：agent 回傳 `pr_body`、外部跑全套 pytest 綠、變更路徑在白名單內（`web_test/automation/entrypoint.py:51-54`）。

## 與當前缺口重疊度最高的五個部分

### 1. 驗證要獨立於生產者

pstack 的 `shipping` 要求每個 PR 由沒寫該程式碼的代理獨立驗證；作者自己的綠燈不算 verdict。

本地缺口：

- 外部只驗證 pytest 退出碼。把成功斷言註解掉，測試仍可能綠。`.scratch/agent-in-ci/model-runs.md:29` 記錄過 agent「commented out the success assertion (gamed green)」。
- `pr_body` 由 agent 自己寫，`entrypoint` 只檢查它不是 `None`，沒有檢查裡面的證據。
- 設計階段有 Jev 的 advisory review（`web_test/planning/entrypoint.py:67`），automation 階段沒有對應的獨立審查。

### 2. 重複的教訓要變成結構

pstack 的 `encode-lessons-in-structure`：同一句話講第二次，就改成 lint、check、hook、fixture 或 script。

本地缺口：

- `page-object-model` 已累積到 rule 19（`.agents/libraries/coding_agent/page-object-model/SKILL.md:76`），前面還有 rule 14 到 18。
- `.scratch/known-issues.md` 的 SUT traps 也是 prose。
- 每次新失敗就再加一條規則，skill 會越來越長，而且靠模型記得。

### 3. 連續失敗時先質問前提

pstack 的 `attack-the-premise`：兩個以上修正共享同一前提且都失敗時，把前提寫下來，直接測試前提。

本地證據：

- `model-runs.md` 的 instructions 從 v0 走到 v6，主要手段是「再加一條規則」。
- 同一份文件也說 v1 到 v5 不是 apples-to-apples，因為規則一直在變（`.scratch/agent-in-ci/model-runs.md:5` 附近）。
- `optimization-runs.md:268` 明白寫出 one run per variant、SUT 會 flake。

### 4. 測行為，不測實作；每個可驗證單位都要收斂

pstack 的 `test-behavior-not-implementation` 與 `sequence-verifiable-units`。

本地缺口：

- Rule 19 要求照 case 的步驟走，但目前只是 prose。
- `model-runs.md` 記錄過 agent 直接開 `/contact_us`，跳過 Home → Contact Us。
- `repair_guard` 只數 pytest 執行次數（`web_test/automation/repair_guard.py:27-33`），不判斷這次修正是讓測試更真，還是讓測試更弱。

### 5. 數字要能被解釋，實驗要能被重跑

pstack 的 `explain-the-number`、`benchmark-checklist`、`eval`。

本地缺口：

- `optimization-runs.md` 的資料有價值，但作者自己標明 one run per variant、directional、不是統計穩健。
- 不同 variant 之間 instructions 也在變，成本與品質的比較有 confound。
- `baseline.py` 只存在文件裡，不是 repo 內可重跑的工具。

## 下一個規模才需要

- **Context 隔離與子代理**：目前 `Coder(sub_agents=False, repo_context=False)`（`web_test/automation/coding_agent.py:106`）。但成本主要是 request 數與 repair 迴圈，不是 token 體積；現在加子代理可能先增加協調成本。
- **共享狀態只能有一個寫者**：`write_guard` 允許 `tests/conftest.py`（`tests/test_write_guard.py:16`），agent 會改 shared fixtures。一次跑一個 case 還好；同時跑多個 case 時，`conftest.py` 與 `pages/` 會碰撞。
- **Verification skill / feature map**：`known-issues.md`、page objects、`PlaywrightBrowser` 已是雛形；變成專案內可重跑的 verify skill 會讓每次 run 用同一種方式驅動 SUT。
- **形式化驗證**：`write_guard` 已是 pure function 且有單元測試；`repair_guard` 很簡單。比較值得的是 publishing 的冪等性、branch naming、CI 狀態轉移。
- **`architect` / `arena` / `interrogate`**：適合 G2 這種設計分岔，但依教學模式應由使用者先寫選項，工具用來挑戰或比較，不替使用者決策。

## 目前不值得投入

- `orchestrate`、`autopilot-full`、`autopilot-stack`、`shipping`、`babysit`：fleet-scale 的機械；現在是一條管線、一次一個 case，ceremony 遠大於收益。
- `setup-pstack` 的多模型面板：已有 designer 與 coding 兩個角色，面板式 review 還沒有明確瓶頸。
- `unslop`、`comment-sicko`：文件與註解已相當克制，邊際收益低。
- `never-block-on-the-human`：和 deliberate Gate 直接衝突（`CONTEXT.md:51-54`、`learn/NOTES.md:12-14`）。
- `laziness-protocol`：已有 `ponytail`，概念重疊。

## 本 repo 已經比 pstack 強的地方

- **`open_questions` 是一等公民**：learning record 0008 把 PRD 未定義的行為升級成 `open_questions`，不讓模型用臆測填滿。
- **人工 Gate**：這是領域決定；pstack 的預設會把很多決策自動化掉。
- **兩階段對稱的 CI 與 app 身分**：比 pstack 的抽象 playbook 更具體，也更適合這個 repo。

## 目前選定的焦點

**產出可信度（output trustworthiness）優先。**

理由不是「pstack 說要這樣」，而是本地證據顯示：

1. 綠燈的定義只到 pytest 退出碼。
2. agent 曾經用弱化斷言的方式讓測試變綠。
3. PR body 由 agent 自寫，沒有獨立證據檢查。
4. 設計階段有獨立 review，automation 階段沒有。
5. repair 迴圈只計次，不判斷修正方向。

## 尚未回答的問題（留給使用者）

1. 「產出」指的是哪一層：generated test、PR body、整條 automation run，還是 test-case 產出？
2. 什麼樣的證據能讓 reviewer 不用重跑就相信這次產出？
3. 優先處理哪種失敗模式：弱化斷言、跳步驟、locator 錯、SUT flake、PR body 不實，還是其他？
4. 驗證者應該是獨立 agent、deterministic checks、人類，還是混合？
5. 可接受的額外成本是多少（每個 case 的 request 數、時間、金錢）？
6. 這會變成第二道人工 Gate，還是一個自動 verdict？兩者與現有 Gate 的關係是什麼？

## 下一步

使用者先寫「產出可信度」的計畫或 spec；agent 只提問、挑戰、補事實，不替使用者定案。  
（教學模式見 `learn/NOTES.md:10-15`。）

## 2026-10-20 更新：Jev 視覺審查 Phase 1

完整研究整理見 [`learn/reference/jev-quality-review.md`](../reference/jev-quality-review.md)；實作票為 `.scratch/prd-to-tests/issues/18-add-jev-quality-checks.md`。

- 先用人工 screen descriptions（`prd/register-login.md` 附錄 A + §6/§8）取代截圖，測 Jev 的三件事。
- 結果：AC 對齊、expected result 可觀察性、step 完整性都可用；4 個 known-bad variants 全抓到，2 個 good cases 沒有被誤 flag。
- 關鍵發現：step 合理性要拆成「合理 / 可達 / 完整」三種問題。`reachable` 抓不到「跳過必填欄位」；`complete` 抓到（0.12）。
- 成本：57 題、約 11.8k input tokens、0.49 秒。
- 產物：`.scratch/jev-register-login-phase1/RESULTS-v3.md`。
- 2026-10-20 追加：v4b 移除 S1–S4、只留完整 PRD 文字，結果與 v3 幾乎相同（4/4 bad 全抓到、good 全部 ≥ 0.8）。對 `register-login.md` 這份完整 PRD 而言，結構化描述是多餘的；PRD 文字本身就足夠。
- 2026-10-20 追加：v4c 再移除附錄 A，結果仍幾乎不變。對這份 PRD，附錄 A 與 S1–S4 都不是必要條件；訊號來自 §4 requirement/AC、§6 verbatim messages、§8 grounding details。
- 2026-10-20 追加：稀疏 PRD（`prd/login-smoke.md`）實驗。原本較豐富的 login cases 被 Jev 大量 flag（G1 AC 0.18、G2 0.47），因為它們断言了 PRD 沒說的 `Logout`、`Delete Account`、`New User Signup!` 等。把 good cases 收斂到 PRD 明說的行為後（S3），G1/G2 全部 ≥ 0.82，4/4 bad variants 仍全抓到。
- 結論修正：關鍵不是「PRD 很長」或「有截圖」，而是 **PRD evidence 範圍與 test case 断言範圍是否一致**。Jev 會把超出 PRD 的 expected result 判成 unsupported；這正是 scope checker 的行為。
- 尚未驗證：Phase 2 的 vision perception。
