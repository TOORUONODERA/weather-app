from flask import Flask, render_template_string
import requests
import pandas as pd
from io import StringIO
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    csv_url = "https://www.data.jma.go.jp/stats/data/mdrr/tem_rct/alltable/mxtemsadext00_rct.csv"
    try:
        # CSVデータ取得
        res = requests.get(csv_url)
        res.raise_for_status()
        
        # CSV読み込み（エンコーディングとパース）
        df = pd.read_csv(StringIO(res.text), encoding="shift_jis")

        # カラム名をすべてクリーンアップ（前後の空白など）
        df.columns = df.columns.str.strip()

        # 必要なカラム名の特定（多少の揺れに耐えるように）
        place_col = next((col for col in df.columns if "地点" in col), None)
        temp_col = next((col for col in df.columns if "最高気温(℃)" in col), None)
        hour_col = next((col for col in df.columns if "最高気温起時（時）" in col), None)
        minute_col = next((col for col in df.columns if "最高気温起時（分）" in col), None)

        if not all([place_col, temp_col, hour_col, minute_col]):
            raise ValueError("必要なカラムが見つかりません")

        # 表示する地点
        targets = ["江別", "札幌", "せたな", "今金", "豊中"]
        results = []

        for place in targets:
            match = df[df[place_col].astype(str).str.contains(place)]
            if not match.empty:
                row = match.iloc[0]
                temp = row[temp_col]
                hour = int(row[hour_col])
                minute = int(row[minute_col])
                results.append(f"<strong>{place}</strong>：{temp}℃（{hour}時{minute}分）")
            else:
                results.append(f"<strong>{place}</strong>：データがありません")

        html = "<br><br>".join(results)

    except Exception as e:
        html = f"<span style='color:red;'>データ取得中にエラーが発生しました: {e}</span>"

    return render_template_string(f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <title>今日の気温</title>
        </head>
        <body style="font-size: 28px; line-height: 2;">
            <h2>🌡️ 今日の気温（最高気温・観測時刻）</h2>
            <p>{html}</p>
        </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


