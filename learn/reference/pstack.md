# pstack 研究筆記

研究日期：2026-10-19  
研究對象：<https://github.com/cursor/plugins/tree/main/pstack>  
版本：`0.15.28`（`plugin.json` 與 `.cursor-plugin/plugin.json` 一致）  
作者：Lauren Tan（poteto）  
授權：MIT（`pstack/LICENSE`）  
上游狀態：`cursor/plugins` 於 2026-10-19 仍有新提交；pstack 最新提交為 `d4575673`，訊息為 `chore(pstack): bump to 0.15.28`。

## 一句話

pstack 是一套給 Cursor（以及部分支援 Claude Code）使用的工程工作流外掛。它不是程式庫，而是一組 `SKILL.md`、子代理定義、腳本與文件，目標是讓代理「寫更少、但品質更高」，並且在可驗證的前提下放心平行執行多個代理。

作者在 README 的主張是：先深入，再求快；產能本身不是目標，沒有品質的產能只是製造更多 slop。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/README.md>

## 安裝與入口

Cursor：

```text
/add-plugin pstack
```

Claude Code：

```text
/plugin marketplace add cursor/plugins
/plugin install pstack@cursor-plugins
```

Claude Code 會為指令加前綴，例如 `/pstack:poteto-mode`。模型設定則寫到 `~/.claude/rules/pstack-models.md`，而不是 Cursor 的 `.mdc`。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/01-setup.md>、<https://github.com/cursor/plugins/blob/main/pstack/docs/harness/claude-code.md>

日常入口有兩個：

1. `/setup-pstack`：偵測可用模型、選推理預算、寫入每個角色的模型設定。
2. `/poteto-mode`：所有需要嚴謹度的工作都從這裡開始。

其餘技能是情境式的，由 `/poteto-mode` 在 playbook 的步驟需要時呼叫。

## 外掛結構

```text
pstack/
├── .cursor-plugin/plugin.json   Cursor 外掛清單
├── plugin.json                  agent-plugins.org schema 清單
├── skills/                      32 個工作流技能 + 24 個原則技能
├── agents/                      poteto-agent、comment-sicko
├── docs/guide/                  10 篇教學
├── docs/harness/                Claude Code 適配
├── automations/benny/           預設未啟用的 Slack 問題自動化包
├── assets/
└── LICENSE
```

`plugin.json` 宣告 `skills: "./skills/"` 與 `agents: "./agents/"`。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/.cursor-plugin/plugin.json>

## `/poteto-mode` 如何路由

`/poteto-mode` 的 `SKILL.md` 有三個重點區塊：

1. **Non-negotiables**：哪些情況一定要觸發哪個技能，例如跨函式邊界要先 `architect`、平行 fan-out 用 `swarm`、有爭議的設計用 `interrogate`、任何文案表面都要 `unslop`。
2. **Principles**：24 條原則的內聯索引。代理在任務開始時讀這份索引，套用時再讀對應的 leaf `SKILL.md`。
3. **Playbooks**：23 個 playbook 的匹配表。匹配後把步驟原樣複製進 todo list；選擇不做的步驟要保留並標 `skip: <reason>`。

流程大致是：

```text
使用者目標
  → poteto-mode 讀原則索引
  → 匹配 playbook
  → 把步驟寫進 todo list
  → 依步驟呼叫 how / architect / arena / swarm / interrogate / tdd ...
  → 驗證真實產物
  → 開 PR 或交付報告
```

來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/02-poteto-mode.md>

### 提示詞哲學

文件建議使用者只說「目標」和「完成條件」，不要枚舉技能。例如：

```text
/poteto-mode users get two notifications after a retry. repro first, then fix and verify.
```

「repro first」是實際約束，不是客套。完成條件必須能通過或失敗，不能是「做得更好」或「做四小時」。文件也建議先不要說自己的因果猜測，避免代理只往那個方向搜尋。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/02-poteto-mode.md>

## 23 個 playbook

