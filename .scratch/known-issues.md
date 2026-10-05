# Known issues

## automationexercise.com — 導覽 "Products" 的 accessible name 含 PUA 字元

- **SUT / page**: https://automationexercise.com/ 首頁 header 導覽
- **Element**: `<a href="/products">` → `<i class="material-icons card_travel"
  style="font-size: 16px;">\ue8f8</i> Products`
- **現象**: header 導覽只有這一項用 Google Material Icons（其餘皆 Font Awesome）；其 `<i>`
  以文字節點直接夾帶 PUA 字元 `\ue8f8`，且無 `aria-hidden`。因此該連結的 accessible name
  為 `"\ue8f8 Products"`（非 `"Products"`），DOM `innerText`/`textContent` 亦同。
- **證據**: `get_by_role("link", name="Products")`（子字串）命中；
  `exact=True` 時 `"Products"` 命中 0、`"\ue8f8 Products"` 命中 1。
- **影響**: 精確比對／grounding 時容易被遮蔽；accessible name 含不可見字元，可能影響輔具朗讀。
- **發現於**: ticket 02 header grounding。
- **狀態**: open；處置未定（SUT 為第三方網站，我們無法修改其 HTML）。
