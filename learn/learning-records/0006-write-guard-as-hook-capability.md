# 把 write guard 做成 Hooks capability（pure function 當 seam）

Stage C 要「自己造一顆 capability」。實作後的核心洞見：**要在既有工具執行前加護欄，用
`Hooks.on.before_tool_execute(tools=[...])` 攔截，比新增/取代工具乾淨得多。**

- Pydantic AI 的 capability 有兩條入門：`Capability`（自帶 instructions/tools 的工具束）與
  `Hooks`（攔截既有生命週期）。write guard 屬後者。
- hook 拿得到**已驗證**的 `args`，所以在 `before_tool_execute` 直接讀 `args["path"]` 是安全的；
  不合法 raise `ModelRetry`，模型會改路徑重試（不是硬失敗）。
- 這樣**不與 `Coder()` 的 `FileSystem.write_file`/`edit_file` 撞名**，也不用關掉它的檔案工具；
  guard 只是疊上去的一層。護欄規則本身抽成 pure function（`check_write_permission`，回
  `WritePermission`），可獨立單測。

## Evidence

- `web_test/write_guard.py`：`check_write_permission(path) -> WritePermission`（純詞法：擋絕對路徑、`..` 逃逸、
  非 `.py`、非 `tests/`／`pages/`／`components/`；`WritePermission.allow` 由 `error_msg` 推導）；
  `write_guard = Hooks(id='write_guard')` ＋
  `@write_guard.on.before_tool_execute(tools=["write_file", "edit_file"])`。
- `tests/test_write_guard.py`：pure function 12 例 ＋ 最小 agent（`LocalWorkspace`＋`FileSystem`
  ＋`write_guard`，`FunctionModel` 腳本化）allow/reject 2 例 → 14 passed。
- 接進 `web_test/coding_agent.py` 後 capabilities 由 12 → 13；以 `gemini-3.5-flash` 重跑
  TC-ENG-004，agent 經 guard 寫 `tests/`、`pages/` 並綠（clone 全套 15 passed，1 已知 PUA）。

## Implications

- **先想 hook，再想新工具**：能攔既有工具就不要自帶工具，避免撞名與重造。
- guard 的允許清單綁 repo 佈局（`tests/`／`pages/`／`components/`）；改佈局要同步改 `check_write_permission`。
- 最小 agent 測試比「硬上 `Coder`」簡單：`Coder` 的 `RepoContext` 會讓請求 streaming，
  `FunctionModel` 需 `stream_function`；測 capability 時用最小組合即可。
- 測試內呼叫 agent 要用 `web_test._run.run_sync`（worker thread 跑 `asyncio.run`），否則在
  pytest 環境會 `RuntimeError: This event loop is already running`。