| 分類 | Playbook | 用途 |
|---|---|---|
| 理解 | Investigation | 只讀問題：如何運作、為何這樣設計、是否確定 |
| 修錯 | Bug fix | 先在真實介面重現，再二分定位、修正、驗證 |
| 修錯 | Perf issue | 對照 baseline 追蹤可測量的變慢 |
| 修錯 | Hillclimb | 對單一指標持續做科學化改進，每次只提交被接受的勝利 |
| 修錯 | Runtime forensics | 從 live instrumentation 診斷洩漏、閒置 CPU、glitch |
| 修錯 | Trace forensics | 從 cpuprofile、trace、spindump、heap snapshot 診斷 |
| 建構 | Feature | 從具名資料形狀出發，建立新行為或修改行為 |
| 建構 | Refactoring | 行為不變的結構調整 |
| 建構 | Prototype | 用一次性草稿回答設計或行為問題 |
| 建構 | Visual parity | 兩個實作之間的像素級一致 |
| 技能 | Authoring a skill | 撰寫或修改 `SKILL.md` |
| 技能 | Eval |blinded 地測試技能或提示詞改動對代理行為的影響 |
| 交付 | Babysit | 把 PR 或 stack 推到 merge-ready：衝突、review thread、CI |
| 交付 | Shipping | 獨立驗證綠色 stack，從底部合併連續通過的區間 |
| 自主 | Autonomous run | 長時間跑到完成，不在中途停 |
| 自主 | Orchestrate | 專案級協調：多天、多 stack PR、數十到數百個子代理 |
| 自主 | Autopilot-full | 佇列中每個獨立 PR 由一位 owner 帶到合併，root 用 swarm 驗證 |
| 自主 | Autopilot-stack | 全自動建構並驗證一個線性 stack，交由人類合併 |
| 接續 | Session pickup | 從 transcript、雲端代理 URL 或已推送分支接手 |
| 接續 | Pause safely | 安全暫停，留下可接續的 checkpoint |
| 規劃 | Multi-phase plan | 跨階段或多 PR 的計畫；計畫本身是交付物 |
| 維護 | Worktree cleanup | 清理已合併或廢棄的 worktree、過期模擬器 |
| 交付 | Opening a PR | 從小型有序 commit 開 PR；每個 playbook 的結尾都會呼叫 |

來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/>（目錄）、<https://github.com/cursor/plugins/blob/main/pstack/README.md>

## 24 條原則

原則是「可命名的方向盤」。使用者不必重寫長篇指令，只要說出原則名稱，代理就必須指出這個原則改變了哪個具體決策。原則是獨立技能，`poteto-mode` 只內聯索引，套用時才讀全文。

### Core（10）

| 原則 | 規則 |
|---|---|
| Laziness Protocol | 偏向刪除與最小改動 |
| Foundational Thinking | 先選核心型別與資料結構，再寫邏輯 |
| Redesign from First Principles | 把新需求當成第一天就存在的基礎假設來重新設計 |
| Attack the Premise | 兩個以上修正共享同一前提且都失敗時，直接檢驗前提 |
| Subtract Before You Add | 先移除死重量，再往上建 |
| Minimize Reader Load | 減少層數與讀者需要記住的隱藏狀態 |
| Outcome-Oriented Execution | 遷移與重寫要收斂到目標架構，不保留過渡相容層 |
| Experience First | 使用者體驗優先於實作便利 |
| Exhaust the Design Space | 沒有前例時，做 2 到 3 個原型比較 |
| Build the Lever | 建立可重跑的工具（codemod、script、generator）而不是手工做 |

### Architecture（6）

| 原則 | 規則 |
|---|---|
| Model the Domain | 用結構（狀態機、型別、表格、reducer）取代散落的條件分支 |
| Boundary Discipline | 守衛集中在系統邊界，內部信任型別 |
| Type System Discipline | 讓非法狀態無法表示，外部資料在邊界解析 |
| Make Operations Idempotent | 崩潰與重試後仍收斂到同一終態 |
| Migrate Callers Then Delete Legacy APIs | 同一波遷移呼叫者並刪除舊 API |
| Separate Before Serializing Shared State | 先消除共享，再考慮序列化 |

### Verification（5）

| 原則 | 規則 |
|---|---|
| Prove It Works | 驗證真實產物，不接受代理、自我回報或「編譯通過」 |
| Fix Root Causes | 追到系統第一次出錯的位置再修 |
| Sequence Work into Verifiable Units | 每個小單位都以可檢查狀態結束，再進下一單位 |
| Test Behavior, Not Implementation | 斷言使用者可觀察的行為 |
| Explain the Number | 報告數字前先找出限制因素，排除測錯東西 |

