from flask import Flask, render_template_string 
import requests
import pandas as pd
from datetime import datetime
import pytz

app = Flask(__name__)

@app.route('/')
def index():
    base_url = "https://www.data.jma.go.jp/stats/data/mdrr/tem_rct/alltable/"
    csv_url = f"{base_url}mxtemsadext00_rct.csv"
    
    try:
        # CSV取得して保存
        res = requests.get(csv_url)
        res.raise_for_status()
        with open("jma_temperature.csv", "wb") as f:
            f.write(res.content)
        
        # 正しい文字コードで読み込み
        try:
            df = pd.read_csv("jma_temperature.csv", encoding="shift_jis")
        except Exception:
            df = pd.read_csv("jma_temperature.csv", encoding="utf-8")

        # 今日の日付（日本時間）を取得して、列名を動的に作成
        today = datetime.now(pytz.timezone('Asia/Tokyo')).day
        temp_col = f"{today}日の最高気温(℃)"
        hour_col = f"{today}日の最高気温起時（時）"
        minute_col = f"{today}日の最高気温起時（分）"
        place_col = "地点"

        # 対象地点
        targets = ["江別", "札幌", "せたな", "今金", "豊中"]
        results = []

        for place in targets:
            df_filtered = df[df[place_col].str.contains(place, na=False)]
            if not df_filtered.empty:
                row = df_filtered.iloc[0]
                temp = row[temp_col]
                hour = int(row[hour_col]) if not pd.isna(row[hour_col]) else None
                minute = int(row[minute_col]) if not pd.isna(row[minute_col]) else None
                if hour is not None and minute is not None:
                    time_str = f"{hour:02d}:{minute:02d}"
                else:
                    time_str = "情報なし"
                results.append(f"{place}の最高気温: {temp}℃（起時: {time_str}）")
            else:
                results.append(f"{place}のデータがありません")

        # データ取得日時（HTTPヘッダーのDate値）
        update_time = res.headers.get('Date', '不明')
        try:
            update_time_dt = datetime.strptime(update_time, "%a, %d %b %Y %H:%M:%S GMT")
            update_time_jst = update_time_dt + pd.Timedelta(hours=9)
            update_str = update_time_jst.strftime("%Y-%m-%d %H:%M:%S JST")
        except Exception:
            update_str = update_time

        html = "<br>".join(results)

    except Exception as e:
        html = f"データ取得中にエラーが発生しました: {e}"

    return render_template_string(f"""
        <html>
        <head>
            <title>今日の気温</title>
            <style>
                body {{
                    background-color: black;
                    color: white;
                    font-size: 20px;
                    padding: 20px;
                }}
            </style>
        </head>
        <body>
        <h2>今日の気温（5地点）</h2>
        <p>データ更新日時: {update_str}</p>
        <p>{html}</p>
        </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

