# ==============================================================================
# Part 1 of 3: Imports and Data
# ==============================================================================
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import pandas as pd
import numpy as np
import io
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pickle # <--- 確保導入 pickle 函式庫

# 內建的CSV數據
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

# ==============================================================================
# Part 2 of 3: Data Loading and Core Analysis Function (with Model Saving)
# ==============================================================================

def load_and_prepare_data(csv_string):
    """讀取CSV字串並準備DataFrame"""
    df = pd.read_csv(io.StringIO(csv_string))
    df = df[['年度季別', 'CPI', 'PIR']]
    def parse_minguo_quarter(mq_str):
        year_str, quarter_str = mq_str.split('Q')
        year = int(year_str) + 1911
        quarter = int(quarter_str)
        month = (quarter - 1) * 3 + 1
        return pd.Timestamp(f'{year}-{month:02d}-01')
    df['Date'] = df['年度季別'].apply(parse_minguo_quarter)
    df.set_index('Date', inplace=True)
    df = df[['PIR', 'CPI']] # 將PIR設為第一個變數
    return df

def perform_var_analysis(df, forecast_steps):
    """
    執行完整的差分VAR模型分析，並將訓練好的模型儲存為 .pkl 檔案。
    """
    report = []
    
    # 步驟 0: 執行定態檢定，以證明為何需要差分
    report.append("--- 1. 定態檢定 (ADF Test) ---")
    def adf_test_report(series, name=''):
        result = adfuller(series.dropna())
        p_value = result[1]
        is_stationary = "定態 (Stationary)" if p_value <= 0.05 else "非定態 (Non-Stationary)"
        return f"變數 '{name}': p-value = {p_value:.4f} -> {is_stationary}"
    
    report.append(adf_test_report(df['PIR'], 'PIR (Level)'))
    report.append(adf_test_report(df['CPI'], 'CPI (Level)'))
    report.append(adf_test_report(df['PIR'].diff(), 'PIR (1st Diff)'))
    report.append(adf_test_report(df['CPI'].diff(), 'CPI (1st Diff)'))
    report.append("\n結論：因水平值非定態，差分後定態，故使用【差分VAR模型】。")

    # 步驟 1: 對數據進行一階差分
    df_diff = df.diff().dropna()

    # 步驟 2: 在差分後的數據上選擇最佳落後期數
    report.append("\n--- 2. 選擇差分VAR模型落後期數 ---")
    model_for_lag_selection = VAR(df_diff)
    lag_selection_results = model_for_lag_selection.select_order(maxlags=8)
    lag_order = lag_selection_results.aic
    report.append(f"根據AIC準則，選擇的最佳落後期為: {lag_order}")
    
    # 步驟 3: 訓練VAR模型
    report.append("\n--- 3. 訓練差分VAR模型 ---")
    model = VAR(df_diff)
    var_results = model.fit(lag_order) # <--- 訓練完成的模型物件
    report.append("模型摘要:")
    report.append(str(var_results.summary()))

    # --- ▼▼▼ 核心修改：儲存模型為 .pkl 檔案 ▼▼▼ ---
    try:
        model_filename = 'var_model.pkl'
        with open(model_filename, 'wb') as f: # 'wb' 代表 write binary (二進位寫入)
            pickle.dump(var_results, f)
        report.append(f"\n--- 模型已成功儲存為【{model_filename}】 ---")
    except Exception as e:
        report.append(f"\n--- 儲存模型失敗: {e} ---")
    # --- ▲▲▲ 核心修改結束 ▲▲▲ ---

    # 步驟 4: 預測未來的「差分值」(變動量)
    last_known_diffs = df_diff.values[-lag_order:]
    forecasted_diffs = var_results.forecast(y=last_known_diffs, steps=forecast_steps)

    # 步驟 5: 將預測的差分值還原成絕對數值
    report.append(f"\n--- 4. 預測未來 {forecast_steps} 季 ---")
    forecasted_levels = []
    last_known_level = df.values[-1] # 取得最後一筆已知的PIR和CPI數值
    
    for diff_prediction in forecasted_diffs:
        next_level = last_known_level + diff_prediction
        forecasted_levels.append(next_level)
        last_known_level = next_level # 更新最新值以供下次迭代使用

    forecast_array = np.array(forecasted_levels)
    forecast_index = pd.date_range(start=df.index[-1], periods=forecast_steps + 1, freq='QS-OCT')[1:]
    forecast_df = pd.DataFrame(forecast_array, index=forecast_index, columns=['PIR_Forecast', 'CPI_Forecast'])
    
    report.append("\n預測結果(絕對數值):")
    report.append(forecast_df.to_string(float_format="%.4f"))
    
    return "\n".join(report), df, forecast_df

