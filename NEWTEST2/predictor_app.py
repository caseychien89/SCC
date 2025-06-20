# predictor_app.py

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, scrolledtext
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
import joblib
import warnings

# 忽略一些 statsmodels 的未來警告，讓輸出更乾淨
warnings.filterwarnings("ignore", category=FutureWarning)

# 處理 Matplotlib 中文顯示問題
plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei', 'Arial Unicode MS'] 
plt.rcParams['axes.unicode_minus'] = False

class PredictionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("房價指數(PIR)預測小工具 (VAR模型)")
        self.root.geometry("1000x750")

        # 初始化資料和模型變數
        self.df_model = None
        self.model_package = None

        # --- 介面佈局 ---
        # 上方控制區塊
        control_frame = tk.Frame(root, padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.btn_load = tk.Button(control_frame, text="1. 選擇 CSV 檔案", command=self.load_file, width=15)
        self.btn_load.pack(side=tk.LEFT, padx=5)

        self.lbl_file = tk.Label(control_frame, text="尚未選擇檔案", fg="blue")
        self.lbl_file.pack(side=tk.LEFT, padx=5)

        tk.Label(control_frame, text="預測未來季數:").pack(side=tk.LEFT, padx=(20, 5))
        self.entry_steps = tk.Entry(control_frame, width=5)
        self.entry_steps.insert(0, "8") # 預設預測8季 (2年)
        self.entry_steps.pack(side=tk.LEFT)

        self.btn_run = tk.Button(control_frame, text="2. 開始分析與預測", command=self.run_analysis, state=tk.DISABLED, width=15)
        self.btn_run.pack(side=tk.LEFT, padx=5)

        self.btn_save = tk.Button(control_frame, text="3. 儲存模型", command=self.save_model, state=tk.DISABLED, width=15)
        self.btn_save.pack(side=tk.LEFT, padx=5)
        
        self.btn_help = tk.Button(control_frame, text="使用說明", command=self.show_help, bg="lightyellow")
        self.btn_help.pack(side=tk.RIGHT, padx=5)

        # 中間圖表區塊
        plot_frame = tk.Frame(root)
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.fig.tight_layout(pad=3.0)

        # 下方文字輸出區塊
        log_frame = tk.Frame(root, height=200)
        log_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.log_message("歡迎使用房價預測小工具！\n請先點擊 [1. 選擇 CSV 檔案] 開始。")

    def log_message(self, msg):
        """在下方的文字框中顯示訊息"""
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END) # 自動捲動到最下方

    def show_help(self):
        """顯示使用說明彈窗"""
        help_text = """
        【程式使用說明】

        這是一個使用 VAR (向量自我迴歸) 模型來預測未來房價指數 (PIR) 的小工具。
        它會分析歷史的 CPI (消費者物價指數) 和 PIR 數據之間的關聯性。

        【操作步驟】

        步驟一：點擊 [1. 選擇 CSV 檔案] 按鈕
        - 請選擇你的資料檔案 (例如 csv.csv)。
        - 選擇成功後，上方的圖表會顯示歷史的 CPI 與 PIR 走勢圖。

        步驟二：點擊 [2. 開始分析與預測] 按鈕
        - 你可以在旁邊的輸入框設定要預測未來幾季 (預設為8季=2年)。
        - 點擊後，程式會自動執行以下所有分析流程：
          1. 檢查數據穩定性 (定態檢定)。
          2. 對數據進行「差分」處理，使其變得穩定。
          3. 建立並訓練 VAR 模型。
          4. 使用訓練好的模型，預測未來 N 季的 PIR 指數。
        - 分析過程和最終預測結果會顯示在下方的文字框中。
        - 下方的圖表會顯示模型預測的結果。

        步驟三：點擊 [3. 儲存模型] 按鈕
        - 當模型訓練完成後，此按鈕會變為可點擊狀態。
        - 點擊後，你可以將訓練好的模型儲存成一個檔案 (var_model_package.joblib)。
        - 這個檔案未來可以用於快速部署到網站或 APP 上，無需重新訓練。

        【圖表說明】
        - 上圖：原始的 CPI 和 PIR 歷史數據。
        - 下圖：實際的歷史 PIR 數據，以及模型預測的未來走勢。
        """
        messagebox.showinfo("使用說明", help_text)

    def load_file(self):
        """載入並處理 CSV 檔案"""
        filepath = filedialog.askopenfilename(
            title="請選擇您的 CSV 檔案",
            filetypes=[("CSV 檔案", "*.csv")]
        )
        if not filepath:
            return

        try:
            self.lbl_file.config(text=filepath.split('/')[-1])
            self.log_message(f"成功讀取檔案: {filepath.split('/')[-1]}")
            
            df = pd.read_csv(filepath, encoding='utf-8-sig')

            # --- 資料前處理 ---
            def convert_minguo_to_date(minguo_q):
                year_str = minguo_q[:3]
                quarter = minguo_q[4]
                gregorian_year = int(year_str) + 1911
                quarter_month_map = {'1': '03-31', '2': '06-30', '3': '09-30', '4': '12-31'}
                month_day = quarter_month_map[quarter]
                return f"{gregorian_year}-{month_day}"

            df['date'] = df['年度季別'].apply(convert_minguo_to_date)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            self.df_model = df[['CPI', 'PIR']]
            
            self.log_message("資料轉換完成，已準備好進行分析。")
            self.btn_run.config(state=tk.NORMAL) # 啟用分析按鈕
            self.plot_initial_data() # 畫出初始數據圖
        except Exception as e:
            messagebox.showerror("讀取錯誤", f"讀取或處理檔案時發生錯誤:\n{e}")
            self.log_message(f"錯誤: {e}")

    def plot_initial_data(self):
        """繪製初始數據圖"""
        self.ax1.clear()
        self.ax2.clear()
        self.df_model.plot(ax=self.ax1, title="歷史 CPI 與 PIR 走勢")
        self.ax1.set_xlabel("年份")
        self.ax1.set_ylabel("指數值")
        self.ax1.legend(["CPI", "PIR"])
        self.ax1.grid(True)
        
        self.ax2.plot(self.df_model.index, self.df_model['PIR'], label='歷史 PIR', color='orange')
        self.ax2.set_title("PIR 歷史數據與預測結果")
        self.ax2.set_xlabel("年份")
        self.ax2.set_ylabel("PIR 指數")
        self.ax2.legend()
        self.ax2.grid(True)

        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()
        self.log_message("已繪製歷史數據圖。")

    def run_analysis(self):
        """執行完整的 VAR 模型分析與預測流程"""
        try:
            steps = int(self.entry_steps.get())
        except ValueError:
            messagebox.showerror("輸入錯誤", "預測季數必須是數字！")
            return
        
        self.log_message("\n" + "="*40)
        self.log_message("開始執行模型分析...")
        
        # --- 步驟 2: 檢查數據定態 ---
        self.log_message("\n[步驟 1/5] 檢查原始數據的穩定性 (定態檢定)...")
        p_value_cpi = adfuller(self.df_model['CPI'])[1]
        p_value_pir = adfuller(self.df_model['PIR'])[1]
        self.log_message(f"原始 CPI 的 p-value: {p_value_cpi:.4f}")
        self.log_message(f"原始 PIR 的 p-value: {p_value_pir:.4f}")
        if p_value_cpi > 0.05 or p_value_pir > 0.05:
            self.log_message("結論：數據非定態，需要進行差分處理。")
        else:
            self.log_message("結論：數據已是定態。")

        # --- 進行差分 ---
        df_diff = self.df_model.diff().dropna()
        self.log_message("\n[步驟 2/5] 執行一階差分...")

        # --- 步驟 3: 建立與訓練 VAR 模型 ---
        self.log_message("\n[步驟 3/5] 建立 VAR 模型並尋找最佳延遲期數...")
        model = VAR(df_diff)
        best_order = model.select_order(maxlags=10)
        p = best_order.aic
        self.log_message(f"模型建議的最佳延遲期數 (p) 為: {p}")
        
        self.log_message(f"使用 p={p} 進行模型訓練...")
        results = model.fit(p)
        
        # --- 步驟 4: 進行預測 ---
        self.log_message(f"\n[步驟 4/5] 預測未來 {steps} 季的數據...")
        lag_order = results.k_ar
        forecast_input = df_diff.values[-lag_order:]
        forecast_diff = results.forecast(y=forecast_input, steps=steps)
        
        # --- 還原預測值 ---
        df_forecast = pd.DataFrame(forecast_diff, columns=self.df_model.columns + '_forecast')
        
        last_original_values = self.df_model.iloc[-1]
        df_results = df_forecast.copy()
        for col in self.df_model.columns:
            df_results[str(col) + '_forecast'] = last_original_values[col] + df_results[str(col) + '_forecast'].cumsum()

        last_date = self.df_model.index[-1]
        forecast_index = pd.date_range(start=last_date, periods=steps + 1, freq='Q')[1:]
        df_results.index = forecast_index
        
        # --- 步驟 5: 顯示結果 ---
        self.log_message("\n[步驟 5/5] 分析完成！預測結果如下：")
        self.log_message("-" * 30)
        self.log_message("      日期       |   預測 PIR")
        self.log_message("-" * 30)
        for date, row in df_results.iterrows():
            self.log_message(f"  {date.strftime('%Y-%m-%d')}   |   {row['PIR_forecast']:.4f}")
        self.log_message("-" * 30)

        # 繪製預測圖
        self.plot_forecast(df_results)
        
        # 保存模型供後續使用
        self.model_package = {
            'model_results': results,
            'last_diff_values': df_diff.values[-results.k_ar:],
            'last_original_values': self.df_model.iloc[-1]
        }
        self.btn_save.config(state=tk.NORMAL) # 啟用儲存按鈕
        messagebox.showinfo("完成", "模型分析與預測已完成！")

    def plot_forecast(self, df_results):
        """繪製包含預測結果的圖"""
        self.ax2.clear()
        self.ax2.plot(self.df_model.index, self.df_model['PIR'], label='歷史 PIR')
        self.ax2.plot(df_results.index, df_results['PIR_forecast'], label='預測 PIR', color='red', linestyle='--')
        self.ax2.set_title("PIR 歷史數據與預測結果")
        self.ax2.set_xlabel("年份")
        self.ax2.set_ylabel("PIR 指數")
        self.ax2.legend()
        self.ax2.grid(True)
        self.fig.tight_layout(pad=3.0)
        self.canvas.draw()
        self.log_message("\n已更新下方圖表，包含預測結果。")
        
    def save_model(self):
        """儲存訓練好的模型"""
        if not self.model_package:
            messagebox.showwarning("警告", "尚未訓練模型，無法儲存。")
            return
            
        filepath = filedialog.asksaveasfilename(
            title="儲存模型檔案",
            defaultextension=".joblib",
            filetypes=[("Joblib 檔案", "*.joblib")],
            initialfile="var_model_package.joblib"
        )
        if not filepath:
            return
            
        try:
            joblib.dump(self.model_package, filepath)
            messagebox.showinfo("成功", f"模型已成功儲存至:\n{filepath}")
            self.log_message(f"\n模型已儲存至: {filepath}")
        except Exception as e:
            messagebox.showerror("儲存失敗", f"儲存模型時發生錯誤:\n{e}")
            self.log_message(f"錯誤: 儲存模型失敗 - {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PredictionApp(root)
    root.mainloop()