### Delegation（2）

| 原則 | 規則 |
|---|---|
| Guard the Context Window | 大量讀取交給子代理，主執行緒只留摘要 |
| Never Block on the Human | 可逆工作直接做，讓人類事後修正 |

### Meta（1）

| 原則 | 規則 |
|---|---|
| Encode Lessons in Structure | 同一句話講第二次時，改成 lint、檢查、腳本或結構 |

來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/08-principles.md>

## 模型角色路由

`/setup-pstack` 會：

1. 偵測目前 session 可傳給 `Task` 的模型 slug。
2. 詢問推理預算：`unlimited`、`large`、`medium`、`small`。
3. 顯示每個角色的模型並確認。
4. 把設定寫到 `~/.cursor/rules/pstack-models.mdc`，`alwaysApply: true`。
5. 重跑時冪等覆寫整個檔案。

預設角色（節錄）：

| 角色 | 預設模型 |
|---|---|
| `feature, refactoring` | `grok-4.7-xhigh-fast` |
| `bug-fix` | `grok-4.7-xhigh-fast` |
| `perf-issue` | `grok-4.7-xhigh-fast` |
| `hillclimb` | `grok-4.7-xhigh-fast` |
| `judgment and prose` | `claude-opus-5-5-xhigh` |
| `hardest tasks` | `claude-opus-5-5-xhigh` |
| `how explorer` | `grok-4.7-xhigh-fast` |
| `how explainer` | `claude-opus-5-5-xhigh` |
| `why investigators` | `grok-4.7-xhigh-fast` |
| `why synthesizer` | `claude-opus-5-5-xhigh` |
| `reflect tooling` | `grok-4.7-xhigh-fast` |
| `reflect judgment, divergent, synthesizer` | `claude-opus-5-5-xhigh` |
| `arena runners` | `claude-opus-5-5-xhigh, grok-4.7-xhigh-fast` |
| `arena cross-judge pool` | `claude-opus-5-5-xhigh, grok-4.7-xhigh-fast` |
| `swarm workers` | `grok-4.7-xhigh-fast` |
| `architect runners` | `claude-opus-5-5-xhigh, grok-4.7-xhigh-fast` |
| `interrogate reviewers` | `claude-opus-5-5-xhigh, grok-4.7-xhigh-fast` |

重點規則：

- 面板角色是列表，一個項目一個子代理，列表長度就是 fan-out 數量。
- `inherit-parent` 與 `auto` 都代表「省略 `Task` 的 `model`，繼承父對話模型」。
- 沒有列出的角色沿用技能預設。
- 實際 slug 必須在偵測到的清單內；不可寫入未確認的模型。
- 推理等級可依工作難度升降，但必須保持同一模型家族，避免多樣性面板失去多樣性。

來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/setup-pstack/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/01-setup.md>

## 子代理協議

`poteto-mode` 對子代理有明確規則：

- 在 playbook 步驟內 spawn 的子代理一律用 `subagent_type: "poteto-agent"`。
- `poteto-agent` 必須先完整讀取 `poteto-mode/SKILL.md`，包含原則索引；用 `generalPurpose` 會跳過這個步驟並產生漂移。
- 預設 `run_in_background: true`，用檔案指標而不是內聯上下文。
- 每個新工作預設開新的子代理，只有在工作需要該代理的本地 checkout、未提交變更或正在執行的 process 時才 resume。
- 程式碼工作按難度分派：最難的跨領域設計、併發、演算法給最強的判斷模型；機械性小改動給快速的程式碼模型。
- 每個工作樹或分支只能有一個寫者。
- 父代理要自己審查 diff 並寫摘要，不能直接轉貼子代理的說法。
- 第二意見要用不同模型跑同一個提示詞。

`comment-sicko` 是另一個子代理，只做註解審查：它會刪除敘述型、橫幅型、被註解掉的屍體、workaround 說教，只保留法律標頭、外部依賴造成的非顯而易見行為、`prettier-ignore`、公開 API doc comment、issue/RFC 連結。它只回報，不改應用程式碼。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/agents/poteto-agent.md>、<https://github.com/cursor/plugins/blob/main/pstack/agents/comment-sicko.md>

