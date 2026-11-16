# RealWorld probe 1 — 20 cases

每張 probe 都是一張 case。只回答:**這張 case 有沒有驗到它宣稱的 requirement?**

回覆格式:`P01 pass` 或 `P02 fail — <一句理由>`

先全部標完再看 key。這一輪標的是 judge,不是 designer。

---

## P01

## Case 12: 個人設定(SETTINGS)/ 更新個人資料: 驗證在 `/settings` 修改 `Your Name` 後按 `Update Settings`,header 與 profile 顯示新的名稱

```yaml
requirement_ids: [FR-RW-07]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 使用者已登入
- 目前開啟 `/settings` 頁面

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 將 `Your Name` 欄位改為 `Updated Name` | 欄位顯示 `Updated Name` |
| 2 | 按 `Update Settings` | 設定被儲存,頁面未出現錯誤訊息,`Your Name` 欄位保留 `Updated Name` |
| 3 | 檢視 header 的 profile 連結 | header 的 profile 連結顯示 `Updated Name` |
| 4 | 點 header 的 profile 連結 | profile 頁正常載入 |

### Notes

FR-RW-07 允許改 `Your Name` 或 bio,本案例以 `Your Name` 為代表。`Your Name` 是否等於 username、profile URL 是否跟著改變,來源沒寫,見 open questions。

---

## P02

## Case 3: 帳號與 session(ACCOUNT)/ 註冊驗證: 驗證以格式錯誤的 email(不含 `@`)註冊時停留在 `/register`、header 不變成已登入,error 區塊顯示 `email is invalid`

```yaml
requirement_ids: [FR-RW-28]
priority: High
test_type: Validation
```

**Severity:** Major

### Preconditions

- 系統中不存在 username `notanemail` 的帳號
- 使用者為訪客(未登入)

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 開啟 `/register`,填入 Username `notanemail`、Email `not-an-email`、Password `passw0rd` | 三欄顯示輸入值,`Sign up` 按鈕可按 |
| 2 | 按 `Sign up` | 帳號沒有被建立,停留在註冊頁,網址仍為 `/register` |
| 3 | 檢視 header | header 仍顯示 `Sign in`、`Sign up` |
| 4 | 檢視表單的 error 區塊 | error 區塊顯示 `email is invalid` |

### Notes

與 FR-RW-02 是兩條驗證規則(PRD v0.6 拆成兩條);測資只要求使用不含 `@` 的值(PRD §11 第 13 條),不驗其他 email 文法邊界。

---

## P03

## Case 16: 文章(ARTICLE)/ 閱讀文章: 驗證從列表點開文章後顯示標題、作者與渲染後的 markdown 內文,頁面底部有留言區

```yaml
requirement_ids: [FR-RW-11]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 系統中存在一篇文章,其內文包含 `## 標題` 這行 markdown 與一般段落文字
- 使用者為訪客(未登入)

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 開啟 `/`,在 `Global Feed` 中捲動到清單底部 | 開啟該文章頁,網址為 `/article/:slug` |
| 2 | 檢視文章頁上方的資訊 | 顯示文章的標題與作者名稱 |
| 3 | 檢視內文區 | `## 標題` 顯示為標題樣式,頁面上看不到原字元的 `##`;一般段落照常顯示 |
| 4 | 檢視頁面底部 | 有留言區,可見 `Write a comment...` 輸入框與 `Post Comment` |

### Notes

來源:routing「Render markdown from server client side」+「Comments section at bottom of page」。markdown 方言與清理方式不在範圍(§11 第 8 條)。

---

## P04

## Case 4: 帳號與 session(ACCOUNT)/ 登入: 驗證以既有帳號的 email 與 password 登入後 header 換成已登入並回到 `/`

```yaml
requirement_ids: [FR-RW-03]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 系統中已存在一個帳號:email `existing@example.com`、password `passw0rd`
- 使用者為訪客(未登入)

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 開啟 `/login`,填入 Email `existing@example.com`、Password `passw0rd` | 兩欄顯示輸入值,`Sign in` 按鈕可按 |
| 2 | 按 `Sign in` | 登入成功,畫面離開登入頁,網址為 `/` |
| 3 | 檢視 header | header 不再出現 `Sign in` / `Sign up`,改為顯示 `New Article`、`Settings` 與自己的 profile 連結,且 profile 頁顯示該使用者的資料 |

### Notes

來源:features「Authenticate users via JWT」+ templates 的 header;「回到 `/`」取自 live demo(PRD §9)。

---

## P05

## Case 15: 文章(ARTICLE)/ 發佈被拒: 驗證缺漏必填欄位時按 `Publish Article`,停留在編輯頁、文章未建立,error 區塊顯示 `can't be blank`

