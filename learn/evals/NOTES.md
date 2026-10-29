# NOTES

## 學習偏好
- 繁體中文；術語先用一句話定義，再放進流程
- leading-word 寫法：一個詞承載一組行為，不寫長串說明
- 邊做邊學；每課要有一個可檢查的產出
- 不排斥被提問；練習由使用者先寫，agent 只給回饋
- 不要用 LaTeX display math（`\[...\]`、`\(...\)`）；公式用純文字或 `<pre class="flow">`

## 工作筆記
- 本目錄是 `teach` skill 的子工作區；母工作區在上一層 `learn/`。
- 不 import、不修改 `web_test` 的程式碼；只新增 `learn/evals/` 底下的檔案。
- 玩具領域：餐廳訂位助理（客觀錯誤＋語氣類主觀錯誤）。
- 課程編號從 `0001` 起，與母工作區的 `0001`–`0003` 分開。
- 刻意簡化：
  - 玩具 pipeline 是離線模板產生器，failure modes 是植入的。
  - judge 校準用已知錯誤率的模擬 judge，不呼叫 API。
- 共用母工作區的 `learn/assets/style.css`；evals 專屬樣式放 `assets/evals.css`。
- `GLOSSARY.md` 已有 Lesson 0001 的 4 個術語；之後只在實際使用後追加。
- `learning-records/` 仍 lazy：等非顯而易見的洞見出現再寫。
- 2026-10-27：Lesson 0001 完成；Lesson 0002 建好。
  - `toy/pipeline.py`：stdlib、deterministic；22 tuples × 2 variants = 44 traces。
  - `toy/answer-key.json` 與 `pipeline.py` 的 `SPOILER` 段是 Lesson 0003 的答案。
  - 新增 t-021 母親節、t-022 情人節。
  - 使用者看不出「不真實」的 tuple。Lesson 0002 練習最後改成：
    「寫 2 條你需要的 policy 規則」＋「記 2 個覆蓋缺口」，不再要求改 tuple。
  - 沒有 `policy.md`：目前 generator 的乾淨回覆會直接接 12 人與假日訂位；
    policy 要等 Lesson 0004 或真的做 routing 時再一起定。
- t-018 走 B：question 的 query 帶上 special（例：需要無障礙座位），
  讓 `dropped_special` 可觀察。已重跑 traces 與 answer key。
- 2026-10-27：Lesson 0003 建好。
  - `toy/review.py`：stdlib HTTP server，`127.0.0.1:8765`。
  - `toy/review.html` / `review.css` / `review.js`：trace 卡片、mode、note、進度。
  - 標註自動存到 `toy/annotations.json`；一個 trace 可用「、」記多個 mode。
  - 簡化：沒有 map view、agent suggestions、inline highlight；只留自由文字。
- 2026-10-27：使用者標了 23/44。主要問題：
  - 把 false availability、missing confirmation、dropped special 混進「缺少確認時間」。
  - 沒有把同一 tuple 的 a/b variant 放在一起 diff；t-021/t-022 的缺陷因此漏掉。
  - 「無法理解語句」（t-009-b/t-011-b）是把 UX 取捨當 failure；目前沒有 policy 可判。
  - 已教：一個 mode 一個可觀察的錯；variant diff；policy 先於 failure 判定。
- 2026-10-27：Lesson 0003 taxonomy 完成，8 個 mode 都有規則與 why：
  時間／日期／人數錯置、特殊需求遺漏、包場未轉業務、客滿仍接單、
  缺少與客戶再次確認、未確認就自行假設時間。
- 2026-10-27：Lesson 0004 建好。
  - `toy/checks.py`：worked example `check_party_mismatch`，stdlib、抓到 5 筆。
  - 練習：使用者加 `check_special_omitted`；預期會遇到「生日 vs 慶生」的 false positive。
  - 教學點：先寫粗 proxy、跑全部 traces、對照人工標註，再收緊規則。
- 2026-10-27：`check_special_omitted` behavior 修正。
  - 原版 early return 只檢查第一個 special；改成先收集全部，再逐一檢查。
  - reason 改為 `not mentioned`，明確這是 mention-only proxy。
  - `self_check()` 覆蓋：t-005-a fail、t-006-b pass（慶生同義詞）、
    雙 special 回歸測試、negative mention 的已知限制。
  - 發現：t-022-b 是使用者人工漏掉的；程式 check 反而抓到。
- 2026-10-27：Lesson 0005 建好。
  - 新 failure mode 候選：語氣不符（t-005-b「記得準時到嘿」、t-016-b「好喔，取消囉」）。
  - `toy/judge_tone.md`：四要素 scaffold，使用者填寫。
  - 資料量不足（只有 2 筆 tone fail）：本課只設計與試跑，不驗證。
  - 測試集：t-016-b、t-002-a、t-018-b、t-009-b、t-021-b；
    few-shot：t-005-b、t-001-b、t-020-b、t-012-b（borderline）。
