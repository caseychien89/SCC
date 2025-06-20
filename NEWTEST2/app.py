# app.py
from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
import joblib

# 建立 Flask 應用程式
app = Flask(__name__)

# --- 還原預測值的函數 (跟上面的一樣) ---
def invert_transformation(last_original_values, df_forecast):
    df_fc = df_forecast.copy()
    columns = last_original_values.index
    for col in columns:
        df_fc[str(col) + '_forecast'] = last_original_values[col] + df_fc[str(col) + '_forecast'].cumsum()
    return df_fc

# 載入我們之前儲存的模型包
try:
    model_package = joblib.load('var_model_package.joblib')
    model_results = model_package['model_results']
    last_diff_values = model_package['last_diff_values']
    last_original_values = model_package['last_original_values']
except FileNotFoundError:
    print("錯誤：找不到 var_model_package.joblib 檔案！")
    model_results = None

# 建立一個 API 端點(endpoint)，網址會是 /predict
@app.route('/predict', methods=['GET'])
def predict():
    if not model_results:
        return jsonify({"error": "模型尚未載入，請檢查伺服器日誌"}), 500

    # 從請求的網址參數中獲取要預測的季數，預設為4
    # 例如: .../predict?steps=8
    try:
        steps = int(request.args.get('steps', 4))
    except ValueError:
        return jsonify({"error": "steps 參數必須是整數"}), 400

    # 使用載入的模型和資料進行預測
    forecast_diff = model_results.forecast(y=last_diff_values, steps=steps)
    
    # 建立 DataFrame
    df_forecast = pd.DataFrame(forecast_diff, columns=last_original_values.index + '_forecast')

    # 還原預測值
    df_results = invert_transformation(last_original_values, df_forecast)
    
    # 準備回傳的 JSON 格式
    # 加上日期索引
    last_date = pd.to_datetime(last_original_values.name)
    forecast_index = pd.date_range(start=last_date, periods=steps + 1, freq='Q')[1:]
    df_results.index = forecast_index.strftime('%Y-%m-%d') # 轉成字串比較好傳輸

    # 只回傳 PIR 的預測結果
    pir_forecast = df_results[['PIR_forecast']]
    
    # 將結果轉成 JSON 格式回傳給 APP
    # to_dict('index') 會產生 { "日期1": {"PIR_forecast": 值1}, "日期2": ... } 的格式
    return jsonify(pir_forecast.to_dict('index'))

# 讓這個 Flask App 跑起來
if __name__ == '__main__':
    # 在本機測試時，可以執行 python app.py
    # port=5000 是 Flask 預設的埠號
    app.run(debug=True, port=5000)