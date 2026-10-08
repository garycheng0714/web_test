<!--
這是「課程」依你選定的 A → B → C 方向整理出的計畫骨架，交給你自己改寫與定案。
標 ⚠ 的欄位是我的建議（你之前明確要我給方向），請改成你的決定；沒標的就是事實或待你填。
寫完後跟我說「grill me」，我只提問、不給建議答案。
欄位說明見 learn/reference/spec-template.html。
-->

# Plan draft: Coding Agent（test case → 自動化測試 → PR）

## Problem Statement
<!-- 你觀察到的問題，從使用者角度看。誰、在什麼情境、痛在哪裡？ -->
test case 已經有了（QA 階段產出、人工審核過），但從 test case 到「可執行的自動化測試」仍是手寫。
我要讓 agent 讀 test case、實作自動化測試，並發 PR。
（⚠ 這一步是 spec 的第二階段 `automate` 的加強版：多了一段 PR。）

## Solution
<!-- 你想做的解法，從使用者角度看。它如何解決上面的問題？ -->
建一支 **coding agent**，輸入是已審核的 test case，輸出是 Playwright Python 測試（POM），最後發 PR。

教學載體：**同一支 agent 由淺入深重構三次**（A → B → C），再加最後的 PR 段（D）：
- **A · 用現成**：`LocalWorkspace` ＋ harness `Coder()`，先跑通。
- **B · 拆開重組**：把 `Coder()` 換成底層 capability 自己疊。
- **C · 自己造**：把 spec 的 write guard（pure function）包成自己的 capability。
- **D · PR**：在 clone 裡 commit／分支，接上開 PR。

## User Stories
<!-- 盡量多列。格式：As a <actor>, I want <feature>, so that <benefit> -->
1. As a QA, I want the agent to read approved test cases, so that I do not hand-write each test.
2. As a QA, I want generated tests to follow the repo's POM conventions, so that the suite does not fork.
3. As a QA, I want the tests actually run, so that output is verified not assumed.
4. As the builder, I want to build the same agent three ways (use / decompose / author), so that I learn Harness from the surface down to the extension point.
5. As the builder, I want the PR step last and optional, so that credentials and irreversible side effects do not block learning.

## Implementation Decisions
<!-- 要建/改哪些 module、介面、技術決策、資料流。不要寫檔名或程式碼片段。 -->

### 模組、介面
| 模組 | 輸入 | 輸出 | 不變量 / 錯誤 |
|------|------|------|----------------|
| Coding Agent | test case 文件 | 生成測試檔 + 執行結果 | **v1 不檢查 `approval` gate**（先不管） |
|（內部）Write Guard | 目標路徑 | 允許 / 拒絕 | 只允許 tests／pages／setup；擋 traversal、其他副檔名、config、原始碼 |
|（D）PR step | branch + 變更 | PR | 無 remote/憑證 → 停在本地 diff ⚠ |

### 流程圖
[test cases] → [Coding Agent] → 生成測試/POM → [uv run pytest] →（紅）修復回圈（上限 3）→（綠）→ [D: commit/分支 → PR]

### Workspace
在本機 **throwaway clone** 上工作（已定案），不是直接動真 repo；Stage A 的 `Coder()` 沒有寫入護欄，用 clone 隔離。

### A / B / C 的 harness 面（⚠ 對照用）
| 階段 | capabilities | 回饋迴圈 | 學到 |
|------|--------------|----------|------|
| A | `LocalWorkspace(clone)` ＋ `Coder()` | `uv run pytest` 綠/紅 | 用工具、workspace 心態 |
| B | `FileSystem`＋`Shell`＋`RepoContext`＋`SubAgents`＋compaction＋`ToolOutputLimits` | 同上，可逐顆調參對照 | 每顆 capability 的介面與 seam |
| C | 自製 `AbstractCapability`（write guard） | 該 capability 的單元測試 | 擴充點與生命週期 |

### Tech Stack
Pydantic AI ＋ Pydantic AI Harness（extras：`[coder]`；D 才需 `[github]`）；Playwright Python；pytest；POM。

## Ticket 切法（⚠ 候選，尚未發佈到 tracker）
| 票 | 內容 | Seam | 完成準則 | Blocked by |
|----|------|------|----------|------------|
| 12 | Stage A：`Coder()` spike | Coding Agent entrypoint | 一條 requirement 的 cases → 一個 `uv run pytest` 綠測試；測試以模型 override、不碰網路 | 09/10 之後 ⚠ |
| 13 | Stage B：拆開重組 | 同上 entrypoint | 同 A 的綠結果；底層自己組；記錄與 `Coder` 預設的差異 | 12 |
| 14 | Stage C：write guard capability | 新 capability ＋ 單元測試 | guard 擋 traversal／副檔名／config／原始碼，放行 tests／pages／setup | 13 |
| 15 | Stage D：PR flow | clone 內分支與 commit | 產出含生成測試的分支；有 remote＋憑證才真的開 PR | 14 |
| 16 | E2E 驗收與文件 | — | A→B→C→D 走通；README/AGENTS 補指令 | 15 |

## Testing Decisions
<!-- 什麼是好測試、要在哪個 seam 測、哪些 module 要測。 -->
- 好測試驗外部行為、可抗重構；A/B 以 `TestModel`／`FunctionModel` override 模型腳本化工具呼叫，斷言生成檔內容與 argv。
- C 的 write guard 是 pure function → 直接單元測試（允許／拒絕清單）。
- 全流程不開真實瀏覽器、不碰網路（navigation 只做 grounding 的 fake）。

## Out of Scope
<!-- 明確不做的事，擋住膨脹。 -->
- 換掉 `playwright-cli` 改 `PlaywrightBrowser`（避免同時學兩件事）⚠
- 真實雲端沙箱（先在本機 throwaway clone 隔離）
- **實作 `approval` gate 檢查**（已定案：v1 先不管）
- 在 D 之前引入 GitHub 憑證
- 取代 PR 的 code review gate（D 只負責「開 PR」）

## Further Notes
<!-- 其他補充、風險、待解問題。 -->
- **安全**：`LocalWorkspace` 的 Shell 無 allowlist，能碰整台機器可及的範圍；`.playwright-cli/` 可能含憑證、永不入版控。Stage A 用 clone 隔離。
- **已定案**：workspace 用本機 throwaway clone；v1 先不管 approval gate。
- **待你定案**：模型換不換（`WEB_TEST_MODEL`）？每階段留哪些教學痕跡（lesson／learning record／ADR）？
- **文件債**：用 `Coder()` 等於委派，與 spec 的 Out of Scope「Delegating code edits to an existing coding agent（ADR-0001）」牴觸；ADR-0001 已被 ADR-0004 supersede。整條決定應補一張 **ADR-0006** 收掉這個不一致。
- **學習機制**：Stage A 動手前先寫預測（`Coder()` 給幾個工具？無 workspace 會如何？）再驗證，避免流暢錯覺。
