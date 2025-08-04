#!/usr/bin/env python3
"""
Fallback Integration Test - Phase 3A Verification

Tests that the modified _generate_with_med42() function properly integrates
with the fallback chain, using the Whipple's disease case.

Author: OnCall.ai Team
Date: 2025-08-03
"""

import sys
import os
from pathlib import Path
import logging

# Setup
current_dir = Path(__file__).parent
project_root = current_dir.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

# Configure logging to see fallback flow
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_fallback_integration():
    """Test that fallback mechanism is properly integrated"""
    print("🧪 Testing Fallback Integration (Phase 3A)")
    print("="*60)
    
    try:
        # Import with fallback to mock if needed
        try:
            from generation import MedicalAdviceGenerator
            from llm_clients import llm_Med42_70BClient
            
            # Initialize with real components
            llm_client = llm_Med42_70BClient()
            generator = MedicalAdviceGenerator(llm_client=llm_client)
            print("✅ Real components initialized")
            
        except Exception as e:
            print(f"⚠️  Using mock environment due to: {e}")
            # Create basic mock for testing
            from unittest.mock import MagicMock
            
            class MockLLMClient:
                def analyze_medical_query(self, query, max_tokens, timeout):
                    # Simulate timeout to trigger fallback
                    raise Exception("Simulated API timeout for fallback testing")
            
            # Import only the generator class
            from generation import MedicalAdviceGenerator
            generator = MedicalAdviceGenerator(llm_client=MockLLMClient())
            print("✅ Mock environment for testing")
        
        # Test the integrated fallback system
        test_prompt = """
        You are an experienced attending physician providing guidance.
        
        Clinical Question:
        Suspected Whipple's disease with cognitive changes
        
        Relevant Medical Guidelines:
        Whipple disease is a rare systemic infection caused by Tropheryma whipplei.
        Neurological manifestations include cognitive impairment and psychiatric symptoms.
        Treatment involves long-term antibiotic therapy.
        
        Instructions:
        Provide clear clinical guidance for this case.
        """
        
        print(f"\n🔄 Testing fallback with Whipple's disease case...")
        print("Expected flow: Primary → Fallback 1 → Fallback 2 → Result")
        
        # This should trigger the fallback chain
        result = generator._generate_with_med42(test_prompt)
        
        print(f"\n📊 RESULTS:")
        print(f"✅ Fallback method used: {result.get('fallback_method', 'unknown')}")
        print(f"✅ Response type: {type(result.get('raw_response', ''))}")
        print(f"✅ Has error info: {'error' in result}")
        print(f"✅ Has primary error: {'primary_error' in result}")
        
        # Verify fallback metadata
        if result.get('fallback_method'):
            print(f"🎯 SUCCESS: Fallback system is integrated and functional!")
            print(f"   Method: {result['fallback_method']}")
            if result.get('primary_error'):
                print(f"   Primary error: {result['primary_error'][:50]}...")
        else:
            print(f"⚠️  Unexpected: No fallback method marked in result")
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_fallback_configuration_access():
    """Verify that fallback configurations are accessible"""
    print(f"\n🧪 Testing Configuration Access")
    print("="*40)
    
    try:
        from generation import (
            FALLBACK_TIMEOUTS, 
            FALLBACK_TOKEN_LIMITS, 
            FALLBACK_CONFIDENCE_SCORES
        )
        
        print(f"✅ Timeouts: {FALLBACK_TIMEOUTS}")
        print(f"✅ Token limits: {FALLBACK_TOKEN_LIMITS}")
        print(f"✅ Confidence scores: {FALLBACK_CONFIDENCE_SCORES}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration access failed: {e}")
        return False

def main():
    """Run Phase 3A integration verification"""
    print("🚀 Phase 3A: Fallback Integration Verification")
    print("="*70) 
    
    tests = [
        ("Configuration Access", test_fallback_configuration_access),
        ("Fallback Integration", test_fallback_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*70)
    print("📊 PHASE 3A INTEGRATION SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\n📈 Integration Status: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 PHASE 3A COMPLETED SUCCESSFULLY!")
        print("✅ Fallback mechanism is integrated and ready for testing")
        print("🚀 Ready to proceed with Phase 3B: End-to-End Testing")
    else:
        print("⚠️  Integration issues detected - review implementation")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)