- 2026-10-27：跑 tone judge（5 筆），結果在 `toy/judge_tone_results.json`。
  - 判決：t-016-b Fail；其餘 4 筆 Pass，與使用者預期一致。
  - 但 4 個 Pass 有 3 個是靠寬容解讀：PASS 定義要求「稱謂或請／謝謝」，
    t-002-a/t-018-b/t-021-b 只有「抱歉／您」；嚴格照字面會誤判 Fail。
  - 修正 Example 1 的 placeholder：Assistant 原本是「（貼上）」、Critique 誤放回覆。
  - 教學點：spot check 一致不等於 judge 對齊；定義的模糊就是變異來源，Lesson 0006 用 TPR/TNR 量。
- 2026-10-27：PASS 定義更新後重跑。
  - 5/5 與預期一致；TPR=1.00、TNR=1.00（只有 5 筆，不能當驗證）。
  - 新的 4 個 Pass 都符合「您／請問／抱歉」字面，不再靠寬容解讀。
  - 使用者選 A：Example 3「收到，已處理。」改 Fail；t-012-b 是 borderline 且 resolved 為 Fail，
    與 PASS 定義一致。
  - prompt 現在沒有定義／範例矛盾；5 筆測試結果不變。
- 2026-10-27：Lesson 0006 建好。
  - `toy/validate.py`：stdlib；模擬已知 TPR/TNR 的 judge、stratified splits、
    confusion matrix、Rogan-Gladen、bootstrap CI。
  - 預設 200 筆（100/100）讓數字穩定；改成 50/50 可看 CI 變寬。
  - 預設輸出：test TPR 0.90 / TNR 0.80；production raw 0.73 ->
    corrected 0.76，95% CI [0.65, 0.89]，true 0.77。
  - 教學點：raw accuracy 會被類別不平衡騙；test 只跑一次；
    分母 TPR+TNR-1 越大，CI 越窄。
  - 加入使用者寫的 bias correction 解釋：心軟 judge 的 8,000/10,000 例子、
    Rogan-Gladen 的流行病學來源、p_obs 定義；reference 也加了一節。
  - 加入 Youden index 與變異數放大：J = TPR + TNR - 1；
    Var(theta) ≈ Var(p_obs)/J^2；CI 約正比於 1/(J*sqrt(n))。
    公式一律用純文字／`pre`，不用 LaTeX。
  - 加入 CI 段：95% CI 是程序覆蓋率（不是真值機率）；
    [5,95]／[49,51]／[65,89] 三個寬度例子；寬度來源是 J、test set、production n。
  - 新增 `reference/ci-methods.html`：必學概念、選方法、公式查表、
    4/4 工作例、工具、背什麼查什麼。`assets/evals.css` 加 `.cols` 兩欄版型。
  - Lesson 0006 與 `evals-loop` 都連到 CI methods。
  - 加入 raw pass rate vs accuracy：raw = (TP+FP)/N，accuracy = (TP+TN)/N；
    Rogan-Gladen 修正的是 true pass rate；FP 高估、FN 低估；
    500 筆 worked example（0.73 -> 0.76，true 0.77）。
  - 使用者跑了三組並寫解讀；修正「單次 run 推論」：J 不變時 expected 寬度不變；
    N 變小 expected CI 變寬；run 3 是 lucky test set。
  - Lesson 0006 加「不要從單次 run 推論」callout；練習加多 seed 步驟。
  - 新增 `toy/validate_many.py`：20 seeds，比較 200 vs 100 筆。
    200: CI width 0.144 ± 0.049, coverage 0.80
    100: CI width 0.174 ± 0.109, coverage 0.50
  - 教學點：N 變小 CI 平均變寬、變異變大；coverage < 95% 表示 CI 是近似
    （test set 小、bootstrap 忽略 production 抽樣）。
  - 新增 `toy/tone_labels.json`：44 個 trace_id 的 binary tone label 模板。
    空白 = 未標；註明不要用 answer-key 填，且 44 筆不足 50／50。
- 2026-10-27：Lesson 0007 建好（七課基礎完成）。
  - `audit.md` scaffold：六區、report format、依 impact 排序。
  - 練習：審 `learn/evals`，寫 5–8 個 findings；每個要找具體檔案或數字。
  - 七課流程：traces → error analysis → evaluator → validation → corrected rate。