## 驗證體系

pstack 把「驗證」拆成多層：

### 1. Prove It Works

完成任務後，必須用真實產物證明，例如：

- CLI 改動：跑真實指令
- UI 改動：在執行中的應用走過改動流程
- Parser 或 migration：重放已保存的輸入
- 效能改動：比較 before/after profile
- 儲存改動：讀回寫入的值

「inconclusive」或「在錯的介面驗證」都不算通過。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/principle-prove-it-works/SKILL.md>

### 2. `/create-verification-skill`

如果專案沒有可腳本化驅動應用的方式，這個技能會訪談 repository，產生 `.cursor/skills/verify-<app>/`，內含 Launch、Doctor、Drive、Evidence、Cleanup 區段，以及 `features/` feature map。產生器會先端到端證明這個技能可用，才交貨。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/create-verification-skill/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/06-verify-and-ship.md>

### 3. `/create-formal-verification-skill`

當測試很難覆蓋某個性質（例如「同一個 job 不得同時執行兩次」），這個技能會選一個性質與對應工具。事件順序問題預設用 TLA+；若語言沒有可用驗證器，就用生成輸入測真實程式碼，而不是手寫模型。它也會用一個故意破壞的變體驗證「這個檢查真的會失敗」。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/create-formal-verification-skill/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/06-verify-and-ship.md>

### 4. `/maintain-verification-skill` 與 `/maintain-formal-verification-skill`

前者定期審核 verification skill 的 feature map 是否漂移；後者在被驗證的程式碼改動後更新模型、harness 或性質，並區分「驗證漂移」與「程式碼真的壞了」。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/maintain-verification-skill/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/skills/maintain-formal-verification-skill/SKILL.md>

### 5. `/benchmark-checklist`

在報告或行動前，用七個問題檢查數字：

1. 什麼限制了這個數字，為何不是兩倍？
2. 兩邊是否都按生產方式調優？
3. 結果是否違反物理限制，例如磁碟頻寬或核心數？
4. 是否有錯誤或錯誤輸出？
5. 交替多次執行後是否重現，median 與範圍是多少？
6. 對使用者等待的路徑是否有端到端影響？
7. 工作是否真的發生在計時區間內？

結論只能是 faster、slower、no measurable difference 或 inconclusive。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/benchmark-checklist/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/06-verify-and-ship.md>

## 交付：Babysit、Shipping、Autopilot

### Babysit

把 PR 或 stack 推到 merge-ready，處理順序是衝突、review thread、CI。已知修正會批次成一次 push，避免每次修正都重啟 CI。對 Bot 與人類的評論採懷疑態度：真問題修正，噪音要用具體理由駁回並貼在 thread 上。Babysit 停在 merge-ready，永不自行合併。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/babysit.md>

### Shipping

核心規則是「綠色不等於安全」：

1. 每個 PR 由沒寫該程式碼的代理獨立驗證，貼上 `PASS`、`PASS+NOTES` 或 `FAIL`。
2. 只合併從最底部開始連續通過的區間；上面有未驗證的 PR 就等待。
3. 用 `git patch-id` 確認舊 verdict 是否仍描述目前的 head。
4. 從下往上一次合併一個 PR，合併後重新指向下一個 PR 的 base。
5. 合併期間不要手動改 stack。
6. 停在 ceiling；延伸區間需要新的 verdict。

來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/shipping.md>

### Autopilot-full 與 Autopilot-stack

- **Autopilot-full**：每個 PR 一位 owner，owner 負責建構、開 PR、自我證明、babysit、合併。root 在 code-ready head 跑一次完整 swarm 驗證；只有 swarm 對即將合併的 patch 給出乾淨 verdict，owner 才能合併。rebase 或小修正只需一位新驗證者。
- **Autopilot-stack**：同樣的 owner loop，但不合併；早上交給人類一個線性 stack，每個 link 都有 verdict。

來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autopilot-full.md>、<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autopilot-stack.md>

## Orchestrate：專案級協調

`Orchestrate` 是整套最重的部分，適合多天、多 stack PR、數十到數百個子代理的專案。角色分三層：

