# Playwright 的 name 比對與 snapshot 顯示會藏住隱藏字元

`get_by_role("link", name="Products")` 會通過，但該連結的 accessible name 其實是
`"\ue8f8 Products"`——Playwright 的 name 預設是「大小寫無關、子字串」比對，子字串照樣
命中，把污染藏住；要 `exact=True` 才露餡。而 `playwright-cli` 的 snapshot 只呈現「人看的
渲染結果」，PUA/不可見字元會被吃掉，畫面上像乾淨的 `" Products"`，只有 `repr()` 才看得到
`\ue8f8`。

影響後續：grounding 與斷言時，(1) 要精確比對就用 `exact=True`；(2) 懷疑有隱藏字元時一律
看 `repr()`，不要相信 snapshot／終端的視覺呈現。這決定了能否正確判斷「被測對象的
accessible name 到底乾淨不乾淨」。

## Evidence

`banner.get_by_role("link", name="Products", exact=True).count()` → 0；
`name="\ue8f8 Products", exact=True` → 1；`innerHTML` 含文字節點 `\ue8f8`（非 CSS
`::before`，`aria-hidden` 為 None）。

## Implications

- 之後做「以 accessible name 當 seam」的斷言時，要留意子字串比對會掩蓋污染。
- 建議把「不信任渲染、改看 repr」當成 grounding 的固定檢查習慣。
