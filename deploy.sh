#!/bin/bash

# EMG分析系統GitHub部署腳本
# EMG Analysis System GitHub Deployment Script

echo "🚀 EMG分析系統GitHub部署腳本"
echo "🚀 EMG Analysis System GitHub Deployment Script"
echo ""

# 檢查是否已設定GitHub用戶名
if [ -z "$1" ]; then
    echo "❌ 請提供您的GitHub用戶名"
    echo "❌ Please provide your GitHub username"
    echo ""
    echo "使用方法 (Usage): ./deploy.sh YOUR_GITHUB_USERNAME"
    echo "例如 (Example): ./deploy.sh john-doe"
    exit 1
fi

GITHUB_USERNAME=$1
REPO_NAME="EMG-Analysis"

echo "📋 部署設定:"
echo "📋 Deployment Settings:"
echo "GitHub用戶名 (Username): $GITHUB_USERNAME"
echo "倉庫名稱 (Repository): $REPO_NAME"
echo ""

# 檢查是否已經設定遠程倉庫
if git remote get-url origin > /dev/null 2>&1; then
    echo "⚠️  遠程倉庫已存在，將更新現有倉庫"
    echo "⚠️  Remote repository exists, updating existing repo"
else
    echo "🔗 添加遠程倉庫..."
    echo "🔗 Adding remote repository..."
    git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git
fi

# 生成最新的EMG報告
echo "📊 生成最新的EMG分析報告..."
echo "📊 Generating latest EMG analysis report..."
python -c "
from emg_web_report import generate_html_report
generate_html_report()
print('✅ EMG報告已更新')
"

# 提交更改
echo "💾 提交更改..."
echo "💾 Committing changes..."
git add .
git commit -m "Update EMG analysis report - $(date '+%Y-%m-%d %H:%M:%S')"

# 推送到GitHub
echo "⬆️  推送到GitHub..."
echo "⬆️  Pushing to GitHub..."
git branch -M main
git push -u origin main

echo ""
echo "✅ 部署完成！"
echo "✅ Deployment completed!"
echo ""
echo "🌐 您的EMG分析系統將在以下網址可用:"
echo "🌐 Your EMG Analysis System will be available at:"
echo ""
echo "主頁面 (Main Page):"
echo "https://$GITHUB_USERNAME.github.io/$REPO_NAME/"
echo ""
echo "EMG分析報告 (EMG Analysis Report):"
echo "https://$GITHUB_USERNAME.github.io/$REPO_NAME/emg_report_live.html"
echo ""
echo "📝 注意事項 (Notes):"
echo "1. 首次部署可能需要5-10分鐘才能生效"
echo "   First deployment may take 5-10 minutes to take effect"
echo ""
echo "2. 請確保在GitHub倉庫設定中啟用GitHub Pages"
echo "   Please ensure GitHub Pages is enabled in repository settings"
echo ""
echo "3. 如需查看部署狀態，請訪問:"
echo "   To check deployment status, visit:"
echo "   https://github.com/$GITHUB_USERNAME/$REPO_NAME/actions"
echo ""
echo "🎉 享受您的EMG分析系統！"
echo "🎉 Enjoy your EMG Analysis System!"
