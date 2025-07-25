#!/usr/bin/env python3
"""
EMG肌力分析系統啟動腳本
EMG Muscle Strength Analysis System Launcher

使用方法 (Usage):
python run.py

然後在瀏覽器中訪問: http://localhost:8000/emg_report_live.html
Then visit in browser: http://localhost:8000/emg_report_live.html
"""

import sys
import os

def main():
    """主函數"""
    print("🚀 啟動EMG肌力分析系統...")
    print("🚀 Starting EMG Muscle Strength Analysis System...")
    print()
    
    # 檢查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    
    # 檢查必要的模組
    try:
        import pandas
        import numpy
        print("✅ 依賴模組檢查通過")
        print("✅ Dependencies check passed")
    except ImportError as e:
        print(f"❌ 缺少必要模組: {e}")
        print("❌ Missing required module")
        print("請運行: pip install -r requirements.txt")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    # 檢查數據檔案
    data_files = ['419-電阻式.csv', '445-藕合式.csv', 'Noraxon.csv']
    missing_files = []
    for file in data_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  缺少數據檔案: {', '.join(missing_files)}")
        print(f"⚠️  Missing data files: {', '.join(missing_files)}")
        print("系統將繼續運行，但可能無法顯示完整結果")
        print("System will continue but may not show complete results")
        print()
    
    # 啟動主程式
    try:
        from emg_web_report import start_web_server
        print("📊 正在生成分析報告...")
        print("📊 Generating analysis report...")
        start_web_server()
    except KeyboardInterrupt:
        print("\n👋 系統已停止")
        print("👋 System stopped")
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        print(f"❌ Failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
