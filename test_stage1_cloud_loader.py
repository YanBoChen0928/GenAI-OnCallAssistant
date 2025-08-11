#!/usr/bin/env python3
"""階段 1 測試：雲端載入器獨立功能測試"""

import os
import sys
from pathlib import Path

# 設置環境變數測試雲端模式
os.environ['USE_CLOUD_DATA'] = 'true'

# 添加 src 到路徑
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_cloud_loader():
    """測試雲端載入器基礎功能"""
    print("🧪 階段 1 測試：雲端載入器連線...")
    
    try:
        from cloud_loader import cloud_loader
        print("✅ cloud_loader 模組載入成功")
        
        # 測試 Dataset Repository 連線
        print(f"📊 Dataset Repository: {cloud_loader.dataset_repo}")
        print(f"🔗 使用雲端模式: {cloud_loader.use_cloud}")
        
        # 測試下載一個小檔案
        print("📁 測試下載小檔案...")
        test_file = cloud_loader.get_model_file_path("models/data_validation_report.json")
        print(f"✅ 檔案下載成功: {test_file}")
        
        # 檢查檔案是否存在
        if os.path.exists(test_file):
            print(f"✅ 檔案確實存在: {Path(test_file).stat().st_size} bytes")
        else:
            print("❌ 檔案下載後不存在")
            return False
            
        print("🎉 階段 1 測試通過：雲端載入器連線正常！")
        return True
        
    except Exception as e:
        print(f"❌ 階段 1 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cloud_loader()
    print(f"\n📋 測試結果: {'成功' if success else '失敗'}")
    exit(0 if success else 1)
