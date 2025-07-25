# EMG肌力分析系統 (EMG Muscle Strength Analysis System)

基於表面肌電圖(sEMG)技術的人類肌力計算與分析系統，實現公式1的計算實作，為非侵入性肌力評估提供可靠的技術方案。

## 🎯 研究目的

本研究旨在透過表面肌電圖技術計算人類肌力輸出，基於EMG信號與肌力之間的線性關係理論，採用均方根值(RMS)作為肌電活動的量化指標，建立肌力估算模型。

## 📊 核心功能

### 肌力計算模型
- **公式1實現**: `F = a × RMS(EMG) + b`
- **簡化實現**: `F ≈ RMS(EMG)` (標準化假設)
- **多系統驗證**: 支援三種不同的EMG測量系統

### 數據預處理
- **異常值處理**: 自動移除最高和最低2.5%的數據點
- **統計分析**: 提供處理前後的完整統計對比
- **品質提升**: 有效降低測量噪聲和電極接觸不良的影響

### 視覺化分析
- **5.1 整合時間序列**: 三組測量系統的10秒高解析度趨勢分析
- **5.2 RMS數值序列**: EMG RMS值的時間變化分析(0.1秒窗口)
- **原始數據預覽**: 完整數據集的互動式查看功能
- **統計報告**: 學術論文級別的詳細分析報告

## 🔬 支援的測量系統

1. **419-電阻式感測器**
   - 股四頭肌: 第8欄
   - 股二頭肌: 第4欄

2. **445-耦合式感測器**
   - 股四頭肌: 第8欄
   - 股二頭肌: 第4欄

3. **Noraxon專業設備**
   - 股四頭肌: RT VMO (右側股內側肌)
   - 股二頭肌: RT SEMITEND. (右側半腱肌)
   - 採樣頻率: 2000 Hz

## 🚀 快速開始

### 環境需求
- Python 3.8+
- 虛擬環境 (推薦)

### 安裝步驟
```bash
# 克隆項目
git clone https://github.com/your-username/EMG-Analysis.git
cd EMG-Analysis

# 創建虛擬環境
python -m venv emg_env
source emg_env/bin/activate  # Linux/Mac
# 或 emg_env\Scripts\activate  # Windows

# 安裝依賴
pip install pandas numpy

# 運行分析系統
python emg_web_report.py
```

### 訪問系統
打開瀏覽器訪問: http://localhost:8000/emg_report_live.html

## 📈 功能特點

### 即時互動分析
- ✅ Checkbox即時更新圖表
- ✅ 多數據源靈活選擇
- ✅ 高解析度時間軸(0.1秒精度)
- ✅ 專業的懸停提示和縮放功能

### 學術級報告
- ✅ Times New Roman字型
- ✅ 完整的數學公式說明
- ✅ 詳細的方法論描述
- ✅ 符合期刊發表標準

### 數據品質保證
- ✅ 智能異常值檢測
- ✅ 統計學驗證
- ✅ 多系統交叉驗證
- ✅ 完整的數據溯源

## 🔬 理論基礎

基於Lippold (1952)和Lawrence & De Luca (1983)的研究，在等長收縮條件下，肌電信號的RMS值與肌力輸出呈現良好的線性相關性。

### 數學模型
```
公式1: F = a × RMS(EMG) + b
簡化實現: F_proxy = RMS(EMG)
RMS計算: RMS = √(1/N × Σ(EMG_i)²)
```

## 📊 數據格式

### CSV文件要求
- **編碼**: UTF-8
- **數值格式**: 浮點數 (μV)
- **Noraxon格式**: 包含標題行，跳過前3行元數據
- **其他格式**: 純數值矩陣，無標題行

## 🎨 技術架構

- **後端**: Python + Pandas + NumPy
- **前端**: HTML5 + JavaScript + Plotly.js + Chart.js
- **數據處理**: 實時統計分析和異常值處理
- **視覺化**: 響應式圖表和互動式界面

## 📚 參考文獻

1. Konrad, P. (2005). The ABC of EMG: A practical introduction to kinesiological electromyography.
2. De Luca, C. J. (1997). The use of surface electromyography in biomechanics. Journal of applied biomechanics, 13(2), 135-163.
3. Merletti, R., & Parker, P. A. (Eds.). (2004). Electromyography: physiology, engineering, and non-invasive applications.

## 📄 授權

MIT License

## 🤝 貢獻

歡迎提交Issue和Pull Request來改進這個項目。

## 📧 聯繫

如有問題或建議，請通過GitHub Issues聯繫。
