# Jev quality checks — experiment index

研究問題：Jev 能不能對 test-case 產出做 AC 對齊、step 品質、expected result 可觀察性？

Jev 是 text-only。這個實驗只給它 PRD 文字與 cases，沒有圖片、screen descriptions 或附錄 A parsing。

## Variants

| Variant | 目的 | Result |
|---|---|---|
| v1 | 基準：groundedness + 基本 step/observable | [`RESULTS-v1.md`](RESULTS-v1.md) |
| v2 | 加 `reachable` | [`RESULTS-v2.md`](RESULTS-v2.md) |
| v3 | B4 改成 `complete` | [`RESULTS-v3.md`](RESULTS-v3.md) |
| v4b | 移除 S1–S4，只留 PRD 文字 | [`RESULTS-v4b.md`](RESULTS-v4b.md) |
| v4c | 再移除附錄 A | [`RESULTS-v4c.md`](RESULTS-v4c.md) |
| S1–S3 | 稀疏 PRD（`login-smoke.md`） | [`RESULTS-login-smoke.md`](RESULTS-login-smoke.md) |

## 關鍵發現

- B4 的缺陷是 **step 不完整**，不是控件不存在，也不是頁面不可達。
  - `reasonable` 0.84 → 漏掉
  - `reachable` 0.80 → 漏掉
  - `complete` 0.12 → 抓到
- 對 `register-login.md`，S1–S4 與附錄 A 都是多餘的；PRD 文字本身已足夠。
- 稀疏 PRD 可以使用，但 cases 只能断言 PRD 明說的行為；Jev 會 flag 超出 evidence 範圍的 expected result。
- 最終決策：票 18 的三個檢查，沒有 `reachable`，`JEV_MODEL` pin 在 `jev-1.13.0`。

## 檔案

```text
.
├── RESULTS-v1.md .. RESULTS-v4c.md
├── RESULTS-login-smoke.md
├── artifacts/        # 原始 request/response JSON，本機用，未進版控
└── scripts/          # 產生 request 的腳本
```

`artifacts/` 被本目錄的 `.gitignore` 忽略。若需要原始 Jev verdict 與 token usage，請在本地保留，或用 scripts 重跑。

## 重跑

```bash
python3 scripts/build_request.py
python3 ../.opencode/skills/jev/scripts/jev.py decide artifacts/request-v2.json \
  --provider typesafe --dry-run
```

實際呼叫前先確認 `TYPESAFE_API_KEY` 存在；不要把 key 寫進 request 或 commit。

## 相關文件

- [`learn/reference/jev-quality-review.md`](../../learn/reference/jev-quality-review.md) — canonical research note
- [`learn/learning-records/0009-pstack-learning-priorities.md`](../../learn/learning-records/0009-pstack-learning-priorities.md) — learning record
- [Ticket 18](../prd-to-tests/issues/18-add-jev-quality-checks.md) — implementation ticket