- **Coordinator**：本地，寫 brief、排空 queue、維持 frontier 綠色、對人類報告；不寫程式碼。
- **Sub-coordinator**：每個 track 一個，本地且 durable；超過一個 coordinator 能處理的 drain 量時才需要。
- **Worker / verifier**：預設雲端；需要 `control-ui`、`control-cli`、本地 transcript、模擬器或本地認證時才留在本機。

儲存在 `orchestrate/<project-slug>/`：

| 檔案 | 用途 |
|---|---|
| `preferences.md` | 長期命令，每次 spawn 與 resume 原樣貼上 |
| `overview.md` | PR 與 issue 的持久 DB，只追加 |
| `units.tsv` | 每個工作單元一列：id、track、state、branch、PR、head SHA、brief 路徑 |
| `frontier.json` | 計算出來的合併 frontier |
| `ledger.tsv` | 驗證帳本，key 是 PR 號加 head SHA |
| `inbox/` | 完成通知指標 |
| `gates.md` | 需要人類決定的事項 |
| `decisions.tsv` | 決策軌跡 |
| `status.md` | 從 `units.tsv` 與 `ledger.tsv` 推導，不手寫 |

Brief 欄位固定：`GOAL`、`SCOPE`、`CONTEXT`、`ACCEPTANCE`、`VERIFY`、`TIMEBOX`、`FORBIDDEN`、`REPORT`、`STANDING`。缺少欄位代表這個單元還沒被界定清楚，應拒絕 spawn。

驗證帳本的值：`live-ui-verified`、`unit-test-verified`、`type-check-only`、`verifier-blocked`、`verifier-failed`。新的 head SHA 會作廢舊列。CI 綠色只是 verdict 的輸入，不是 verdict。

腳本：`skills/poteto-mode/scripts/orch/orch.ts`，用 Bun 執行。它只做狀態讀寫，不 spawn、不等待、不喚醒任何東西。另有 `watch-pr`、`worktree-audit.sh`、`check-plan.mjs`。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/orchestrate.md>、<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/scripts/>

## 決策軌跡：`/show-me-your-work`

長時間或無人看管的工作要留有 TSV 決策軌跡，一行一個決策：

```text
ts	phase	decision	why	evidence	result
```

規則：

- 只追加，錯誤的決策用新行取代，不修改歷史。
- evidence 是指標，不是段落：commit SHA、PR 號、`file:line`、截圖或 trace 路徑。
- 預設留在本地 `decisions.tsv` 或 `.audit/<task-slug>.tsv`；只有審查者需要靠它建立信任時才 commit。
- 結束前要對照 transcript 審核，並由不同模型家族的子代理做交叉審查，回覆結尾要有 `Attention` 區段。

來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/show-me-your-work/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/07-overnight.md>

## 寫作與反 slop

`poteto-mode` 對回覆有硬規則：

- 短宣告句，一句一個想法。
- 不使用長破折號。
- 不用冒號當句中連接詞；冒號只用於引出列表。
- 每個區段都要保留內容，簡短不是刪內容的藉口。
- 先說對使用者與維護者的影響，再說實作細節。
- 不捏造連結、引用或 transcript。
- 每個論斷都要在同一句帶證據或標籤：measured、inferred、guess。

另外有 `/unslop`（移除 AI 寫作痕跡）、`/no-comments`（註解審查）、`/technical-writing`（Diátaxis + Google developer style + STE + Global English）、`/bro`（把上一則訊息用白話重說）。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/skills/unslop/SKILL.md>、<https://github.com/cursor/plugins/blob/main/pstack/skills/technical-writing/SKILL.md>

## Automations：benny

`automations/benny/` 是預設休眠的 Slack 問題自動化包：

- `triage-issue-reports`：分診 Slack 問題回報。
- `reproduce-and-fix-issues`：重現已確認的 bug，必要時準備小型草稿修正。
- `setup-benny`：把包安裝到目標 repo 的 `.cursor/automations/benny/`。

它是 Cursor-only，因為依賴 Cursor Automations。設定入口是 `FOR_AGENTS.md`。  
來源：<https://github.com/cursor/plugins/blob/main/pstack/automations/benny/README.md>、<https://github.com/cursor/plugins/blob/main/pstack/automations/benny/FOR_AGENTS.md>

