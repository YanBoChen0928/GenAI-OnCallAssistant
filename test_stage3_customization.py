#!/usr/bin/env python3
"""階段 3 測試：Customization Pipeline 雲端載入測試"""

import os
import sys
from pathlib import Path

# 設置環境變數測試雲端模式
os.environ['USE_CLOUD_DATA'] = 'true'

# 添加路徑
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

def test_customization_pipeline():
    """測試 Customization Pipeline 雲端載入"""
    print("🧪 階段 3 測試：Customization Pipeline 雲端載入...")
    
    try:
        from customization.customization_pipeline import retrieve_document_chunks
        print("✅ customization_pipeline 模組載入成功")
        
        # 測試 customization pipeline (會觸發雲端下載)
        print("🏥 測試 customization 查詢...")
        results = retrieve_document_chunks("chest pain", top_k=3)
        print(f"✅ Customization search 成功，返回 {len(results)} 個結果")
        
        # 測試另一個查詢
        print("🏥 測試另一個 customization 查詢...")
        results2 = retrieve_document_chunks("emergency treatment", top_k=5)
        print(f"✅ 第二個查詢成功，返回 {len(results2)} 個結果")
        
        print("🎉 階段 3 測試通過：Customization Pipeline 雲端載入正常！")
        return True
        
    except Exception as e:
        print(f"❌ 階段 3 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_customization_pipeline()
    print(f"\n📋 測試結果: {'成功' if success else '失敗'}")
    exit(0 if success else 1)