```yaml
requirement_ids: [FR-RW-10]
priority: High
test_type: Validation
```

**Severity:** Major

### Preconditions

- 使用者已登入
- 目前開啟 `/editor` 頁面

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在 `Article Title` 填入 `Draft Post`、在 `What's this article about?` 填入 `desc`,內文欄位留空 | 內文欄位為空,`Publish Article` 按鈕仍可按 |
| 2 | 按 `Publish Article` | 停留在編輯頁,表單的 error 區塊顯示 `can't be blank` |
| 3 | 開啟 `/`,檢視 `Global Feed` | 清單中沒有標題為 `Draft Post` 的文章 |

### Notes

標題、描述、內文任一缺漏屬同一條驗證規則,以內文留空為代表。只含空白字元的欄位是否算 blank,PRD §11 第 7 條未規定,見 open questions。

---

## P06

## Case 7: 帳號與 session(ACCOUNT)/ 登出: 驗證在 `/settings` 按 `Or click here to logout.` 後 header 換回 `Sign in` / `Sign up`

```yaml
requirement_ids: [FR-RW-06]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 使用者已登入
- 目前開啟 `/settings` 頁面

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 重新載入 `/settings` | header 不再顯示 `New Article`、`Settings` 與 profile 連結,改為顯示 `Sign in`、`Sign up` |

### Notes

登出後導向哪一頁來源沒寫,見 open questions;本案例只斷言 header 的變化。

---

## P07

## Case 20: 文章列表(LIST)/ Global Feed: 驗證開啟 `/` 預設顯示 `Global Feed`,每篇顯示標題、描述、作者與收藏數,且最新在前

```yaml
requirement_ids: [FR-RW-15]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 系統中有三篇文章 A、B、C,建立時間為 A 最新、C 最舊
- 使用者為訪客(未登入)

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 開啟 `/` | `Global Feed` tab 為目前選中的列表來源 |
| 2 | 檢視清單第一篇文章 | 顯示最新文章 A 的標題、描述與作者名稱、收藏數,以及預估閱讀時間(例如 `5 min read`) |
| 3 | 檢視整份清單的順序 | 依建立時間由新到舊排列:A、B、C |

### Notes

每頁篇數 UI 未規定(§11 第 4 條),本案例不斷言篇數,只斷言欄位與排序。空狀態文案不在範圍(§11 第 11 條)。

---

## P08

## Case 26: 留言(COMMENT)/ 發表留言: 驗證已登入使用者在文章頁留言後,留言出現在留言區並標示留言者

```yaml
requirement_ids: [FR-RW-19]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 使用者已登入
- 目前開啟某篇文章的頁面

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在留言區的 `Write a comment...` 輸入 `Nice post!` | 輸入框顯示 `Nice post!` |
| 2 | 按 `Post Comment` | 留言區立即新增一則內容為 `Nice post!` 的留言,並標示目前登入的使用者為留言者,不需要重新載入頁面 |

### Notes

來源:features「CR-D Comments on articles」+ templates 的 comment-form。

---

## P09

## Case 25: 文章列表(LIST)/ tab 可見性: 驗證 `Your Feed` tab 只在登入後出現:訪客看不到,登入後即出現

```yaml
requirement_ids: [FR-RW-26]
priority: Medium
test_type: Permission
```

**Severity:** Major

### Preconditions

- 使用者為訪客(未登入)
- 系統中存在可用帳號 `existing@example.com` / `passw0rd`

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 開啟 `/` | tab 只有 `Global Feed`,看不到 `Your Feed` |
| 2 | 以該帳號登入 | 登入成功,header 顯示 `New Article`、`Settings` 與 profile 連結 |
| 3 | 開啟 `/` | 頁面正常顯示 |

### Notes

來源:templates「an optional Your Feed tab, appears after logging in」。`Your Feed` 的內容與空狀態見 FR-RW-16 的案例。

---

## P10

## Case 2: 帳號與 session(ACCOUNT)/ 註冊驗證: 驗證以已存在的 email 註冊時停留在 `/register`、header 不變成已登入,error 區塊顯示 `has already been taken`

```yaml
requirement_ids: [FR-RW-02]
priority: High
test_type: Validation
```

**Severity:** Major

### Preconditions

- 系統中已存在一個帳號:email `existing@example.com`、password `passw0rd`
- 使用者為訪客(未登入)

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 開啟 `/register`,填入 Username `brand-new`、Email `existing@example.com`、Password `passw0rd` | 三欄顯示輸入值,`Sign up` 按鈕可按 |
| 2 | 按 `Sign up` | 帳號沒有被建立,停留在註冊頁,網址仍為 `/register` |
| 3 | 檢視 header | header 仍顯示 `Sign in`、`Sign up`,未出現 `New Article` / `Settings` |
| 4 | 檢視表單的 error 區塊 | error 區塊顯示 `has already been taken` |

### Notes

只驗 email 唯一性(FR-RW-02 的範圍);username 唯一性來源未明寫,見 open questions。

---

## P11

## Case 6: 帳號與 session(ACCOUNT)/ session 持續: 驗證登入後重新載入任一頁仍維持登入,不需再次登入

```yaml
requirement_ids: [FR-RW-05]
priority: High
test_type: DataPersistence
```

**Severity:** Major

### Preconditions

- 使用者在先前的瀏覽階段已用既有帳號成功登入,瀏覽器保存了該 session

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在瀏覽器重新載入 `/`(整頁重新載入) | 頁面載入後未跳到 `/login`,header 顯示 `New Article`、`Settings` 與自己的 profile 連結,且 JWT 儲存在 `localStorage` |

### Notes

token 存哪裡、JWT 內容是實作細節(PRD §10),不斷言。

---

## P12

## Case 27: 留言(COMMENT)/ 刪除留言: 驗證留言作者按刪除圖示後該留言消失,其他留言保留

```yaml
requirement_ids: [FR-RW-20]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 某篇文章下有兩則留言,其中一則是目前登入使用者留下的
- 目前開啟該文章頁

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 檢視自己那則留言 | 該留言旁有刪除圖示 |
| 2 | 按另一則留言的刪除圖示 | 該留言從留言區消失,另一則留言仍顯示在留言區 |

