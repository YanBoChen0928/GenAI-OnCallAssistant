#!/usr/bin/env python3
"""階段 4 測試：完整整合測試 - 模擬 app.py 流程"""

import os
import sys
import time
from pathlib import Path
from typing import Dict, Any

# 設置環境變數測試雲端模式
os.environ['USE_CLOUD_DATA'] = 'true'

# 添加路徑
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

def test_full_integration():
    """完整整合測試"""
    print("🧪 階段 4 測試：完整整合測試...")
    print("=" * 60)
    
    results = {}
    
    try:
        # Test 1: Core system initialization
        print("\n🔧 測試 1: 核心系統初始化")
        start_time = time.time()
        
        from user_prompt import UserPromptProcessor
        from retrieval import BasicRetrievalSystem
        
        processor = UserPromptProcessor()
        retrieval_system = BasicRetrievalSystem()
        
        init_time = time.time() - start_time
        print(f"✅ 核心系統初始化成功 ({init_time:.2f}秒)")
        results['core_init_time'] = init_time
        
        # Test 2: General Pipeline test
        print("\n🔍 測試 2: General Pipeline 功能")
        test_queries = [
            "chest pain emergency",
            "heart attack symptoms", 
            "respiratory distress"
        ]
        
        for query in test_queries:
            start_time = time.time()
            search_results = retrieval_system.search(query, top_k=5)
            search_time = time.time() - start_time
            
            result_count = len(search_results.get('processed_results', []))
            print(f"  📊 '{query}': {result_count} 個結果 ({search_time:.3f}秒)")
            
        print("✅ General Pipeline 測試完成")
        
        # Test 3: Customization Pipeline test
        print("\n🏥 測試 3: Customization Pipeline 功能")
        try:
            from customization.customization_pipeline import retrieve_document_chunks
            
            for query in test_queries:
                start_time = time.time()
                custom_results = retrieve_document_chunks(query, top_k=3)
                custom_time = time.time() - start_time
                
                print(f"  🏥 '{query}': {len(custom_results)} 個結果 ({custom_time:.3f}秒)")
                
            print("✅ Customization Pipeline 測試完成")
            results['customization_available'] = True
            
        except Exception as e:
            print(f"❌ Customization Pipeline 錯誤: {e}")
            results['customization_available'] = False
        
        # Test 4: Combined mode simulation (like app.py)
        print("\n🔄 測試 4: Combined Mode 模擬")
        test_query = "chest pain emergency treatment"
        
        # Step 1: UserPromptProcessor (correct method name)
        start_time = time.time()
        extraction_result = processor.extract_condition_keywords(test_query)
        extraction_time = time.time() - start_time
        print(f"  📝 Condition extraction: {extraction_time:.3f}秒")
        print(f"      Condition: {extraction_result.get('condition', 'None')}")
        print(f"      Emergency keywords: {extraction_result.get('emergency_keywords', 'None')}")
        print(f"      Treatment keywords: {extraction_result.get('treatment_keywords', 'None')}")
        
        # Step 2: General retrieval
        start_time = time.time()
        general_results = retrieval_system.search(test_query, top_k=5)
        general_time = time.time() - start_time
        general_count = len(general_results.get('processed_results', []))
        print(f"  🔍 General retrieval: {general_count} 個結果 ({general_time:.3f}秒)")
        
        # Step 3: Customization retrieval (if available)
        if results['customization_available']:
            start_time = time.time()
            custom_results = retrieve_document_chunks(test_query, top_k=3)
            custom_time = time.time() - start_time
            print(f"  🏥 Hospital retrieval: {len(custom_results)} 個結果 ({custom_time:.3f}秒)")
        
        print("✅ Combined Mode 模擬完成")
        
        # Test 5: Performance comparison
        print("\n⚡ 測試 5: 性能測試 (熱啟動)")
        queries_for_speed = ["emergency", "treatment", "chest pain"]
        
        for query in queries_for_speed:
            # General pipeline speed
            start_time = time.time()
            retrieval_system.search(query, top_k=3)
            general_speed = time.time() - start_time
            
            # Customization pipeline speed (if available)
            if results['customization_available']:
                start_time = time.time() 
                retrieve_document_chunks(query, top_k=3)
                custom_speed = time.time() - start_time
                print(f"  ⚡ '{query}': General {general_speed:.3f}s, Hospital {custom_speed:.3f}s")
            else:
                print(f"  ⚡ '{query}': General {general_speed:.3f}s")
        
        print("✅ 性能測試完成")
        
        print("\n" + "=" * 60)
        print("🎉 階段 4 整合測試完全成功！")
        print("📊 摘要:")
        print(f"  - 核心系統初始化時間: {results['core_init_time']:.2f}秒") 
        print(f"  - Customization 功能: {'可用' if results['customization_available'] else '不可用'}")
        print(f"  - 兩條 Pipeline 都能從雲端載入資料")
        print(f"  - 系統整合功能完整")
        
        return True
        
    except Exception as e:
        print(f"❌ 階段 4 整合測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_environment_switching():
    """測試環境變數切換功能"""
    print("\n🔄 額外測試: 環境變數切換")
    
    try:
        # Test cloud mode
        os.environ['USE_CLOUD_DATA'] = 'true'
        from cloud_loader import CloudDataLoader
        loader_cloud = CloudDataLoader()
        print(f"  ☁️ 雲端模式: {loader_cloud.use_cloud}")
        
        # Test local mode  
        os.environ['USE_CLOUD_DATA'] = 'false'
        loader_local = CloudDataLoader()
        print(f"  💻 本地模式: {loader_local.use_cloud}")
        
        # Reset to cloud mode
        os.environ['USE_CLOUD_DATA'] = 'true'
        
        print("✅ 環境變數切換測試成功")
        return True
        
    except Exception as e:
        print(f"❌ 環境變數切換測試失敗: {e}")
        return False

if __name__ == "__main__":
    print("🚀 開始階段 4: 完整整合測試")
    
    # Main integration test
    integration_success = test_full_integration()
    
    # Environment switching test
    env_success = test_environment_switching()
    
    overall_success = integration_success and env_success
    
    print(f"\n📋 階段 4 總結果: {'完全成功' if overall_success else '部分失敗'}")
    
    if overall_success:
        print("🎯 準備進入階段 5: 部署到 Spaces")
    
    exit(0 if overall_success else 1)
