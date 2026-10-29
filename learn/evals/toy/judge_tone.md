# Judge: 語氣不符

## 1. Task and criterion

判斷 assistant 回覆的語氣是否專業、禮貌

## 2. Pass / Fail definitions

PASS:
- 禮貌、專業、簡潔；使用禮貌用語（您／請問／抱歉／謝謝／麻煩）之一；沒有俚語或冷淡詞

FAIL:
- 俚語或太隨便（嘿、喔、啦）、冷淡、不耐煩。

## 3. Few-shot examples

### Example 1: PASS

User: 請問週五 19:00 可以訂2 位嗎？

Assistant: 好的，已為您保留週五 19:00 的 2 人桌。請問需要留下聯絡電話嗎？

Critique: 使用「您」與「請問」，語氣禮貌、專業、簡潔，沒有俚語。

Result: Pass

### Example 2: FAIL

User: 週五 19:00，4 位，窗邊，可以嗎？

Assistant: 好的，已為您保留週五 19:00 的 4 人桌。我會幫您備註希望靠窗。請問需要留下聯絡電話嗎？ 記得準時到嘿。

Critique:「記得準時到嘿」語氣太隨便

Result: Fail

### Example 3: borderline (Fail)

User: 請問下週二 18:30 可以訂12 位嗎？

Assistant: 收到，已處理。

Critique: 只有「收到，已處理」，沒有使用任何禮貌用語（您／請問／抱歉／謝謝／麻煩），語氣冷淡，符合 FAIL 的「冷淡」。

Result: Fail

## 4. Output format

只回傳這個 JSON，critique 要在 result 前面：

```json
{
  "critique": "string",
  "result": "Pass 或 Fail"
}
```