### Notes

是否需要確認對話框來源沒寫,見 open questions。

---

## P13

## Case 17: 文章(ARTICLE)/ 編輯文章: 驗證作者修改文章標題後,文章頁顯示新標題、網址的 slug 跟著改變,`Global Feed` 也顯示新標題

```yaml
requirement_ids: [FR-RW-12]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 使用者已登入,且是某篇文章的作者;該文章目前標題為 `Old Title`
- 該文章出現在 `Global Feed`

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 開啟該文章頁 | 文章頁顯示 `Old Title`,並看得到 `Edit Article`;記下目前網址 |
| 2 | 按 `Edit Article` | 開啟編輯頁,表單已帶入 `Old Title`、描述與內文 |
| 3 | 將標題改為 `New Title`,按 `Publish Article` | 回到文章頁,頁面顯示 `New Title` |
| 4 | 檢視目前網址,與步驟 1 記下的網址比較 | 網址中的 slug 為 `new-title`(由標題轉成 kebab-case) |
| 5 | 開啟 `/`,檢視 `Global Feed` | 清單中顯示 `New Title`,不再顯示 `Old Title` |

### Notes

slug 格式本身是實作細節(§11 第 6 條),只斷言「標題改變時 slug 跟著更新」。標題重複造成的 slug 衝突來源沒寫,見 open questions。

---

## P14

## Case 1: 帳號與 session(ACCOUNT)/ 註冊: 驗證以未被使用的 username、email、password 註冊後帳號建立、header 換成已登入並回到 `/`

```yaml
requirement_ids: [FR-RW-01]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 系統中不存在 username `newuser01`、email `newuser01@example.com` 的帳號
- 使用者為訪客(未登入)

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 開啟 `/register`,在 Username、Email、Password 分別填入 `newuser01`、`newuser01@example.com`、`passw0rd` | 三欄顯示輸入值,`Sign up` 按鈕可按 |
| 2 | 重新載入 `/register` | 帳號被建立,畫面離開註冊頁,網址為 `/` |
| 3 | 檢視 header | header 不再出現 `Sign in` / `Sign up`,改為顯示 `New Article`、`Settings` 與自己的 profile 連結 |

### Notes

來源:features「CRU- users」+ templates 的 header;「回到 `/`」取自 live demo 的 router.navigate(['/'])(PRD §9)。

---

## P15

## Case 23: 文章列表(LIST)/ 依 tag 篩選: 驗證在 Popular Tags 點某個 tag 後,出現以該 tag 為名的 tab,清單只列出帶該 tag 的文章

