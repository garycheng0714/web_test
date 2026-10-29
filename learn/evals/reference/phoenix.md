# Arize Phoenix 研究筆記

> 狀態：只讀官方文件，**未實跑**。查閱日 2026-10-28。
> 本文只記 Phoenix 本身，不含 LangSmith / Braintrust 對照。

## 一句話

Arize AI 的開源 LLM observability 平台：接收 OpenTelemetry traces，提供
trace 檢視、evaluation、dataset/experiment、prompt 版本管理。
授權 **Elastic License 2.0**，可自架、無功能分級；商業託管版是 Arize AX。

## 跟這門課的關係

Phoenix 提供的是**容器**，不是方法論：

- 它幫你存 trace、掛分數、把同一批輸入跑兩次並排比較。
- 它不幫你做 error analysis，也不幫你校準 judge；failure mode 還是要自己從
  trace 收斂出來。
- 它的 pytest plugin 把檢查分成 **hard invariant**（`assert`，讓 CI 紅）與
  **quality signal**（`log_evaluation`，只看趨勢），跟 Lesson 0004/0005 的
  分法一致。
- evaluator 自己也會被 trace，所以「judge 為什麼這樣判」是可查的，這對
  Lesson 0006 的 judge 校準是有用的證據來源，但不能取代人工標註。

## 架構

```text
app / agent
  │  OTLP (HTTP :6006 / gRPC :4317)
  ▼
Phoenix collector ──> SQLite (預設, ~/.phoenix/) 或 PostgreSQL (團隊)
  │
  ▼
UI：traces → annotations/evals → datasets → experiments → prompts
```

- **資料入口是 OTLP**，不是 Phoenix 自家 SDK。任何送得出 OpenTelemetry 的程式
  都能接；OpenInference 是一套語意約定，負責把 LLM/tool/retriever span 標成
  UI 看得懂的樣子。
- 啟動：`uvx arize-phoenix serve`，或
  `docker run -p 6006:6006 -p 4317:4317 arizephoenix/phoenix:latest`。
- 儲存：SQLite 適合本機；PostgreSQL（最低 14）適合多人與 production。
- **一個 instance = 一個 tenant**。多團隊要開多個 instance，或用 Postgres
  schema 隔離；細到 project 層級的權限仍是 roadmap。
- 擴充：多個 instance 共用同一個 Postgres，前面掛 load balancer。
- 生產要 pin `version-X.X.X`，不要用 `latest`。

## 四個能力

| 能力 | 回答什麼 | 介面 |
| --- | --- | --- |
| Tracing | 這次執行發生了什麼、慢在哪 | OTLP；各框架的 auto-instrumentation |
| Evaluation | 輸出品質好不好 | client-side SDK、server-side（UI 掛在 dataset 上）、人工標註 |
| Datasets & Experiments | 改了 prompt/model 是真的變好嗎 | `run_experiment`、pytest plugin |
| Prompt Engineering | 用真實案例迭代 prompt | Playground、prompt 版本、span replay、prompts in code |

補充事實：

- Evaluation 支援 code evaluator（exact match、regex、自訂函式）與
  LLM-as-a-judge。Judge 用 tool calling 取結構化輸出（label + explanation），
  不是解析自由文字。
- Pre-built metrics 涵蓋 faithfulness、hallucination、correctness、toxicity、
  refusal、PII、retrieval relevance、tool selection / invocation / response
  handling、user friction 等。
- 內建 executor 處理 rate limit、retry 與動態併發；官方宣稱最高 20x 加速，
  這是供應商說法。
- Dataset 的 example 有 `input`、選填的 reference `output`、`metadata`；
  支援 splits、repetitions、從 traces / code / CSV 建立。
- Dataset evaluator 的角色就是「這份資料集的測試案例」，跑 experiment 時自動
  套用同一組標準。
- 每次 evaluator 執行都進一個專屬 project 的 trace，包含送給 judge 的完整
  prompt、推理、分數與耗時。

## 跟這個 repo 的接點

### 1. Pydantic AI

`openinference-instrumentation-pydantic-ai` 提供 `OpenInferenceSpanProcessor`，
搭配 Pydantic AI 的 `Instrumentation` capability。structured output、tool call、
retry、validation error 都會變成 span。

### 2. Pydantic Evals

可以先用 Phoenix 收 trace，再把 span 匯出成 dataframe，餵給
`pydantic_evals.Dataset`；跑完的結果用
`client.spans.log_span_annotations_dataframe` 寫回 Phoenix 當 annotation
（`annotator_kind="CODE"` 或 `"LLM"`）。等於「本機跑 eval，Phoenix 存歷史」。

