<!--
這是「你的」計畫草稿。請用自己的話填寫，先寫得粗糙沒關係。
規則：不要看 .scratch/prd-to-tests/spec.md（那是我寫的舊版本）。
寫完後跟我說「grill me」，我只提問、不給建議答案。
欄位說明見 learn/reference/spec-template.html。
-->

# Plan draft: PRD → TestCase → 自動化測試

## Problem Statement
<!-- 你觀察到的問題，從使用者角度看。誰、在什麼情境、痛在哪裡？ -->
測試工程師的工作內容是把 PRD 轉成 TestCase 再實作成自動化測試。我要把這個流程自動化。



## Solution
<!-- 你想做的解法，從使用者角度看。它如何解決上面的問題？ -->
建立一個 QA Agent，使用者提供 PRD 後，agent 能生成 TestCase 並轉成自動化測試


## User Stories
<!-- 盡量多列。格式：As a <actor>, I want <feature>, so that <benefit> -->
1. As a QA, I want QA agent, so that QA agent can help me to create test cases from PRD
2. As a QA, I want QA agent, so that QA agent can help me implement automation
3. As a developer, I want QA agent, so that I can learn how to build an agent


## Implementation Decisions
<!-- 要建/改哪些 module、介面、技術決策、資料流。不要寫檔名或程式碼片段。 -->

### 模組、介面

| 模組             | 輸入         | 輸出        | 不變量 / 錯誤        |
|----------------|------------|-----------|-----------------|
| PRD Agent      | File path  | PRD       | file path exist |
| TestCase Agent | PRD        | TestCases | 每個需求至少一個測試      |
| Automate Agent | TestCases  | Test code |                 |

```text
PRD
- base_url: str
- requirement: list[Requirement] # id: str, text: str

TestCase
- id: str
- requirement_id: str
- priority: str # p1, p2, p3
- type: str # happy path, boundary, negative
- steps: list[str]
- expected_result: str
```

### 流程圖
[PRD Agent] → PRD → [TestCase agent] → TestCase → [人工審核] → approved → [自動化 agent] → specs → [執行/修復] -> [PR 人工審核]

### Tech Stack
Pydantic AI、Playwright、pytest、POM

## Testing Decisions
<!-- 什麼是好測試、要在哪個 seam 測、哪些 module 要測。 -->
- 

## Out of Scope
<!-- 明確不做的事，擋住膨脹。 -->
- 

## Further Notes
<!-- 其他補充、風險、待解問題。 -->
- 
