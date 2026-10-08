# Resources

## Pydantic AI Harness

### Knowledge

- [Pydantic AI Harness 官方文件](https://pydantic.dev/docs/ai/harness/)
  權威來源。整體定位（harness 是什麼、core 與 harness 的機械性分界）、完整 capability
  清單與分群、版本政策。
  用途：查任何 harness capability 的定位與安裝；判斷某能力屬 core 還是 harness。
- [套件內一手說明：`pydantic_ai_harness/skills/README.md`](../../.venv/lib/python3.13/site-packages/pydantic_ai_harness/skills/README.md)
  本機已安裝 0.54.0 的 `Skills` 官方 README（`Skills` 的完整行為、include/exclude、
  workspace、skill 格式、bundled files 不載入）。
  用途：`Skills` 細節的第一手依據；比線上文件更貼近目前鎖定的版本。
- [Capabilities on Demand](https://pydantic.dev/docs/ai/capabilities/on-demand/)
  progressive disclosure、`defer_loading`、`load_capability` 的觀念與 runtime 語意。
  用途：理解「為何 base prompt 要小」以及 deferred 工具如何隨 provider 呈現。
- [Capabilities overview](https://pydantic.dev/docs/ai/capabilities/overview/)
  capability 這個原語本身（instructions／tools／settings／hooks）。
  用途：建立 harness 的底層心智模型。
- [Agent Skills specification](https://agentskills.io/specification)
  `SKILL.md` 的跨工具格式規格。
  用途：寫或審查 skill 時的格式依據。
- [GitHub: pydantic/pydantic-ai — harness 原始碼](https://github.com/pydantic/pydantic-ai/tree/main/src/pydantic_ai_harness/pydantic_ai_harness)
  每個 capability 的實作，也是可照抄的範例。
  用途：文件不足、或想學「怎麼寫自己的 capability」時。

### Wisdom (Communities)

- [Pydantic Logfire Slack](https://logfire.pydantic.dev/docs/join-slack/)
  官方 Slack，維護者會回覆 harness／Pydantic AI 問題。
  用途：API 改版遷移、capability 組合踩坑時求助。
- [GitHub Issues: pydantic/pydantic-ai](https://github.com/pydantic/pydantic-ai/issues)
  bug 與設計討論；harness 0.x 的破壞性變更線索常在此。
  用途：確認某行為是 bug 還是預期。

### Gaps

- Harness 為 **0.x 版本政策**：minor 版之間 API 可能改名／改預設。本課以鎖定的
  0.54.0 為準（見 `uv.lock`），升級時須重讀該 capability 的 README。
- 尚無繁體中文的 harness 教學資源；本 repo 的課程即為第一份。

---

## Matt Pocock 工程流程 Resources

### Knowledge

- [GitHub repo: mattpocock/skills — README](https://github.com/mattpocock/skills)
  這套流程的權威來源。README 有完整的主流程說明與「user-invoked vs model-invoked」分類。
  用途：查任何 skill 的定位、安裝方式、以及每條流程的動機。
- [Skill 原始檔: `ask-matt/SKILL.md`](../../.agents/skills/ask-matt/SKILL.md)
  所有 flow 的路由圖（main flow、on-ramps、vocabulary 層）。
  用途：不確定下一步該用哪個 skill 時的第一站。
- [AI Coding Dictionary](https://www.aihero.dev/ai-coding-dictionary)
  Matt Pocock 的術語表（harness、attention degradation、smart zone、compaction、ticket、spec…）。
  用途：建立共同的底層語言；讀完全部章節會得到一套心智模型。
- [GitHub: dictionary-of-ai-coding](https://github.com/mattpocock/dictionary-of-ai-coding)
  上述字典的開源版本，逐詞可引用。
  用途：需要精確引用某術語定義時。
- [本 repo 內各流程 SKILL.md](../../.agents/skills/)
  每個流程的第一手規則。最重要者：`to-spec`、`to-tickets`、`implement`、`tdd`、`codebase-design`、`writing-for-agents`。
  用途：執行前的細節查核（格式、模板、完成準則）。

### Wisdom (Communities)

- [mattpocock/skills — Discussions](https://github.com/mattpocock/skills/discussions)
  使用者與貢獻者討論 skill 用法與踩坑。
  用途：流程卡關、想看別人怎麼改寫這些 skill 時。
- [AI Hero newsletter](https://www.aihero.dev/s/skills-newsletter)
  Skill 更新與新流程發布（作者本人的一手消息）。
  用途：追蹤流程演進。

### Gaps

- `ask-matt` 內引用的 `https://www.aihero.dev/ai-coding-dictionary/smart-zone` 目前 404；
  暫時以字典首頁（`#4 Failure Modes` 一節含 smart zone）與 GitHub 版替代。
- 尚無「本 repo 專屬」的實作範例社群資源。
