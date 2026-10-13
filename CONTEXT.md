# web-test

`web-test` 是一個自建 AI agent：讀 PRD，以 QA 職能推導測試案例，再產生可執行的
自動化測試並修復失敗。本檔是本專案的領域詞彙表（glossary），不含實作細節。

## Language

**PRD**:
產品需求文件；本 agent 的輸入，描述產品「應該做什麼」。
_Avoid_: spec, requirements doc

**Requirement**:
PRD 中一項可被驗證的功能需求，具有唯一 id；測試案例的追溯單位。
_Avoid_: feature, user story, item

**Test Case**:
意圖層的一個驗證情境，對應一條或多條 Requirement（以 `requirement_ids` 追溯），帶
priority、severity、test type、preconditions、steps 與 expected result。由 PRD 經
`qa-test-case-generation` skill 產生。
_Avoid_: 測試項目、測試案例（三者指同一物，勿當成不同東西）

**Step**:
Test Case 內的一個使用者層級動作（Given/When/Then 的其中一步）。
_Avoid_: action

**Action**:
Page Object 上的一個方法，封裝某個元素的互動或查詢。
_Avoid_: step, operation

**Page**:
被測應用的一個畫面。
_Avoid_: screen, view

**Page readiness check**:
Page Object 對「本頁已就緒」的檢查（`expect_loaded()`）；斷言本頁獨有的 URL／標題／內容，
不得依賴共享的 header／nav／footer。
_Avoid_: assertion, visibility check

**Component**:
跨頁面重用的 UI 區塊（如 Header、Nav），有自己的物件，存放於共用元件庫。
_Avoid_: widget, fragment

**State**:
與 Page 正交的條件，決定哪些元素存在（例如未登入／已登入、購物車空／有商品）。
_Avoid_: page mode

**Automation Test**:
由 Test Case 產生的可執行自動化測試。
_Avoid_: script, test code

**Gate**:
Test Case 設計與自動化之間的**人工審核**點；審核通過才能進入自動化。以「新增 `test-case/<id>.md`
的 PR 被 merge」表示。
_Avoid_: approval, checkpoint

**Snapshot**:
對 live 頁面取得的無障礙樹觀察，作為 grounding 的依據。
_Avoid_: DOM dump

**Grounding**:
把意圖（Step）對應到真實元素的過程；靠觀察 live 頁面完成。
_Avoid_: locating, matching
