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

## Phase 1: Initial Assessment

### Step 1.1 - 分析您的說明

我重新理解了您的意思！

### Step 1.2 - 無不清楚的需求

### Step 1.3 - 確認理解（中文）

完全明白了！您的評估架構是：

## 🎯 **評估指標的測試層級**

### **單獨測試 Retrieval（指標 2, 3, 4）**

```python
# 只測試 RAG 系統，因為只有 RAG 系統有這些組件：
retrieval_only_metrics = [
    "條件抽取成功率",    # 只有您的系統有 user_prompt.py
    "檢索相關性",        # 只有 RAG 系統有檢索結果
    "檢索覆蓋率"         # 只有 RAG 系統有檢索→生成的映射
]

# 測試對象：
- Med42-70B_general_RAG（您的系統）✅
- Med42-70B_customized_RAG（Jeff系統）✅
- Med42-70B_direct（無RAG）❌ 沒有檢索組件
- OpenBioLLM-70B（無RAG）❌ 沒有檢索組件
```

### **三模型一起測試（指標 1, 5, 6）**

```python
# 所有模型都能測試的指標：
universal_metrics = [
    "總處理時長",        # 所有模型都有響應時間
    "臨床可操作性",      # Llama3-70B 評估所有模型的輸出
    "臨床證據評分"       # Llama3-70B 評估所有模型的輸出
]

# 測試對象：
- Med42-70B_direct ✅
- Med42-70B_general_RAG ✅
- OpenBioLLM-70B ✅
```

## 📊 **分層評估策略**

### **階段 1：RAG 系統內部評估**

```python
# 只測試有 RAG 的系統
rag_systems = ["Med42-70B_general_RAG", "Med42-70B_customized_RAG"]

# 測試 RAG 特有指標
for system in rag_systems:
    evaluate_retrieval_metrics(system)  # 指標 2, 3, 4
```

### **階段 2：全模型比較評估**

```python
# 測試所有三個模型
all_systems = ["Med42-70B_direct", "Med42-70B_general_RAG", "OpenBioLLM-70B"]

# 測試通用指標
for system in all_systems:
    evaluate_universal_metrics(system)  # 指標 1, 5, 6
```

### **階段 3：綜合分析**

```python
# 合併兩階段結果，生成完整報告
combine_evaluation_results()
```

### Step 1.4 - 無視覺修改確認 ✅

此為評估策略討論，無涉及代碼修改。

**您的理解完全正確！RAG 特有的指標只能在 RAG 系統內部測試，而通用指標可以跨所有模型比較。這樣的分層評估策略非常合理！**

---

## 📊 第七個評估指標（YanBo系統特有）

### 7. 多層級 Fallback 效率（早期攔截率）

**定義：** 系統通過多層級 Fallback 機制在早期層級成功處理查詢的效率

**測量位置：** `src/user_prompt.py` 的 `extract_condition_keywords` 多層級處理邏輯

**計算公式：**
```
Early_Interception_Rate = (Level1_Success + Level2_Success) / Total_Queries

其中：
- Level1_Success = 在預定義映射中直接找到條件的查詢數
- Level2_Success = 通過LLM抽取成功的查詢數  
- Total_Queries = 測試查詢總數

時間節省效果：
Time_Savings = (Late_Avg_Time - Early_Avg_Time) / Late_Avg_Time

早期攔截效率：
Efficiency_Score = Early_Interception_Rate × (1 + Time_Savings)
```

**ASCII 流程圖：**
```
多層級 Fallback 效率示意圖：
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 用戶查詢    │───▶│ Level 1     │───▶│ 直接成功    │
│ "胸痛診斷"  │    │ 預定義映射  │    │ 35% (快)    │
└─────────────┘    └─────────────┘    └─────────────┘
                           │
                           ▼ (失敗)
                   ┌─────────────┐    ┌─────────────┐
                   │ Level 2     │───▶│ LLM抽取成功 │
                   │ LLM 條件抽取│    │ 40% (中等)  │
                   └─────────────┘    └─────────────┘
                           │
                           ▼ (失敗)
                   ┌─────────────┐    ┌─────────────┐
                   │ Level 3-5   │───▶│ 後備成功    │
                   │ 後續層級    │    │ 20% (慢)    │
                   └─────────────┘    └─────────────┘
                           │
                           ▼ (失敗)
                   ┌─────────────┐
                   │ 完全失敗    │
                   │ 5% (錯誤)   │
                   └─────────────┘

早期攔截率 = (35% + 40%) = 75% ✅ 目標 > 70%
```

