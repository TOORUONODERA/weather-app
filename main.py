from flask import Flask, render_template_string 
import requests
import pandas as pd

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

        # デバッグ用：カラム一覧（必要ならコメントアウトしてOK）
        # print(df.columns.tolist())

        # 時間に相当しそうなカラムを探す例（以下は一例です）
        time_col = next((col for col in df.columns if "日時" in col or "時間" in col or "基準" in col), None)

        temp_col = next((col for col in df.columns if "の最高気温(℃)" in col), None)
        place_col = "地点"

        targets = ["江別", "札幌", "せたな", "今金", "豊中"]
        results = []

        # 時間表示
        if time_col is not None:
            # 一般的に時間情報は全行同じか先頭だけ表示することが多い
            time_val = df.iloc[0][time_col]
            results.append(f"データ日時: {time_val}")
        else:
            results.append("データ日時情報はありません")

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

