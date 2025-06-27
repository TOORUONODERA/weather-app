from flask import Flask, render_template_string 
import requests
import pandas as pd
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    base_url = "https://www.data.jma.go.jp/stats/data/mdrr/tem_rct/alltable/"
    csv_url = f"{base_url}mxtemsadext00_rct.csv"
    
    try:
        res = requests.get(csv_url)
        res.raise_for_status()
        with open("jma_temperature.csv", "wb") as f:
            f.write(res.content)

        try:
            df = pd.read_csv("jma_temperature.csv", encoding="shift_jis")
        except Exception:
            df = pd.read_csv("jma_temperature.csv", encoding="utf-8")

        targets = ["江別", "札幌", "せたな", "今金", "豊中"]
        place_col = "地点"
        temp_col = "27日の最高気温(℃)"
        hour_col = "27日の最高気温起時（時）"
        min_col = "27日の最高気温起時（分）"

        results = []

        for place in targets:
            df_filtered = df[df[place_col].str.contains(place, na=False)]
            if not df_filtered.empty:
                temp = df_filtered.iloc[0][temp_col]

                try:
                    hour = int(df_filtered.iloc[0][hour_col])
                    minute = int(df_filtered.iloc[0][min_col])
                    if hour == 0 and minute == 0:
                        raise ValueError
                    time_str = f"{hour:02d}:{minute:02d}"
                except Exception:
                    time_str = "情報なし"

                results.append(f"{place}の最高気温: {temp}℃（起時: {time_str}）")
            else:
                results.append(f"{place}のデータがありません")

        date_header = res.headers.get("Date")
        if date_header:
            dt_gmt = datetime.strptime(date_header, "%a, %d %b %Y %H:%M:%S GMT")
            dt_jst = dt_gmt + timedelta(hours=9)
            updated_str = dt_jst.strftime("%Y-%m-%d %H:%M:%S JST")
        else:
            updated_str = "不明"

        html = "<br>".join(results)

    except Exception as e:
        html = f"データ取得中にエラーが発生しました: {e}"
        updated_str = ""

    return render_template_string(f"""
        <html>
        <head>
            <title>今日の気温</title>
            <style>
                body {{
                    background-color: black;
                    color: white;
                    font-size: 24px;
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }}
                h2 {{
                    font-size: 36px;
                    margin-bottom: 20px;
                }}
                p {{
                    line-height: 1.6;
                }}
            </style>
        </head>
        <body>
            <h2>今日の気温（5地点）</h2>
            <p>データ更新日時: {updated_str}</p>
            <p>{html}</p>
        </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
