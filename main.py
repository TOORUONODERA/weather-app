from flask import Flask, render_template_string
import pandas as pd
import requests
from io import StringIO
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    base_url = "https://www.data.jma.go.jp/stats/data/mdrr/tem_rct/alltable/"
    csv_url = f"{base_url}mxtemsadext00_rct.csv"
    try:
        # 気象庁のCSVデータを取得
        res = requests.get(csv_url)
        res.raise_for_status()

        # CSVデータをDataFrameに読み込み（shift_jisエンコーディング）
        df = pd.read_csv(StringIO(res.text), encoding="shift_jis")

        # 今日の日付（例：27日）を取得
        today = datetime.now()
        day = today.day

        # 今日の日付を使った「最高気温」列名を作成
        temp_col = f"{day}日の最高気温(℃)"  # 例: "27日の最高気温(℃)"

        place_col = "地点"  # 地点名の列
        targets = ["江別", "札幌", "せたな", "今金", "豊中"]  # 取得したい地点名リスト

        results = []
        for place in targets:
            # 地点列に対象文字列が含まれる行を抽出
            df_filtered = df[df[place_col].str.contains(place, na=False)]
            if not df_filtered.empty:
                temp = df_filtered.iloc[0][temp_col]
                results.append(f"{place}の最高気温: {temp}℃")
            else:
                results.append(f"{place}のデータがありません")

        # 結果をHTMLの改行で結合
        html = "<br>".join(results)

    except Exception as e:
        html = f"データ取得中にエラーが発生しました: {e}"

    # HTMLを返す
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

