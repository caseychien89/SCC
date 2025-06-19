import pandas as pd
import numpy as np
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
import pickle # 確保導入 pickle 函式庫

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

    # ==========================================================
    # ▼▼▼ 新增：儲存模型為 .pkl 檔案 ▼▼▼
    # ==========================================================
    try:
        model_filename = 'var_model.pkl'
        with open(model_filename, 'wb') as f: # 'wb' 代表 write binary (二進位寫入)
            pickle.dump(var_results, f)
        report.append(f"\n--- 模型已成功儲存為【{model_filename}】 ---")
    except Exception as e:
        report.append(f"\n--- 儲存模型失敗: {e} ---")
    # ==========================================================
    # ▲▲▲ 新增程式碼結束 ▲▲▲
    # ==========================================================

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