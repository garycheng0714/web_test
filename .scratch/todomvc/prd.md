# PRD:TodoMVC(designer eval 的第二份 PRD)

> **版本**:v0.1(2026-11-05)
> **性質**:由公開規格**抽取**,不是反推,也不是本專案撰寫
> **來源**:[`tastejs/todomvc` 的 `app-spec.md`](https://github.com/tastejs/todomvc/blob/master/app-spec.md)
> @ `d040877fd8895c4f18fa5190e4b8ee474ffa8ac4`
> **live**:https://demo.playwright.dev/todomvc/
> **用途**:held-out PRD,用來驗證 judge 的判準在另一份規格、另一種顆粒度上是否成立。不進
> production 管線(`prd/` 底下新增檔案會觸發 `plan.yml`)。
> **抽取規則**:
> 1. 只收使用者可見的結果;實作細節(CSS class、`localStorage` key、`<strong>` 包裝)不進
>    requirement。
> 2. 同一段動作序列合成一個 requirement(與 working PRD v0.8 相同:一個 requirement = 一段
>    旅程,不使用 AC 標號)。
> 3. 能用規格原句就用原句,不改寫成我們的語氣。
> 4. 規格沒寫的行為放進第 11 章,不自行補。
> 5. 被丟掉的東西列在第 10 章,讓切法可被檢查。

## 1. 產品概述

一個單頁的 todo 清單 app:新增、勾選完成、編輯、刪除、依狀態篩選,並在重新載入後保留內容。
規格本身是「如何實作一個一致的 TodoMVC 範例」,本 PRD 只取其中對使用者可見的行為。

## 2. 使用者角色

| 角色 | 說明 |
|---|---|
| 使用者 | 唯一的角色。沒有登入、沒有多使用者、沒有權限。 |

## 3. 資訊架構

### 3.1 頁面與元件

| 元件 | 內容 |
|---|---|
| 新增輸入框 | 位於 app 頂部;載入時應取得焦點 |
| 主列表(`#main`) | 全部 todo;頂端有「全部標記完成」checkbox |
| 單一 todo | checkbox、標題、懸停時顯示的移除按鈕;雙擊標題進入編輯 |
| Footer(`#footer`) | 未完成計數、篩選連結(All / Active / Completed)、「清除已完成」按鈕 |

### 3.2 狀態

- 清單為空:主列表與 footer 都隱藏。
- 篩選:`#/`(全部)、`#/active`、`#/completed`。

## 4. 功能需求

> 編號 `FR-<模組>-<序號>`;一個 requirement 就是一段旅程:起始狀態、動作、可觀察的結果。
> 括號內是規格對應的段落名。

### 4.1 清單 (TODO)

#### FR-TODO-01 空狀態
- 主列表(`#main`)與 footer(`#footer`)承載清單、計數與篩選。
- 開啟 app 且沒有任何 todo → 主列表與 footer 都隱藏。(No todos)

#### FR-TODO-02 新增 todo
- 新增輸入框位於 app 頂部;載入時應取得焦點(規格建議使用 `autofocus`)。
- 在輸入框輸入文字後按 Enter → 該文字成為清單最後一項,輸入框清空。
- 只輸入空白(trim 後為空)後按 Enter → 不建立新項目。(New todo)

#### FR-TODO-03 勾選完成
- 每個 todo 有一個 checkbox。
- 點某一項的 checkbox → 該項被標記為完成,清單上以已完成樣式呈現。(Item, 1)

#### FR-TODO-04 全部標記完成
- 清單頂端有一個「全部標記完成」checkbox。
- 勾選它 → 所有 todo 變成與它相同的狀態。
- 所有 todo 都被勾選時,它自動變為勾選;任一項被取消勾選時,它跟著取消。
- 按下「清除已完成」後,它的勾選狀態被清除。(Mark all as complete)

#### FR-TODO-05 顯示移除按鈕
- 每個 todo 在懸停時顯示移除按鈕(規格標為 `.destroy`)。
- 滑鼠移到某一項上 → 該項的移除按鈕出現。(Item, 3)

#### FR-TODO-06 編輯 todo
- 編輯模式會隱藏該項的其他控制項,顯示一個含原標題的輸入框。
- 雙擊某一項的標題 → 進入編輯模式,輸入框取得焦點並帶有原標題。
- 修改後按 Enter 或讓輸入框失焦 → 標題更新,離開編輯模式。
- 清空輸入框後按 Enter 或失焦 → 該項目被刪除。
- 編輯中按 Escape → 放棄修改,離開編輯模式。(Item, 2 + Editing)

#### FR-TODO-07 未完成計數
- Footer 顯示未完成 todo 的數量,`item` 依數量單複數。
- 未完成數量為 0 / 1 / 2 時 → footer 顯示 `0 items` / `1 item` / `2 items`;新增、勾選或取消
  勾選時數字隨之更新。(Counter)

#### FR-TODO-08 清除已完成
- Footer 有一個「清除已完成」按鈕。
- 有已完成項目時按下它 → 所有已完成項目從清單移除。
- 沒有已完成項目時 → 該按鈕隱藏。(Clear completed button)

#### FR-TODO-09 重新載入後保留
- todo 存放在瀏覽器的 `localStorage`;編輯模式不持久化。
- 新增、勾選或編輯 todo 後重新載入頁面 → 清單內容與完成狀態與重新載入前一致,且沒有任何項目
  處於編輯模式。(Persistence)

#### FR-TODO-10 篩選路由
- 三個路由:`#/`(全部,預設)、`#/active`、`#/completed`;footer 有對應的篩選連結。
- 開啟 `#/active` → 只顯示未完成項目,且 `Active` 連結為選取狀態;開啟 `#/completed` → 只顯示
  已完成項目。
- 在篩選狀態下把某一項改成不符合當前篩選 → 該項立即從清單消失。
- 重新載入後 → 仍停在同一個篩選。(Routing)

## 5. 關鍵流程

```text
開啟 app
  │
  ├─ 沒有 todo ──► 主列表與 footer 隱藏
  │
  └─ 有 todo ──► 新增 / 勾選 / 編輯 / 刪除
                    │
                    ▼
              篩選(All / Active / Completed)
                    │
                    ▼
              重新載入 ──► 內容與篩選保留
```

## 6. 訊息文案清單(Verbatim)

| 情境 | 文案 |
|---|---|
| 未完成計數,0 | `0 items` |
| 未完成計數,1 | `1 item` |
| 未完成計數,2 | `2 items` |
| 篩選連結 | `All`、`Active`、`Completed` |

> 規格原文的計數範例是 `**2** items left`;`<strong>` 是 markup,`left` 屬文案。本 PRD 只收
> 文案部分。

## 7. 資料模型(規格明寫的部分)

| 實體 | 欄位 |
|---|---|
| Todo | `id`、`title`、`completed` |

- 儲存位置:`localStorage`,key 格式 `todos-[framework]`(實作細節,不列為需求)。

## 8. 非功能需求

規格的「Template Application」「Structure」「Directory Structure」「Code」段落是給實作者的
要求(目錄結構、npm、code style、瀏覽器支援),不是使用者可見行為,因此不列為需求。

## 9. 追溯矩陣

| 規格段落 | 對應 requirement |
|---|---|
| No todos | `FR-TODO-01` |
| New todo | `FR-TODO-02` |
| Item(1)checkbox 勾選 | `FR-TODO-03` |
| Mark all as complete | `FR-TODO-04` |
| Item(3)懸停移除按鈕 | `FR-TODO-05` |
| Item(2)雙擊 + Editing | `FR-TODO-06` |
| Counter | `FR-TODO-07` |
| Clear completed button | `FR-TODO-08` |
| Persistence | `FR-TODO-09` |
| Routing | `FR-TODO-10` |

## 10. 抽取時丟掉的東西

| 被丟掉的 | 原因 |
|---|---|
| class 名稱(`completed`、`editing`、`selected`、`.destroy`)與 `#main` / `#footer` 之外的 id | 實作細節;只有辨識元件時寫進正文,不當斷言值 |
| `localStorage` key 格式 `todos-[framework]` | 實作細節 |
| 計數的 `<strong>` 包裝 | markup |
| 目錄結構、`package.json`、npm、`.gitignore`、code style、瀏覽器支援 | 實作要求 |
| 「apps should look and behave exactly like the template」 | 對範例實作者的比較要求,不是使用者行為 |
| `autofocus` attribute | 規格建議的實作方式;保留「載入時取得焦點」這個可觀察結果 |

## 11. 未定義事項

| # | 項目 | 說明 |
|---|---|---|
| 1 | 點擊移除按鈕的結果 | 規格只寫「懸停時顯示移除按鈕」,沒寫點擊後的行為 |
| 2 | 移開滑鼠後移除按鈕是否隱藏 | 規格未寫 |
| 3 | 重複標題 | 規格只處理 trim 後為空,未提是否允許重複 |
| 4 | 空清單時「全部標記完成」是否顯示 | 空狀態只寫主列表與 footer 隱藏 |
| 5 | 計數是否只算目前篩選可見的項目 | 規格寫「active todos」,未提篩選 |
| 6 | 篩選狀態下新增項目的顯示時機 | 規格只寫「更新時要依篩選處理」 |
| 7 | 多分頁同時開啟時的同步 | `localStorage` 寫入的跨分頁行為未寫 |
| 8 | 瀏覽器上一頁 / 下一頁與 hash 路由的互動 | 規格未寫 |
| 9 | 刪除後 id 是否重用、清單排序 | 規格未寫 |
