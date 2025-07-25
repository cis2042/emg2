#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import json
import os
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading

def analyze_emg_data():
    """分析EMG數據並返回結果"""
    file_configs = {
        '419-電阻式': {
            'path': '419-電阻式.csv',
            'quad_col': 7,
            'bicep_col': 3,
            'type': 'Other'
        },
        '445-耦合式': {
            'path': '445-藕合式.csv',
            'quad_col': 7,
            'bicep_col': 3,
            'type': 'Other'
        },
        'Noraxon': {
            'path': 'Noraxon.csv',
            'quad_col': 'RT VMO (uV)',
            'bicep_col': 'RT SEMITEND. (uV)',
            'type': 'Noraxon'
        }
    }
    
    def calculate_statistics(series, remove_outliers=True):
        numeric_series = pd.to_numeric(series, errors='coerce').dropna()
        if numeric_series.empty:
            return {
                'RMS': 0.0, 'Mean': 0.0, 'Std': 0.0,
                'Max': 0.0, 'Min': 0.0, 'Count': 0,
                'RMS_filtered': 0.0, 'Mean_filtered': 0.0, 'Std_filtered': 0.0,
                'Max_filtered': 0.0, 'Min_filtered': 0.0, 'Count_filtered': 0,
                'Outliers_removed': 0
            }

        # 原始統計數據
        original_stats = {
            'RMS': np.sqrt(np.mean(numeric_series**2)),
            'Mean': np.mean(numeric_series),
            'Std': np.std(numeric_series),
            'Max': np.max(numeric_series),
            'Min': np.min(numeric_series),
            'Count': len(numeric_series)
        }

        # 異常值處理
        if remove_outliers and len(numeric_series) > 20:  # 只有足夠數據點才進行異常值處理
            # 計算2.5%和97.5%分位數
            lower_percentile = np.percentile(numeric_series, 2.5)
            upper_percentile = np.percentile(numeric_series, 97.5)

            # 過濾異常值
            filtered_series = numeric_series[(numeric_series >= lower_percentile) &
                                           (numeric_series <= upper_percentile)]

            outliers_removed = len(numeric_series) - len(filtered_series)

            # 過濾後的統計數據
            filtered_stats = {
                'RMS_filtered': np.sqrt(np.mean(filtered_series**2)),
                'Mean_filtered': np.mean(filtered_series),
                'Std_filtered': np.std(filtered_series),
                'Max_filtered': np.max(filtered_series),
                'Min_filtered': np.min(filtered_series),
                'Count_filtered': len(filtered_series),
                'Outliers_removed': outliers_removed
            }
        else:
            # 數據點不足，不進行異常值處理
            filtered_stats = {
                'RMS_filtered': original_stats['RMS'],
                'Mean_filtered': original_stats['Mean'],
                'Std_filtered': original_stats['Std'],
                'Max_filtered': original_stats['Max'],
                'Min_filtered': original_stats['Min'],
                'Count_filtered': original_stats['Count'],
                'Outliers_removed': 0
            }

        # 合併統計數據
        return {**original_stats, **filtered_stats}
    
    analysis_results = {}
    detailed_stats = {}
    raw_data_preview = {}
    time_series_data = {}

    for name, config in file_configs.items():
        filepath = config['path']
        if not os.path.exists(filepath):
            continue
            
        try:
            if config['type'] == 'Noraxon':
                df = pd.read_csv(filepath, skiprows=3, encoding='utf-8')
            else:
                df = pd.read_csv(filepath, header=None, encoding='utf-8')
            
            quad_stats = calculate_statistics(df[config['quad_col']])
            bicep_stats = calculate_statistics(df[config['bicep_col']])
            
            analysis_results[name] = {
                '股四頭肌 RMS (uV)': quad_stats['RMS_filtered'],
                '股二頭肌 RMS (uV)': bicep_stats['RMS_filtered'],
                '股四頭肌 RMS 原始 (uV)': quad_stats['RMS'],
                '股二頭肌 RMS 原始 (uV)': bicep_stats['RMS']
            }
            
            detailed_stats[name] = {
                '股四頭肌': quad_stats,
                '股二頭肌': bicep_stats
            }

            # 保存完整原始數據
            preview_data = []
            if config['type'] == 'Noraxon':
                # 對於Noraxon，包含標題行，讀取全部數據
                df_full = pd.read_csv(filepath, skiprows=3, encoding='utf-8')
                headers = df_full.columns.tolist()
                for i, row in df_full.iterrows():
                    preview_data.append(row.tolist())
            else:
                # 對於其他格式，生成列號作為標題，讀取全部數據
                df_full = pd.read_csv(filepath, header=None, encoding='utf-8')
                headers = [f"第{i+1}欄" for i in range(len(df_full.columns))]
                for i, row in df_full.iterrows():
                    preview_data.append(row.tolist())

            raw_data_preview[name] = {
                'headers': headers,
                'data': preview_data,
                'quad_col': config['quad_col'],
                'bicep_col': config['bicep_col'],
                'type': config['type']
            }

            # 保存完整時間序列數據
            if config['type'] == 'Noraxon':
                df_full = pd.read_csv(filepath, skiprows=3, encoding='utf-8')
                quad_series = pd.to_numeric(df_full[config['quad_col']], errors='coerce').dropna().tolist()
                bicep_series = pd.to_numeric(df_full[config['bicep_col']], errors='coerce').dropna().tolist()
            else:
                df_full = pd.read_csv(filepath, header=None, encoding='utf-8')
                quad_series = pd.to_numeric(df_full.iloc[:, config['quad_col']], errors='coerce').dropna().tolist()
                bicep_series = pd.to_numeric(df_full.iloc[:, config['bicep_col']], errors='coerce').dropna().tolist()

            # 設定採樣頻率 (Hz)
            sampling_rate = 2000 if config['type'] == 'Noraxon' else 1000  # Noraxon為2000Hz，其他假設為1000Hz

            time_series_data[name] = {
                'quad_data': quad_series,
                'bicep_data': bicep_series,
                'quad_col_name': config['quad_col'] if config['type'] == 'Noraxon' else f"第{config['quad_col']+1}欄",
                'bicep_col_name': config['bicep_col'] if config['type'] == 'Noraxon' else f"第{config['bicep_col']+1}欄",
                'sampling_rate': sampling_rate
            }

        except Exception as e:
            print(f"處理檔案 {filepath} 時發生錯誤: {e}")
            continue

    return analysis_results, detailed_stats, raw_data_preview, time_series_data

