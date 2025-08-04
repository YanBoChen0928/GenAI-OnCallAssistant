# Model use
llm model: (for comparison) with our-own version.
https://huggingface.co/aaditya/Llama3-OpenBioLLM-70B
https://huggingface.co/m42-health/Llama3-Med42-70B

evaluation model:
https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct

```python
"""
參閱 user_query.txt
"""
```


### 評估執行流程
```python
def run_complete_evaluation(model_name: str, test_cases: List[str]) -> Dict[str, Any]:
    """執行完整的六項指標評估"""
    
    results = {
        "model": model_name,
        "metrics": {},
        "detailed_results": []
    }
    
    total_latencies = []
    extraction_successes = []
    relevance_scores = []
    coverage_scores = []
    actionability_scores = []
    evidence_scores = []
    
    for query in test_cases:
        # 運行模型並測量所有指標
        start_time = time.time()
        
        # 1. 總處理時長
        latency_result = measure_total_latency(query)
        total_latencies.append(latency_result['total_latency'])
        
        # 2. 條件抽取成功率
        extraction_result = evaluate_condition_extraction([query])
        extraction_successes.append(extraction_result['success_rate'])
        
        # 3 & 4. 檢索相關性和覆蓋率（需要實際檢索結果）
        retrieval_results = get_retrieval_results(query)
        relevance_result = evaluate_retrieval_relevance(retrieval_results)
        relevance_scores.append(relevance_result['average_relevance'])
        
        generated_advice = get_generated_advice(query, retrieval_results)
        coverage_result = evaluate_retrieval_coverage(generated_advice, retrieval_results)
        coverage_scores.append(coverage_result['coverage'])
        
        # 5 & 6. LLM 評估（需要完整回應）
        response_data = {
            'query': query,
            'advice': generated_advice,
            'retrieval_results': retrieval_results
        }
        
        actionability_result = evaluate_clinical_actionability([response_data])
        actionability_scores.append(actionability_result[0]['overall_score'])
        
        evidence_result = evaluate_clinical_evidence([response_data])
        evidence_scores.append(evidence_result[0]['overall_score'])
        
        # 記錄詳細結果
        results["detailed_results"].append({
            "query": query,
            "latency": latency_result,
            "extraction": extraction_result,
            "relevance": relevance_result,
            "coverage": coverage_result,
            "actionability": actionability_result[0],
            "evidence": evidence_result[0]
        })
    
    # 計算平均指標
    results["metrics"] = {
        "average_latency": sum(total_latencies) / len(total_latencies),
        "extraction_success_rate": sum(extraction_successes) / len(extraction_successes),
        "average_relevance": sum(relevance_scores) / len(relevance_scores),
        "average_coverage": sum(coverage_scores) / len(coverage_scores),
        "average_actionability": sum(actionability_scores) / len(actionability_scores),
        "average_evidence_score": sum(evidence_scores) / len(evidence_scores)
    }
    
    return results
```

---

## 📈 評估結果分析框架

### 統計分析
```python
def analyze_evaluation_results(results_A: Dict, results_B: Dict, results_C: Dict) -> Dict:
    """比較三個模型的評估結果"""
    
    models = ['Med42-70B_direct', 'RAG_enhanced', 'OpenBioLLM-70B']
    metrics = ['latency', 'extraction_success_rate', 'relevance', 'coverage', 'actionability', 'evidence_score']
    
    comparison = {}
    
    for metric in metrics:
        comparison[metric] = {
            models[0]: results_A['metrics'][f'average_{metric}'],
            models[1]: results_B['metrics'][f'average_{metric}'],
            models[2]: results_C['metrics'][f'average_{metric}']
        }
        
        # 計算相對改進
        baseline = comparison[metric][models[0]]
        rag_improvement = ((comparison[metric][models[1]] - baseline) / baseline) * 100
        
        comparison[metric]['rag_improvement_percent'] = rag_improvement
    
    return comparison
```

### 報告生成
```python
def generate_evaluation_report(comparison_results: Dict) -> str:
    """生成評估報告"""
    
    report = f"""
    # OnCall.ai 系統評估報告
    
    ## 評估摘要
    
    | 指標 | Med42-70B | RAG增強版 | OpenBioLLM | RAG改進% |
    |------|-----------|-----------|------------|----------|
    | 處理時長 | {comparison_results['latency']['Med42-70B_direct']:.2f}s | {comparison_results['latency']['RAG_enhanced']:.2f}s | {comparison_results['latency']['OpenBioLLM-70B']:.2f}s | {comparison_results['latency']['rag_improvement_percent']:+.1f}% |
    | 條件抽取成功率 | {comparison_results['extraction_success_rate']['Med42-70B_direct']:.1%} | {comparison_results['extraction_success_rate']['RAG_enhanced']:.1%} | {comparison_results['extraction_success_rate']['OpenBioLLM-70B']:.1%} | {comparison_results['extraction_success_rate']['rag_improvement_percent']:+.1f}% |
    | 檢索相關性 | - | {comparison_results['relevance']['RAG_enhanced']:.3f} | - | - |
    | 檢索覆蓋率 | - | {comparison_results['coverage']['RAG_enhanced']:.1%} | - | - |
    | 臨床可操作性 | {comparison_results['actionability']['Med42-70B_direct']:.1f}/10 | {comparison_results['actionability']['RAG_enhanced']:.1f}/10 | {comparison_results['actionability']['OpenBioLLM-70B']:.1f}/10 | {comparison_results['actionability']['rag_improvement_percent']:+.1f}% |
    | 臨床證據評分 | {comparison_results['evidence_score']['Med42-70B_direct']:.1f}/10 | {comparison_results['evidence_score']['RAG_enhanced']:.1f}/10 | {comparison_results['evidence_score']['OpenBioLLM-70B']:.1f}/10 | {comparison_results['evidence_score']['rag_improvement_percent']:+.1f}% |
    
    """
    
    return report
```

