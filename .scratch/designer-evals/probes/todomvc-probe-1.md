# TodoMVC probe 1 — 20 cases

每個 probe 都是一個 case。只回答:**這個 case 有沒有驗到它宣稱的 requirement?**

回覆格式:`P01 pass` 或 `P02 fail — <一句理由>`


---

## P01 fail - 沒有警告圖示這個功能

## Case 27: 新增 todo: Verify that 以相同標題新增 todo 時，兩項各自獨立存在

```yaml
requirement_ids: [FR-TODO-26]
priority: Medium
test_type: Functional
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中有 1 個未完成 todo（`Buy milk`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在新增輸入框輸入 `Buy milk` 後按 Enter | 清單出現兩項標題皆為 `Buy milk` 的 todo，各自有獨立的 checkbox；未被拒絕，也未合併成一項 |
| 2 | 勾選清單中第二項 `Buy milk` 的 checkbox | 只有第二項顯示為已完成（刪除線 + 灰字），第一項仍為未完成；兩項重複標題旁顯示警告圖示 |

### Notes

prd §4.1 FR-TODO-26／§9：由「spec 沒有唯一性要求」推得，非 spec 明文。


---

## P02 fail - 勾選狀態，文字顏色是灰色

## Case 5: 單一 todo: Verify that 點某項 todo 的 checkbox 後該項顯示為已完成，再點一次回到未完成

```yaml
requirement_ids: [FR-TODO-05]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 應用已開啟，清單中有 2 個未完成的 todo（`First`、`Second`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 點 `First` 的 checkbox | `First` 的 checkbox 為勾選狀態，其標題顯示刪除線且文字轉為綠色；`Second` 外觀不變 |
| 2 | 再次點 `First` 的 checkbox 取消勾選 | `First` 的刪除線與灰色文字消失，回到未完成外觀 |


---

## P03 fail - 少了下一頁的測試步驟

## Case 26: 篩選: Verify that 瀏覽器上一頁／下一頁可在 Active 與 Completed 篩選間切換，清單與選取狀態跟著改變

```yaml
requirement_ids: [FR-TODO-25]
priority: Medium
test_type: Workflow
```

**Severity:** Minor

### Preconditions

- 應用已開啟，清單中有 1 個未完成 todo（`First`）與 1 個已完成 todo（`Second`）
- 目前停在 `All` 篩選

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 點 `Active` 連結 | 顯示 Active 篩選，清單只顯示 `First`，`Active` 為選取狀態 |
| 2 | 點 `Completed` 連結 | 顯示 Completed 篩選，清單只顯示 `Second`，`Completed` 為選取狀態 |
| 3 | 按瀏覽器「上一頁」 | 回到 `Active` 篩選：`Active` 為選取狀態，清單只顯示 `First` |


---

## P04 fail - 測試步驟跟 requirement 無關

## Case 12: 編輯: Verify that 編輯模式清空標題後按 Enter 或失焦，該項 todo 被刪除

```yaml
requirement_ids: [FR-TODO-12]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中有 2 個 todo（`First`、`Second`）
- `First` 處於編輯模式，輸入框顯示 `First`

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 按 Escape | `First` 維持原標題，離開編輯模式，清單仍有 `First` 與 `Second` |
| 2 | 雙擊 `Second` 標題進入編輯模式，按 Escape | `Second` 維持原標題，離開編輯模式，清單仍有 `First` 與 `Second` |

### Notes

FR-TODO-12 明文把「按 Enter」與「失焦」兩個觸發放在同一條，故以同一案例的兩個步驟覆蓋。


---

## P05 fail - 只驗 FR-08 的出現,沒驗移開隱藏,且夾帶 FR-23 的旅程

## Case 8: 單一 todo: Verify that 點某項 todo 的移除按鈕後，該項被移除且其他項目保留

```yaml
requirement_ids: [FR-TODO-08]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中有 3 個未完成的 todo（`First`、`Second`、`Third`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 將滑鼠移到 `Second` 該列上 | 該項的移除按鈕出現 |
| 2 | 點擊該移除按鈕 | `Second` 從清單移除；`First`、`Third` 保留且相對順序不變 |

