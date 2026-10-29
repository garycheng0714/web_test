# Evals 基礎 Glossary

這個工作區的術語以這裡為準；定義會隨理解加深而改寫。

## Terms

**Trace**:
一次完整執行的紀錄：輸入、中間步驟、工具呼叫、最終輸出。
_Avoid_: Log, conversation

**Eval**:
一個「行為是否成立」的檢查，回傳 Pass 或 Fail。
_Avoid_: Metric, score

**Failure mode**:
一種可命名的錯，附一個可觀察的例子。
_Avoid_: Bug, issue

**Vanity metric**:
會動、但無法指出產品哪裡壞的數字，例如 token 數或 1–5 分主觀評分。
_Avoid_: KPI, dashboard metric

**Error analysis**:
人看 traces、替錯誤命名，產出 failure mode 清單的過程。
_Avoid_: Error review, bug triage

**Saturation**:
新 traces 不再帶出新的 failure mode 的狀態。
_Avoid_: Coverage, done

**Code evaluator**:
用程式檢查客觀規則的 evaluator，回傳 Pass／Fail 與理由。
_Avoid_: Script, test

**LLM judge**:
用模型判斷需要詮釋的規則的 evaluator；一次只判斷一個 failure mode。
_Avoid_: AI reviewer, grader

**TPR**:
人類說 Pass 時，evaluator 也說 Pass 的比率。
_Avoid_: Recall, sensitivity

**TNR**:
人類說 Fail 時，evaluator 也說 Fail 的比率。
_Avoid_: Specificity

**Train／dev／test split**:
Train 提供 few-shot；dev 反覆迭代；test 只跑一次。
_Avoid_: Holdout, validation set（ambiguous）

**Data leakage**:
把 dev／test 的例子放進 prompt 或 few-shot，讓量測虛高。
_Avoid_: Overfitting

**Youden index（J）**:
J = TPR + TNR − 1；衡量 evaluator 的鑑別力；J=0 表示沒有資訊。
_Avoid_: Sensitivity sum, accuracy

**Rogan-Gladen correction**:
用 TPR／TNR 把觀察通過率修正成真實通過率估計。
_Avoid_: Bias fix, adjusted accuracy

**Confidence interval（CI）**:
重複抽樣下，約 95% 的區間會涵蓋真值的範圍。
_Avoid_: Error bar, probability range

**Paired diff**:
固定情境、只動一個變因，用兩筆輸出的差異找 failure。
_Avoid_: A/B test, comparison
