# app.py

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg') # 非常重要！讓 Matplotlib 在沒有 GUI 的伺服器環境下也能運作
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm # <--- 新增：用於管理字型
from statsmodels.tsa.api import VAR
import warnings
from flask import Flask, render_template, request
import io
import base64
from functools import lru_cache

# --- 初始化 Flask App ---
app = Flask(__name__)

# --- 核心模型邏輯 ---

# 忽略警告
warnings.filterwarnings("ignore", category=FutureWarning)

def convert_minguo_to_date(minguo_q):
    """將民國年季轉換為西元日期"""
    year_str = minguo_q[:3]
    quarter = minguo_q[4]
    gregorian_year = int(year_str) + 1911
    quarter_month_map = {'1': '03-31', '2': '06-30', '3': '09-30', '4': '12-31'}
    month_day = quarter_month_map[quarter]
    return f"{gregorian_year}-{month_day}"

# 使用 lru_cache 來快取模型訓練結果，避免每次請求都重新訓練，大幅提升效能
@lru_cache(maxsize=1)
def get_model_data():
    """載入數據、進行前處理、並訓練 VAR 模型"""
    print("--- 正在載入數據並訓練模型 (此過程只會在第一次請求時執行) ---")
    df = pd.read_csv('csv.csv', encoding='utf-8-sig')
    
    # 資料前處理
    df['date'] = df['年度季別'].apply(convert_minguo_to_date)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    df_model = df[['CPI', 'PIR']]
    
    # 差分
    df_diff = df_model.diff().dropna()
    
    # 建立與訓練 VAR 模型
    model = VAR(df_diff)
    # 為了部署穩定，我們直接指定一個延遲期數。
    # 從 Tkinter 程式的分析結果來看，4 是一個合理的選擇。
    p = 4 
    results = model.fit(p)
    
    # 儲存預測所需的重要資訊
    model_package = {
        'df_model': df_model,
        'df_diff': df_diff,
        'model_results': results
    }
    print("--- 模型訓練完成 ---")
    return model_package

def make_prediction(steps):
    """使用訓練好的模型進行預測"""
    model_data = get_model_data()
    df_model = model_data['df_model']
    df_diff = model_data['df_diff']
    results = model_data['model_results']

    # 進行預測
    lag_order = results.k_ar
    forecast_input = df_diff.values[-lag_order:]
    forecast_diff = results.forecast(y=forecast_input, steps=steps)
    
    # 還原預測值
    df_forecast = pd.DataFrame(forecast_diff, columns=df_model.columns + '_forecast')
    
    last_original_values = df_model.iloc[-1]
    df_results = df_forecast.copy()
    for col in df_model.columns:
        df_results[str(col) + '_forecast'] = last_original_values[col] + df_results[str(col) + '_forecast'].cumsum()

    last_date = df_model.index[-1]
    forecast_index = pd.date_range(start=last_date, periods=steps + 1, freq='Q')[1:]
    df_results.index = forecast_index
    
    return df_results

def create_plot(df_model, df_results):
    """生成包含歷史數據和預測結果的圖表（已修正中文亂碼問題）"""
    
    # --- 解決中文亂碼的關鍵部分 ---
    # 指定我們專案中 `fonts` 資料夾下的字型檔路徑
    font_path = './fonts/NotoSansTC-Regular.otf'
    
    # 載入字型檔
    try:
        my_font = fm.FontProperties(fname=font_path)
    except FileNotFoundError:
        print(f"警告：字型檔未找到於 {font_path}。圖表標題可能顯示亂碼。")
        my_font = fm.FontProperties() # 如果找不到，使用預設字型以防程式崩潰
    # --- 結束 ---

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df_model.index, df_model['PIR'], label='歷史 PIR')
    ax.plot(df_results.index, df_results['PIR_forecast'], label='預測 PIR', color='red', linestyle='--')
    
    # 在所有需要顯示中文的地方，加上 fontproperties=my_font 參數
    ax.set_title("PIR 歷史數據與預測結果", fontproperties=my_font, fontsize=16)
    ax.set_xlabel("年份", fontproperties=my_font, fontsize=12)
    ax.set_ylabel("PIR 指數", fontproperties=my_font, fontsize=12)
    
    # 設定圖例的字型
    ax.legend(prop=my_font)
    
    ax.grid(True)
    fig.tight_layout()
    
    # 將圖表儲存到記憶體中
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    
    # 將圖片轉換為 Base64 字串，以便在 HTML 中顯示
    img_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    plt.close(fig) # 關閉圖表釋放記憶體
    return img_base64

# --- Flask 路由 (Web Pages) ---

@app.route('/', methods=['GET', 'POST'])
def index():
    # 首次載入或有請求時，確保模型已準備好
    model_data = get_model_data()
    df_model = model_data['df_model']
    
    # 如果是 POST 請求 (使用者提交了表單)
    if request.method == 'POST':
        try:
            steps = int(request.form.get('steps', 8)) # 從表單獲取季數，預設為 8
        except (ValueError, TypeError):
            steps = 8
            
        # 進行預測
        df_results = make_prediction(steps)
        
        # 生成圖表
        plot_url = create_plot(df_model, df_results)
        
        # 準備要傳送到 HTML 的預測數據
        predictions = df_results[['PIR_forecast']].reset_index()
        predictions['index'] = predictions['index'].dt.strftime('%Y-%m-%d')
        predictions = predictions.to_dict(orient='records')
        
        return render_template('index.html', 
                               steps=steps, 
                               predictions=predictions, 
                               plot_url=plot_url)
    
    # 如果是 GET 請求 (第一次載入頁面)
    else:
        # 預設預測 8 季並顯示
        steps = 8
        df_results = make_prediction(steps)
        plot_url = create_plot(df_model, df_results)
        
        predictions = df_results[['PIR_forecast']].reset_index()
        predictions['index'] = predictions['index'].dt.strftime('%Y-%m-%d')
        predictions = predictions.to_dict(orient='records')

        return render_template('index.html', 
                               steps=steps, 
                               predictions=predictions, 
                               plot_url=plot_url)

# --- 讓 Gunicorn 可以運行 ---
if __name__ == '__main__':
    # 這行僅用於在本機開發測試，Render 會直接使用 gunicorn
    app.run(debug=True, port=5001)