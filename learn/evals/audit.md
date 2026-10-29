# Eval pipeline audit

> 依 impact 排序。每個 finding 都要指出具體檔案或數字，不要寫 generic advice。

## Scope

依 `MISSION.md`，production monitoring、CI gate、dashboard、RAG 專項、vendor API
都是 out of scope；以下不列為 finding。

## Findings

### 1. Tone judge is not validated

**Area:** Judge Validation
**Status:** Problem exists

`judge_tone.md` 只有 5 筆 spot check；Lite B-toy 的 dev/test 各 16 筆全對
（combined TPR/TNR 1.000，95% CI [0.806, 1.000]），但 runner 是 agent-as-judge、
單一 annotator、合成資料，且 delayed self-review 被跳過。Baseline regex 的 TNR
是 0.938，只漏 tl-014；judge 抓到這一筆，但這只是一個案例。

**Fix:** 加可重現 runner（pin model snapshot、temperature 0、prompt hash、原始 log）；
補到 ~50 Pass + 50 Fail 的人類標籤；切 train/dev/test；量 TPR/TNR 與 bootstrap CI。
在這之前，`judge_tone.md` 保持 draft，已知 pattern 先用 code proxy。

### 2. Most known failure modes have no evaluator

**Area:** Evaluator Design
**Status:** Problem exists

`toy/checks.py` 只有 `party_mismatch` 與 `special_omitted` 兩個 check；
`NOTES.md` 的 taxonomy 有 10 個 mode（時間、日期、人數、特殊需求、包場、客滿、
缺少確認、假設時間、語氣、外送）。8 個 mode 沒有 evaluator，tone judge 仍是 draft。

**Fix:** 先用 code evaluator 覆蓋 objective modes：時間／日期／人數（regex + 參考值）、
缺少確認（回覆是否含 day/time/party）、自行假設時間（user 無 HH:MM → reply 有 HH:MM）、
外送（policy keyword）、包場（policy → 業務）。客滿仍接單需要 availability data 或
a/b pair。用 `write-code-eval`。

### 3. Human review has no second annotator

**Area:** Human Review
**Status:** Problem exists

所有標註由單一 annotator 完成；tl-014 原本標 Pass，跑完 dev 後才改成 Fail；
delayed self-review 被跳過。沒有 inter-annotator agreement，也沒有獨立第二標籤。

**Fix:** 找第二人覆核 20–50 筆，或至少做 delayed self-review；不一致的案例用
labeling guide adjudicate；記錄 agreement。用 `build-review-interface` 或目前的
review app。

### 4. Labeled data is not sufficient for validation

**Area:** Labeled Data
**Status:** Problem exists

原始 44 筆 traces 只有 4 個 tone fail；Lite B-toy 是 40 筆合成資料（20／20），
combined CI [0.806, 1.000] 仍寬；train 8 預留但未使用，few-shot 仍用舊 44 筆。
沒有真實 production traces，也沒有 50／50 的 tone 標籤。

**Fix:** 收集 ~50 Pass + 50 Fail，優先用真實 traces；合成資料只補缺口，且必須
人工標籤；保持 balanced、stratified；test 凍結。用 `generate-synthetic-data`。

### 5. Routing policy is implicit

**Area:** Evaluator Design
**Status:** Problem exists

`包場未轉業務`、9 人以上、無障礙 handoff 沒有 `policy.md`；同一種請求可能被
判成 failure 或正確行為。`t-009-b`／`t-011-b` 的「時間都可以」也有同樣問題。

**Fix:** 寫 `toy/policy.md`，明訂 handoff 與例外；重標 policy-dependent traces；
把 policy 寫進 evaluator。

### 6. Judge runs are not reproducible

**Area:** Pipeline Hygiene
**Status:** Problem exists

Judge 由 agent 一次性執行，沒有 model snapshot、temperature、prompt hash 或
原始 log；prompt 改過幾次（PASS 定義、Example 3），但沒有正式的 re-validation
流程。其他人無法重跑或稽核判決。

**Fix:** 建 `judge_runner.py`，pin model snapshot、temperature 0、log raw response
與 prompt version；每次改 prompt／模型就重跑 dev，test 只跑一次；把版本寫進結果檔。

## What's OK

- **Error Analysis:** `annotations.json` 44／44；10 個 observed modes；
  25 defects、19 clean；taxonomy 有規則與例子。Answer-key 對照沒有 missed／extra
  （至少一個 mode），但這不是獨立驗證。
- **Scope:** MISSION 已排除的項目沒有被當成缺失。