- 2026-10-27：Lite B-toy artifacts 建好。
  - `tone_lite_dataset.jsonl`：40 筆，20 Pass／20 Fail；20 correct／20 wrong；
    5 contexts × 8。
  - `tone_lite_splits.json`：train 8／dev 16／test 16；各 4/4、8/8、8/8。
  - `tone_lite_labels.json`：40 筆空白，等使用者標。
  - `tone_lite_answer_key.json`：spoiler；judge run 前不可開。
  - `tone_labeling_guide.md`：tone-only、控制組、delayed self-review。
  - 跑完 Lite B-toy：
    - dev 16/16、test 16/16；combined TPR／TNR 1.000，CI [0.806, 1.000]。
    - baseline regex TNR 0.938，漏 tl-014；judge 抓到。
    - tl-014 由 Pass 修正為 Fail；40/40 labels 與 answer key 一致。
    - delayed self-review 被跳過；tl-014 是跑完 dev 後才發現。
    - `tone_lite_metrics.md` 記錄 caveats 與 audit note。
  - 下一步：把 toy rehearsal 寫進 `audit.md`，Judge Validation 仍 Problem exists。
- 2026-10-27：`audit.md` 完成（agent 代寫，經使用者同意）。
  - 6 findings，依 impact 排序；Error Analysis 列為 OK。
  - Scope 明確排除 MISSION 的 out-of-scope 項目。
  - 最優先修的是 Judge Validation；其次是 evaluator 覆蓋與 human review。
- 2026-10-27：收尾。
  - 建立 `learning-records/0001-evals-basics-complete.md`。
  - MISSION 加 Status；GLOSSARY 補 12 個術語。
  - 七課 + capstone 完成；下一步見 MISSION Status。

## Lesson 0001 guesses
- 未掌握正確的訂位狀況。ex: 已客滿卻讓來電客戶訂位 
- 未獲得完整的訂位資訊。ex: 缺少日期、時間、人數 
- 未執行訂位動作。ex: 獲得訂位資訊後卻沒有實際保留位子 
- 未執行取消訂位。ex: 客戶來電取消訂位，卻依舊保留該訂位 
- 修改既有訂位資訊失敗。ex: 客戶來電變更時間，未如期調整訂位資訊

## Lesson 0003 failure modes
- 時間錯置 
  * 規則：回覆的時段不是客戶希望的時段
  * 為什麼重要：把訂位時間弄錯會讓客戶體驗不好
```text
User
你好，我想訂下週二 18:30，4 位，兒童椅。

Assistant
好的，已為您保留下週二 19:00 的 4 人桌。我會幫您準備兒童椅。請問需要留下聯絡電話嗎？
```
- 日期錯置
  * 規則：回覆的日期不是客戶希望的日期
  * 為什麼重要：把日期弄錯會讓客戶體驗不好
```text
User
你好，我想訂週日 12:00，7 位。

Assistant
好的，已為您保留下週二 12:00 的 7 人桌。請問需要留下聯絡電話嗎？
```
- 人數錯置
  * 規則：回覆的人數不是客戶希望的人數
  * 為什麼重要：把人數弄錯會讓客戶體驗不好
```text
User
你好，我想訂週日晚上，7 位。

Assistant
沒問題。請問您想訂週日的幾點？8 人的位子我先幫您留意。
```
- 特殊需求遺漏
  * 規則：未回覆客戶的特殊需求
  * 為什麼重要：客戶到場後發現實際與需求不符，體驗不佳
```text
User
你好，我想訂週五 19:00，4 位，窗邊。

Assistant
好的，已為您保留週五 19:00 的 4 人桌。請問需要留下聯絡電話嗎？
```
- 包場未轉業務
  * 規則：包場沒有轉給業務處理
  * 為什麼重要：包場需要讓業務與客戶接洽，因為有很多細節要討論
```text
t-020-a

User
你好，我想訂下週二 18:30，12 位，包場。

Assistant
好的，已為您保留下週二 18:30 的 12 人桌。請問需要留下聯絡電話嗎？


t-020-b

User
下週二 18:30，12 位，包場，可以嗎？

Assistant
下週二 18:30 的包場需要專人報價，我會請業務與您聯繫。請問方便留下聯絡方式嗎？
```
- 客滿仍接單
  * 規則：客滿不能再接受訂位
  * 為什麼重要：客戶到場後會沒有位子入位
```text
t-021-a

User
你好，我想訂母親節 19:00，12 位。

Assistant
好的，已為您保留母親節 19:00 的 12 人桌。請問需要留下聯絡電話嗎？


t-021-b

User
請問母親節 19:00 可以訂12 位嗎？

Assistant
抱歉，母親節 19:00 已經客滿。當天 18:00 或 21:00 還有位子，需要幫您保留嗎？
```
- 缺少與客戶再次確認
    * 規則：處理完訂位後未再跟客戶核對訂位資料
    * 為什麼重要：確保訂位資訊正確，符合客戶期望