### 3. pytest plugin

`arize-phoenix-client[pytest]>=2.10.0`，用 `@pytest.mark.phoenix(dataset=...)`。

```text
test file        → Phoenix dataset
parametrize case → dataset example
test run         → experiment
assert 結果      → pass annotation
log_evaluation() → 自訂 annotation
```

- `assert` 失敗 = CI 紅；`log_evaluation()` 只記錄，不 gate。
- 上傳是 best-effort：Phoenix 掛掉只會 warning，不會讓測試失敗。
- 支援 `-n auto`（pytest-xdist）、async、`-k`、repetitions。
- 用 `PHOENIX_TEST_TRACKING=0` 可完全離線跑。
- 完整跑會修剪 dataset 中已不存在的案例；部分跑（`-k`、單檔）只追加。

### 4. `px` CLI / MCP / coding agent

- `px` 可讀 traces、sessions、datasets、experiments、prompts，並寫入
  annotation / note。**不能**建 dataset、改 prompt、跑 experiment。
- MCP server 走 `/mcp`，讓沒有 terminal 的 client 直接查。
- 官方有 opencode 的 tracing plugin（`Arize-ai/coding-harness-tracing`），
  每個 turn 一個 trace，tool call 是 nested span；sub-agent 目前各自獨立，
  不會連回父 trace。

## 限制

- 沒有 online eval、alerting、threshold 觸發；那是 Arize AX 的功能。
- 單租戶；跨團隊隔離要靠多 instance 或 schema。
- `px` 對 dataset / prompt / experiment 是唯讀的。
- ELv2 不是 OSI 認證授權：自用與修改可以，但不能拿去做託管競品。
- 官方文件給的效能與加速數字屬供應商宣稱，未獨立驗證。
- 本課程的 MISSION 仍把「特定 eval 框架 API 操作」與 production 監控列為
  out of scope；下面的「本 repo 實測」屬專案 spike，不是課程要求。

## 本 repo 實測（2026-10-29）

- 本機 `uvx arize-phoenix serve` 可啟動；UI 與 OTLP HTTP 都在 `:6006`。
- Python 3.13 可安裝 `openinference-instrumentation-pydantic-ai==0.1.30` 與
  `pydantic-ai==2.54.0`；用 `uv run --with` 不會改 `uv.lock`。
- 用 `Agent.instrument_all(InstrumentationSettings(version=5, tracer_provider=...))`
  搭配 `OpenInferenceSpanProcessor` + OTLP exporter，designer run 會變成：
  `invoke_agent test_case_designer` → `chat ...` → `execute_tool load_capability` → `chat ...`。
- `version=2` 也能映射，但 Pydantic AI 已標為 deprecated；預設用 5。
- Runbook 與本 repo 專屬細節：`.scratch/designer-evals/phoenix/README.md`。

## 尚未驗證

- 最新版號與 Docker tag（文件範例出現 `version-8.0.0`，僅供參考）。
- UI 的 trace review 是否真能取代 `toy/review.py` 的自由文字標註流程。
- pytest plugin 在本 repo 的 `uv run pytest` 下是否可直接運作。
- dataset / experiment / annotation / prompt 流程尚未在本 repo 實跑。

## Sources

- 首頁 / 功能總覽 — https://arize.com/docs/phoenix
- 啟動與埠 — https://arize.com/docs/phoenix/get-started
- 架構、儲存、租戶、擴充 — https://arize.com/docs/phoenix/self-hosting/architecture
- 自架與映像 tag — https://arize.com/docs/phoenix/self-hosting
- 授權 — https://arize.com/docs/phoenix/self-hosting/license
- Traces 概念 — https://arize.com/docs/phoenix/tracing/llm-traces
- Evaluation 總覽 — https://arize.com/docs/phoenix/evaluation/llm-evals
- Pre-built metrics — https://arize.com/docs/phoenix/evaluation/pre-built-metrics
- Datasets & Experiments — https://arize.com/docs/phoenix/datasets-and-experiments/overview-datasets
- pytest plugin — https://arize.com/docs/phoenix/evaluation/integrations/pytest
- Pydantic AI tracing — https://arize.com/docs/phoenix/integrations/python/pydantic/pydantic-tracing
- Pydantic Evals — https://arize.com/docs/phoenix/integrations/python/pydantic/pydantic-evals
- CLI — https://arize.com/docs/phoenix/integrations/developer-tools/cli
- OpenCode tracing — https://arize.com/docs/phoenix/integrations/coding-agents/opencode
