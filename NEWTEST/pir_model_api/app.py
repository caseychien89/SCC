from flask import Flask, request, jsonify
import pandas as pd
import numpy as np
import pickle
import io

# 初始化 Flask App
app = Flask(__name__)

# --- 載入模型和必要的數據 ---
# 載入訓練好的VAR模型
try:
    with open('var_model.pkl', 'rb') as f:
        model = pickle.load(f)
    # 從模型中獲取落後期數，這是預測時需要的
    lag_order = model.k_ar 
except FileNotFoundError:
    print("錯誤: 'var_model.pkl' 不存在！請先執行分析程式生成模型。")
    exit()

# 我們需要原始數據來計算預測時的起點（最後幾期的差分值）
csv_data = """item,年度季別,CPI,PIR
1,091Q1,81.64,4.47
2,091Q2,81.71,4.43
3,091Q3,81.71,4.15
4,091Q4,81.98,4.26
5,092Q1,81.46,4.41
6,092Q2,81.61,4.43
7,092Q3,81.22,4.5
8,092Q4,81.82,4.59
9,093Q1,81.88,4.7
10,093Q2,82.58,4.7
11,093Q3,83.57,4.63
12,093Q4,83.33,4.84
13,094Q1,83.17,5.01
14,094Q2,84.33,5.25
15,094Q3,86.11,5.25
16,094Q4,85.40,4.97
17,095Q1,84.30,5.19
18,095Q2,85.61,5.17
19,095Q3,85.82,5.3
20,095Q4,85.32,4.97
21,096Q1,85.12,5.15
22,096Q2,85.83,5.46
23,096Q3,87.07,5.33
24,096Q4,89.15,5.76
25,097Q1,88.18,6.13
26,097Q2,89.43,6.25
27,097Q3,91.01,6.09
28,097Q4,90.81,5.87
29,098Q1,88.17,6.19
30,098Q2,88.67,6.45
31,098Q3,89.78,6.55
32,098Q4,89.67,6.67
33,099Q1,89.30,6.8
34,099Q2,89.64,6.99
35,099Q3,90.12,7.01
36,099Q4,90.66,7.11
37,100Q1,90.44,7.31
38,100Q2,91.11,7.3
39,100Q3,91.33,7.29
40,100Q4,91.96,7.29
41,101Q1,91.6,7.44
42,101Q2,92.61,8.05
43,101Q3,94.02,7.46
44,101Q4,93.66,7.79
45,102Q1,93.25,8.35
46,102Q2,93.35,8.95
47,102Q3,94.06,8.95
48,102Q4,94.18,8.37
49,103Q1,93.99,7.51
50,103Q2,94.88,8.34
51,103Q3,95.48,8.39
52,103Q4,94.97,8.41
53,104Q1,93.44,8.46
54,104Q2,94.21,8.69
55,104Q3,95.23,8.52
56,104Q4,95.27,8.51
57,105Q1,95.07,8.46
58,105Q2,95.47,8.97
59,105Q3,95.91,9.35
60,105Q4,96.98,9.32
61,106Q1,95.81,9.24
62,106Q2,96.01,9.46
63,106Q3,96.62,9.22
64,106Q4,97.37,9.16
65,107Q1,97.31,9.08
66,107Q2,97.66,9
67,107Q3,98.23,8.82
68,107Q4,97.82,8.57
69,108Q1,97.62,8.66
70,108Q2,98.45,8.79
71,108Q3,98.64,8.47
72,108Q4,98.50,8.58
73,109Q1,98.15,8.62
74,109Q2,97.49,8.66
75,109Q3,98.17,9.19
76,109Q4,98.46,9.2
77,110Q1,98.93,9.13
78,110Q2,99.57,9.07
79,110Q3,100.41,9.24
80,110Q4,101.09,9.46
81,111Q1,101.71,9.58
82,111Q2,103.00,9.69
83,111Q3,103.35,9.8
84,111Q4,103.72,9.61
85,112Q1,104.36,9.72
86,112Q2,105.10,9.82
87,112Q3,105.88,9.86
88,112Q4,106.71,9.97
89,113Q1,106.80,10.35
90,113Q2,107.41,10.65
91,113Q3,108.24,10.82
"""

def load_and_prepare_data(csv_string):
    # --- ▼▼▼ 這是唯一的修改處 ▼▼▼ ---
    # 使用 dtype 參數強制 '年度季別' 為字串類型
    df = pd.read_csv(io.StringIO(csv_string), dtype={'年度季別': str})
    # --- ▲▲▲ 修改結束 ▲▲▲ ---
    
    # 接下來的程式碼保持不變
    df = df.dropna(subset=['年度季別']) # 為保險起見，順便移除 '年度季別' 是空值的行
    df = df[['年度季別', 'CPI', 'PIR']]
    
    def parse_minguo_quarter(mq_str):
        year_str, quarter_str = mq_str.split('Q')
        year = int(year_str) + 1911
        quarter = int(quarter_str)
        month = (quarter - 1) * 3 + 1
        return pd.Timestamp(f'{year}-{month:02d}-01')

    df['Date'] = df['年度季別'].apply(parse_minguo_quarter)
    df.set_index('Date', inplace=True)
    df = df[['PIR', 'CPI']]
    return df

df_original = load_and_prepare_data(csv_data)
df_diff = df_original.diff().dropna()
last_known_diffs = df_diff.values[-lag_order:]
last_known_level = df_original.values[-1]


# --- 建立API端點 (Endpoint) ---
@app.route('/predict', methods=['POST'])
def predict():
    # 1. 獲取來自App的請求 (JSON格式)
    data = request.get_json()
    if not data or 'steps' not in data:
        return jsonify({'error': '無效的請求，需要提供 "steps" 參數'}), 400

    try:
        forecast_steps = int(data['steps'])
    except ValueError:
        return jsonify({'error': '"steps" 必須是一個整數'}), 400
    
    # 2. 使用模型進行預測
    forecasted_diffs = model.forecast(y=last_known_diffs, steps=forecast_steps)

    # 3. 將預測的差分值還原成絕對數值
    current_level = last_known_level.copy()
    forecasted_levels = []
    for diff in forecasted_diffs:
        current_level += diff
        forecasted_levels.append(current_level.tolist())

    # 4. 準備回傳給App的結果 (JSON格式)
    forecast_index = pd.date_range(start=df_original.index[-1], periods=forecast_steps + 1, freq='QS-OCT')[1:]
    
    results = []
    for i in range(forecast_steps):
        results.append({
            'quarter': forecast_index[i].strftime('%Y-Q') + str(forecast_index[i].quarter),
            'pir_forecast': round(forecasted_levels[i][0], 4),
            'cpi_forecast': round(forecasted_levels[i][1], 4)
        })

    return jsonify(results)

if __name__ == '__main__':
    # 在本機電腦上以 5000 port 啟動伺服器
    app.run(debug=True, host='0.0.0.0', port=5000)