#!/usr/bin/env python3
"""階段 2 測試：核心檢索系統雲端載入測試"""

import os
import sys
from pathlib import Path

# 設置環境變數測試雲端模式
os.environ['USE_CLOUD_DATA'] = 'true'

# 添加 src 到路徑
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def test_core_retrieval_system():
    """測試核心檢索系統雲端載入"""
    print("🧪 階段 2 測試：核心檢索系統雲端載入...")
    
    try:
        from retrieval import BasicRetrievalSystem
        print("✅ BasicRetrievalSystem 模組載入成功")
        
        # 初始化檢索系統 (會觸發雲端下載)
        print("📊 初始化檢索系統...")
        retrieval_system = BasicRetrievalSystem()
        print("✅ 檢索系統初始化成功")
        
        # 測試 emergency search (使用 general search 方法)
        print("🚨 測試 emergency search...")
        emergency_results = retrieval_system.search("chest pain emergency", top_k=3)
        print(f"✅ Emergency search 成功，返回 {len(emergency_results.get('processed_results', []))} 個結果")
        
        # 測試 treatment search (使用 general search 方法)
        print("💊 測試 treatment search...")
        treatment_results = retrieval_system.search("chest pain treatment", top_k=3)
        print(f"✅ Treatment search 成功，返回 {len(treatment_results.get('processed_results', []))} 個結果")
        
        # 測試 general search
        print("🔍 測試 general search...")
        general_results = retrieval_system.search("medical emergency", top_k=5)
        print(f"✅ General search 成功，返回 {len(general_results.get('processed_results', []))} 個結果")
        
        print("🎉 階段 2 測試通過：核心檢索系統雲端載入正常！")
        return True
        
    except Exception as e:
        print(f"❌ 階段 2 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_core_retrieval_system()
    print(f"\n📋 測試結果: {'成功' if success else '失敗'}")
    exit(0 if success else 1)