### Notes

移除按鈕的點擊行為在 app-spec.md 無明文，本 PRD 由按鈕名稱與 template 推得（§9），為 PRD 唯一推論項。


---

## P06 fail - 規則並沒有提到「顯示錯誤訊息 Title cannot be empty」

## Case 4: 新增 todo: Verify that 在新增輸入框只輸入空白後按 Enter，不會建立新項目

```yaml
requirement_ids: [FR-TODO-04]
priority: Medium
test_type: Negative
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中已有 1 個 todo（標題 `First`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在新增輸入框只輸入空白（例如三個空格 `   `）後按 Enter | 清單仍只有 `First`，未建立任何新項目；並顯示錯誤訊息 `Title cannot be empty` |

### Notes

§11 未定義「空白」是否包含 Tab／換行、是否需 trim 前後空白，見 open questions。


---

## P07 pass

## Case 21: 篩選: Verify that 點 `Completed` 連結只顯示已完成項目且該連結為選取狀態

```yaml
requirement_ids: [FR-TODO-20]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中有 1 個未完成 todo（`First`）與 1 個已完成 todo（`Second`）
- 目前停在 `All` 篩選，兩項都顯示

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 點 footer 的 `Completed` 連結 | 清單只顯示 `Second`，`First` 不顯示；`Completed` 連結為選取狀態（`All`、`Active` 非選取）；footer 計數顯示 `1 item left` |


---

## P08 pass

## Case 5: 單一 todo: Verify that 點某項 todo 的 checkbox 後該項顯示為已完成，再點一次回到未完成

```yaml
requirement_ids: [FR-TODO-05]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 應用已開啟，清單中有 2 個未完成的 todo（`First`、`Second`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 點 `First` 的 checkbox | `First` 的 checkbox 為勾選狀態，其標題顯示刪除線且文字轉為灰色；`Second` 外觀不變；footer 顯示 `1 item left` |
| 2 | 再次點 `First` 的 checkbox 取消勾選 | `First` 的刪除線與灰色文字消失，回到未完成外觀 |


---

## P09 fail - 少了切換 filter 的測試

## Case 14: Footer 未完成計數: Verify that 未完成計數隨新增、勾選、取消勾選更新，且不隨篩選改變

```yaml
requirement_ids: [FR-TODO-14]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中有 1 個未完成的 todo

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 觀察 footer 的計數文案 | 顯示 `1 item left` |
| 2 | 在新增輸入框輸入 `Second` 後按 Enter | 計數更新為 `2 items left` |
| 3 | 勾選其中 1 個 todo | 計數更新為 `1 item left` |
| 4 | 取消勾選該 todo | 計數更新為 `2 items left` |

### Notes

§6 只列出 0／1／2 的文案；3 項以上推得為 `<N> items left` 複數形式，未在 PRD 明文，實測時以質疑方式記錄結果。


---

## P10 pass

## Case 25: 篩選: Verify that 在 Active 篩選下新增的 todo 立即出現，在 Completed 篩選下新增的 todo 不出現直到切換篩選

