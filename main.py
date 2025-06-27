from flask import Flask, render_template_string
import pandas as pd
import requests
from io import StringIO

app = Flask(__name__)

@app.route('/')
def index():
    csv_url = "https://www.data.jma.go.jp/stats/data/mdrr/tem_rct/alltable/mxtemsadext00_rct.csv"
    try:
        # CSV取得
        res = requests.get(csv_url)
        res.raise_for_status()

        # pandasで読み込み（Shift-JIS）
        df = pd.read_csv(StringIO(res.content.decode("shift_jis")))

        # 欲しい列を探す
        temp_col = next((col for col in df.columns if "の最高気温" in col), None)
        place_col = "地点"

        targets = ["江別", "札幌", "せたな", "今金", "豊中"]
        results = []

        for place in targets:
            match = df[df[place_col].str.contains(place, na=False)]
            if not match.empty:
                temp = match.iloc[0][temp_col]
                results.append(f"{place}の最高気温：{temp}℃")
            else:
                results.append(f"{place}のデータが見つかりません")

        html_content = "<br>".join(results)

    except Exception as e:
        html_content = f"データ取得中にエラーが発生しました: {e}"

    # HTML生成（大きな文字サイズ）
    return render_template_string(f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>今日の気温</title>
    </head>
    <body style="font-size:32px; line-height:1.8; font-family:sans-serif; padding:30px;">
        <h2 style="font-size:40px;">今日の気温（5地点）</h2>
        <p>{html_content}</p>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)


