# 🚀 EMG分析系統部署指南

## 📋 GitHub部署步驟

### 1. 創建GitHub倉庫
1. 登入您的GitHub帳號
2. 點擊右上角的 "+" 按鈕，選擇 "New repository"
3. 倉庫名稱建議: `EMG-Analysis` 或 `EMG-Muscle-Strength-Analysis`
4. 設為 **Public** (公開倉庫)
5. **不要** 勾選 "Add a README file" (我們已經有了)
6. 點擊 "Create repository"

### 2. 推送代碼到GitHub
在終端機中執行以下命令 (請將 `YOUR_USERNAME` 替換為您的GitHub用戶名):

```bash
# 添加遠程倉庫
git remote add origin https://github.com/YOUR_USERNAME/EMG-Analysis.git

# 推送代碼
git branch -M main
git push -u origin main
```

### 3. 啟用GitHub Pages
1. 進入您的GitHub倉庫頁面
2. 點擊 "Settings" 標籤
3. 在左側選單中找到 "Pages"
4. 在 "Source" 部分選擇 "GitHub Actions"
5. 系統會自動檢測到我們的 `.github/workflows/deploy.yml` 文件

### 4. 等待自動部署
- 推送代碼後，GitHub Actions會自動運行
- 可以在 "Actions" 標籤中查看部署進度
- 部署完成後，您的網站將可在以下網址訪問:

```
https://YOUR_USERNAME.github.io/EMG-Analysis/
```

## 🌐 訪問網址

部署完成後，您將獲得以下網址:

### 主頁面
```
https://YOUR_USERNAME.github.io/EMG-Analysis/
```

### EMG分析報告
```
https://YOUR_USERNAME.github.io/EMG-Analysis/emg_report_live.html
```

## 🔧 本地開發

如果需要在本地繼續開發:

```bash
# 安裝依賴
pip install -r requirements.txt

# 運行開發服務器
python run.py

# 或直接運行主程式
python emg_web_report.py
```

## 📊 功能驗證

部署完成後，請驗證以下功能:

### ✅ 基本功能
- [ ] 主頁面正常載入
- [ ] EMG分析報告頁面正常顯示
- [ ] 三組數據的統計結果正確顯示

### ✅ 互動功能
- [ ] 5.1圖表的checkbox即時更新
- [ ] 5.2圖表的checkbox即時更新
- [ ] 原始數據預覽功能正常

### ✅ 視覺效果
- [ ] 所有圖表使用實線顯示
- [ ] Times New Roman字型正確載入
- [ ] 響應式設計在不同設備上正常

## 🐛 故障排除

### 如果GitHub Pages沒有自動部署:
1. 檢查 "Actions" 標籤中的錯誤訊息
2. 確認 `.github/workflows/deploy.yml` 文件存在
3. 確認倉庫設定中的Pages設定正確

### 如果網站顯示404錯誤:
1. 等待5-10分鐘讓DNS生效
2. 檢查倉庫名稱是否正確
3. 確認倉庫設為Public

### 如果圖表不顯示:
1. 檢查瀏覽器控制台的錯誤訊息
2. 確認網路連線正常 (需要載入外部JS庫)
3. 嘗試重新整理頁面

## 📱 分享您的項目

部署完成後，您可以:

1. **分享網址**: 直接分享GitHub Pages網址
2. **嵌入網站**: 將報告嵌入其他網站
3. **學術引用**: 在論文中引用您的分析系統
4. **教學使用**: 用於EMG信號處理的教學演示

## 🔄 更新部署

當您修改代碼後:

```bash
# 提交更改
git add .
git commit -m "更新描述"
git push

# GitHub Actions會自動重新部署
```

## 📧 技術支援

如遇到部署問題，請:
1. 檢查GitHub Actions的執行日誌
2. 確認所有文件都已正確推送
3. 查看GitHub Pages的設定狀態