```yaml
requirement_ids: [FR-TODO-24]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中有 1 個未完成 todo（`First`）與 1 個已完成 todo（`Second`）
- 目前停在 `All` 篩選

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 點 `Active` 連結，在新增輸入框輸入 `Third` 後按 Enter | `Third` 立即出現在 Active 清單中，與 `First` 一起顯示 |
| 2 | 點 `Completed` 連結 | 清單只顯示 `Second`，`Third` 不在清單中 |
| 3 | 在 `Completed` 篩選下，於新增輸入框輸入 `Fourth` 後按 Enter | 目前的 Completed 清單不顯示 `Fourth`（清單仍只有 `Second`）；footer 計數顯示 `3 items left` |
| 4 | 點 `All` 連結 | `Fourth` 出現在清單中，且為未完成狀態 |


---

## P11 pass

## Case 3: 新增 todo: Verify that 在新增輸入框輸入文字後按 Enter，該文字成為清單最後一項且輸入框清空

```yaml
requirement_ids: [FR-TODO-03]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 應用已開啟，清單中已有 1 個 todo（標題 `First`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在新增輸入框輸入 `Buy milk` 後按 Enter | 清單最後一項為 `Buy milk`，`First` 仍顯示在前一項；新增輸入框已清空；footer 顯示 `2 items left` |


---

## P12 fail - PRD 沒有「頁面不會重新載入」

## Case 26: 篩選: Verify that 瀏覽器上一頁／下一頁可在 Active 與 Completed 篩選間切換，清單與選取狀態跟著改變

```yaml
requirement_ids: [FR-TODO-25]
priority: Medium
test_type: Workflow
```

**Severity:** Minor

### Preconditions

- 應用已開啟，清單中有 1 個未完成 todo（`First`）與 1 個已完成 todo（`Second`）
- 目前停在 `All` 篩選

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 點 `Active` 連結 | 顯示 Active 篩選，清單只顯示 `First`，`Active` 為選取狀態 |
| 2 | 點 `Completed` 連結 | 顯示 Completed 篩選，清單只顯示 `Second`，`Completed` 為選取狀態 |
| 3 | 按瀏覽器「上一頁」 | 回到 `Active` 篩選：`Active` 為選取狀態，清單只顯示 `First`；頁面不會重新載入（維持單頁應用狀態） |
| 4 | 按瀏覽器「下一頁」 | 回到 `Completed` 篩選：`Completed` 為選取狀態，清單只顯示 `Second` |


---

## P13 - fail 規則沒有提到最多幾個字元

## Case 9: 編輯: Verify that 雙擊 todo 標題後進入編輯模式，輸入框含原標題且取得焦點

```yaml
requirement_ids: [FR-TODO-09]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中有 1 個 todo（`First`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 雙擊 `First` 的標題 | 該列顯示編輯輸入框，內容為 `First` 並已取得焦點；該列的 checkbox 與移除按鈕隱藏；輸入框限制最多 50 個字元 |


---

## P14 pass

## Case 18: 持久化: Verify that 新增、勾選與編輯後重新載入頁面，清單內容與完成狀態保持一致

```yaml
requirement_ids: [FR-TODO-17]
priority: High
test_type: DataPersistence
```

**Severity:** Critical

### Preconditions

- 應用已開啟，清單中有 1 個未完成的 todo（`First`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在新增輸入框輸入 `Second` 後按 Enter | 清單有 `First`、`Second` 兩項 |
| 2 | 勾選 `Second` 的 checkbox | `Second` 顯示為已完成（刪除線 + 灰字） |
| 3 | 雙擊 `First` 的標題，改為 `First updated` 後按 Enter | 清單顯示 `First updated`（未完成）與 `Second`（已完成） |
| 4 | 重新載入頁面 | 清單顯示 `First updated`（未完成）與 `Second`（已完成），與重新載入前一致 |


---

## P15 fail - 測試步驟跟 requirement 對不上，少了重新整理頁面的步驟

## Case 23: 篩選: Verify that 停在 Active／Completed 篩選時重新載入頁面，仍停在該篩選

```yaml
requirement_ids: [FR-TODO-22]
priority: High
test_type: DataPersistence
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中有 1 個未完成 todo（`First`）與 1 個已完成 todo（`Second`）
- 目前停在 `All` 篩選

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 點 `Active` 連結 | 清單只顯示 `First`，`Active` 連結為選取狀態 |
| 2 | 點 `Completed` 連結 | 清單只顯示 `Second`，`Completed` 連結為選取狀態 |


