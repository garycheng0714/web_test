# PRD:RealWorld / Conduit(designer eval 的第三份 PRD)

> **版本**:v0.4(2026-11-13)
> **性質**:由公開規格**及其模板與 API 契約**衍生(derivation),加上 2026-11-13 對 live demo 的四項
> 觀察;不是反推自 live 站,也不是本專案撰寫
> **來源**:
> - 規格:[`realworld-apps/realworld`](https://github.com/realworld-apps/realworld) @
>   `25588846c314b15a5e427ffe816e6b4af7be68c7`(2026-11-02,MIT)
>   - `docs/.../implementation-creation/features.md`(七條功能,本 PRD 的範圍線)
>   - `docs/.../specifications/frontend/routing.md`(頁面與 URL)
>   - `docs/.../specifications/frontend/templates.md`(DOM、控制項文案、`error-messages` 區塊)
>   - `docs/.../specifications/backend/endpoints.md`(端點與必填欄位)
>   - `docs/.../specifications/backend/error-handling.md`(驗證訊息與狀態碼)
> **live**:https://demo.realworld.show(API:https://api.realworld.show)
> **用途**:held-out PRD,用來驗證 eval 的判準在第三種 domain 上是否成立——這個 domain 有登入
> 狀態、伺服器回傳的錯誤、以及「只有作者能操作」的權限規則,都是 TodoMVC 沒有的。不進
> production 管線(`prd/` 底下新增檔案會觸發 `plan.yml`)。
>
> **v0.2 調整**:新增 `FR-RW-24`、`FR-RW-25`——註冊與登入在欄位未填完時,送出按鈕不可按。來源是
> live demo 的觀察,不是規格;PRD 的性質因此從「衍生」變成「衍生 + 觀察」。同一批觀察也確認編輯器
> 沒有這個行為,所以 `FR-RW-10` 走得通。v0.1 只收規格、模板與 API 契約。
>
> **v0.3 調整**:`FR-RW-16` 補上「沒有追蹤任何人」的空狀態。文案
> `Your feed is empty. Follow some users to see their articles here, or check out the Global Feed!`
> 取自 live demo 的 Angular 實作(`article-list.component.ts` 的 `empty-feed-message`),規格沒寫;
> 因此 §11 第 11 條只涵蓋其他列表。三項觀察都記在 §9。
>
> **v0.4 調整**:補上訪客的兩條規則。`FR-RW-26`(`Your Feed` tab 只在登入後出現)來自 templates;
> `FR-RW-27`(訪客開 `/settings`、`/editor` 被導向 `/login`)來自 live demo。訪客的行為不再只
> 出現在 precondition 裡,而是有自己的 claim 與覆蓋率。
>
> **範圍(A+)**:只收 `features.md` 的七條功能,加上來源明寫的失敗路徑。只由 `routing.md` 增加、
> 而七條功能沒點名的旅程(例如 Profile 頁的 My Articles / Favorited Articles 兩個 tab)不列為
> requirement。
>
> **抽取規則**:
> 1. 只收使用者可見的結果;實作細節(CSS class、localStorage key、slug 格式、JWT 內容)不進
>    requirement。
> 2. 一個 requirement = **一條被測邏輯**。同一條邏輯的不同方向、不同輸入放進 steps;不同的驗證
>    規則或不同的行為規則各自一條 requirement。不使用 AC 標號。
> 3. 能用來源原句就用原句,不改寫成我們的語氣;文案照抄,不改大小寫。
> 4. **失敗路徑只有在來源明寫時才是 requirement。** 驗證訊息與 `error-messages` 在來源裡,所以
>    「登入失敗」「註冊被拒」可以是 requirement;來源沒寫的行為列為第 11 章的非目標。
>    例外:live demo 可觀察、但來源沒寫的行為,只有在 §9 明列時才可成為 requirement(目前是
>    `FR-RW-16` 的空狀態文案、`FR-RW-24`、`FR-RW-25`、`FR-RW-27`)。
> 5. 被丟掉的東西列在第 10 章,讓切法可被檢查。
> 6. 新增 requirement 一律附加編號,不重排既有編號。
> 7. `specs/e2e/` 與其 SELECTORS 契約**不是**來源,寫作與 review 期間都不讀(ticket 11)。

## 1. 產品概述

Conduit 是一個文章分享站:使用者註冊後發文、編輯、刪除,追蹤其他作者,收藏文章,並在文章下
留言。首頁有三種文章列表來源(Global Feed、Your Feed、依 tag),都支援分頁。規格本身是「如何
用不同框架實作同一個 Medium 複製品」;本 PRD 只取其中對使用者可見的行為。

## 2. 使用者角色

| 角色 | 說明 |
|---|---|
| 訪客 | 未登入。可讀文章與留言,不能發文、留言、收藏或追蹤 |
| 已登入使用者 | 可發文、留言、收藏、追蹤,並管理自己的設定 |
| 作者 | 文章的建立者;只有他看到該文章的 `Delete Article` |
| 留言作者 | 留言的建立者;只有他看到該留言的刪除圖示 |

## 3. 資訊架構

### 3.1 頁面

| 頁面 | URL | 內容 |
|---|---|---|
| Home | `/` | 文章列表;Global Feed、登入後的 Your Feed、點 tag 後的該 tag tab;Popular Tags;分頁 |
| Sign in | `/login` | Email、Password、`Sign in`、`Need an account?` |
| Sign up | `/register` | Username、Email、Password、`Sign up`、`Have an account?` |
| Settings | `/settings` | 頭像 URL、`Your Name`、bio、Email、`New Password`、`Update Settings`、登出按鈕 |
| Editor | `/editor`、`/editor/:slug` | `Article Title`、`What's this article about?`、內文、`Enter tags`、`Publish Article` |
| Article | `/article/:slug` | 標題、作者、追蹤與收藏按鈕、`Edit Article`、`Delete Article`、內文、留言區 |
| Profile | `/profile/:username` | 使用者資訊、`Follow <username>`、`My Articles` / `Favorited Articles` 兩個 tab |

### 3.2 登入狀態

Header 依登入狀態換一組連結:訪客看到 `Home`、`Sign in`、`Sign up`;已登入者看到 `Home`、
`New Article`、`Settings` 與自己的 profile 連結(含頭像)。

### 3.3 列表來源

| tab | 內容 | 出現條件 |
|---|---|---|
| `Global Feed` | 全站文章,最新的在前 | always;訪客的預設 tab |
| `Your Feed` | 你追蹤的作者的文章,最新的在前 | 登入後 |
| `<tag>`(tab 名就是 tag) | 帶該 tag 的文章 | 點了側邊欄 Popular Tags 的某個 tag 之後 |

## 4. 功能需求

> 編號 `FR-RW-<序號>`;一個 requirement 就是一段旅程:起始狀態、動作、可觀察的結果。
> 括號內是來源對應。

### 4.1 帳號與 session(ACCOUNT)

#### FR-RW-01 註冊成功
- 在 `/register` 填入未被使用的 username、email、password 後送出 → 帳號建立,header 由
  `Sign in` / `Sign up` 換成 `New Article`、`Settings` 與自己的 profile 連結。
  (features「CRU- users」+ templates 的 header;登入後導向哪一頁來源沒寫,見 §11)

#### FR-RW-02 註冊被拒
- 以已存在的 email 註冊 → 停留在 `/register`,header 不變成已登入,表單的 error 區塊顯示
  `has already been taken`。
- 以格式錯誤的 email(例如不含 `@` 的 `not-an-email`)註冊 → 同樣停留、同樣未登入,error 區塊顯示
  `is invalid`。
  (error-handling「Validation messages」+ templates 的 `error-messages`)

#### FR-RW-03 登入成功
- 在 `/login` 填入既有帳號的 email 與 password 後送出 → header 換成 `New Article`、`Settings`
  與自己的 profile 連結。
  (features「Authenticate users via JWT」+ templates 的 header)

#### FR-RW-04 登入被拒
- 在 `/login` 填入錯誤的 password 後送出 → 停留在 `/login`,header 不變成已登入,error 區塊顯示
  伺服器回傳的錯誤。
  (error-handling:401 for unauthorized;templates 的 `error-messages`)

#### FR-RW-05 重新載入後維持登入
- 登入後重新載入任一頁 → header 仍是 `New Article`、`Settings` 與自己的 profile 連結,不需要再次
  登入。
  (routing「Uses JWT (store the token in localStorage)」;token 存哪裡是實作細節)

#### FR-RW-06 登出
- 在 `/settings` 按 `Or click here to logout.` → header 換回 `Sign in` / `Sign up`。
  (features「logout button on settings page」+ templates)

#### FR-RW-24 註冊按鈕在欄位未填時不可按
- 在 `/register`,Username、Email、Password 任一欄位為空時 → `Sign up` 按鈕不可按。
- 三個欄位都有值後 → `Sign up` 按鈕可按。
  (來源沒寫;取自 live demo 的觀察,見 §9)

#### FR-RW-25 登入按鈕在欄位未填時不可按
- 在 `/login`,Email 或 Password 為空時 → `Sign in` 按鈕不可按。
- 兩欄都有值後 → `Sign in` 按鈕可按。
  (來源沒寫;取自 live demo 的觀察,見 §9)

#### FR-RW-27 訪客開啟需要登入的頁面被導向登入
- 以訪客身分直接開啟 `/settings` → 被導向 `/login`。
- 以訪客身分直接開啟 `/editor` → 被導向 `/login`。
  (來源沒寫;取自 live demo 的觀察,見 §9)

### 4.2 個人設定(SETTINGS)

#### FR-RW-07 更新個人資料
- 在 `/settings` 修改 `Your Name` 或 bio 後按 `Update Settings` → header 與 profile 顯示新的名稱
  (或新的 bio)。
  (features「CRU- users」+ templates 的 Settings 表單 + endpoints `PUT /api/user`)

#### FR-RW-08 變更密碼
- 在 `/settings` 的 `New Password` 填入新密碼後按 `Update Settings`,登出後用新密碼登入 →
  登入成功;用舊密碼登入 → 被拒。
  (endpoints `PUT /api/user` 接受 `password` + `POST /api/users/login`)

### 4.3 文章(ARTICLE)

#### FR-RW-09 發佈文章
- 已登入,在 `/editor` 填入標題、`What's this article about?` 與內文後按 `Publish Article` →
  該文章以新標題出現在 `Global Feed` 的第一篇(列表以最新在前排序)。
  (features「CRUD Articles」+ endpoints「ordered by most recent first」)

#### FR-RW-10 發佈被拒
- 在 `/editor` 缺漏必填欄位(標題、描述、內文任一)後按 `Publish Article` → 停留在編輯頁,文章
  沒有被建立,error 區塊顯示 `can't be blank`。
  (endpoints:title / description / body 為 required + error-handling 的訊息表)

#### FR-RW-11 閱讀文章
- 從列表點一篇文章 → 文章頁顯示標題、作者與內文;內文的 markdown 被渲染(例如 `## 標題` 顯示為
  標題,而不是原字元的 `##`)。頁面底部有留言區。
  (routing「Render markdown from server client side」+「Comments section at bottom of page」)

#### FR-RW-12 編輯文章
- 作者在文章頁按 `Edit Article`,修改標題後儲存 → 文章頁顯示新標題,且網址的 slug 跟著改變;
  `Global Feed` 也顯示新標題。
  (endpoints「The `slug` also gets updated when the `title` is changed」+ templates 的 `Edit Article`)

#### FR-RW-13 刪除文章
- 作者在文章頁按 `Delete Article` → 回到列表,該文章不再出現在 `Global Feed`。
  (features「CRUD Articles」+ templates 的 `Delete Article` + endpoints `DELETE /api/articles/:slug`)

#### FR-RW-14 刪除按鈕僅作者可見
- 以非作者身分開啟一篇文章 → 看不到 `Delete Article`;以作者身分開啟同一篇 → 看得到。
  (routing「Delete article button (only shown to article's author)」)

### 4.4 文章列表(LIST)

#### FR-RW-15 Global Feed
- 開啟 `/` → 預設顯示 `Global Feed`,列出全站文章(最新的在前),每一篇顯示標題、描述、作者與
  收藏數。
  (features「GET and display paginated lists of articles」+ templates 的 article-preview +
  endpoints「most recent articles globally by default」)

#### FR-RW-16 Your Feed
- 已登入且追蹤了作者 A,A 有一篇文章、B 有一篇未被追蹤者的文章 → 點 `Your Feed` 只列出 A 的文
  章,B 的不在其中。
- 已登入但沒有追蹤任何人 → 點 `Your Feed` 不列出任何文章,並顯示 `Your feed is empty. Follow some
  users to see their articles here, or check out the Global Feed!`;句中的 `Global Feed` 是指向
  `/` 的連結。
  (features「GET and display paginated lists of articles」+ endpoints `GET /api/articles/feed`
  「created by followed users」;空狀態文案取自 live demo,見 §9)

#### FR-RW-17 依 tag 篩選
- 在側邊欄 Popular Tags 點某個 tag → 出現以該 tag 為名的 tab,清單只列出帶該 tag 的文章。
  (routing「List of articles pulled from either Feed, Global, or by Tag」+ templates 的 tag tab +
  endpoints `?tag=`)

#### FR-RW-18 分頁
- 文章總數超過一頁時,清單下方出現分頁連結;點第 2 頁 → 顯示下一批文章。
  (features「paginated lists」+ templates 的 `pagination` + endpoints `limit` / `offset`)

#### FR-RW-26 Your Feed tab 只在登入後出現
- 以訪客身分開啟 `/` → 只有 `Global Feed` tab,看不到 `Your Feed`。
- 登入後開啟 `/` → 多出 `Your Feed` tab。
  (templates「an optional Your Feed tab, appears after logging in」)

### 4.5 留言(COMMENT)

#### FR-RW-19 發表留言
- 已登入,在文章頁的留言區輸入文字後按 `Post Comment` → 該留言出現在留言區,並標示留言者。
  (features「CR-D Comments on articles」+ templates 的 comment-form)

#### FR-RW-20 刪除留言
- 留言作者在自己的留言上按刪除圖示 → 該留言從留言區消失,其他留言保留。
  (features「CR-D Comments」+ templates 的 `mod-options` + endpoints `DELETE .../comments/:id`)

#### FR-RW-21 刪除留言僅作者可見
- 非留言作者看同一則留言 → 看不到刪除圖示;留言作者看到 → 看得到。
  (routing「Delete comment button (only shown to comment's author)」)

### 4.6 收藏與追蹤(SOCIAL)

#### FR-RW-22 收藏 / 取消收藏
- 已登入,在文章頁按收藏按鈕 → 按鈕進入已收藏狀態,旁邊的計數 +1;再按一次 → 回到未收藏狀態,
  計數回到原值。
  (features「Favorite articles」+ templates 的收藏按鈕與 `counter` + endpoints
  `POST` / `DELETE /api/articles/:slug/favorite`)

#### FR-RW-23 追蹤 / 取消追蹤
- 已登入,在他人文章頁按 `Follow <username>` → 按鈕進入已追蹤狀態,旁邊的計數 +1;再按一次 →
  回到 `Follow <username>`,計數回到原值。
  (features「Follow other users」+ templates 的 follow 按鈕與 `counter` + endpoints
  `POST` / `DELETE /api/profiles/:username/follow`)

## 5. 關鍵流程

```text
訪客
  │
  ├─ 讀文章 ──► 看不到 Edit / Delete、也不顯示收藏與追蹤的已選狀態
  │
  └─ 註冊 / 登入
        │  成功 ──► header 換成已登入
        │  失敗 ──► 留在原頁,error 區塊顯示訊息
        ▼
      發文 ──► 出現在 Global Feed 第一篇
        │
        ├─ 編輯(作者)──► 標題與 slug 一起更新
        ├─ 刪除(作者)──► 從列表消失
        ├─ 留言 ──► 留言區新增;只有留言作者能刪
        ├─ 收藏 / 追蹤 ──► 計數 +1;再按一次還原
        └─ 設定 ──► 改資料 / 改密碼 / 登出
```

## 6. 訊息文案清單(Verbatim)

| 情境 | 文案 |
|---|---|
| Header,訪客 | `Home`、`Sign in`、`Sign up` |
| Header,已登入 | `Home`、`New Article`、`Settings`、profile 連結 |
| 登入頁 | `Sign in`、`Need an account?`、`Email`、`Password` |
| 註冊頁 | `Sign up`、`Have an account?`、`Username`、`Email`、`Password` |
| 設定頁 | `Your Settings`、`URL of profile picture`、`Your Name`、`Short bio about you`、`Email`、`New Password`、`Update Settings`、`Or click here to logout.` |
| 編輯頁 | `Article Title`、`What's this article about?`、`Write your article (in markdown)`、`Enter tags`、`Publish Article` |
| 文章頁 | `Follow <username>`、`Edit Article`、`Delete Article`、`Write a comment...`、`Post Comment` |
| 列表 | `Global Feed`、`Your Feed`、`Popular Tags`、`Read more...` |
| 驗證訊息(伺服器) | `can't be blank`、`is invalid`、`has already been taken` |

> 收藏按鈕在 templates 有兩種寫法:第一次出現是 `Favorite Post`,下方 actions 區是
> `Favorite Article`。來源自相矛盾,因此 requirement 只斷言「已收藏狀態」與計數,不斷言按鈕文字。
>
> templates 的 `error-messages` 範例文字(`That email is already taken`、`That name is required`、
> `That title is required`)是模板示意,與 `error-handling.md` 的實際訊息不同。本 PRD 以
> `error-handling.md` 為準。

## 7. 資料模型(來源明寫的部分)

| 實體 | 欄位 |
|---|---|
| User | `email`、`username`、`bio`、`image`、`token` |
| Profile | `username`、`bio`、`image`、`following` |
| Article | `slug`、`title`、`description`、`body`、`tagList`、`createdAt`、`updatedAt`、`favorited`、`favoritesCount`、`author` |
| Comment | `id`、`createdAt`、`body`、`author` |
| 列表回應 | `articles`、`articlesCount` |

- 每頁預設 `limit=20`、`offset=0`(API 預設值;UI 每頁幾篇來源沒寫,見 §11)。
- `slug` 是文章的唯一識別字串,格式由實作決定;標題改變時 slug 跟著更新。

## 8. 非功能需求

`styles.md`(共用 CSS、字型、圖示)、`implementation-creation/expectations.md`(repo、README、
300 stars、至少一個測試)與 `frontend/tests.md` 是給實作者的要求,不是使用者可見行為,因此不列為
需求。

## 9. 追溯矩陣

| 來源 | 對應 requirement |
|---|---|
| features:Authenticate users via JWT | `FR-RW-03`、`FR-RW-04`、`FR-RW-05`、`FR-RW-06` |
| features:CRU- users | `FR-RW-01`、`FR-RW-02`、`FR-RW-07`、`FR-RW-08` |
| features:CRUD Articles | `FR-RW-09`、`FR-RW-11`、`FR-RW-12`、`FR-RW-13`、`FR-RW-15` |
| features:CR-D Comments | `FR-RW-19`、`FR-RW-20` |
| features:paginated lists | `FR-RW-15`、`FR-RW-16`、`FR-RW-17`、`FR-RW-18` |
| features:Favorite articles | `FR-RW-22` |
| features:Follow other users | `FR-RW-23` |
| routing:只顯示給作者 | `FR-RW-14`、`FR-RW-21` |
| routing:markdown 與留言區 | `FR-RW-11` |
| error-handling:驗證訊息與 401 | `FR-RW-02`、`FR-RW-04`、`FR-RW-10` |
| endpoints:slug 隨標題更新 | `FR-RW-12` |
| templates:header 兩態 | `FR-RW-01`、`FR-RW-03`、`FR-RW-06` |
| live demo 觀察(2026-11-13):註冊欄位未填完,`Sign up` 不可按 | `FR-RW-24` |
| live demo 觀察(2026-11-13):登入欄位未填完,`Sign in` 不可按 | `FR-RW-25` |
| live demo 觀察(2026-11-13):Your Feed 空狀態文案與其中的 `Global Feed` 連結 | `FR-RW-16` |
| templates:Your Feed tab 只在登入後出現 | `FR-RW-26` |
| live demo 觀察(2026-11-13):訪客開 `/settings`、`/editor` 被導向 `/login` | `FR-RW-27` |

> **三處推論,都在這裡標記**:
> 1. `FR-RW-09` 的「出現在 Global Feed 第一篇」由「列表以最新在前排序」加上「建立文章」推得;
>    來源沒有明寫發佈後導向哪裡。
> 2. `FR-RW-22`、`FR-RW-23` 的「計數 +1」由模板中按鈕旁的 `<span class="counter">` 推得;
>    來源沒有明寫那個數字是收藏數或追蹤者數。
> 3. `FR-RW-02`、`FR-RW-10` 的「error 區塊顯示伺服器訊息」由 `error-handling.md` 的訊息表加上模板
>    的 `error-messages` 區塊推得;來源沒有明寫前端會原樣顯示伺服器訊息,而不是自己的文案。

> `FR-RW-10` 的可執行性由同日觀察支撐:編輯器**不**因必填欄位為空而讓送出按鈕不可按,所以
> 「缺欄位後按 `Publish Article`」走得通。這一項不是 requirement。

## 10. 抽取時丟掉的東西

| 被丟掉的 | 原因 |
|---|---|
| Profile 頁的 `My Articles` / `Favorited Articles` 兩個 tab | 只由 `routing.md` 增加,七條功能沒有點名(範圍 A+) |
| Popular Tags 當成獨立 requirement | 只當 `FR-RW-17` 的入口動作,不另外驗排序或數量 |
| `?author=`、`?favorited=` 兩種過濾 | 服務 profile 的兩個 tab,已丟棄 |
| 預設頭像(smiley) | `styles.md` 的 UI 細節,不是七條功能之一 |
| active 頁面的 CSS class | 實作細節 |
| `localStorage` 的 key 與 JWT 內容 | 實作細節;只保留「重新載入後仍登入」這個可觀察結果 |
| CSS、字型、圖示、共用主題 | 非功能需求 |
| `expectations.md`:repo、README、300 stars、單元測試 | 對實作 repo 的要求 |
| `frontend/tests.md` 與 E2E SELECTORS 契約 | 不是來源(ticket 11 的決定) |
| 文章列表不回傳 `body`(2024 變更) | API 效能細節 |
| demo API 的內容可見度限制 | 環境特性,不是產品行為 |
| XSS / 安全性 | 來源沒寫;不列為 requirement |

## 11. 非目標與未支援

| # | 項目 | 決定 |
|---|---|---|
| 1 | 密碼規則(長度、複雜度) | 來源沒寫;不要求 |
| 2 | token / session 的有效期 | 來源沒寫;不要求 |
| 3 | 登入或註冊成功後導向哪一頁 | 來源沒寫;只要求 header 變成已登入,不要求落地頁 |
| 4 | 每頁文章數 | API 預設 20;UI 未規定,不要求固定篇數 |
| 5 | tag 正規化(大小寫、空白、重複) | 不規定 |
| 6 | slug 格式 | 由實作決定;只要求標題改變時 slug 跟著更新(`FR-RW-12`) |
| 7 | 表單輸入的 trim 與空白字串 | 只沿用 `can't be blank` 的定義,不另外規定 trim |
| 8 | markdown 方言與 XSS 清理 | 只要求 markdown 被渲染,不規定方言與清理方式 |
| 9 | 錯誤訊息在頁面上的位置與樣式 | 只要求出現在表單的 `error-messages` 區塊 |
| 10 | 載入中狀態、樂觀更新、離線、多分頁同步 | 不要求 |
| 11 | Global Feed 與 tag 列表的「沒有文章」空狀態文案 | 來源沒寫;不要求(Your Feed 的空狀態見 `FR-RW-16`) |
| 12 | 訪客按收藏或追蹤 | 來源沒寫;live demo 不一致(收藏 → `/register`,追蹤 → `/login`),不寫死 |
| 13 | email 文法邊界(`a@b`、TLD 長度、unicode) | 由實作決定;測試只要求用不含 `@` 的值(見 `FR-RW-02`) |
