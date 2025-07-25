# -*- coding: utf-8 -*-
"""
EMG 肌力分析報告 - 改進版

本報告根據使用者提供的三份EMG數據(.csv檔案)，使用線性回歸模型對肌力進行量化分析。
報告將詳細說明分析方法、使用的公式、計算過程，並以圖表形式呈現結果。
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
from scipy import stats
import matplotlib.font_manager as fm

def setup_chinese_font():
    """設定中文字體"""
    try:
        # 嘗試不同的中文字體
        font_names = ['Heiti TC', 'Microsoft JhengHei', 'SimHei', 'Arial Unicode MS', 'PingFang SC']
        for font_name in font_names:
            try:
                plt.rcParams['font.sans-serif'] = [font_name]
                plt.rcParams['axes.unicode_minus'] = False
                print(f"✓ 成功設定圖表字體為 {font_name}")
                return True
            except Exception:
                continue
        print("⚠️ 無法設定中文字體，圖表標籤可能無法正常顯示")
        return False
    except Exception as e:
        print(f"⚠️ 字體設定錯誤: {e}")
        return False

def calculate_rms(series):
    """計算一維數據的均方根值(RMS)"""
    numeric_series = pd.to_numeric(series, errors='coerce').dropna()
    if numeric_series.empty:
        return 0.0
    return np.sqrt(np.mean(numeric_series**2))

def calculate_statistics(series):
    """計算詳細統計指標"""
    numeric_series = pd.to_numeric(series, errors='coerce').dropna()
    if numeric_series.empty:
        return {
            'RMS': 0.0,
            'Mean': 0.0,
            'Std': 0.0,
            'Max': 0.0,
            'Min': 0.0,
            'Count': 0
        }
    
    return {
        'RMS': np.sqrt(np.mean(numeric_series**2)),
        'Mean': np.mean(numeric_series),
        'Std': np.std(numeric_series),
        'Max': np.max(numeric_series),
        'Min': np.min(numeric_series),
        'Count': len(numeric_series)
    }

def load_and_process_data():
    """載入和處理所有EMG數據"""
    # 根據使用者說明定義檔案路徑和對應的欄位資訊
    file_configs = {
        '419-電阻式': {
            'path': '419-電阻式.csv',
            'quad_col': 7,  # H欄 (索引7) -> 股四頭肌
            'bicep_col': 3, # D欄 (索引3) -> 股二頭肌
            'type': 'Other'
        },
        '445-耦合式': {
            'path': '445-藕合式.csv',  # 注意：實際文件名是藕合式
            'quad_col': 7,  # H欄 (索引7) -> 股四頭肌
            'bicep_col': 3, # D欄 (索引3) -> 股二頭肌
            'type': 'Other'
        },
        'Noraxon': {
            'path': 'Noraxon.csv',
            'quad_col': 'RT VMO (uV)',         # D欄 -> 股四頭肌
            'bicep_col': 'RT SEMITEND. (uV)',  # E欄 -> 股二頭肌
            'type': 'Noraxon'
        }
    }

    analysis_results = {}
    detailed_stats = {}
    raw_data_storage = {}
    
    print("\n=== 開始分析EMG數據 ===")
    
    for name, config in file_configs.items():
        filepath = config['path']
        if not os.path.exists(filepath):
            print(f"❌ 檔案不存在，已跳過: {filepath}")
            continue
            
        try:
            print(f"📊 正在處理: {filepath}...")
            
            # 根據文件類型讀取數據
            if config['type'] == 'Noraxon':
                df = pd.read_csv(filepath, skiprows=4, encoding='utf-8')
                print(f"   Noraxon數據形狀: {df.shape}")
            else:
                df = pd.read_csv(filepath, header=None, encoding='utf-8')
                print(f"   數據形狀: {df.shape}")

            # 計算統計指標
            quad_stats = calculate_statistics(df[config['quad_col']])
            bicep_stats = calculate_statistics(df[config['bicep_col']])
            
            # 儲存結果
            analysis_results[name] = {
                '股四頭肌 RMS (uV)': quad_stats['RMS'], 
                '股二頭肌 RMS (uV)': bicep_stats['RMS']
            }
            
            detailed_stats[name] = {
                '股四頭肌': quad_stats,
                '股二頭肌': bicep_stats
            }
            
            # 儲存原始數據用於繪圖
            raw_data_storage[name] = {'data': df, 'config': config}
            
            print(f"   ✓ 股四頭肌 RMS: {quad_stats['RMS']:.2f} uV")
            print(f"   ✓ 股二頭肌 RMS: {bicep_stats['RMS']:.2f} uV")
            
        except Exception as e:
            print(f"❌ 處理檔案 {filepath} 時發生錯誤: {e}")
            continue

    return analysis_results, detailed_stats, raw_data_storage

def create_comparison_chart(analysis_results):
    """創建比較圖表"""
    if not analysis_results:
        print("❌ 無數據可供繪圖")
        return
        
    print("\n📈 正在生成比較圖表...")
    
    # 準備數據
    results_df = pd.DataFrame.from_dict(analysis_results, orient='index')
    plot_df = results_df.reset_index().rename(columns={'index': '資料來源'})
    plot_df_melted = plot_df.melt(id_vars='資料來源', var_name='肌肉', value_name='RMS (uV)')
    
    # 創建圖表
    plt.style.use('seaborn-v0_8-whitegrid')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # 長條圖
    sns.barplot(data=plot_df_melted, x='資料來源', y='RMS (uV)', 
                hue='肌肉', ax=ax1, palette='viridis')
    ax1.set_title('EMG 肌力分析比較 (長條圖)', fontsize=16, pad=20)
    ax1.set_xlabel('數據來源', fontsize=12)
    ax1.set_ylabel('肌力代理指標 (RMS, uV)', fontsize=12)
    
    # 添加數值標籤
    for container in ax1.containers:
        ax1.bar_label(container, fmt='%.2f', fontsize=10, padding=3)
    
    ax1.legend(title='肌肉', fontsize=11)
    ax1.tick_params(axis='x', rotation=45)
    
    # 散點圖
    for i, muscle in enumerate(['股四頭肌 RMS (uV)', '股二頭肌 RMS (uV)']):
        x_pos = np.arange(len(results_df))
        y_values = results_df[muscle].values
        ax2.scatter(x_pos, y_values, s=100, alpha=0.7, 
                   label=muscle.replace(' RMS (uV)', ''),
                   color=['royalblue', 'seagreen'][i])
        
        # 連接線
        ax2.plot(x_pos, y_values, '--', alpha=0.5, 
                color=['royalblue', 'seagreen'][i])
    
    ax2.set_title('EMG 肌力分析比較 (趨勢圖)', fontsize=16, pad=20)
    ax2.set_xlabel('數據來源', fontsize=12)
    ax2.set_ylabel('肌力代理指標 (RMS, uV)', fontsize=12)
    ax2.set_xticks(range(len(results_df)))
    ax2.set_xticklabels(results_df.index, rotation=45)
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    
    # 添加公式說明
    formula_text = (
        r"$\bf{分析模型與計算過程}$" + "\n"
        r"1. $\bf{模型}$: 線性回歸 $F = a \times RMS(EMG) + b$" + "\n"
        r"2. $\bf{假設}$: 因無實際肌力(F)數據, 簡化為 $a=1, b=0$, "
        r"故 $F \approx RMS(EMG)$" + "\n"
        r"3. $\bf{計算}$: $RMS = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (EMG_i)^2}$"
    )
    
    fig.text(0.5, 0.02, formula_text, ha='center', fontsize=11, 
             bbox=dict(boxstyle="round,pad=0.5", fc='aliceblue', ec='grey', lw=1))
    
    plt.tight_layout(rect=[0, 0.15, 1, 0.95])
    plt.show()

def create_detailed_statistics_table(detailed_stats):
    """創建詳細統計表格"""
    print("\n📋 詳細統計分析結果:")
    print("=" * 80)
    
    for source, muscles in detailed_stats.items():
        print(f"\n📊 {source}:")
        print("-" * 50)
        
        for muscle, stats in muscles.items():
            print(f"  {muscle}:")
            print(f"    RMS:   {stats['RMS']:.3f} uV")
            print(f"    平均:   {stats['Mean']:.3f} uV")
            print(f"    標準差: {stats['Std']:.3f} uV")
            print(f"    最大值: {stats['Max']:.3f} uV")
            print(f"    最小值: {stats['Min']:.3f} uV")
            print(f"    數據點: {stats['Count']} 個")
            print()

def create_noraxon_signal_plot(raw_data_storage):
    """創建Noraxon原始訊號圖"""
    if 'Noraxon' not in raw_data_storage:
        print("⚠️ 無Noraxon數據可供繪製原始訊號圖")
        return
        
    print("\n📈 正在生成Noraxon原始訊號圖...")
    
    noraxon_data = raw_data_storage['Noraxon']['data']
    noraxon_config = raw_data_storage['Noraxon']['config']
    
    if 'time' in noraxon_data.columns:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
        
        quad_col_name = noraxon_config['quad_col']
        bicep_col_name = noraxon_config['bicep_col']
        
        # 股四頭肌訊號
        ax1.plot(noraxon_data['time'], noraxon_data[quad_col_name], 
                label=f'股四頭肌 ({quad_col_name.split(" ")[0]})', 
                color='royalblue', linewidth=0.8)
        ax1.set_title('Noraxon 原始EMG訊號 - 股四頭肌', fontsize=16)
        ax1.set_ylabel('EMG Amplitude (uV)', fontsize=12)
        ax1.legend(fontsize=11)
        ax1.grid(True, alpha=0.3)
        
        # 股二頭肌訊號
        ax2.plot(noraxon_data['time'], noraxon_data[bicep_col_name], 
                label=f'股二頭肌 ({bicep_col_name.split(" ")[0]})', 
                color='seagreen', linewidth=0.8)
        ax2.set_title('Noraxon 原始EMG訊號 - 股二頭肌', fontsize=16)
        ax2.set_xlabel('時間 (秒)', fontsize=12)
        ax2.set_ylabel('EMG Amplitude (uV)', fontsize=12)
        ax2.legend(fontsize=11)
        ax2.grid(True, alpha=0.3)
        
        fig.suptitle('原始數據範例 (Noraxon.csv)', fontsize=18, y=0.98)
        plt.tight_layout(rect=[0, 0.03, 1, 0.96])
        plt.show()
    else:
        print("⚠️ Noraxon數據中未找到時間欄位")

def main():
    """主執行函數"""
    print("🚀 EMG 肌力分析報告 - 改進版")
    print("=" * 50)
    
    # 初始設定
    warnings.filterwarnings('ignore', category=UserWarning, module='pandas')
    setup_chinese_font()
    
    # 載入和處理數據
    analysis_results, detailed_stats, raw_data_storage = load_and_process_data()
    
    if not analysis_results:
        print("\n❌ 所有檔案分析失敗，無法生成報告。")
        return
    
    # 顯示基本結果
    print("\n📊 基本分析結果:")
    results_df = pd.DataFrame.from_dict(analysis_results, orient='index')
    print(results_df.round(3))
    
    # 創建詳細統計表格
    create_detailed_statistics_table(detailed_stats)
    
    # 創建比較圖表
    create_comparison_chart(analysis_results)
    
    # 創建Noraxon原始訊號圖
    create_noraxon_signal_plot(raw_data_storage)
    
    print("\n✅ 分析完成！")

if __name__ == "__main__":
    main()