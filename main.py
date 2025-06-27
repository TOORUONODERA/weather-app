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
        res = requests.get(csv_url)
        res.raise_for_status()

        df = pd.read_csv(StringIO(res.text), encoding="shift_jis")
        df.columns = df.columns.str.strip()

        # Debug: カラム一覧をログで確認したい場合
        print("実際のカラム名:", df.columns.tolist())

        # 日付を自動取得してカラム名生成
        today = datetime.now().day
        temp_col = f"{today}日の最高気温(℃)"
        hour_col = f"{today}日の最高気温起時（時）"
        minute_col = f"{today}日の最高気温起時（分）"

        place_col = next((col for col in df.columns if "地点" in col), None)

        if not all([place_col, temp_col, hour_col, minute_col]):
            raise ValueError("必要なカラムが見つかりません")

        targets = ["江別", "札幌", "せたな", "今金", "豊中"]
        results = []

        for place in targets:
            row = df[df[place_col].astype(str).str.contains(place, na=False)]
            if not row.empty:
                data = row.iloc[0]
                temp = data[temp_col]
                hour = int(data[hour_col])
                minute = int(data[minute_col])
                results.append(f"<strong>{place}</strong>：{temp}℃（{hour}時{minute}分）")
            else:
                results.append(f"<strong>{place}</strong>：データなし")

        html = "<br><br>".join(results)

    except Exception as e:
        html = f"<span style='color:red;'>データ取得中にエラーが発生しました: {e}</span>"

    return render_template_string(f"""
        <html>
        <head><meta charset="UTF-8"><title>今日の気温</title></head>
        <body style="font-size: 28px; line-height: 2;">
            <h2>🌡️ 今日の気温（最高気温・観測時刻）</h2>
            <p>{html}</p>
        </body>
        </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