**實現框架：**
```python
# 基於 user_prompt.py 的多層級處理邏輯
def evaluate_early_interception_efficiency(test_queries: List[str]) -> Dict[str, float]:
    """評估早期攔截率 - YanBo系統核心優勢"""
    
    level1_success = 0  # Level 1: 預定義映射成功
    level2_success = 0  # Level 2: LLM 抽取成功
    later_success = 0   # Level 3-5: 後續層級成功
    total_failures = 0  # 完全失敗
    
    early_times = []    # 早期成功的處理時間
    late_times = []     # 後期成功的處理時間
    
    for query in test_queries:
        # 追蹤每個查詢的成功層級和時間
        success_level, processing_time = track_query_success_level(query)
        
        if success_level == 1:
            level1_success += 1
            early_times.append(processing_time)
        elif success_level == 2:
            level2_success += 1
            early_times.append(processing_time)
        elif success_level in [3, 4, 5]:
            later_success += 1
            late_times.append(processing_time)
        else:
            total_failures += 1
    
    total_queries = len(test_queries)
    early_success_count = level1_success + level2_success
    
    # 計算時間節省效果
    early_avg_time = sum(early_times) / len(early_times) if early_times else 0
    late_avg_time = sum(late_times) / len(late_times) if late_times else 0
    time_savings = (late_avg_time - early_avg_time) / late_avg_time if late_avg_time > 0 else 0
    
    # 綜合效率分數
    early_interception_rate = early_success_count / total_queries
    efficiency_score = early_interception_rate * (1 + time_savings)
    
    return {
        # 核心指標
        "early_interception_rate": early_interception_rate,  # 早期攔截率
        "level1_success_rate": level1_success / total_queries,
        "level2_success_rate": level2_success / total_queries,
        
        # 時間效率
        "early_avg_time": early_avg_time,
        "late_avg_time": late_avg_time,
        "time_savings_rate": time_savings,
        
        # 系統健康度
        "total_success_rate": (total_queries - total_failures) / total_queries,
        "miss_rate": total_failures / total_queries,
        
        # 綜合效率
        "overall_efficiency_score": efficiency_score,
        
        # 詳細分布
        "success_distribution": {
            "level1": level1_success,
            "level2": level2_success, 
            "later_levels": later_success,
            "failures": total_failures
        }
    }

def track_query_success_level(query: str) -> Tuple[int, float]:
    """
    追蹤查詢在哪個層級成功並記錄時間
    
    Args:
        query: 測試查詢
        
    Returns:
        Tuple of (success_level, processing_time)
    """
    start_time = time.time()
    
    # 模擬 user_prompt.py 的層級處理邏輯
    try:
        # Level 1: 檢查預定義映射
        if check_predefined_mapping(query):
            processing_time = time.time() - start_time
            return (1, processing_time)
        
        # Level 2: LLM 條件抽取
        llm_result = llm_client.analyze_medical_query(query)
        if llm_result.get('extracted_condition'):
            processing_time = time.time() - start_time
            return (2, processing_time)
        
        # Level 3: 語義搜索
        semantic_result = semantic_search_fallback(query)
        if semantic_result:
            processing_time = time.time() - start_time
            return (3, processing_time)
        
        # Level 4: 醫學驗證
        validation_result = validate_medical_query(query)
        if not validation_result:  # 驗證通過
            processing_time = time.time() - start_time
            return (4, processing_time)
        
        # Level 5: 通用搜索
        generic_result = generic_medical_search(query)
        if generic_result:
            processing_time = time.time() - start_time
            return (5, processing_time)
        
        # 完全失敗
        processing_time = time.time() - start_time
        return (0, processing_time)
        
    except Exception as e:
        processing_time = time.time() - start_time
        return (0, processing_time)

def check_predefined_mapping(query: str) -> bool:
    """檢查查詢是否在預定義映射中"""
    # 基於 medical_conditions.py 的 CONDITION_KEYWORD_MAPPING
    from medical_conditions import CONDITION_KEYWORD_MAPPING
    
    query_lower = query.lower()
    for condition, keywords in CONDITION_KEYWORD_MAPPING.items():
        if any(keyword.lower() in query_lower for keyword in keywords):
            return True
    return False
```

**目標閾值：** 
- 早期攔截率 ≥ 70%（前兩層解決）
- 時間節省率 ≥ 60%（早期比後期快）
- 總成功率 ≥ 95%（漏接率 < 5%）

---

## 🧪 更新的完整評估流程

