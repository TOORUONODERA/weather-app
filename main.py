import requests
import pandas as pd
from flask import Flask, render_template_string
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

@app.route('/')
def index():
    csv_url = "https://www.data.jma.go.jp/stats/data/mdrr/tem_rct/alltable/mxtemsadext00_rct.csv"
    try:
        res = requests.get(csv_url)
        res.raise_for_status()

        # 更新日時をGMTからJSTに変換
        last_modified_str = res.headers.get('Last-Modified', None)
        if last_modified_str:
            dt_utc = datetime.strptime(last_modified_str, "%a, %d %b %Y %H:%M:%S %Z")
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
            jst = timezone(timedelta(hours=9))
            dt_jst = dt_utc.astimezone(jst)
            last_modified = dt_jst.strftime("%Y-%m-%d %H:%M:%S JST")
        else:
            last_modified = "不明"

        with open("jma_temperature.csv", "wb") as f:
            f.write(res.content)

        try:
            df = pd.read_csv("jma_temperature.csv", encoding="shift_jis")
        except Exception:
            df = pd.read_csv("jma_temperature.csv", encoding="utf-8")

        print(df.columns.tolist())  # ここでカラム名を確認してください

        temp_col = next((col for col in df.columns if "の最高気温(℃)" in col), None)
        
        # 起時の正確なカラム名をここにコピーしてください（例："起時"）
        time_col = "起時"
        
        place_col = "地点"
        targets = ["江別", "札幌", "せたな", "今金", "豊中"]
        results = []

        for place in targets:
            df_filtered = df[df[place_col].str.contains(place, na=False)]
            if not df_filtered.empty:
                temp = df_filtered.iloc[0][temp_col]
                # 起時カラムがあるかをチェックして値を取得
                time_val = df_filtered.iloc[0][time_col] if time_col in df.columns else "情報なし"
                results.append(f"{place}の最高気温: {temp}℃（起時: {time_val}）")
            else:
                results.append(f"{place}のデータがありません")

        html = "<br>".join(results)

    except Exception as e:
        html = f"データ取得中にエラーが発生しました: {e}"
        last_modified = ""

    return render_template_string(f"""
    <html>
    <head><title>今日の気温</title></head>
    <body>
    <h2>今日の気温（5地点）</h2>
    <p>データ更新日時: {last_modified}</p>
    <p>{html}</p>
    </body>
    </html>
    """)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

