# Tone judge — Lite B-toy metrics

## Setup

- 40 examples: 20 Pass / 20 Fail; 20 factual-correct / 20 factual-wrong.
- Split: train 8, dev 16, test 16; each balanced (4/4, 8/8, 8/8).
- Judge: `judge_tone.md`（目前版本）。
- Runner: agent-as-judge（不可重現；這是流程練習）。

## Dev

```text
n=16
TP=8  FN=0  TN=8  FP=0
TPR=1.000  95% Wilson CI [0.676, 1.000]
TNR=1.000  95% Wilson CI [0.676, 1.000]
```

一筆 label 修正：tl-014 原本標 Pass，跑完 dev 後改成 Fail；它符合 labeling guide
的「您確定嗎？」反諷例子。修正後 dev 沒有 disagreement。

## Test

```text
n=16
TP=8  FN=0  TN=8  FP=0
TPR=1.000  95% Wilson CI [0.676, 1.000]
TNR=1.000  95% Wilson CI [0.676, 1.000]
```

Test 只跑一次；沒有用來調 prompt。

## Combined

```text
n=32
TPR=1.000  95% Wilson CI [0.806, 1.000]
TNR=1.000  95% Wilson CI [0.806, 1.000]
```

## Baseline code proxy

Regex：

```text
嘿|喔|啦|囉|嗨嗨|收到|已記錄|自己看|就這樣|怎麼可能|怎麼會|可以啦
```

```text
combined: TPR=1.000, TNR=0.938
TNR 95% Wilson CI [0.717, 0.989]
```

Proxy 唯一漏掉的是 **tl-014**（「您確定是週六 20:00 嗎？…」）。Judge 抓到了這一筆。

解讀：judge 在這種細微的反諷案例上有價值；但這個 dataset 很小、很乾淨，regex 已經很接近，不能推論 judge 在真實世界也一樣好。

## Label quality

- 修正 tl-014 後，40/40 labels 與 answer key 一致。
- Delayed self-review 被跳過；tl-014 的不一致是跑完 dev 後才發現的。
- 這說明單一標註者仍需要第二遍或第二人。

## Caveats

- Agent-as-judge 不可重現；不能當 production 證據。
- 單一 annotator；沒有獨立第二標籤。
- 合成資料；n=32；CI 很寬（每類 16 筆）。
- Judge vs answer key 不是獨立驗證；answer key 是生成意圖，不是人類。
- Dev / test 全對可能代表資料太容易；不能推論 generalization。

## Audit note

**Judge Validation: Problem exists（production）**。Toy rehearsal 完成：

```text
dev/test 16/16, combined CI [0.806, 1.000]
baseline proxy TNR 0.938（漏 tl-014）
```

這是流程證據，不是 production evidence。