---

## P16 fail requirement 是在測 All, 但測試步驟完全跟 All 無關

## Case 19: 篩選: Verify that 預設篩選顯示全部 todo 且 `All` 為選取狀態，點 `All` 連結同樣顯示全部

```yaml
requirement_ids: [FR-TODO-18]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 瀏覽器已儲存 1 個未完成 todo（`First`）與 1 個已完成 todo（`Second`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 點 footer 的 `Active` 連結 | 清單只顯示 `First`；`Active` 連結為選取狀態 |
| 2 | 點 footer 的 `Completed` 連結 | 清單只顯示 `Second`；`Completed` 連結為選取狀態 |


---

## P17 fail - 規格並沒有「Edit cancelled」

## Case 13: 編輯: Verify that 編輯模式按 Escape 會放棄修改並離開編輯模式

```yaml
requirement_ids: [FR-TODO-13]
priority: High
test_type: Negative
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中有 1 個 todo（`First`）
- 該項處於編輯模式，輸入框內容已改為 `Changed`

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 按 Escape | 該項標題維持原值 `First`，`Changed` 未生效；離開編輯模式（輸入框消失）；footer 顯示 `Edit cancelled` 訊息 |


---

## P18 fail - 重新載入後，頁面焦點不會在 item 上

## Case 18: 持久化: Verify that 新增、勾選與編輯後重新載入頁面，清單內容與完成狀態保持一致

```yaml
requirement_ids: [FR-TODO-17]
priority: High
test_type: DataPersistence
```

**Severity:** Critical

### Preconditions

- 應用已開啟，清單中有 1 個未完成的 todo（`First`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 在新增輸入框輸入 `Second` 後按 Enter | 清單有 `First`、`Second` 兩項 |
| 2 | 勾選 `Second` 的 checkbox | `Second` 顯示為已完成（刪除線 + 灰字） |
| 3 | 雙擊 `First` 的標題，改為 `First updated` 後按 Enter | 清單顯示 `First updated`（未完成）與 `Second`（已完成） |
| 4 | 重新載入頁面 | 清單顯示 `First updated`（未完成）與 `Second`（已完成），與重新載入前一致；沒有任何項目處於編輯模式；頁面焦點自動回到 `First updated` 的標題 |


---

## P19 fail - 規格沒有「Item removed 提示」

## Case 24: 單一 todo: Verify that 點某項 todo 的移除按鈕後，該項被移除且其他項目保留

```yaml
requirement_ids: [FR-TODO-23]
priority: High
test_type: Functional
```

**Severity:** Major

### Preconditions

- 應用已開啟，清單中有 3 個未完成的 todo（`First`、`Second`、`Third`）

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 將滑鼠移到 `Second` 該列上 | 該項的移除按鈕出現 |
| 2 | 點擊該移除按鈕 | `Second` 從清單移除；`First`、`Third` 保留且相對順序不變；頁面顯示 `Item removed` 提示，並提供 `Undo` 連結 |

### Notes

移除按鈕的點擊行為在 app-spec.md 無明文，本 PRD 由按鈕名稱與 template 推得（§9），為 PRD 唯一推論項。


---

## P20 fail - 沒有測試 requirement 的「再取消勾選使所有 todo 回到未完成」

## Case 6: 清單頂端「全部標記完成」: Verify that 勾選「全部標記完成」使所有 todo 完成，再取消勾選使所有 todo 回到未完成

```yaml
requirement_ids: [FR-TODO-06]
priority: High
test_type: Functional
```

**Severity:** Critical

### Preconditions

- 應用已開啟，清單中有 3 個未完成的 todo

### Test Steps

| Step | Action | Expected Result |
| --- | --- | --- |
| 1 | 勾選清單頂端的「全部標記完成」 | 3 個 todo 的 checkbox 全部為勾選狀態，標題皆顯示刪除線與灰色文字 |
