"""抓證交所最新股價，更新 data.json。由 GitHub Actions 定時執行。"""
import json
import sys
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data.json"
TPE = timezone(timedelta(hours=8))
KEEP_DAYS = 100  # 頁面畫近三個月，多留一點


def fetch_quotes(codes):
    ex_ch = "|".join(f"tse_{c}.tw" for c in codes)
    url = f"https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch={ex_ch}&json=1&delay=0"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://mis.twse.com.tw/stock/index.jsp",
    })
    with urllib.request.urlopen(req, timeout=20) as r:
        payload = json.load(r)
    out = {}
    for row in payload.get("msgArray", []):
        def num(v):
            try:
                return float(v)
            except (TypeError, ValueError):
                return None
        price = num(row.get("z"))
        if price is None:  # 這一刻沒有成交，用最佳買價
            price = num((row.get("b") or "").split("_")[0])
        prev = num(row.get("y"))
        d = row.get("d")  # 例如 20261016
        if price and prev and d:
            out[row["c"]] = {"price": price, "prev": prev,
                             "date": f"{d[:4]}-{d[4:6]}-{d[6:]}", "time": row.get("t", "")}
    return out


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    codes = [h["code"] for h in data["holdings"]]
    quotes = fetch_quotes(codes)
    if set(quotes) != set(codes):
        print("查不到完整股價，這次不更新：", quotes)
        return 0

    day = quotes[codes[0]]["date"]
    now = datetime.now(TPE)
    for h in data["holdings"]:
        q = quotes[h["code"]]
        h["price"], h["prevClose"] = q["price"], q["prev"]

    closed = day != now.strftime("%Y-%m-%d") or now.strftime("%H:%M") >= "13:30"
    data["updatedAt"] = f"{day} 收盤" if closed else f"{day} {now:%H:%M} 盤中"

    hist = [r for r in data["history"] if r["date"] != day]
    hist.append({"date": day, "prices": {c: quotes[c]["price"] for c in codes}})
    cutoff = (date.fromisoformat(day) - timedelta(days=KEEP_DAYS)).isoformat()
    data["history"] = sorted((r for r in hist if r["date"] >= cutoff), key=lambda r: r["date"])

    text = "{\n" + ",\n".join([
        f' "updatedAt": {json.dumps(data["updatedAt"], ensure_ascii=False)}',
        ' "holdings": [\n  ' + ",\n  ".join(json.dumps(h, ensure_ascii=False) for h in data["holdings"]) + "\n ]",
        ' "history": [\n  ' + ",\n  ".join(json.dumps(r, ensure_ascii=False) for r in data["history"]) + "\n ]",
    ]) + "\n}\n"
    DATA.write_text(text, encoding="utf-8")
    print("已更新：", data["updatedAt"], {c: quotes[c]["price"] for c in codes})
    return 0


if __name__ == "__main__":
    sys.exit(main())
