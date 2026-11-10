# PRD:TodoMVC(designer eval 的第二份 PRD)

> **版本**:v0.7(2026-11-10)
> **性質**:由公開規格**與其參考實作**抽取,不是反推自 live 站,也不是本專案撰寫
> **來源**:
> - 規格:[`tastejs/todomvc` 的 `app-spec.md`](https://github.com/tastejs/todomvc/blob/master/app-spec.md) @ `d040877fd8895c4f18fa5190e4b8ee474ffa8ac4`
> - 參考實作:`todomvc-app-template` 的 `index.html`、`todomvc-app-css` 的 `index.css`
> **live**:https://demo.playwright.dev/todomvc/
> **用途**:held-out PRD,用來驗證 judge 的判準在另一份規格、另一種顆粒度上是否成立。不進
> production 管線(`prd/` 底下新增檔案會觸發 `plan.yml`)。
> **v0.2 調整**:依「分支 = 獨立旅程」重切,10 → 21 條。v0.1 把同一段旅程的替代路徑(例如編輯
> 的儲存 / 清空 / 取消)併成一條,設計師只好自己拆。requirement 不再使用 HTML id 當主詞。
> **v0.3 調整**:review 後的四個修正——全選補上「再取消勾選」;進入編輯模式明寫隱藏的是
> checkbox 與移除按鈕;Enter 與失焦各自一條 requirement;篩選改用 footer 的連結當動作,hash
> 留作背景。
> **v0.4 調整**:計數文案補回 `left`。v0.3 把規格 example 裡的 `left` 誤判成範例的一部分,
> 但它是渲染文字的一部分;`FR-TODO-14` 與 §6 已同步。
> **v0.5 調整**:把 §11 中可由參考實作確定的行為寫進 requirement:移開滑鼠後按鈕隱藏、空清單
> 時全選一起隱藏、計數不受篩選影響、篩選下新增的顯示、上一頁 / 下一頁切換篩選、編輯中重新載入
> 丟棄未儲存修改、已完成樣式(刪除線 + 灰字)。新增三條 requirement(移除 todo、篩選下新增、
> 上一頁 / 下一頁),需求由 22 增至 25;§11 改為「非目標與未支援」。標頭性質改為「規格 + 參考
> 實作」。
> **v0.6 調整**:修正 §11 第 2 條。v0.5 寫「不規定,排序為新增順序」——先說不規定又給了順序,
> 而 `FR-TODO-03` 已經定義新增在最後。現在只留「id 重用不規定」,順序正式由 `FR-TODO-03`
> 與本條定義。
> **v0.7 調整**:依「一條 requirement = 一條被測邏輯」拆出兩條。`FR-03` 只保留「新增」,
> 「允許重複標題」成為 `FR-26`;`FR-17` 只保留「重新載入後保留」,「未儲存的編輯被丟棄」
> 成為 `FR-27`。需求由 25 增至 27。
> **抽取規則**:
> 1. 只收使用者可見的結果;實作細節(CSS class、HTML id、`localStorage` key、`<strong>` 包裝)
>    不進 requirement。
> 2. 一個 requirement = **一條被測邏輯**。同一條邏輯的不同方向、不同輸入放進 steps;不同的
>    驗證規則或不同的行為規則各自一條 requirement(例如「新增」與「允許重複標題」是兩條)。
>    不使用 AC 標號。
> 3. 能用規格原句就用原句,不改寫成我們的語氣。
> 4. 規格與參考實作都沒寫的行為,列為第 11 章的非目標,不自行發明。
> 5. 被丟掉的東西列在第 10 章,讓切法可被檢查。
> 6. 新增 requirement 一律附加編號,不重排既有編號。

## 1. 產品概述

一個單頁的 todo 清單 app:新增、勾選完成、編輯(清空即刪)、移除、依狀態篩選,並在重新載入後
保留內容與篩選。規格本身是「如何實作一個一致的 TodoMVC 範例」,本 PRD 只取其中對使用者可見的
行為。

## 2. 使用者角色

| 角色 | 說明 |
|---|---|
| 使用者 | 唯一的角色。沒有登入、沒有多使用者、沒有權限。 |

## 3. 資訊架構

### 3.1 頁面與元件

| 元件 | 內容 |
|---|---|
| 新增輸入框 | 位於 app 頂部;載入時應取得焦點 |
| 清單區 | 全部 todo;頂端有「全部標記完成」checkbox |
| 單一 todo | checkbox、標題、懸停時顯示的移除按鈕;雙擊標題進入編輯 |
| Footer | 未完成計數、篩選連結(All / Active / Completed)、「清除已完成」按鈕 |

> 規格的 HTML id(`#main`、`#footer`)與 class(`.destroy` 等)只當定位線索,不是斷言值。

### 3.2 狀態

- 清單為空:清單區(含「全部標記完成」)、計數與篩選連結都看不到。
- 篩選:footer 的 `All`、`Active`、`Completed` 連結,對應 `#/`、`#/active`、`#/completed`。

## 4. 功能需求

> 編號 `FR-<模組>-<序號>`;一個 requirement 就是一段旅程:起始狀態、動作、可觀察的結果。
> 括號內是規格或參考實作的對應來源。

### 4.1 清單 (TODO)

#### FR-TODO-01 空狀態
- 開啟 app 且沒有任何 todo → 清單、未完成計數、篩選連結與清單頂端的「全部標記完成」都看不到。
  (No todos + template 的 `.main` 結構)

#### FR-TODO-02 載入時輸入框有焦點
- 開啟 app → 新增 todo 的輸入框已取得焦點,可直接輸入。(New todo)

#### FR-TODO-03 新增 todo
- 在新增輸入框輸入文字後按 Enter → 該文字成為清單最後一項,輸入框清空。(New todo)

#### FR-TODO-04 空白不成案
- 在新增輸入框只輸入空白後按 Enter → 清單不變,不建立新項目。(New todo)

#### FR-TODO-05 勾選完成
- 點某一項 todo 的 checkbox → 該項被標記為完成,標題顯示刪除線且文字轉為灰色。
  (Item, 1 + template 的 CSS)

#### FR-TODO-06 全部標記完成
- 勾選清單頂端的「全部標記完成」→ 所有 todo 變成已完成;再取消勾選 → 所有 todo 回到未完成。
  (Mark all as complete)

#### FR-TODO-07 全選反映單項狀態
- 所有 todo 都被勾選時 → 「全部標記完成」checkbox 自動變為勾選;任一項被取消勾選時 → 它跟著
  取消。(Mark all as complete)

#### FR-TODO-08 懸停顯示移除按鈕
- 滑鼠移到某一項 todo 上 → 該項的移除按鈕出現;移開 → 按鈕再次隱藏。
  (Item, 3 + template 的 CSS)

#### FR-TODO-09 進入編輯模式
- 雙擊某一項 todo 的標題 → 進入編輯模式:該項的 checkbox 與移除按鈕隱藏,顯示含原標題且已
  取得焦點的輸入框。(Item, 2 + Editing)

#### FR-TODO-10 按 Enter 儲存編輯
- 在編輯模式修改標題後按 Enter → 標題更新,離開編輯模式。(Editing)

#### FR-TODO-11 失焦儲存編輯
- 在編輯模式修改標題後讓輸入框失焦 → 標題更新,離開編輯模式。(Editing)

#### FR-TODO-12 清空標題即刪除
- 在編輯模式把標題清空後按 Enter 或讓輸入框失焦 → 該項 todo 被刪除。(Editing)

#### FR-TODO-13 取消編輯
- 在編輯模式按 Escape → 放棄修改,標題保持原值,離開編輯模式。(Editing)

#### FR-TODO-14 未完成計數
- Footer 顯示未完成 todo 的數量:0 / 1 / 2 個未完成時 → `0 items left` / `1 item left` /
  `2 items left`;新增、勾選或取消勾選後 → 數字隨之更新。
- 數字永遠是全部未完成的數量,不隨目前篩選改變。(Counter)

#### FR-TODO-15 清除已完成
- 有已完成項目時按下「清除已完成」→ 所有已完成項目從清單移除,「全部標記完成」的勾選狀態被
  清除。(Clear completed button + Mark all as complete)

#### FR-TODO-16 沒有已完成時隱藏清除按鈕
- 沒有已完成項目時 → 「清除已完成」按鈕隱藏。(Clear completed button)

#### FR-TODO-17 重新載入後保留
- 新增、勾選或編輯 todo 後重新載入頁面 → 清單內容與完成狀態與重新載入前一致,且沒有任何項目
  處於編輯模式。(Persistence)

#### FR-TODO-18 預設篩選顯示全部
- 開啟 app(預設 `#/`)→ 顯示所有 todo,footer 的 `All` 連結為選取狀態;點 `All` 連結 →
  同樣顯示所有 todo。(Routing)

#### FR-TODO-19 篩選未完成
- 點 footer 的 `Active` 連結 → 只顯示未完成項目,且 `Active` 連結為選取狀態。(Routing)

#### FR-TODO-20 篩選已完成
- 點 footer 的 `Completed` 連結 → 只顯示已完成項目,且 `Completed` 連結為選取狀態。(Routing)

#### FR-TODO-21 篩選中改動立即反映
- 在 `Active` 篩選下把某一項勾選完成 → 該項立即從清單消失;在 `Completed` 篩選下把某一項取消
  勾選 → 該項立即從清單消失。(Routing)

#### FR-TODO-22 重新載入後保留篩選
- 停在 `Active` 或 `Completed` 篩選時重新載入頁面 → 仍停在該篩選,該連結仍為選取狀態,清單仍
  依它顯示。(Routing)

#### FR-TODO-23 移除 todo
- 點某一項 todo 的移除按鈕 → 該項從清單移除,其他項目保留。
  (Item, 3 的 `destroy` 按鈕;規格未寫點擊後的行為,由按鈕名稱與 class 推得)

#### FR-TODO-24 篩選下新增 todo
- 在 `Active` 篩選下新增 todo → 新項目立即出現在清單。
- 在 `Completed` 篩選下新增 todo → 新項目不出現在清單,直到切換到 `All` 或 `Active`。
  (Routing:清單以 model 層級的篩選產生)

#### FR-TODO-25 上一頁 / 下一頁切換篩選
- 依序開啟 `#/active`、`#/completed` 後按瀏覽器上一頁 → 回到 `Active` 篩選,清單與選取狀態
  跟著改變;按下一頁 → 回到 `Completed` 篩選。(Routing:路由改變時重新篩選)

#### FR-TODO-26 建立重複名稱的 todo
- 以與既有 todo 相同的標題新增 → 新項目照樣建立,兩項各自獨立(各有自己的 checkbox),
  不被拒絕、也不合併。
  (非 spec 明文;由「spec 沒有唯一性要求」推得,與 `FR-TODO-23` 同類)

#### FR-TODO-27 未儲存的編輯在重新載入後丟棄
- 在編輯模式修改標題,但尚未按 Enter 或失焦就重新載入頁面 → 標題維持原值,未儲存的修改
  被丟棄。(Editing「只在 Enter 或失焦時儲存」+ Persistence)

## 5. 關鍵流程

```text
開啟 app
  │
  ├─ 沒有 todo ──► 清單(含全選)、計數、篩選都看不到
  │
  └─ 有 todo ──► 新增 / 勾選 / 編輯 / 移除
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
| 未完成計數,0 | `0 items left` |
| 未完成計數,1 | `1 item left` |
| 未完成計數,2 | `2 items left` |
| 篩選連結 | `All`、`Active`、`Completed` |

> 規格原文的計數範例是 `**2** items left`;`<strong>` 是 markup,`left` 屬文案的一部分。
> 完整字串是 `0 items left`、`1 item left`、`2 items left`。

## 7. 資料模型(規格明寫的部分)

| 實體 | 欄位 |
|---|---|
| Todo | `id`、`title`、`completed` |

- 儲存位置:`localStorage`,key 格式 `todos-[framework]`(實作細節,不列為需求)。

## 8. 非功能需求

規格的「Template Application」「Structure」「Directory Structure」「Code」段落是給實作者的
要求(目錄結構、npm、code style、瀏覽器支援),不是使用者可見行為,因此不列為需求。

## 9. 追溯矩陣

| 規格 / 參考實作 | 對應 requirement |
|---|---|
| No todos + `.main` 結構 | `FR-TODO-01` |
| New todo | `FR-TODO-02`、`FR-TODO-03`、`FR-TODO-04` |
| 非 spec 明文;新增的驗證規則(重複標題) | `FR-TODO-26` |
| Item(1)checkbox 勾選 + CSS 完成樣式 | `FR-TODO-05` |
| Mark all as complete | `FR-TODO-06`、`FR-TODO-07`、`FR-TODO-15` |
| Item(3)懸停 + CSS hover | `FR-TODO-08`、`FR-TODO-23` |
| Item(2)雙擊 + Editing | `FR-TODO-09`、`FR-TODO-10`、`FR-TODO-11`、`FR-TODO-12`、`FR-TODO-13` |
| Counter | `FR-TODO-14` |
| Clear completed button | `FR-TODO-15`、`FR-TODO-16` |
| Persistence | `FR-TODO-17` |
| Persistence + Editing(只在 Enter / 失焦提交) | `FR-TODO-27` |
| Routing | `FR-TODO-18`、`FR-TODO-19`、`FR-TODO-20`、`FR-TODO-21`、`FR-TODO-22`、`FR-TODO-24`、`FR-TODO-25` |

> `FR-TODO-23` 的點擊行為在 `app-spec.md` 沒有明文;按鈕名為「remove」、class 為 `destroy`,
> 且 template 的 `index.html` 有該按鈕,故寫成「點擊即移除」。這是本 PRD 唯一的推論,標在這裡。

## 10. 抽取時丟掉的東西

| 被丟掉的 | 原因 |
|---|---|
| class 名稱(`completed`、`editing`、`selected`、`.destroy`)與 HTML id(`#main`、`#footer`) | 實作細節;只在 §3 當定位線索,不進 requirement、不當斷言值 |
| CSS selector 本身(`li:hover .destroy`、`li.completed label`) | 只取行為(懸停顯示、刪除線 + 灰字),不寫 selector |
| `localStorage` key 格式 `todos-[framework]` | 實作細節 |
| 計數的 `<strong>` 包裝 | markup |
| 目錄結構、`package.json`、npm、`.gitignore`、code style、瀏覽器支援 | 實作要求 |
| 「apps should look and behave exactly like the template」 | 對範例實作者的比較要求,不是使用者行為 |
| `autofocus` attribute | 規格建議的實作方式;保留「載入時取得焦點」這個可觀察結果 |

### 10.1 v0.1 → v0.2 的切法修正

| v0.1 | v0.2 | 理由 |
|---|---|---|
| `FR-TODO-01` 用「`#main` / `#footer` 承載…」當主詞 | 拿掉那行,改成可觀察的「都看不到」 | id 是實作細節;「承載」不是結果 |
| `FR-TODO-06` 編輯 = 進入 + 儲存 + 清空刪除 + 取消 | 拆成進入 / 儲存 / 刪除 / 取消 | 從共用狀態分岔的四條路徑 |
| `FR-TODO-02` 新增 = 焦點 + 新增 + 空白 | 拆成焦點 / 新增 / 空白 | 焦點是獨立旅程;空白是新增的失敗分支 |
| `FR-TODO-04` 全選 = 設定 + 反映 + 清除後重置 | 拆成設定 / 反映;重置併入「清除已完成」 | 動作不同;重置是「清除」這個動作的結果 |
| `FR-TODO-07` 計數 = 顯示 + 更新 + 0 items | 留一條 | 同一個顯示在不同狀態,不是新旅程 |
| `FR-TODO-08` 清除 = 移除 + 隱藏 | 拆成動作 / 狀態顯示 | 動作 vs 狀態 |
| `FR-TODO-09` 保留 = 內容 + 編輯狀態 | 留一條 | 同一個動作(重新載入)的兩個結果 |
| `FR-TODO-10` 路由 = active + completed + 更新 + 篩選保留 | 拆成五條並補上預設篩選 | 每一條是不同的動作 |

### 10.2 v0.2 → v0.3 的 review 修正

| v0.2 | v0.3 | 理由 |
|---|---|---|
| 全選只寫「勾選」 | 補「再取消勾選 → 全部回到未完成」 | 規格原文是 toggles |
| 進入編輯只寫「其他控制項」 | 明寫 checkbox 與移除按鈕 | 具體清單取自 template |
| 儲存編輯把 Enter 與失焦放在同一條 | 拆成 `FR-TODO-10`(Enter)與 `FR-TODO-11`(失焦) | 兩個觸發各自一段旅程 |
| 清空即刪保留「Enter 或失焦」 | 不動 | 規格只說空標題則 destroy,未拆觸發 |
| 路由用 hash 當動作 | 改用 footer 的 `All` / `Active` / `Completed` 連結;hash 留作背景 | 使用者點的是連結 |

## 11. 非目標與未支援

| # | 項目 | 決定 |
|---|---|---|
| 1 | 多分頁同步 | 不要求;跨分頁不即時同步,重新載入才反映 |
| 2 | id 重用 | 不規定,由實作決定。清單順序為新增順序:新增項目位於最後(見 `FR-TODO-03`),移除或編輯不改變其他項目的相對順序 |
| 3 | 標題長度上限 | 不設上限 |
| 4 | 觸控裝置 | 不支援;移除按鈕僅以滑鼠懸停觸發 |
