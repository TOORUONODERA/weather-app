from flask import Flask, render_template_string
import requests
import pandas as pd
from io import StringIO
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    base_url = "https://www.data.jma.go.jp/stats/data/mdrr/tem_rct/alltable/"
    csv_url = f"{base_url}mxtemsadext00_rct.csv"
    try:
        # データ取得
        res = requests.get(csv_url)
        res.raise_for_status()

        # BOM対応で文字列化
        csv_text = res.content.decode("shift_jis_sig", errors="ignore")

        # ファイルに保存（ログや手動確認用、なくても動く）
        with open("jma_temperature.csv", "w", encoding="utf-8") as f:
            f.write(csv_text)

        # DataFrame作成
        df = pd.read_csv(StringIO(csv_text))

        # 列名確認
        if "地点" not in df.columns:
            return f"<p>エラー：'地点'列がCSVに存在しません。列名一覧：{df.columns.tolist()}</p>"

        # 最高気温の列名を探す
        temp_col = next((col for col in df.columns if "の最高気温(℃)" in col or "の最高気温(℃)" in col.replace("（","(").replace("）",")")), None)
        if temp_col is None:
            return f"<p>エラー：最高気温の列が見つかりません。列名一覧：{df.columns.tolist()}</p>"

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

