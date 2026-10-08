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

## automationexercise.com — Google 廣告 vignette 干擾導覽

- **SUT / page**: https://automationexercise.com/（Google AdSense 插頁）
- **現象**: 頁面載入時 `adsbygoogle.js` 會注入全螢幕廣告插頁並把 URL 加上
  `#google_vignette`，遮住 header；點連結被吃掉，導覽不發生 → 測試間歇性失敗。
- **證據**: 失敗時 `to_have_url(.../test_cases)` 實際值為
  `https://automationexercise.com/#google_vignette`；約每 3 次出現 1 次。
- **處置**: 在 `tests/conftest.py` 以 autouse fixture 於 BrowserContext 網路層攔截並 `abort()`
  廣告網域（`googlesyndication.com`、`doubleclick.net` 等）；`test_test_cases.py` 連跑 6/6 穩定。
- **發現於**: Stage A（TC-ENG-004）。
- **狀態**: mitigated（網路層封鎖）；SUT 為第三方網站，無法修改其 HTML。