## 限制與風險

1. **強綁 Cursor**：`Task`、`AskQuestion`、cloud agents、Bugbot、Automations 都是 Cursor 概念。Claude Code 有適配表，但 cloud agents、Bugbot、Automations 等步驟會直接跳過。
2. **成本高**：多子代理、多模型面板、獨立驗證者都會增加 token 與時間。作者在 setup 文件建議縮小預算、面板或角色。
3. **預設 slug 會過期**：`grok-4.7-xhigh-fast`、`claude-opus-5-5-xhigh` 是 2026-10-19 的預設值，不是穩定 API。
4. **外部依賴**：`/deslop`、`control-cli`、`control-ui` 在 `cursor-team-kit`，不在 pstack 內。
5. **刻意沒有 planning 技能**：作者認為最好的 spec 是程式碼；計畫要在設計用原型定下來之後才寫。
6. **腳本是 TypeScript/Bun**：`orch.ts`、`watch-pr` 不能直接搬進 Python 專案。
7. **流程本身很重**：playbook、原則、brief 模板都需要紀律；小工作不適合全套。
8. **部分文件假設 Cursor 介面**：例如 Custom Mode 要用 Option+Enter 釘住，`/loop` 是 Cursor 內建指令。

來源：<https://github.com/cursor/plugins/blob/main/pstack/docs/harness/claude-code.md>、<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/01-setup.md>、<https://github.com/cursor/plugins/blob/main/pstack/README.md>

## 與本倉庫的對照（事實陳述）

- 本倉庫的 `ponytail` 與 pstack 的 `laziness-protocol`、`subtract-before-you-add` 高度重疊：都偏向最小改動與刪除。
- 本倉庫的 `playwright-cli` 與 QA 測試用例生成技能，和 pstack 的 `verify-<app>` 思路可對應；差別在 pstack 把驗證技能做成可生成、可維護、可形式化的基礎設施。
- 本倉庫的 `AGENTS.md` 已有「boundary data 用 Pydantic、內部資料用 dataclass」的慣例，和 pstack 的 `boundary-discipline`、`type-system-discipline` 同方向。
- pstack 的 `bug-fix`、`feature`、`shipping` 是純 prose，跨語言可讀；真正執行仍依賴 Cursor 子代理與雲端環境。
- 本倉庫是 Python 3.13 + Pydantic AI，pstack 的 orchestration 腳本與 Cursor 欄位不能直接移植。

## 一手來源清單

- 上游目錄：<https://github.com/cursor/plugins/tree/main/pstack>
- README：<https://github.com/cursor/plugins/blob/main/pstack/README.md>
- 外掛清單：<https://github.com/cursor/plugins/blob/main/pstack/.cursor-plugin/plugin.json>
- 入口技能：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/SKILL.md>
- 模型設定：<https://github.com/cursor/plugins/blob/main/pstack/skills/setup-pstack/SKILL.md>
- 指南索引：<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/README.md>
- 安裝：<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/01-setup.md>
- 路由：<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/02-poteto-mode.md>
- 設計：<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/04-design.md>
- 驗證與交付：<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/06-verify-and-ship.md>
- 過夜執行：<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/07-overnight.md>
- 原則：<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/08-principles.md>
- 食譜與陷阱：<https://github.com/cursor/plugins/blob/main/pstack/docs/guide/10-recipes-and-pitfalls.md>
- Claude Code 適配：<https://github.com/cursor/plugins/blob/main/pstack/docs/harness/claude-code.md>
- 子代理：<https://github.com/cursor/plugins/blob/main/pstack/agents/poteto-agent.md>
- 註解審查：<https://github.com/cursor/plugins/blob/main/pstack/agents/comment-sicko.md>
- Orchestrate：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/orchestrate.md>
- Shipping：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/shipping.md>
- Autopilot-full：<https://github.com/cursor/plugins/blob/main/pstack/skills/poteto-mode/playbooks/autopilot-full.md>
- 決策軌跡：<https://github.com/cursor/plugins/blob/main/pstack/skills/show-me-your-work/SKILL.md>
- benny 自動化：<https://github.com/cursor/plugins/blob/main/pstack/automations/benny/README.md>