# ==============================================================================
# Part 3 of 3: GUI Application Class
# ==============================================================================

class VarOnlyAnalyzerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("純VAR模型 PIR預測器 (含模型儲存)")
        self.geometry("1100x800")
        self.df = load_and_prepare_data(csv_data)
        self.create_widgets()
        self.initial_plot()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        control_frame = ttk.LabelFrame(main_frame, text="控制面板", padding="10")
        control_frame.pack(fill=tk.X, pady=5)
        ttk.Label(control_frame, text="輸入要預測的未來季數:").pack(side=tk.LEFT, padx=5)
        self.steps_entry = ttk.Entry(control_frame, width=10)
        self.steps_entry.insert(0, "4")
        self.steps_entry.pack(side=tk.LEFT, padx=5)
        self.run_button = ttk.Button(control_frame, text="執行VAR模型分析", command=self.run_analysis)
        self.run_button.pack(side=tk.LEFT, padx=10)
        results_frame = ttk.Frame(main_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        paned_window = ttk.PanedWindow(results_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)
        report_frame = ttk.LabelFrame(paned_window, text="分析報告", padding="5")
        self.report_text = scrolledtext.ScrolledText(report_frame, wrap=tk.WORD, width=70, font=("Courier New", 9))
        self.report_text.pack(fill=tk.BOTH, expand=True)
        self.report_text.insert(tk.END, "此程式專門使用差分後的VAR模型進行分析。\n請輸入預測季數並點擊按鈕。")
        self.report_text.config(state=tk.DISABLED)
        paned_window.add(report_frame, weight=1)
        plot_frame = ttk.LabelFrame(paned_window, text="預測圖表", padding="5")
        self.fig, self.ax = plt.subplots(figsize=(7, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        paned_window.add(plot_frame, weight=1)

    def initial_plot(self):
        self.ax.clear()
        self.ax.plot(self.df.index, self.df['PIR'], label='歷史PIR', color='blue')
        self.ax.set_title('歷史PIR數據')
        self.ax.set_xlabel('日期')
        self.ax.set_ylabel('PIR 指數')
        self.ax.legend()
        self.ax.grid(True)
        self.fig.tight_layout()
        self.canvas.draw()

    def run_analysis(self):
        try:
            steps = int(self.steps_entry.get())
            if steps <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("輸入錯誤", "請輸入一個正整數。")
            return
        self.run_button.config(state=tk.DISABLED)
        self.report_text.config(state=tk.NORMAL)
        self.report_text.delete('1.0', tk.END)
        self.report_text.insert(tk.END, "執行差分VAR模型分析中，請稍候...\n\n")
        self.update_idletasks()
        
        # 執行純VAR分析
        report, df_hist, df_forecast = perform_var_analysis(self.df, steps)
        
        self.report_text.insert(tk.END, report)
        self.report_text.config(state=tk.DISABLED)
        self.ax.clear()
        if df_hist is not None:
            self.ax.plot(df_hist.index, df_hist['PIR'], label='歷史PIR', color='blue', marker='.')
        if df_forecast is not None:
            self.ax.plot(df_forecast.index, df_forecast['PIR_Forecast'], label='預測PIR (VAR)', color='red', linestyle='--')
        self.ax.set_title('PIR 歷史數據與差分VAR模型預測')
        self.ax.set_xlabel('日期')
        self.ax.set_ylabel('PIR 指數')
        self.ax.legend()
        self.ax.grid(True)
        self.fig.tight_layout()
        self.canvas.draw()
        self.run_button.config(state=tk.NORMAL)

if __name__ == "__main__":
    app = VarOnlyAnalyzerApp()
    app.mainloop()