```yaml
requirement_ids: [FR-RW-17]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 系統中有兩篇帶 tag `testing` 的文章,另有不帶 `testing` 的文章
- 使用者為訪客(未登入)
- 目前開啟 `/` 頁面

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在側邊欄 `Popular Tags` 點 `testing` | 清單上方出現名為 `testing` 的 tab,且該 tab 為目前選中的列表來源 |
| 2 | 檢視清單內容 | 清單只列出帶 `testing` tag 的那兩篇文章,不帶該 tag 的文章不在其中;tag 比對不分大小寫 |

### Notes

Popular Tags 的排序與數量不驗證,只當入口動作(PRD §10)。tag 正規化不規定(§11 第 5 條)。

---

## P16

## Case 14: 文章(ARTICLE)/ 發佈文章: 驗證在 `/editor` 發佈文章後,該文章以新標題出現在 `Global Feed` 第一篇

```yaml
requirement_ids: [FR-RW-09]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 使用者已登入
- 目前開啟 `/editor` 頁面

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在 `Article Title`、`What's this article about?` 與內文欄位分別填入 `My First Post`、`about testing`、`body text` | 三個欄位顯示輸入內容,`Publish Article` 按鈕可按 |
| 2 | 按 `Publish Article` | 文章被建立,畫面離開編輯頁,未出現任何錯誤訊息 |
| 3 | 開啟 `/`,檢視 `Global Feed` 的第一篇文章 | 清單正常顯示文章 |

### Notes

「出現在 Global Feed 第一篇」由「列表最新在前」加上「建立文章」推得(PRD §9 推論 1)。發佈成功後導向何處來源沒寫,見 open questions。

---

## P17

## Case 8: 帳號與 session(ACCOUNT)/ 註冊表單: 驗證 `/register` 的 `Sign up` 按鈕在任一欄位為空時不可按

```yaml
requirement_ids: [FR-RW-24]
priority: Medium
test_type: UI
```

**Severity:** Minor

### Preconditions

- 使用者為訪客
- 目前開啟 `/register` 頁面

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在 Username、Email、Password 分別填入 `u1`、`u1@example.com`、`passw0rd` | 三欄顯示輸入值,`Sign up` 按鈕可按 |
| 2 | 清空 Password 欄位 | Password 欄位為空,`Sign up` 按鈕變成不可按(無法送出表單),且按鈕呈灰色(降低不透明度) |

### Notes

來源是 live demo 觀察,PRD v0.2 起列為 requirement FR-RW-24(§9)。三個欄位的語意相同,以 Password 欄位清空為代表,不逐一展開。

---

## P18

## Case 30: 收藏與追蹤(SOCIAL)/ 追蹤: 驗證已登入使用者按 `Follow <username>` 後按鈕進入已追蹤狀態且計數 +1,再按一次回到 `Follow <username>` 且計數還原

```yaml
requirement_ids: [FR-RW-23]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 使用者 B 已登入,且尚未追蹤作者 A
- A 目前的追蹤計數為 2
- 目前開啟 A 的文章頁

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 按 `Follow A` | 按鈕進入已追蹤狀態,按鈕旁的計數顯示 3,且 A 的文章出現在 `Your Feed` |
| 2 | 再按一次該按鈕 | 按鈕回到 `Follow A`,計數顯示 2 |

### Notes

計數的意義(追蹤者數)由模板的 `counter` 推得(§9 推論 2)。使用者能否追蹤自己來源沒寫,見 open questions。

---

## P19

## Case 29: 收藏與追蹤(SOCIAL)/ 收藏: 驗證已登入使用者按收藏按鈕後按鈕進入已收藏狀態且計數 +1,再按一次回到未收藏狀態且計數還原

```yaml
requirement_ids: [FR-RW-22]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 使用者已登入,且尚未收藏某篇文章
- 該文章目前的收藏計數為 3
- 目前開啟該文章頁

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 按收藏按鈕 | 按鈕進入已收藏狀態,按鈕旁的收藏計數顯示 6 |
| 2 | 再按一次收藏按鈕 | 按鈕回到未收藏狀態,收藏計數顯示 5 |

### Notes

按鈕文字在 templates 有兩種寫法(§6 註),故不斷言文字;計數的意義由模板的 `counter` 推得(§9 推論 2)。訪客按收藏的行為不在範圍(§11 第 12 條)。

---

## P20

## Case 24: 文章列表(LIST)/ 分頁: 驗證文章總數超過一頁時清單下方出現分頁連結,點第 2 頁顯示下一批文章

```yaml
requirement_ids: [FR-RW-18]
priority: Medium
test_type: Functional
```

**Severity:** Major

### Preconditions

- 系統中的文章總數超過一頁可顯示的數量
- 使用者為訪客(未登入)
- 目前開啟 `/` 頁面

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 檢視 `Global Feed` 清單下方 | 出現分頁連結,顯示目前頁碼與總頁數(例如 `Page 1 of 3`),其中包含可前往第 2 頁的連結 |
| 2 | 記下第 1 頁清單中的文章標題 | 第 1 頁顯示一批文章 |
| 3 | 點分頁中的第 2 頁 | 清單換成另一批文章,與第 1 頁記下的文章不同 |

### Notes

每頁篇數 UI 未規定(§11 第 4 條),因此「超過一頁」以資料量達成;分頁控制項的樣式不驗證。換頁後 tab 是否保留,見 open questions。

---
