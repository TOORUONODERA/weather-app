from flask import Flask, render_template_string
import requests
import pandas as pd
from datetime import datetime

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

        # 欲しいカラム名を取得
        temp_col = next((col for col in df.columns if "の最高気温(℃)" in col), None)
        place_col = "地点"

        targets = ["江別", "札幌", "せたな", "今金", "豊中"]
        results = []

        for place in targets:
            df_filtered = df[df[place_col].str.contains(place, na=False)]
            if not df_filtered.empty:
                temp = df_filtered.iloc[0][temp_col]
                results.append(f"{place}の最高気温: {temp}℃")
            else:
                results.append(f"{place}のデータがありません")

        html = "<br>".join(results)

    except Exception as e:
        html = f"データ取得中にエラーが発生しました: {e}"

    return render_template_string(f"""
        <html>
        <head><title>今日の気温</title></head>
        <body>
        <h2>今日の気温（5地点）</h2>
        <p>{html}</p>
        </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


