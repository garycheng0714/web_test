# Evals 資源

## Knowledge

- [Article: "Your AI Product Needs Evals" by Hamel Husain](https://hamel.dev/blog/posts/evals/index.html)
  這門課的骨架：error analysis 先於 evaluator，用真實 traces 找 failure modes。
  Use for: 建立整體流程與「為什麼」。
- [Article: "LLM Evals FAQ" by Hamel Husain](https://hamel.dev/blog/posts/evals-faq/)
  常見誤解與實務問答：vanity metrics、judge 的盲點、資料量。
  Use for: 遇到「這樣做對嗎」的疑問時查。
- [Article: "Creating an LLM Judge That Drives Business Results" by Hamel Husain](https://hamel.dev/blog/posts/llm-judge/)
  Binary judge、few-shot、TPR/TNR 校準與 bias correction 的完整範例。
  Use for: Lesson 0005–0006。
- [Article: "A Field Guide to Improving AI Products" by Hamel Husain](https://hamel.dev/blog/posts/field-guide/)
  從 trace review 到產品改進的實務流程。
  Use for: 把 eval 結果轉成修正動作。
- [Paper: "Who Validates the Validators? Aligning LLM-Assisted Evaluation of LLM Outputs with Human Preferences"](https://arxiv.org/abs/2404.12272)
  為什麼 failure categories 要從觀察來，而不是從研究術語借用。
  Use for: Lesson 0003 與 audit 的立論。
- [筆記: Arize Phoenix 研究](reference/phoenix.md)
  Phoenix 的架構、四項能力、與 Pydantic AI / pytest 的接點、限制。
  Use for: 判斷它的 trace / eval / experiment 能不能放進你的流程；目前只讀文件，未實跑。

## Wisdom (Communities)

- 尚未選定。先以 trace review 與課堂練習累積判斷力；等你有真實專案再找社群。

## Gaps

- 沒有真實 production traces；目前用合成的玩具資料。
- 沒有可直接參與的高訊號 evals 社群。
- Phoenix 已讀官方文件（見 Knowledge 的筆記），但尚未實跑；Braintrust、LangSmith 仍未查。