### 測試用例設計
```python
# 基於 readme.md 中的範例查詢設計測試集
MEDICAL_TEST_CASES = [
    # Level 1 預期成功（預定義映射）
    "患者胸痛怎麼處理？",
    "心肌梗死的診斷方法？",
    
    # Level 2 預期成功（LLM抽取）
    "60歲男性，有高血壓病史，突發胸痛。可能的原因和評估方法？",
    "30歲患者突發嚴重頭痛和頸部僵硬。鑑別診斷？", 
    
    # Level 3+ 預期成功（複雜查詢）
    "患者急性呼吸困難和腿部水腫。應該考慮什麼？",
    "20歲女性，無病史，突發癲癇。可能原因和完整處理流程？",
    
    # 邊界測試
    "疑似急性出血性中風。下一步處理？"
]
```

### 更新的評估執行流程
```python
def run_complete_evaluation(model_name: str, test_cases: List[str]) -> Dict[str, Any]:
    """執行完整的七項指標評估"""
    
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
    fallback_efficiency_scores = []  # 新增
    
    for query in test_cases:
        # 運行模型並測量所有指標
        
        # 1. 總處理時長
        latency_result = measure_total_latency(query)
        total_latencies.append(latency_result['total_latency'])
        
        # 2. 條件抽取成功率
        extraction_result = evaluate_condition_extraction([query])
        extraction_successes.append(extraction_result['success_rate'])
        
        # 3 & 4. 檢索相關性和覆蓋率
        retrieval_results = get_retrieval_results(query)
        relevance_result = evaluate_retrieval_relevance(retrieval_results)
        relevance_scores.append(relevance_result['average_relevance'])
        
        generated_advice = get_generated_advice(query, retrieval_results)
        coverage_result = evaluate_retrieval_coverage(generated_advice, retrieval_results)
        coverage_scores.append(coverage_result['coverage'])
        
        # 5 & 6. LLM 評估
        response_data = {
            'query': query,
            'advice': generated_advice,
            'retrieval_results': retrieval_results
        }
        
        actionability_result = evaluate_clinical_actionability([response_data])
        actionability_scores.append(actionability_result[0]['overall_score'])
        
        evidence_result = evaluate_clinical_evidence([response_data])
        evidence_scores.append(evidence_result[0]['overall_score'])
        
        # 7. 多層級 Fallback 效率（新增）
        if model_name == "Med42-70B_general_RAG":  # 只對YanBo系統測量
            fallback_result = evaluate_early_interception_efficiency([query])
            fallback_efficiency_scores.append(fallback_result['overall_efficiency_score'])
        
        # 記錄詳細結果...
    
    # 計算平均指標
    results["metrics"] = {
        "average_latency": sum(total_latencies) / len(total_latencies),
        "extraction_success_rate": sum(extraction_successes) / len(extraction_successes),
        "average_relevance": sum(relevance_scores) / len(relevance_scores),
        "average_coverage": sum(coverage_scores) / len(coverage_scores),
        "average_actionability": sum(actionability_scores) / len(actionability_scores),
        "average_evidence_score": sum(evidence_scores) / len(evidence_scores),
        # 新增指標（只對RAG系統有效）
        "average_fallback_efficiency": sum(fallback_efficiency_scores) / len(fallback_efficiency_scores) if fallback_efficiency_scores else 0.0
    }
    
    return results
```

---

## 📊 更新的系統成功標準

### 系統性能目標（七個指標）
```
✅ 達標條件：
1. 總處理時長 ≤ 30秒
2. 條件抽取成功率 ≥ 80%  
3. 檢索相關性 ≥ 0.25（基於實際醫學數據）
4. 檢索覆蓋率 ≥ 60%
5. 臨床可操作性 ≥ 7.0/10
6. 臨床證據評分 ≥ 7.5/10
7. 早期攔截率 ≥ 70%（多層級 Fallback 效率）

🎯 YanBo RAG 系統成功標準：
- RAG增強版在 5-7 項指標上優於基線 Med42-70B
- 早期攔截率體現多層級設計的優勢
- 整體提升幅度 ≥ 15%
```

### YanBo 系統特有優勢分析
```
多層級 Fallback 優勢：
├── 漏接防護：通過多層級降低失敗率至 < 5%
├── 時間優化：70%+ 查詢在前兩層快速解決
├── 系統穩定：即使某層級失敗，後續層級提供保障
└── 智能分流：不同複雜度查詢自動分配到合適層級
```

---

**第七個指標已添加完成，專注測量您的多層級 Fallback 系統的早期攔截效率和時間節省效果。**
