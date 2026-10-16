# 存股看板

給長輩看的大字持股頁面（0050、00646），顯示目前總值、買進以來總獲利，以及近三個月的獲利走勢。

- `index.html`：頁面本身，打開時讀 `data.json`
- `data.json`：持股（張數、均價）與每日收盤價
- `scripts/update_prices.py`：從證交所抓最新股價，更新 `data.json`
- `.github/workflows/update-prices.yml`：交易日自動執行更新

## 修改持股

加碼或賣出時，直接編輯 `data.json` 裡 `holdings` 的 `lots`（張數）和 `avgCost`（均價）。

## 手動更新股價

到 GitHub 的 Actions 分頁 →「更新股價」→ Run workflow。

股價資料來自臺灣證券交易所，僅供參考，金額未扣手續費與稅。