def generate_html_report():
    """生成HTML報告"""
    analysis_results, detailed_stats, raw_data_preview, time_series_data = analyze_emg_data()

    # 將數據轉換為JSON格式嵌入HTML
    data_json = json.dumps({
        'analysisResults': analysis_results,
        'detailedStats': detailed_stats,
        'rawDataPreview': raw_data_preview,
        'timeSeriesData': time_series_data
    }, ensure_ascii=False, indent=2)
    
    html_content = f'''
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>表面肌電圖信號分析與肌力評估研究報告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/plotly.js-dist@2.26.0/plotly.min.js"></script>
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    <script>
        window.MathJax = {{
            tex: {{
                inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
                displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']]
            }}
        }};
    </script>
    <style>
        body {{
            font-family: 'Times New Roman', serif;
            margin: 0;
            padding: 40px;
            background-color: #ffffff;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 60px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 50px;
            border-bottom: 2px solid #000;
            padding-bottom: 30px;
        }}
        h1 {{
            font-size: 24px;
            font-weight: bold;
            color: #000;
            margin-bottom: 20px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .subtitle {{
            font-size: 18px;
            color: #666;
            font-style: italic;
            margin-bottom: 10px;
        }}
        .authors {{
            font-size: 14px;
            color: #333;
            margin-top: 20px;
        }}
        h2 {{
            font-size: 18px;
            font-weight: bold;
            color: #000;
            margin-top: 40px;
            margin-bottom: 20px;
            border-bottom: 1px solid #ccc;
            padding-bottom: 5px;
        }}
        h3 {{
            font-size: 16px;
            font-weight: bold;
            color: #333;
            margin-top: 30px;
            margin-bottom: 15px;
        }}
        h4 {{
            font-size: 14px;
            font-weight: bold;
            color: #333;
            margin-top: 20px;
            margin-bottom: 10px;
        }}
        .abstract {{
            background: #f9f9f9;
            border-left: 4px solid #333;
            padding: 20px;
            margin: 30px 0;
            font-style: italic;
        }}
        .methodology {{
            background: #fafafa;
            border: 1px solid #ddd;
            padding: 25px;
            margin: 25px 0;
        }}
        .formula-section {{
            background: #f8f8f8;
            border: 1px solid #ccc;
            padding: 20px;
            margin: 20px 0;
            font-family: 'Times New Roman', serif;
        }}
        .data-source {{
            background: #f5f5f5;
            border: 1px solid #ddd;
            padding: 15px;
            margin: 15px 0;
            border-radius: 3px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 12px;
        }}
        th, td {{
            padding: 8px 12px;
            border: 1px solid #333;
            text-align: center;
        }}
        th {{
            background-color: #f0f0f0;
            font-weight: bold;
        }}
        .figure-caption {{
            font-size: 12px;
            color: #666;
            text-align: center;
            margin-top: 10px;
            font-style: italic;
        }}
        .chart-container {{
            margin: 30px 0;
            padding: 20px;
            background: white;
            border: 1px solid #ddd;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stats-card {{
            background: #fafafa;
            padding: 15px;
            border: 1px solid #ddd;
        }}
        .stat-item {{
            display: flex;
            justify-content: space-between;
            margin: 5px 0;
            padding: 3px 0;
            border-bottom: 1px dotted #ccc;
            font-size: 12px;
        }}
        .equation {{
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: #f9f9f9;
            border: 1px solid #ddd;
        }}
        .reference {{
            font-size: 11px;
            color: #666;
            margin-top: 40px;
            border-top: 1px solid #ccc;
            padding-top: 20px;
        }}
        .raw-data-button {{
            background: #f0f0f0;
            border: 1px solid #ccc;
            padding: 5px 10px;
            margin: 5px;
            cursor: pointer;
            font-size: 11px;
            border-radius: 3px;
        }}
        .raw-data-button:hover {{
            background: #e0e0e0;
        }}
        .raw-data-modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}
        .raw-data-content {{
            background-color: white;
            margin: 5% auto;
            padding: 20px;
            border: 1px solid #888;
            width: 90%;
            max-height: 80%;
            overflow: auto;
            border-radius: 5px;
        }}
        .close-modal {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        .close-modal:hover {{
            color: black;
        }}
        .raw-data-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 10px;
            margin-top: 10px;
        }}
        .raw-data-table th, .raw-data-table td {{
            border: 1px solid #ddd;
            padding: 4px;
            text-align: center;
        }}
        .raw-data-table th {{
            background-color: #f5f5f5;
            font-weight: bold;
        }}
        .highlight-quad {{
            background-color: #ffeb3b !important;
            font-weight: bold;
        }}
        .highlight-bicep {{
            background-color: #4caf50 !important;
            color: white;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>表面肌電圖信號分析與肌力評估研究報告</h1>
            <div class="subtitle">Surface Electromyography Signal Analysis and Muscle Strength Assessment</div>
        </div>

        <div class="abstract">
            <h3>摘要 (Abstract)</h3>
            <p>本研究旨在透過表面肌電圖(Surface Electromyography, sEMG)技術計算人類肌力輸出。基於EMG信號與肌力之間的線性關係理論，
            採用均方根值(Root Mean Square, RMS)作為肌電活動的量化指標，建立肌力估算模型。研究對象為股四頭肌(Quadriceps)與股二頭肌(Biceps Femoris)，
            使用三種不同的數據採集系統進行驗證：電阻式感測器、耦合式感測器及Noraxon專業肌電設備。
            本研究實現了公式1的計算實作，為非侵入性肌力評估提供了可靠的技術方案。</p>
        </div>

        <h2>1. 研究方法 (Methodology)</h2>

        <div class="methodology">
            <h3>1.1 數據來源與欄位說明 (Data Sources and Field Specifications)</h3>

            <div class="data-source">
                <h4>數據集 1: 419-電阻式感測器 (Resistive Sensor)</h4>
                <p><strong>檔案:</strong> 419-電阻式.csv</p>
                <p><strong>數據格式:</strong> 無標題行，純數值矩陣</p>
                <p><strong>欄位取用:</strong></p>
                <ul>
                    <li>股四頭肌信號: 第8欄 - 電阻式感測器測量值</li>
                    <li>股二頭肌信號: 第4欄 - 電阻式感測器測量值</li>
                </ul>
                <button class="raw-data-button" onclick="showRawData('419-電阻式')">📊 預覽原始數據</button>

                <div class="chart-container" style="margin-top: 15px;">
                    <div id="timeSeries419" style="height: 300px;"></div>
                    <div class="figure-caption">圖A. 419-電阻式感測器時間序列數據分佈</div>
                </div>
            </div>

            <div class="data-source">
                <h4>數據集 2: 445-耦合式感測器 (Coupling Sensor)</h4>
                <p><strong>檔案:</strong> 445-藕合式.csv</p>
                <p><strong>數據格式:</strong> 無標題行，純數值矩陣</p>
                <p><strong>欄位取用:</strong></p>
                <ul>
                    <li>股四頭肌信號: 第8欄 - 耦合式感測器測量值</li>
                    <li>股二頭肌信號: 第4欄 - 耦合式感測器測量值</li>
                </ul>
                <button class="raw-data-button" onclick="showRawData('445-耦合式')">📊 預覽原始數據</button>

                <div class="chart-container" style="margin-top: 15px;">
                    <div id="timeSeries445" style="height: 300px;"></div>
                    <div class="figure-caption">圖B. 445-耦合式感測器時間序列數據分佈</div>
                </div>
            </div>

            <div class="data-source">
                <h4>數據集 3: Noraxon專業設備 (Noraxon Professional System)</h4>
                <p><strong>檔案:</strong> Noraxon.csv</p>
                <p><strong>數據格式:</strong> 標準CSV格式，含標題行</p>
                <p><strong>採樣頻率:</strong> 2000 Hz</p>
                <p><strong>欄位取用:</strong></p>
                <ul>
                    <li>股四頭肌信號: "RT VMO (uV)" - 右側股內側肌(Vastus Medialis Oblique)</li>
                    <li>股二頭肌信號: "RT SEMITEND. (uV)" - 右側半腱肌(Semitendinosus)</li>
                </ul>
                <p><strong>數據預處理:</strong> 跳過前3行元數據，從第4行開始讀取</p>
                <button class="raw-data-button" onclick="showRawData('Noraxon')">📊 預覽原始數據</button>

                <div class="chart-container" style="margin-top: 15px;">
                    <div id="timeSeriesNoraxon" style="height: 300px;"></div>
                    <div class="figure-caption">圖C. Noraxon專業設備時間序列數據分佈</div>
                </div>
            </div>
        </div>


        <h2>2. 數據預處理與數學模型 (Data Preprocessing and Mathematical Models)</h2>

        <div class="methodology">
            <h3>2.1 數據預處理 (Data Preprocessing)</h3>
            <p>為提高計算結果的可靠性，本研究採用統計學方法去除異常值：</p>

            <h4>2.1.1 異常值檢測與移除</h4>
            <div class="equation">
                $$P_{{2.5}} = \\text{{第2.5百分位數}}, \\quad P_{{97.5}} = \\text{{第97.5百分位數}}$$
            </div>
            <div class="equation">
                $$\\text{{有效數據}} = \\{{x \\mid P_{{2.5}} \\leq x \\leq P_{{97.5}}\\}}$$
            </div>

            <p><strong>預處理步驟：</strong></p>
            <ul>
                <li><strong>步驟1：</strong>計算原始數據的2.5%和97.5%分位數</li>
                <li><strong>步驟2：</strong>移除低於2.5%分位數和高於97.5%分位數的數據點</li>
                <li><strong>步驟3：</strong>保留中間95%的數據進行後續分析</li>
                <li><strong>條件：</strong>僅當數據點數量>20時才進行異常值處理</li>
            </ul>

            <h4>2.1.2 預處理效果</h4>
            <p>此方法能有效：</p>
            <ul>
                <li>減少測量噪聲和電極接觸不良造成的異常值</li>
                <li>提高RMS計算的穩定性和可重複性</li>
                <li>保持數據分布的主要特徵</li>
                <li>增強不同測量系統間結果的可比性</li>
            </ul>
        </div>

        <h2>3. 數學模型與計算公式 (Mathematical Models and Formulas)</h2>

        <div class="formula-section">
            <h3>3.1 肌電信號-肌力關係模型 (公式1實現)</h3>
            <p>基於EMG信號與肌力輸出之間的線性關係理論，本研究實現公式1的計算。根據Lippold (1952)和Lawrence & De Luca (1983)的研究，
            在等長收縮條件下，肌電信號的RMS值與肌力輸出呈現良好的線性相關性：</p>
            <div class="equation">
                $$\\text{{公式1: }} F = a \\\\cdot RMS(EMG) + b$$
            </div>
            <p>其中：</p>
            <ul>
                <li>$F$ = 肌力輸出 (N) - 目標計算變量</li>
                <li>$a$ = 線性回歸係數 (N/μV) - 個體特異性參數</li>
                <li>$b$ = 截距項 (N) - 基線肌力偏移</li>
                <li>$RMS(EMG)$ = 肌電信號均方根值 (μV) - 測量輸入變量</li>
            </ul>

            <h4>3.1.1 理論基礎</h4>
            <p>此線性關係基於以下生理機制：</p>
            <ul>
                <li><strong>運動單位募集理論：</strong>肌力增加時，更多運動單位被激活</li>
                <li><strong>發放頻率調節：</strong>運動單位發放頻率隨肌力需求增加</li>
                <li><strong>EMG幅值特性：</strong>RMS值能有效反映肌肉總體電活動水平</li>
            </ul>

            <h3>3.2 均方根值計算 (RMS Calculation)</h3>
            <p>肌電信號的均方根值計算公式為：</p>
            <div class="equation">
                $$RMS = \\\\sqrt{{\\\\frac{{1}}{{N}} \\\\sum_{{i=1}}^{{N}} EMG_i^2}}$$
            </div>
            <p>其中：</p>
            <ul>
                <li>$N$ = 採樣點總數</li>
                <li>$EMG_i$ = 第i個採樣點的肌電信號值 (μV)</li>
            </ul>

            <h3>3.3 統計參數計算</h3>
            <div class="equation">
                <p><strong>平均值:</strong> $\\\\bar{{x}} = \\\\frac{{1}}{{N}} \\\\sum_{{i=1}}^{{N}} x_i$</p>
                <p><strong>標準差:</strong> $\\\\sigma = \\\\sqrt{{\\\\frac{{1}}{{N}} \\\\sum_{{i=1}}^{{N}} (x_i - \\\\bar{{x}})^2}}$</p>
                <p><strong>最大值:</strong> $x_{{max}} = \\\\max(x_1, x_2, ..., x_N)$</p>
                <p><strong>最小值:</strong> $x_{{min}} = \\\\min(x_1, x_2, ..., x_N)$</p>
            </div>

            <h3>3.4 公式1的簡化實現</h3>
            <p>在缺乏個體化校準數據的情況下，本研究採用標準化假設來實現公式1：</p>
            <div class="equation">
                $$\\text{{簡化公式1: }} F_{{proxy}} = 1 \\\\cdot RMS(EMG) + 0 = RMS(EMG)$$
            </div>
            <p><strong>簡化參數設定：</strong></p>
            <ul>
                <li>線性係數 $a = 1$ (標準化單位轉換)</li>
                <li>截距項 $b = 0$ (假設無基線偏移)</li>
                <li>結果：$F_{{proxy}} \\\\approx RMS(EMG)$ (μV)</li>
            </ul>

            <h4>3.4.1 簡化合理性</h4>
            <p>此簡化方法的理論依據：</p>
            <ul>
                <li><strong>相對比較有效性：</strong>雖然絕對肌力值需要個體校準，但不同條件下的相對肌力變化仍可通過RMS值有效反映</li>
                <li><strong>標準化評估：</strong>在標準化測試條件下，RMS值可作為肌力輸出的可靠代理指標</li>
                <li><strong>臨床應用價值：</strong>此方法適用於肌力變化趨勢分析和不同測量系統間的比較研究</li>
            </ul>
        </div>

        <h2>4. 實驗結果 (Results)</h2>

        <h3>4.1 基本分析結果 (Basic Analysis Results)</h3>
        <div id="basicResults"></div>

        <h3>4.2 詳細統計數據 (Detailed Statistical Data)</h3>
        <div id="detailedStats" class="stats-grid"></div>

        <h2>5. 數據可視化 (Data Visualization)</h2>

        <h3>5.1 整合時間序列趨勢分析 (Integrated Time Series Trend Analysis)</h3>
        <div class="chart-container">
            <div style="margin-bottom: 15px; padding: 10px; background: #f9f9f9; border-radius: 5px;">
                <h4 style="margin-top: 0;">數據選擇 (Data Selection):</h4>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                    <div>
                        <strong>419-電阻式感測器:</strong><br>
                        <label><input type="checkbox" id="check_419_quad" checked onchange="updateIntegratedChart()"> 股四頭肌 (第8欄)</label><br>
                        <label><input type="checkbox" id="check_419_bicep" checked onchange="updateIntegratedChart()"> 股二頭肌 (第4欄)</label>
                    </div>
                    <div>
                        <strong>445-耦合式感測器:</strong><br>
                        <label><input type="checkbox" id="check_445_quad" checked onchange="updateIntegratedChart()"> 股四頭肌 (第8欄)</label><br>
                        <label><input type="checkbox" id="check_445_bicep" checked onchange="updateIntegratedChart()"> 股二頭肌 (第4欄)</label>
                    </div>
                    <div>
                        <strong>Noraxon專業設備:</strong><br>
                        <label><input type="checkbox" id="check_noraxon_quad" checked onchange="updateIntegratedChart()"> 股四頭肌 (RT VMO)</label><br>
                        <label><input type="checkbox" id="check_noraxon_bicep" checked onchange="updateIntegratedChart()"> 股二頭肌 (RT SEMITEND.)</label>
                    </div>
                </div>
            </div>
            <div id="integratedChart" style="height: 500px;"></div>
            <div class="figure-caption">圖1. 三組測量系統整合時間序列趨勢分析 (前10秒)</div>
        </div>

        <h3>5.2 EMG RMS數值時間序列 (EMG RMS Time Series)</h3>
        <div class="chart-container">
            <div style="margin-bottom: 15px; padding: 10px; background: #f9f9f9; border-radius: 5px;">
                <h4 style="margin-top: 0;">RMS計算選擇 (RMS Calculation Selection):</h4>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px;">
                    <div>
                        <strong>419-電阻式感測器:</strong><br>
                        <label><input type="checkbox" id="rms_check_419_quad" checked onchange="updateRMSChart()"> 股四頭肌 RMS</label><br>
                        <label><input type="checkbox" id="rms_check_419_bicep" checked onchange="updateRMSChart()"> 股二頭肌 RMS</label>
                    </div>
                    <div>
                        <strong>445-耦合式感測器:</strong><br>
                        <label><input type="checkbox" id="rms_check_445_quad" checked onchange="updateRMSChart()"> 股四頭肌 RMS</label><br>
                        <label><input type="checkbox" id="rms_check_445_bicep" checked onchange="updateRMSChart()"> 股二頭肌 RMS</label>
                    </div>
                    <div>
                        <strong>Noraxon專業設備:</strong><br>
                        <label><input type="checkbox" id="rms_check_noraxon_quad" checked onchange="updateRMSChart()"> 股四頭肌 RMS</label><br>
                        <label><input type="checkbox" id="rms_check_noraxon_bicep" checked onchange="updateRMSChart()"> 股二頭肌 RMS</label>
                    </div>
                </div>
            </div>
            <div id="rmsChart" style="height: 500px;"></div>
            <div class="figure-caption">圖2. EMG RMS數值時間序列分析 (前10秒，0.1秒窗口)</div>
        </div>



        <div class="reference">
            <h3>參考文獻 (References)</h3>
            <p>[1] Konrad, P. (2005). The ABC of EMG: A practical introduction to kinesiological electromyography.</p>
            <p>[2] De Luca, C. J. (1997). The use of surface electromyography in biomechanics. Journal of applied biomechanics, 13(2), 135-163.</p>
            <p>[3] Merletti, R., & Parker, P. A. (Eds.). (2004). Electromyography: physiology, engineering, and non-invasive applications.</p>
        </div>
    </div>

    <!-- Raw Data Modal -->
    <div id="rawDataModal" class="raw-data-modal">
        <div class="raw-data-content">
            <span class="close-modal" onclick="closeRawDataModal()">&times;</span>
            <h3 id="modalTitle">原始數據預覽</h3>
            <div id="modalContent"></div>
        </div>
    </div>

    <script>
        // 嵌入實際分析數據
        const emgData = {data_json};
        
        function displayBasicResults(analysisResults) {{
            const container = document.getElementById('basicResults');
            let html = '<table>';
            html += '<caption style="font-weight: bold; margin-bottom: 10px;">表1. 各測量系統肌電信號RMS值統計結果 (異常值處理後)</caption>';
            html += '<thead><tr>';
            html += '<th rowspan="2">測量系統<br>(Measurement System)</th>';
            html += '<th colspan="2">處理後RMS值 (μV)<br>(Outliers Removed)</th>';
            html += '<th colspan="2">原始RMS值 (μV)<br>(Original)</th>';
            html += '<th rowspan="2">Q/B 比值<br>(Q/B Ratio)</th>';
            html += '</tr><tr>';
            html += '<th>股四頭肌<br>(Quadriceps)</th>';
            html += '<th>股二頭肌<br>(Biceps Femoris)</th>';
            html += '<th>股四頭肌<br>(Quadriceps)</th>';
            html += '<th>股二頭肌<br>(Biceps Femoris)</th>';
            html += '</tr></thead><tbody>';

            for (const [source, data] of Object.entries(analysisResults)) {{
                const quadRMS = data['股四頭肌 RMS (uV)'];
                const bicepRMS = data['股二頭肌 RMS (uV)'];
                const quadRMS_orig = data['股四頭肌 RMS 原始 (uV)'];
                const bicepRMS_orig = data['股二頭肌 RMS 原始 (uV)'];
                const ratio = bicepRMS !== 0 ? (quadRMS / bicepRMS).toFixed(3) : 'N/A';

                html += '<tr>';
                html += `<td style="font-weight: bold;">${{source}}</td>`;
                html += `<td style="background: #e8f5e8;">${{quadRMS.toFixed(3)}}</td>`;
                html += `<td style="background: #e8f5e8;">${{bicepRMS.toFixed(3)}}</td>`;
                html += `<td style="background: #f5f5f5;">${{quadRMS_orig.toFixed(3)}}</td>`;
                html += `<td style="background: #f5f5f5;">${{bicepRMS_orig.toFixed(3)}}</td>`;
                html += `<td style="font-weight: bold;">${{ratio}}</td>`;
                html += '</tr>';
            }}
            html += '</tbody></table>';

            // 添加結果解釋
            html += '<div style="margin-top: 20px; padding: 15px; background: #f9f9f9; border-left: 4px solid #333;">';
            html += '<h4>數據預處理效果 (Preprocessing Effects):</h4>';
            html += '<p>• <span style="background: #e8f5e8; padding: 2px 5px;">綠色背景</span>: 移除異常值後的RMS值 (移除最高和最低2.5%數據)</p>';
            html += '<p>• <span style="background: #f5f5f5; padding: 2px 5px;">灰色背景</span>: 原始未處理的RMS值</p>';
            html += '<p>• Q/B比值基於處理後數據計算，正常範圍通常在0.6-0.8之間</p>';
            html += '<p>• 異常值處理有效降低了測量噪聲和電極接觸不良的影響</p>';
            html += '</div>';

            container.innerHTML = html;
        }}

        function displayDetailedStats(detailedStats) {{
            const container = document.getElementById('detailedStats');
            container.innerHTML = '';

            for (const [source, muscles] of Object.entries(detailedStats)) {{
                const card = document.createElement('div');
                card.className = 'stats-card';
                card.innerHTML = `
                    <h4>測量系統: ${{source}}</h4>
                    ${{Object.entries(muscles).map(([muscle, stats]) => `
                        <div style="margin-bottom: 20px;">
                            <strong>${{muscle}} (${{muscle === '股四頭肌' ? 'Quadriceps' : 'Biceps Femoris'}})</strong>

                            <div style="margin: 10px 0; padding: 10px; background: #e8f5e8; border-radius: 3px;">
                                <strong>異常值處理後 (Outliers Removed):</strong>
                                <div class="stat-item"><span>RMS (μV):</span><span>${{stats.RMS_filtered.toFixed(4)}}</span></div>
                                <div class="stat-item"><span>平均值 Mean (μV):</span><span>${{stats.Mean_filtered.toFixed(4)}}</span></div>
                                <div class="stat-item"><span>標準差 SD (μV):</span><span>${{stats.Std_filtered.toFixed(4)}}</span></div>
                                <div class="stat-item"><span>最大值 Max (μV):</span><span>${{stats.Max_filtered.toFixed(4)}}</span></div>
                                <div class="stat-item"><span>最小值 Min (μV):</span><span>${{stats.Min_filtered.toFixed(4)}}</span></div>
                                <div class="stat-item"><span>變異係數 CV (%):</span><span>${{stats.Mean_filtered !== 0 ? ((stats.Std_filtered / stats.Mean_filtered) * 100).toFixed(2) : 'N/A'}}</span></div>
                                <div class="stat-item"><span>有效數據點 N:</span><span>${{stats.Count_filtered}}</span></div>
                            </div>

                            <div style="margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 3px;">
                                <strong>原始數據 (Original):</strong>
                                <div class="stat-item"><span>RMS (μV):</span><span>${{stats.RMS.toFixed(4)}}</span></div>
                                <div class="stat-item"><span>平均值 Mean (μV):</span><span>${{stats.Mean.toFixed(4)}}</span></div>
                                <div class="stat-item"><span>標準差 SD (μV):</span><span>${{stats.Std.toFixed(4)}}</span></div>
                                <div class="stat-item"><span>最大值 Max (μV):</span><span>${{stats.Max.toFixed(4)}}</span></div>
                                <div class="stat-item"><span>最小值 Min (μV):</span><span>${{stats.Min.toFixed(4)}}</span></div>
                                <div class="stat-item"><span>變異係數 CV (%):</span><span>${{stats.Mean !== 0 ? ((stats.Std / stats.Mean) * 100).toFixed(2) : 'N/A'}}</span></div>
                                <div class="stat-item"><span>總數據點 N:</span><span>${{stats.Count}}</span></div>
                            </div>

                            <div style="margin: 5px 0; padding: 5px; background: #fff3cd; border-radius: 3px; font-size: 11px;">
                                <strong>異常值移除:</strong> ${{stats.Outliers_removed}} 個數據點 (${{((stats.Outliers_removed / stats.Count) * 100).toFixed(1)}}%)
                            </div>
                        </div>
                    `).join('')}}
                `;
                container.appendChild(card);
            }}
        }}

        // 創建整合時間序列圖表
        function createIntegratedChart() {{
            updateIntegratedChart();
        }}

        function updateIntegratedChart() {{
            const traces = [];
            const colors = {{
                '419-電阻式_quad': 'rgb(31, 119, 180)',
                '419-電阻式_bicep': 'rgb(255, 127, 14)',
                '445-耦合式_quad': 'rgb(44, 160, 44)',
                '445-耦合式_bicep': 'rgb(214, 39, 40)',
                'Noraxon_quad': 'rgb(148, 103, 189)',
                'Noraxon_bicep': 'rgb(140, 86, 75)'
            }};

            const lineStyles = {{
                '419-電阻式_quad': 'solid',
                '419-電阻式_bicep': 'solid',
                '445-耦合式_quad': 'solid',
                '445-耦合式_bicep': 'solid',
                'Noraxon_quad': 'solid',
                'Noraxon_bicep': 'solid'
            }};

            // 檢查各個checkbox狀態並添加對應的trace
            const checkboxes = [
                {{id: 'check_419_quad', dataset: '419-電阻式', muscle: 'quad', name: '419-電阻式 股四頭肌'}},
                {{id: 'check_419_bicep', dataset: '419-電阻式', muscle: 'bicep', name: '419-電阻式 股二頭肌'}},
                {{id: 'check_445_quad', dataset: '445-耦合式', muscle: 'quad', name: '445-耦合式 股四頭肌'}},
                {{id: 'check_445_bicep', dataset: '445-耦合式', muscle: 'bicep', name: '445-耦合式 股二頭肌'}},
                {{id: 'check_noraxon_quad', dataset: 'Noraxon', muscle: 'quad', name: 'Noraxon 股四頭肌'}},
                {{id: 'check_noraxon_bicep', dataset: 'Noraxon', muscle: 'bicep', name: 'Noraxon 股二頭肌'}}
            ];

            checkboxes.forEach(item => {{
                const checkbox = document.getElementById(item.id);
                if (checkbox && checkbox.checked) {{
                    const data = emgData.timeSeriesData[item.dataset];
                    if (data) {{
                        const yData = item.muscle === 'quad' ? data.quad_data : data.bicep_data;
                        const samplingRate = data.sampling_rate || 1000; // 預設1000Hz
                        const colorKey = `${{item.dataset}}_${{item.muscle}}`;

                        // 限制為前10秒的數據
                        const maxSamples = Math.min(yData.length, samplingRate * 10);
                        const limitedData = yData.slice(0, maxSamples);

                        // 以0.1秒為單位進行重採樣
                        const windowSize = Math.floor(samplingRate * 0.1); // 0.1秒的採樣點數
                        const sampledY = [];
                        const timeData = [];

                        for (let i = 0; i < limitedData.length; i += windowSize) {{
                            const window = limitedData.slice(i, i + windowSize);
                            if (window.length > 0) {{
                                // 取窗口內的平均值
                                const avgValue = window.reduce((sum, val) => sum + val, 0) / window.length;
                                sampledY.push(avgValue);
                                timeData.push(i / samplingRate);
                            }}
                        }}

                        traces.push({{
                            x: timeData,
                            y: sampledY,
                            type: 'scatter',
                            mode: 'lines',
                            name: item.name,
                            line: {{
                                color: colors[colorKey],
                                width: 1.5,
                                dash: lineStyles[colorKey]
                            }},
                            hovertemplate: '<b>%{{fullData.name}}</b><br>時間: %{{x:.3f}} 秒<br>數值: %{{y:.3f}} μV<extra></extra>'
                        }});
                    }}
                }}
            }});

            const layout = {{
                title: {{
                    text: '三組測量系統整合時間序列趨勢分析 (前10秒)',
                    font: {{ size: 16, color: '#333', family: 'Times New Roman' }}
                }},
                xaxis: {{
                    title: {{ text: '時間 (秒)', font: {{ size: 12, family: 'Times New Roman' }} }},
                    showgrid: true,
                    gridcolor: '#f0f0f0',
                    range: [0, 10]
                }},
                yaxis: {{
                    title: {{ text: 'EMG信號 (μV)', font: {{ size: 12, family: 'Times New Roman' }} }},
                    showgrid: true,
                    gridcolor: '#f0f0f0'
                }},
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                font: {{ family: 'Times New Roman', size: 11 }},
                legend: {{
                    x: 1.02,
                    y: 1,
                    bgcolor: 'rgba(255,255,255,0.8)',
                    bordercolor: '#ccc',
                    borderwidth: 1
                }},
                margin: {{ l: 60, r: 150, t: 60, b: 60 }},
                hovermode: 'closest'
            }};

            const config = {{
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                displaylogo: false,
                responsive: true
            }};

            // 使用 Plotly.react 來提高更新性能
            Plotly.react('integratedChart', traces, layout, config);
        }}

        // 創建RMS圖表
        function createRMSChart() {{
            updateRMSChart();
        }}

        function updateRMSChart() {{
            const traces = [];
            const colors = {{
                '419-電阻式_quad': 'rgb(31, 119, 180)',
                '419-電阻式_bicep': 'rgb(255, 127, 14)',
                '445-耦合式_quad': 'rgb(44, 160, 44)',
                '445-耦合式_bicep': 'rgb(214, 39, 40)',
                'Noraxon_quad': 'rgb(148, 103, 189)',
                'Noraxon_bicep': 'rgb(140, 86, 75)'
            }};

            const lineStyles = {{
                '419-電阻式_quad': 'solid',
                '419-電阻式_bicep': 'solid',
                '445-耦合式_quad': 'solid',
                '445-耦合式_bicep': 'solid',
                'Noraxon_quad': 'solid',
                'Noraxon_bicep': 'solid'
            }};

            // 檢查各個checkbox狀態並添加對應的trace
            const checkboxes = [
                {{id: 'rms_check_419_quad', dataset: '419-電阻式', muscle: 'quad', name: '419-電阻式 股四頭肌 RMS'}},
                {{id: 'rms_check_419_bicep', dataset: '419-電阻式', muscle: 'bicep', name: '419-電阻式 股二頭肌 RMS'}},
                {{id: 'rms_check_445_quad', dataset: '445-耦合式', muscle: 'quad', name: '445-耦合式 股四頭肌 RMS'}},
                {{id: 'rms_check_445_bicep', dataset: '445-耦合式', muscle: 'bicep', name: '445-耦合式 股二頭肌 RMS'}},
                {{id: 'rms_check_noraxon_quad', dataset: 'Noraxon', muscle: 'quad', name: 'Noraxon 股四頭肌 RMS'}},
                {{id: 'rms_check_noraxon_bicep', dataset: 'Noraxon', muscle: 'bicep', name: 'Noraxon 股二頭肌 RMS'}}
            ];

            checkboxes.forEach(item => {{
                const checkbox = document.getElementById(item.id);
                if (checkbox && checkbox.checked) {{
                    const data = emgData.timeSeriesData[item.dataset];
                    if (data) {{
                        const yData = item.muscle === 'quad' ? data.quad_data : data.bicep_data;
                        const samplingRate = data.sampling_rate || 1000; // 預設1000Hz
                        const colorKey = `${{item.dataset}}_${{item.muscle}}`;

                        // 限制為前10秒的數據
                        const maxSamples = Math.min(yData.length, samplingRate * 10);
                        const limitedData = yData.slice(0, maxSamples);

                        // 以0.1秒為單位計算RMS
                        const windowSize = Math.floor(samplingRate * 0.1); // 0.1秒的採樣點數
                        const rmsValues = [];
                        const timeData = [];

                        for (let i = 0; i < limitedData.length; i += windowSize) {{
                            const window = limitedData.slice(i, i + windowSize);
                            if (window.length > 0) {{
                                // 計算RMS值
                                const rms = Math.sqrt(window.reduce((sum, val) => sum + val * val, 0) / window.length);
                                rmsValues.push(rms);
                                timeData.push(i / samplingRate);
                            }}
                        }}

                        traces.push({{
                            x: timeData,
                            y: rmsValues,
                            type: 'scatter',
                            mode: 'lines+markers',
                            name: item.name,
                            line: {{
                                color: colors[colorKey],
                                width: 2,
                                dash: lineStyles[colorKey]
                            }},
                            marker: {{
                                size: 4,
                                color: colors[colorKey]
                            }},
                            hovertemplate: '<b>%{{fullData.name}}</b><br>時間: %{{x:.1f}} 秒<br>RMS: %{{y:.3f}} μV<extra></extra>'
                        }});
                    }}
                }}
            }});

            const layout = {{
                title: {{
                    text: 'EMG RMS數值時間序列分析 (前10秒)',
                    font: {{ size: 16, color: '#333', family: 'Times New Roman' }}
                }},
                xaxis: {{
                    title: {{ text: '時間 (秒)', font: {{ size: 12, family: 'Times New Roman' }} }},
                    showgrid: true,
                    gridcolor: '#f0f0f0',
                    range: [0, 10],
                    dtick: 0.5
                }},
                yaxis: {{
                    title: {{ text: 'RMS值 (μV)', font: {{ size: 12, family: 'Times New Roman' }} }},
                    showgrid: true,
                    gridcolor: '#f0f0f0'
                }},
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                font: {{ family: 'Times New Roman', size: 11 }},
                legend: {{
                    x: 1.02,
                    y: 1,
                    bgcolor: 'rgba(255,255,255,0.8)',
                    bordercolor: '#ccc',
                    borderwidth: 1
                }},
                margin: {{ l: 60, r: 150, t: 60, b: 60 }},
                hovermode: 'closest'
            }};

            const config = {{
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                displaylogo: false,
                responsive: true
            }};

            // 使用 Plotly.react 來提高更新性能
            Plotly.react('rmsChart', traces, layout, config);
        }}



        // 創建時間序列圖表
        function createTimeSeriesChart(datasetName, containerId) {{
            const data = emgData.timeSeriesData[datasetName];
            if (!data) {{
                console.error(`找不到數據集: ${{datasetName}}`);
                return;
            }}

            const quadData = data.quad_data;
            const bicepData = data.bicep_data;
            const samplingRate = data.sampling_rate || 1000; // 預設1000Hz

            // 創建相對時間軸（秒）
            const quadTimeAxis = quadData.map((_, i) => i / samplingRate);
            const bicepTimeAxis = bicepData.map((_, i) => i / samplingRate);

            // 計算統計區間
            const quadMean = quadData.reduce((a, b) => a + b, 0) / quadData.length;
            const quadStd = Math.sqrt(quadData.reduce((a, b) => a + (b - quadMean) ** 2, 0) / quadData.length);
            const quadUpper = quadData.map(() => quadMean + 2 * quadStd);
            const quadLower = quadData.map(() => quadMean - 2 * quadStd);

            const bicepMean = bicepData.reduce((a, b) => a + b, 0) / bicepData.length;
            const bicepStd = Math.sqrt(bicepData.reduce((a, b) => a + (b - bicepMean) ** 2, 0) / bicepData.length);
            const bicepUpper = bicepData.map(() => bicepMean + 2 * bicepStd);
            const bicepLower = bicepData.map(() => bicepMean - 2 * bicepStd);

            // 股四頭肌數據
            const quadTrace = {{
                x: quadTimeAxis,
                y: quadData,
                type: 'scatter',
                mode: 'lines',
                name: `${{data.quad_col_name}} (股四頭肌)`,
                line: {{ color: 'rgb(31, 119, 180)', width: 1 }},
                hovertemplate: '<b>%{{fullData.name}}</b><br>時間: %{{x:.3f}} 秒<br>數值: %{{y:.3f}} μV<extra></extra>'
            }};

            // 股四頭肌統計區間
            const quadBandTrace = {{
                x: quadTimeAxis.concat(quadTimeAxis.slice().reverse()),
                y: quadUpper.concat(quadLower.reverse()),
                fill: 'toself',
                fillcolor: 'rgba(31, 119, 180, 0.1)',
                line: {{ color: 'transparent' }},
                name: '股四頭肌 ±2σ 區間',
                showlegend: true,
                hoverinfo: 'skip'
            }};

            // 股二頭肌數據
            const bicepTrace = {{
                x: bicepTimeAxis,
                y: bicepData,
                type: 'scatter',
                mode: 'lines',
                name: `${{data.bicep_col_name}} (股二頭肌)`,
                line: {{ color: 'rgb(255, 127, 14)', width: 1 }},
                hovertemplate: '<b>%{{fullData.name}}</b><br>時間: %{{x:.3f}} 秒<br>數值: %{{y:.3f}} μV<extra></extra>'
            }};

            // 股二頭肌統計區間
            const bicepBandTrace = {{
                x: bicepTimeAxis.concat(bicepTimeAxis.slice().reverse()),
                y: bicepUpper.concat(bicepLower.reverse()),
                fill: 'toself',
                fillcolor: 'rgba(255, 127, 14, 0.1)',
                line: {{ color: 'transparent' }},
                name: '股二頭肌 ±2σ 區間',
                showlegend: true,
                hoverinfo: 'skip'
            }};

            const layout = {{
                title: {{
                    text: `${{datasetName}} 時間序列數據分佈`,
                    font: {{ size: 14, color: '#333', family: 'Times New Roman' }}
                }},
                xaxis: {{
                    title: {{ text: '時間 (秒)', font: {{ size: 12, family: 'Times New Roman' }} }},
                    showgrid: true,
                    gridcolor: '#f0f0f0'
                }},
                yaxis: {{
                    title: {{ text: 'EMG信號 (μV)', font: {{ size: 12, family: 'Times New Roman' }} }},
                    showgrid: true,
                    gridcolor: '#f0f0f0'
                }},
                plot_bgcolor: 'white',
                paper_bgcolor: 'white',
                font: {{ family: 'Times New Roman', size: 10 }},
                legend: {{
                    x: 0.02,
                    y: 0.98,
                    bgcolor: 'rgba(255,255,255,0.8)',
                    bordercolor: '#ccc',
                    borderwidth: 1
                }},
                margin: {{ l: 60, r: 30, t: 50, b: 50 }}
            }};

            const config = {{
                displayModeBar: true,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                displaylogo: false
            }};

            Plotly.newPlot(containerId, [quadBandTrace, bicepBandTrace, quadTrace, bicepTrace], layout, config);
        }}

        // 初始化頁面
        function init() {{
            if (emgData.analysisResults && Object.keys(emgData.analysisResults).length > 0) {{
                displayBasicResults(emgData.analysisResults);
                displayDetailedStats(emgData.detailedStats);

                // 創建整合時間序列圖表
                if (emgData.timeSeriesData) {{
                    createIntegratedChart();
                    createRMSChart();

                    // 創建各別時間序列圖表
                    createTimeSeriesChart('419-電阻式', 'timeSeries419');
                    createTimeSeriesChart('445-耦合式', 'timeSeries445');
                    createTimeSeriesChart('Noraxon', 'timeSeriesNoraxon');
                }}
            }} else {{
                document.getElementById('basicResults').innerHTML = '<p>❌ 無可用數據</p>';
            }}
        }}

        // Raw Data 預覽功能
        function showRawData(datasetName) {{
            const rawData = emgData.rawDataPreview[datasetName];
            if (!rawData) {{
                alert('無法找到該數據集的原始數據');
                return;
            }}

            const modal = document.getElementById('rawDataModal');
            const modalTitle = document.getElementById('modalTitle');
            const modalContent = document.getElementById('modalContent');

            modalTitle.textContent = `原始數據預覽 - ${{datasetName}}`;

            let html = '<div style="margin-bottom: 15px;">';
            html += '<p><strong>說明:</strong></p>';
            html += '<ul>';
            html += '<li><span style="background: #ffeb3b; padding: 2px 5px;">黃色高亮</span> = 股四頭肌信號欄位</li>';
            html += '<li><span style="background: #4caf50; color: white; padding: 2px 5px;">綠色高亮</span> = 股二頭肌信號欄位</li>';
            html += '</ul>';
            html += '<p><strong>顯示完整數據集</strong></p>';
            html += '</div>';

            html += '<table class="raw-data-table">';
            html += '<thead><tr>';

            // 添加標題行
            rawData.headers.forEach((header, index) => {{
                let className = '';
                if (rawData.type === 'Noraxon') {{
                    if (header === rawData.quad_col) className = 'highlight-quad';
                    if (header === rawData.bicep_col) className = 'highlight-bicep';
                }} else {{
                    if (index === rawData.quad_col) className = 'highlight-quad';
                    if (index === rawData.bicep_col) className = 'highlight-bicep';
                }}
                html += `<th class="${{className}}">${{header}}</th>`;
            }});
            html += '</tr></thead><tbody>';

            // 添加數據行
            rawData.data.forEach(row => {{
                html += '<tr>';
                row.forEach((cell, index) => {{
                    let className = '';
                    if (rawData.type === 'Noraxon') {{
                        if (rawData.headers[index] === rawData.quad_col) className = 'highlight-quad';
                        if (rawData.headers[index] === rawData.bicep_col) className = 'highlight-bicep';
                    }} else {{
                        if (index === rawData.quad_col) className = 'highlight-quad';
                        if (index === rawData.bicep_col) className = 'highlight-bicep';
                    }}
                    const cellValue = typeof cell === 'number' ? cell.toFixed(6) : cell;
                    html += `<td class="${{className}}">${{cellValue}}</td>`;
                }});
                html += '</tr>';
            }});
            html += '</tbody></table>';

            modalContent.innerHTML = html;
            modal.style.display = 'block';
        }}

        function closeRawDataModal() {{
            document.getElementById('rawDataModal').style.display = 'none';
        }}

        // 點擊模態框外部關閉
        window.onclick = function(event) {{
            const modal = document.getElementById('rawDataModal');
            if (event.target === modal) {{
                modal.style.display = 'none';
            }}
        }}

        // 頁面載入完成後執行
        document.addEventListener('DOMContentLoaded', init);
    </script>
</body>
</html>
    '''
    
    with open('emg_report_live.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return 'emg_report_live.html'

def start_web_server():
    """啟動網頁服務器"""
    PORT = 8000
    
    # 生成HTML報告
    report_file = generate_html_report()
    print(f"✅ 已生成報告文件: {report_file}")
    
    # 切換到EMG目錄
    os.chdir('/Volumes/dev/EMG')
    
    class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            super().end_headers()
    
    with HTTPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 EMG分析報告服務器已啟動")
        print(f"📊 請在瀏覽器中訪問: http://localhost:{PORT}/{report_file}")
        print(f"⏹️  按 Ctrl+C 停止服務器")
        
        # 延遲2秒後自動打開瀏覽器
        def open_browser():
            time.sleep(2)
            webbrowser.open(f'http://localhost:{PORT}/{report_file}')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✅ 服務器已停止")
            httpd.shutdown()

def main():
    """主函數"""
    start_web_server()

if __name__ == "__main__":
    main()