```text
User
請問下週二 18:30 可以訂12 位嗎？

Assistant
收到，已處理。
```
- 未確認就自行假設時間
  * 規則：客戶沒有提供時間，卻自行假設時間
  * 為什麼重要：自行假設時間不一定能符合客戶期望
```text
User
你好，我想訂週五晚上，2 位。

Assistant
好的，已為您保留週五 19:00 的 2 人桌。請問需要留下聯絡電話嗎？
```
- 語氣不符
  * 規則：回覆的語氣不夠禮貌、正式
  * 為什麼重要：對待客戶要展現禮貌、專業，否則影響餐廳形象
```text
User
週五 19:00，4 位，窗邊，可以嗎？

Assistant
好的，已為您保留週五 19:00 的 4 人桌。我會幫您備註希望靠窗。請問需要留下聯絡電話嗎？ 記得準時到嘿。
```
- 提供外送服務
  * 規則：回覆承諾了餐廳沒有的外送服務
  * 為什麼重要：提供不存在的服務會導致商譽受損
```text
User
請問你們有外送嗎？

Assistant
有的，我們有外送服務，滿 500 元免運。
```

## 未覆蓋（Lesson 0002）
- （從 lesson 的缺口清單挑 2 個寫在這裡）

## Lesson 0006
- Origin
```text
simulated judge: TPR=0.90 TNR=0.85
splits: train=30 dev=90 test=80
dev: n=90 TP=42 FN=3 TN=39 FP=6 TPR=0.93 TNR=0.87
test: n=80 TP=36 FN=4 TN=32 FP=8 TPR=0.90 TNR=0.80

production: n=500 raw pass=0.73
corrected=0.76  95% CI=[0.65, 0.89]
true rate (simulation only)=0.77
```
- TPR 0.95 / TNR 0.8
```text
simulated judge: TPR=0.95 TNR=0.80
splits: train=30 dev=90 test=80
dev: n=90 TP=43 FN=2 TN=37 FP=8 TPR=0.96 TNR=0.82
test: n=80 TP=37 FN=3 TN=31 FP=9 TPR=0.93 TNR=0.78

production: n=500 raw pass=0.78
corrected=0.79  95% CI=[0.70, 0.91]
true rate (simulation only)=0.77
```
- TPR 0.95 / TNR 0.8 + N_PASS／N_FAIL 為 50／50
```text
simulated judge: TPR=0.95 TNR=0.80
splits: train=16 dev=44 test=40
dev: n=44 TP=21 FN=1 TN=14 FP=8 TPR=0.95 TNR=0.64
test: n=40 TP=19 FN=1 TN=18 FP=2 TPR=0.95 TNR=0.90

production: n=500 raw pass=0.78
corrected=0.80  95% CI=[0.72, 0.91]
true rate (simulation only)=0.77
```

解讀：
1. (TPR + TNR) 總合不變但 TPR 變大、TNR 變小會讓 CI 變窄、真實通過率變高
2. N_PASS／N_FAIL 減少會讓 CI 變窄、真實通過率變高

### 修正（agent review）
- 第 1 點不成立：origin 與 run 2 的 TPR+TNR 都是 1.75，J 都是 0.75；
  expected CI 寬度不變。觀察到的 CI 0.24 -> 0.21、corrected 0.76 -> 0.79
  是抽樣波動，不是「TPR 變大、TNR 變小」的法則。
  corrected 上升主要是 raw p_obs 從 0.73 升到 0.78，不是 TPR 的因果效果。
- 第 2 點方向相反：N 從 200 降到 100，expected CI 應該變寬
  （寬度約 1/(J*sqrt(n))）。run 3 的 CI 看起來較窄，是因為 test set
  剛好抽到 TPR 0.95 / TNR 0.90（J=0.85），不是因為 N 變小。
  以 expected width 估算：
    run 2: 1/(0.71*sqrt(80)) ≈ 0.158
    run 3: 1/(0.85*sqrt(40)) ≈ 0.186（反而更寬）
- 「真實通過率變高」要改成「corrected 估計變高」；true rate 在模擬中固定是 0.77。
- 結論：不要從單一 seed 的 3 次 run 推論法則；要看分布，至少跑多個 seed
  或多次重抽樣。

## 待辦
- 若接真實專案：改 MISSION 的 Constraints（real traces／API），並補 runner + 50／50 labels。
- 可選：CI 兩個噪聲來源、full bootstrap、特殊需求未滿足的 action detection。
