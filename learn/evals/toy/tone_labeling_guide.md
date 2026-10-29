# Tone labeling guide（Lite B-toy）

你只判斷**語氣**，不判斷事實正確性。事實錯誤由其他 failure mode 處理；這裡不是用它來決定 tone。

## 標什麼

`tone_lite_dataset.jsonl` 每筆有 `user` 與 `assistant`。讀完後，在
`tone_lite_labels.json` 填 `Pass` 或 `Fail`。

## PASS

- 禮貌、專業、簡潔。
- 使用禮貌用語之一：您、請問、抱歉、謝謝、麻煩。
- 沒有俚語、冷淡、不耐煩、反諷、輕蔑。

## FAIL

- **俚語／太隨便**：嘿、喔、啦、囉、嗨嗨、超讚。
- **冷淡／制式**：「已記錄。」「有。2 位。」「已處理。」
- **不耐煩／輕蔑**：「自己看。」「就這樣。」「怎麼可能？」
- **反諷／居高臨下**：「您確定嗎？」「當然有啊。」
- **過度隨便**：「幫你訂好囉～」「沒問題der」。

## Borderline

- 「收到，已處理。」→ **Fail**（目前 judge prompt 的 Example 3 定為 Fail）。
- 簡短但有禮貌（例如「好的，已為您保留。」）→ **Pass**。
- 不確定時，先標你認為最合理的一邊，並在 `notes` 寫下理由；不要留空。

## 控制組（刻意設計）

- 有些回覆**事實錯誤，但語氣禮貌** → tone 應標 **Pass**。
- 有些回覆**事實正確，但語氣差** → tone 應標 **Fail**。

這是為了確認 judge 沒有把事實錯誤混進 tone。不要因為事實錯就標 Fail。

## 標註流程

1. 只打開 `tone_lite_dataset.jsonl` 與 `tone_lite_labels.json`。
2. 一次標完 40 筆；`context` 只是方便你分類，不是 label。
3. 不要打開 `tone_lite_answer_key.json`，也不要看 `tone_lite_splits.json` 的 dev／test 來猜答案。
4. 標完後，等至少 30 分鐘，再做 **delayed self-review**：隨機挑 10 筆重標，記錄不一致。
5. 不一致的筆數與理由，寫在 `notes` 或告訴 agent。

## 檔案

- `tone_lite_dataset.jsonl`：inputs（可讀）
- `tone_lite_labels.json`：你的 labels（你填）
- `tone_lite_splits.json`：train／dev／test（judge run 時才用）
- `tone_lite_answer_key.json`：spoiler，標完與 judge run 完再開
