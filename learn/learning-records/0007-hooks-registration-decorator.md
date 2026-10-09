# Hooks 的註冊 decorator：`@` 是重新綁定名字，註冊是 import 副作用

Pydantic AI 的 `Hooks` 用 decorator 註冊生命週期掛鉤，例如
`@write_guard.on.before_tool_execute(tools=[...])`。搞懂它，才不會誤解「私有名 `_guard` 怎麼被找到」。

- 這是**參數化 decorator**：`before_tool_execute(tools=[...])` 先回傳一個 `decorator`，
  再由它去裝飾 `_guard`。等價於：
  ```python
  async def _guard(...): ...
  _guard = write_guard.on.before_tool_execute(tools=[...])(_guard)
  ```
- 一般 Python 規則：`@dec def f(): ...` ≡ `f = dec(f)`。**decorator 的回傳值會被重新綁定到 `f`**；
  若 decorator 回 `None`，`f` 就變成 `None`（經典陷阱）。
- 這個 decorator 的實作是「把 `f` 加進 registry（**副作用**）後 `return f`」——所以被裝飾的
  `_guard` 仍指向原函式。但**就算它回傳別的東西，註冊也已完成**。
- `_guard` 的底線是**慣例**（表示模組內部用），Python 不強制。capability 靠的是**註冊當下存下的參照**，
  與這個名字私不私有無關。

## Evidence

- `.venv/lib/python3.13/site-packages/pydantic_ai/capabilities/hooks.py`：`_tool_bare_or_parameterized`
  （316–334）在 `decorator(f)` 內 `registry.setdefault(...).append(_ToolHookEntry(f, ...))` 後 `return f`。
- `web_test/write_guard.py`：`@write_guard.on.before_tool_execute(tools=["write_file", "edit_file"])`
  裝飾 `_guard`。

## Implications

- 讀這類「註冊型 decorator」時，別假設被裝飾的名字還指向函式；必要時回原始碼確認回傳值。
- 掛鉤在**import 該模組時**就註冊完畢——只要 capability 被 import／掛上，掛鉤即生效，
  不依賴之後再呼叫 `_guard`。
- 名字加底線（`_`）只表達「別從外部引用」，不影響框架如何找到已註冊的函式。