---

## 🔧 實驗執行步驟

### 1. 環境準備
```bash
# 設置 HuggingFace token（用於 Inference Providers）
export HF_TOKEN=your_huggingface_token

# 設置評估模式
export ONCALL_EVAL_MODE=true
```

### 2. 實驗執行腳本框架
```python
# evaluation/run_evaluation.py
def main():
    """主要評估執行函數"""
    
    # 加載測試用例
    test_cases = MEDICAL_TEST_CASES
    
    # 實驗 A: YanBo 系統評估
    print("🔬 開始實驗 A: YanBo 系統評估")
    results_med42_direct = run_complete_evaluation("Med42-70B_direct", test_cases)
    results_general_rag = run_complete_evaluation("Med42-70B_general_RAG", test_cases)  
    results_openbio = run_complete_evaluation("OpenBioLLM-70B", test_cases)
    
    # 分析和報告
    comparison_A = analyze_evaluation_results(results_med42_direct, results_general_rag, results_openbio)
    report_A = generate_evaluation_report(comparison_A)
    
    # 保存結果
    save_results("evaluation/results/yanbo_evaluation.json", {
        "comparison": comparison_A,
        "detailed_results": [results_med42_direct, results_general_rag, results_openbio]
    })
    
    print("✅ 實驗 A 完成，結果已保存")
    
    # 實驗 B: Jeff 系統評估
    print("🔬 開始實驗 B: Jeff 系統評估")
    results_med42_direct_b = run_complete_evaluation("Med42-70B_direct", test_cases)
    results_customized_rag = run_complete_evaluation("Med42-70B_customized_RAG", test_cases)
    results_openbio_b = run_complete_evaluation("OpenBioLLM-70B", test_cases)
    
    # 分析和報告
    comparison_B = analyze_evaluation_results(results_med42_direct_b, results_customized_rag, results_openbio_b)
    report_B = generate_evaluation_report(comparison_B)
    
    # 保存結果
    save_results("evaluation/results/jeff_evaluation.json", {
        "comparison": comparison_B,
        "detailed_results": [results_med42_direct_b, results_customized_rag, results_openbio_b]
    })
    
    print("✅ 實驗 B 完成，結果已保存")

if __name__ == "__main__":
    main()
```

### 3. 預期評估時間
```
總評估時間估算：
├── 每個查詢處理時間：~30秒（包含LLM評估）
├── 測試用例數量：7個
├── 模型數量：3個
└── 總時間：~10-15分鐘每個實驗
```

---

## 📊 評估成功標準

### 系統性能目標
```
✅ 達標條件：
1. 總處理時長 ≤ 30秒
2. 條件抽取成功率 ≥ 80%  
3. 檢索相關性 ≥ 0.2
4. 檢索覆蓋率 ≥ 60%
5. 臨床可操作性 ≥ 7.0/10
6. 臨床證據評分 ≥ 7.5/10

🎯 RAG 系統成功標準：
- RAG增強版在 4-6 項指標上優於基線 Med42-70B
- 整體提升幅度 ≥ 10%
```

### 比較分析重點
```
重點分析維度：
├── RAG 對處理時間的影響（可能增加延遲）
├── RAG 對回答質量的提升（可操作性和證據品質）
├── 不同 RAG 策略的效果差異（general vs customized）
└── 與其他醫學模型的競爭力比較
```

---

## 🛠️ 實施建議

### 分階段實施
```
階段1: 基礎指標實現（1-4項）
├── 利用現有 app.py 中的時間測量
├── 擴展 user_prompt.py 的條件抽取評估
├── 增強 retrieval.py 的相關性分析
└── 實現 generation.py 的覆蓋率計算

階段2: LLM評估實現（5-6項）
├── 設置 HuggingFace Inference Providers
├── 實現 Llama3-70B 評估客戶端
├── 測試評估 prompts 的穩定性
└── 建立評估結果解析邏輯

階段3: 完整實驗執行
├── 準備標準測試用例
├── 執行 YanBo 系統評估（實驗A）
├── 執行 Jeff 系統評估（實驗B）
└── 生成比較分析報告
```

### 實施注意事項
```
⚠️ 重要提醒：
1. 所有評估代碼應獨立於現有系統，避免影響正常運行
2. LLM 評估可能不穩定，建議多次運行取平均值
3. 注意 API 費用控制，特別是 Llama3-70B 調用
4. 保存詳細的中間結果，便於調試和分析
5. 測試用例應涵蓋不同複雜度和醫學領域
```

---

**評估指南完成。請根據此指南實施評估實驗。**
