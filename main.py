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

        # 更新日時をHTTPヘッダーから取得（無ければ「不明」）
        last_modified = res.headers.get('Last-Modified', '不明')

        with open("jma_temperature.csv", "wb") as f:
            f.write(res.content)
        
        try:
            df = pd.read_csv("jma_temperature.csv", encoding="shift_jis")
        except Exception:
            df = pd.read_csv("jma_temperature.csv", encoding="utf-8")

        temp_col = next((col for col in df.columns if "の最高気温(℃)" in col), None)
        place_col = "地点"
        time_col = "起時"  # 「起時」カラムがあれば表示

        targets = ["江別", "札幌", "せたな", "今金", "豊中"]
        results = []

        for place in targets:
            df_filtered = df[df[place_col].str.contains(place, na=False)]
            if not df_filtered.empty:
                temp = df_filtered.iloc[0][temp_col]
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

