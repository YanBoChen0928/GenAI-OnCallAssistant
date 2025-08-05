_Chunk
- Semantic_Similarity_Score = cosine_similarity(generated_text, chunk_text)
- 使用BGE-Large-Medical模型计算语义相似度

# Model
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

# **ASCII 流程图：**
```
定制化系统覆盖率计算流程：
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 两阶段检索  │───▶│ 生成的      │───▶│ 计算使用    │
│ 8-15个块    │    │ 医学建议    │    │ 比例        │
└─────────────┘    └─────────────┘    └─────────────┘
      │                    │                    │
      ▼                    ▼                    ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│ 医院PDF     │    │ 医学术语    │    │ Coverage =  │
│ 文档内容    │    │ 匹配分析    │    │ 10/15 = 67% │
└─────────────┘    └─────────────┘    └─────────────┘
```

**实现框架：**
```python
# 基于定制化系统的文档块分析
def evaluate_customization_coverage(generated_advice: str, retrieved_chunks: List[Dict]) -> Dict[str, float]:
    """评估定制化检索覆盖率"""
    
    if not retrieved_chunks:
        return {"coverage": 0.0, "used_chunks": 0, "total_chunks": 0}
    
    used_chunks = 0
    chunk_usage_details = []
    
    # 使用BGE-Large-Medical模型计算语义相似度
    embedding_model = SentenceTransformer("BAAI/bge-large-zh-v1.5")  # Jeff系统使用的模型
    
    for i, chunk in enumerate(retrieved_chunks):
        chunk_text = chunk.get('chunk_text', '')
        document_name = chunk.get('document', '')
        similarity_score = chunk.get('score', 0.0)
        
        # 方法1: 医学术语匹配（基于医院文档特有术语）
        medical_terms = extract_hospital_medical_terms(chunk_text)
        term_matches = count_medical_term_matches(generated_advice, medical_terms)
        term_match_score = term_matches / len(medical_terms) if medical_terms else 0
        
        # 方法2: 语义相似度（使用BGE-Large-Medical）
        chunk_embedding = embedding_model.encode([chunk_text])[0]
        advice_embedding = embedding_model.encode([generated_advice])[0]
        semantic_score = cosine_similarity([chunk_embedding], [advice_embedding])[0][0]
        
        # 综合评分（考虑原始检索分数）
        usage_score = max(term_match_score, semantic_score, similarity_score)
        
        # 阈值判断（使用率 > 0.25 视为已使用，适应医学领域特点）
        is_used = usage_score > 0.25
        if is_used:
            used_chunks += 1
            
        chunk_usage_details.append({
            "chunk_id": i,
            "document": document_name,
            "original_score": similarity_score,
            "term_match_score": term_match_score,
            "semantic_score": semantic_score,
            "usage_score": usage_score,
            "is_used": is_used
        })
    
    coverage = used_chunks / len(retrieved_chunks)
    
    return {
        "coverage": coverage,
        "used_chunks": used_chunks,
        "total_chunks": len(retrieved_chunks),
        "chunk_details": chunk_usage_details,
        "average_original_score": sum(chunk['original_score'] for chunk in chunk_usage_details) / len(chunk_usage_details)
    }

def extract_hospital_medical_terms(text: str) -> List[str]:
    """提取医院文档特有的医学术语"""
    # 基于医院临床指南的专业术语库
    hospital_medical_terms = []
    # 实现细节：结合医院特定术语和标准医学词汇
    return hospital_medical_terms
```

**目标阈值：** ≥ 55%（考虑医院文档的专业性和复杂性）

---

### 5. 临床可操作性（Clinical Actionability）

**定义：** 基于医院定制文档生成建议的临床实用性

**测量位置：** 独立评估模块，使用 LLM 评估

**评估者：** `meta-llama/Llama-3.3-70B-Instruct`

**评估 Prompt：**
```python
CUSTOMIZATION_ACTIONABILITY_PROMPT = """
你是一位在该医院工作了15年的资深主治医师和临床科室主任。你非常熟悉医院的临床指南、诊疗流程和设备资源情况。

现在有一位年轻医师询问临床问题，系统基于医院的内部文档给出了建议。请你评估这个建议在本医院环境下的临床可操作性。

【原始临床问题】
{original_query}

【基于医院文档的建议】
{medical_advice}

【引用的医院文档片段】
{hospital_document_chunks}

【评估标准】
请从以下四个维度评估在医院环境下的临床可操作性（每项 1-10 分）：

1. **医院资源匹配度 (Hospital Resource Compatibility)**
   - 建议所需的设备、药物、检查是否在医院可获得？
   - 是否符合医院的实际诊疗能力和资源配置？
   - 评分：1-10 分

2. **医院流程一致性 (Hospital Process Consistency)**  
   - 建议是否符合医院的标准诊疗流程？
   - 是否与医院的临床路径和指南一致？
   - 评分：1-10 分

3. **实施可行性 (Implementation Feasibility)**
   - 建议是否可在医院当前条件下立即实施？
   - 涉及的科室协作和流程是否现实可行？
   - 评分：1-10 分

4. **医院特色适应性 (Hospital-Specific Adaptation)**
   - 建议是否体现了医院的专科优势和特色？
   - 是否考虑了医院的患者群体特点？
   - 评分：1-10 分

【回答格式】
请严格按照以下 JSON 格式回答：

```json
{
  "resource_compatibility_score": <1-10整数>,
  "process_consistency_score": <1-10整数>, 
  "implementation_feasibility_score": <1-10整数>,
  "hospital_adaptation_score": <1-10整数>,
  "overall_actionability_score": <四项平均分，保留一位小数>,
  "detailed_feedback": "<详细说明各项评分理由，特别指出建议与医院实际情况的匹配程度>"
}
```

请记住：作为本医院的资深医师，你的评估应该基于医院的实际情况和资源能力。
"""
```

**计算公式：**
```
Hospital_Actionability = (Resource_Compatibility + Process_Consistency + Implementation_Feasibility + Hospital_Adaptation) / 4

医院定制化评分标准：
- 9-10 分：完全适合本医院，可立即实施
- 7-8 分：高度适合，需要少量调整
- 5-6 分：基本适合，需要一定适配
- 3-4 分：部分适合，需要显著修改
- 1-2 分：不适合本医院环境
```

**实现框架：**
```python
def evaluate_customization_actionability(responses: List[Dict]) -> List[Dict]:
    """评估医院定制化系统的临床可操作性"""
    evaluator_client = HuggingFaceInferenceClient(
        model="meta-llama/Llama-3.3-70B-Instruct",
        provider="sambanova"
    )
    
    actionability_results = []
    
    for response in responses:
        # 格式化医院文档片段
        hospital_chunks = format_hospital_document_chunks(response.get('retrieval_results', []))
        
        prompt = CUSTOMIZATION_ACTIONABILITY_PROMPT.format(
            original_query=response['query'],
            medical_advice=response['advice'],
            hospital_document_chunks=hospital_chunks
        )
        
        # 调用 Llama3-70B 评估
        evaluation = evaluator_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000
        )
        
        # 解析 JSON 响应
        try:
            scores = json.loads(evaluation.choices[0].message.content)
            actionability_results.append({
                "model": response['model'],
                "actionability_scores": scores,
                "overall_score": scores['overall_actionability_score']
            })
        except json.JSONDecodeError:
            actionability_results.append({
                "model": response['model'],
                "error": "Failed to parse evaluation",
                "overall_score": 0.0
            })
    
    return actionability_results

def format_hospital_document_chunks(retrieval_results: List[Dict]) -> str:
    """格式化医院文档片段用于评估"""
    if not retrieval_results:
        return "未找到相关医院文档"
    
    chunks_text = ""
    for i, result in enumerate(retrieval_results[:5], 1):
        doc_name = result.get('document', '未知文档')
        chunk_content = result.get('chunk_text', '')
        similarity = result.get('score', 0.0)
        
        chunks_text += f"""
        【医院文档 {i}】
        文档来源：{doc_name}
        相关性：{similarity:.3f}
        内容：{chunk_content}
        
        """
    
    return chunks_text.strip()
```

**目标阈值：** ≥ 7.5 分

---

### 6. 临床证据评分（Clinical Evidence Score）

**定义：** 基于医院文档的建议的证据可靠性和科学性

**测量位置：** 独立评估模块，使用 LLM 评估

**评估者：** `meta-llama/Llama-3.3-70B-Instruct`

**评估 Prompt：**
```python
CUSTOMIZATION_EVIDENCE_PROMPT = """
你是一位医院医务处的循证医学专家和临床指南审查委员。你负责审核和更新医院的各种临床指南和诊疗规范，对医院内部文档的证据质量有深入了解。

现在需要你评估一个基于医院内部文档生成的医学建议的证据基础品质。

【原始临床问题】  
{original_query}

【基于医院文档的建议】
{medical_advice}

【引用的医院文档内容】
{hospital_document_sources}

【评估标准】
请从以下四个维度评估医院文档证据品质（每项 1-10 分）：

1. **医院文档权威性 (Hospital Document Authority)**
   - 引用的医院文档是否为权威临床指南？
   - 文档版本是否为最新且有效的？  
   - 评分：1-10 分

2. **证据与建议一致性 (Evidence-Recommendation Consistency)**
   - 提供的建议是否与医院文档内容完全一致？
   - 是否存在与医院指南矛盾的声明？
   - 评分：1-10 分

3. **医院标准符合性 (Hospital Standard Compliance)**
   - 建议是否符合医院的诊疗标准和质量要求？
   - 是否体现了医院的诊疗规范和特色？
   - 评分：1-10 分

4. **文档引用准确性 (Document Citation Accuracy)**
   - 是否准确引用和解读了医院文档内容？
   - 是否避免了对文档内容的误解或扭曲？
   - 评分：1-10 分

【回答格式】
请严格按照以下 JSON 格式回答：

```json
{
  "document_authority_score": <1-10整数>,
  "consistency_score": <1-10整数>,
  "hospital_standard_score": <1-10整数>, 
  "citation_accuracy_score": <1-10整数>,
  "overall_evidence_score": <四项平均分，保留一位小数>,
  "detailed_feedback": "<详细说明各项评分理由，特别关注医院文档的使用是否准确和恰当>"
}
```

请记住：作为医院的循证医学专家，你的评估应该确保建议完全符合医院的文档标准和诊疗规范。
"""
```

**计算公式：**
```
Hospital_Evidence_Score = (Document_Authority + Consistency + Hospital_Standard + Citation_Accuracy) / 4

医院文档证据等级：
- Level A: 医院权威指南和临床路径
- Level B: 医院科室诊疗规范和SOP
- Level C: 医院培训材料和临床经验总结
- Level D: 外部指南的医院本地化版本
```

**实现框架：**
```python
def evaluate_customization_evidence(responses: List[Dict]) -> List[Dict]:
    """评估医院定制化系统的证据品质"""
    evaluator_client = HuggingFaceInferenceClient(
        model="meta-llama/Llama-3.3-70B-Instruct", 
        provider="sambanova"
    )
    
    evidence_results = []
    
    for response in responses:
        # 格式化医院文档来源
        hospital_sources = format_hospital_document_sources(response.get('retrieval_results', []))
        
        prompt = CUSTOMIZATION_EVIDENCE_PROMPT.format(
            original_query=response['query'],
            medical_advice=response['advice'],
            hospital_document_sources=hospital_sources
        )
        
        # 调用 Llama3-70B 评估
        evaluation = evaluator_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1200
        )
        
        # 解析评估结果
        try:
            scores = json.loads(evaluation.choices[0].message.content)
            evidence_results.append({
                "model": response['model'],
                "evidence_scores": scores,
                "overall_score": scores['overall_evidence_score']
            })
        except json.JSONDecodeError:
            evidence_results.append({
                "model": response['model'], 
                "error": "Failed to parse evaluation",
                "overall_score": 0.0
            })
    
    return evidence_results

def format_hospital_document_sources(retrieval_results: List[Dict]) -> str:
    """格式化医院文档来源用于证据评估"""
    if not retrieval_results:
        return "未引用医院文档"
    
    sources_text = ""
    for i, result in enumerate(retrieval_results[:5], 1):
        doc_name = result.get('document', '未知文档.pdf')
        chunk_content = result.get('chunk_text', '')
        score = result.get('score', 0.0)
        metadata = result.get('metadata', {})
        
        sources_text += f"""
        【医院文档来源 {i}】
        文档名称：{doc_name}
        相关性：{score:.3f}
        内容片段：{chunk_content}
        元数据：{metadata}
        
        """
    
    return sources_text.strip()
```

**目标阈值：** ≥ 8.0 分（医院内部文档应有更高的证据可靠性）

---

## 🧪 完整评估流程

### 测试用例设计（医院场景）
```python
# 基于医院定制化系统的典型查询
HOSPITAL_TEST_CASES = [
    # 急诊科常见问题
    "患者胸痛应该如何诊断和处理？",
    "急性心肌梗死的诊断标准是什么？",
    "儿童发热的处理流程？",
    
    # 内科专业问题
    "孕妇头晕的鉴别诊断？",
    "老年患者跌倒的风险评估和预防？",
    
    # 外科相关问题
    "急性阑尾炎的手术指征？",
    "术前准备的标准流程？"
]
```

### 评估执行流程
```python
def run_customization_evaluation(model_name: str, test_cases: List[str]) -> Dict[str, Any]:
    """执行定制化系统的完整评估"""
    
    results = {
        "model": model_name,
        "metrics": {},
        "detailed_results": []
    }
    
    total_latencies = []
    efficiency_scores = []
    relevance_scores = []
    coverage_scores = []
    actionability_scores = []
    evidence_scores = []
    
    for query in test_cases:
        # 1. 总处理时长
        latency_result = measure_customization_latency(query)
        total_latencies.append(latency_result['total_latency'])
        
        # 2. 两阶段检索效率
        efficiency_result = evaluate_two_stage_efficiency([query])
        efficiency_scores.append(efficiency_result['overall_efficiency'])
        
        # 3. 检索相关性（实际数据）
        retrieval_results = get_customization_retrieval_results(query)
        relevance_result = evaluate_customization_relevance(retrieval_results)
        relevance_scores.append(relevance_result['average_relevance'])
        
        # 4. 检索覆盖率
        generated_advice = get_customization_generated_advice(query, retrieval_results)
        coverage_result = evaluate_customization_coverage(generated_advice, retrieval_results)
        coverage_scores.append(coverage_result['coverage'])
        
        # 5 & 6. LLM 评估（医院定制化版本）
        response_data = {
            'query': query,
            'advice': generated_advice,
            'retrieval_results': retrieval_results
        }
        
        actionability_result = evaluate_customization_actionability([response_data])
        actionability_scores.append(actionability_result[0]['overall_score'])
        
        evidence_result = evaluate_customization_evidence([response_data])
        evidence_scores.append(evidence_result[0]['overall_score'])
        
        # 记录详细结果
        results["detailed_results"].append({
            "query": query,
            "latency": latency_result,
            "efficiency": efficiency_result,
            "relevance": relevance_result,
            "coverage": coverage_result,
            "actionability": actionability_result[0],
            "evidence": evidence_result[0]
        })
    
    # 计算平均指标
    results["metrics"] = {
        "average_latency": sum(total_latencies) / len(total_latencies),
        "average_efficiency": sum(efficiency_scores) / len(efficiency_scores),
        "average_relevance": sum(relevance_scores) / len(relevance_scores),
        "average_coverage": sum(coverage_scores) / len(coverage_scores),
        "average_actionability": sum(actionability_scores) / len(actionability_scores),
        "average_evidence_score": sum(evidence_scores) / len(evidence_scores)
    }
    
    return results
```

---

## 📈 评估结果分析框架

### 定制化系统特有分析
```python
def analyze_customization_results(results_A: Dict, results_B: Dict, results_C: Dict) -> Dict:
    """比较三个模型在医院定制化场景下的表现"""
    
    models = ['OpenBioLLM-70B_direct', 'Jeff_customization_RAG', 'Med42-70B_direct']
    metrics = ['latency', 'efficiency', 'relevance', 'coverage', 'actionability', 'evidence_score']
    
    comparison = {}
    
    for metric in metrics:
        comparison[metric] = {
            models[0]: results_A['metrics'][f'average_{metric}'],
            models[1]: results_B['metrics'][f'average_{metric}'],
            models[2]: results_C['metrics'][f'average_{metric}']
        }
        
        # 计算定制化系统的优势
        baseline_openbio = comparison[metric][models[0]]
        baseline_med42 = comparison[metric][models[2]]
        customization_score = comparison[metric][models[1]]
        
        # 相对于两个基线模型的改进
        improvement_vs_openbio = ((customization_score - baseline_openbio) / baseline_openbio) * 100
        improvement_vs_med42 = ((customization_score - baseline_med42) / baseline_med42) * 100
        
        comparison[metric]['improvement_vs_openbio'] = improvement_vs_openbio
        comparison[metric]['improvement_vs_med42'] = improvement_vs_med42
    
    return comparison
```

### 医院定制化报告生成
```python
def generate_customization_report(comparison_results: Dict) -> str:
    """生成医院定制化系统评估报告"""
    
    report = f"""
    # 医院定制化RAG系统评估报告
    
    ## 评估摘要
    
    | 指标 | OpenBioLLM | 定制化系统 | Med42-70B | vs OpenBio | vs Med42 |
    |------|------------|------------|-----------|-----------|----------|
    | 处理时长 | {comparison_results['latency']['OpenBioLLM-70B_direct']:.2f}s | {comparison_results['latency']['Jeff_customization_RAG']:.2f}s | {comparison_results['latency']['Med42-70B_direct']:.2f}s | {comparison_results['latency']['improvement_vs_openbio']:+.1f}% | {comparison_results['latency']['improvement_vs_med42']:+.1f}% |
    | 检索效率 | - | {comparison_results['efficiency']['Jeff_customization_RAG']:.3f} | - | - | - |
    | 检索相关性 | - | {comparison_results['relevance']['Jeff_customization_RAG']:.3f} | - | - | - |
    | 检索覆盖率 | - | {comparison_results['coverage']['Jeff_customization_RAG']:.1%} | - | - | - |
    | 临床可操作性 | {comparison_results['actionability']['OpenBioLLM-70B_direct']:.1f}/10 | {comparison_results['actionability']['Jeff_customization_RAG']:.1f}/10 | {comparison_results['actionability']['Med42-70B_direct']:.1f}/10 | {comparison_results['actionability']['improvement_vs_openbio']:+.1f}% | {comparison_results['actionability']['improvement_vs_med42']:+.1f}% |
    | 临床证据评分 | {comparison_results['evidence_score']['OpenBioLLM-70B_direct']:.1f}/10 | {comparison_results['evidence_score']['Jeff_customization_RAG']:.1f}/10 | {comparison_results['evidence_score']['Med42-70B_direct']:.1f}/10 | {comparison_results['evidence_score']['improvement_vs_openbio']:+.1f}% | {comparison_results['evidence_score']['improvement_vs_med42']:+.1f}% |
    
    ## 定制化系统优势分析
    
    ### 🏥 医院特定性优势
    - **文档本地化**: 基于医院实际临床指南和诊疗规范
    - **资源匹配度**: 建议完全符合医院设备和人员配置
    - **流程一致性**: 与医院现有诊疗流程高度契合
    
    ### ⚡ 技术架构优势  
    - **两阶段检索**: 先文档筛选后块检索，精度和效率并重
    - **BGE-Large-Medical**: 医学专用嵌入模型，语义理解更准确
    - **Top-P智能过滤**: 动态质量阈值，避免低质量结果
    
    ### 📊 性能表现
    - **检索速度**: 平均{comparison_results['latency']['Jeff_customization_RAG']:.1f}秒响应
    - **检索精度**: {comparison_results['relevance']['Jeff_customization_RAG']:.1%}平均相关性
    - **内容覆盖**: {comparison_results['coverage']['Jeff_customization_RAG']:.1%}文档内容利用率
    """
    
    return report
```

---

## 🔧 实验执行步骤

### 1. 环境准备
```bash
# 设置 HuggingFace token（用于 Inference Providers）
export HF_TOKEN=your_huggingface_token

# 激活定制化系统环境
source rag_env/bin/activate

# 确保医院文档库已构建
python customization/customization_pipeline.py
```

### 2. Jeff 系统评估脚本
```python
# evaluation/run_customization_evaluation.py
def main():
    """Jeff 定制化系统评估主函数"""
    
    # 加载医院场景测试用例
    test_cases = HOSPITAL_TEST_CASES
    
    print("🏥 开始 Jeff 医院定制化系统评估")
    
    # 三个模型评估
    results_openbio = run_customization_evaluation("OpenBioLLM-70B_direct", test_cases)
    results_customization = run_customization_evaluation("Jeff_customization_RAG", test_cases)
    results_med42 = run_customization_evaluation("Med42-70B_direct", test_cases)
    
    # 分析和报告
    comparison_results = analyze_customization_results(results_openbio, results_customization, results_med42)
    report = generate_customization_report(comparison_results)
    
    # 保存结果
    save_results("evaluation/results/jeff_customization_evaluation.json", {
        "comparison": comparison_results,
        "detailed_results": [results_openbio, results_customization, results_med42],
        "hospital_specific_analysis": analyze_hospital_advantages(results_customization)
    })
    
    print("✅ Jeff 定制化系统评估完成，结果已保存")
    
    # 生成可视化图表
    generate_customization_visualization(comparison_results)

def analyze_hospital_advantages(customization_results: Dict) -> Dict:
    """分析医院定制化系统的特有优势"""
    return {
        "document_diversity": len(set([r['document'] for r in customization_results['detailed_results']])),
        "average_hospital_relevance": customization_results['metrics']['average_relevance'],
        "two_stage_effectiveness": customization_results['metrics']['average_efficiency'],
        "hospital_actionability": customization_results['metrics']['average_actionability']
    }

if __name__ == "__main__":
    main()
```

### 3. 预期评估时间
```
医院定制化系统评估时间：
├── 系统初始化：3-6秒（BGE-Large-Medical加载）
├── 每个查询处理：1-3秒（两阶段检索）
├── LLM评估：15-25秒/查询
├── 测试用例数量：7个
└── 总评估时间：8-12分钟
```

---

## 📊 定制化系统成功标准

### 系统性能目标（调整后）
```
✅ 达标条件：
1. 总处理时长 ≤ 5秒
2. 两阶段检索效率 ≥ 0.8  
3. 检索相关性 ≥ 0.25（基于实际医学数据）
4. 检索覆盖率 ≥ 55%
5. 临床可操作性 ≥ 7.5/10（医院特定优势）
6. 临床证据评分 ≥ 8.0/10（医院文档高可靠性）

🎯 定制化系统成功标准：
- 在医院特定场景下优于通用医学模型
- 体现医院文档的本地化优势
- 检索精度和速度的最佳平衡
```

### 关键性能指标（KPI）
```
医院定制化系统 KPI：
├── 检索相关性改进：相比通用模型提升 15-25%
├── 医院适用性：可操作性评分 > 7.5分
├── 文档利用率：覆盖率 > 55%，体现定制化价值
├── 响应速度：< 3秒平均响应时间
└── 证据可靠性：> 8.0分，基于医院权威文档
```

---

## 🛠️ 实施建议

### 分阶段实施（Jeff 系统特定）
```
阶段1: 基础指标实现（1-4项）
├── 利用现有 customization_pipeline.py 的时间测量
├── 实现两阶段检索效率评估
├── 分析 BGE-Large-Medical 的检索相关性
└── 实现基于医院文档的覆盖率计算

阶段2: LLM评估实现（5-6项）
├── 设置 HuggingFace Inference Providers
├── 实现 Llama3-70B 医院特定评估客户端
├── 测试医院场景评估 prompts
└── 建立医院文档引用分析逻辑

阶段3: 完整实验执行
├── 准备医院场景测试用例
├── 执行 Jeff 定制化系统评估
├── 对比通用医学模型表现
└── 生成医院定制化优势分析报告
```

### 医院定制化特有注意事项
```
⚠️ 重要提醒：
1. 确保医院文档库已正确构建和索引
2. BGE-Large-Medical 模型需要充足内存（2-4GB）
3. 两阶段检索的参数调优（top_p=0.6, min_similarity=0.3）
4. 注意医院文档的隐私和安全要求
5. 相关性阈值应基于实际医学检索数据（0.25-0.35）
6. LLM 评估应强调医院特定性和本地化优势
```

### 与 YanBo 系统的区别
```
核心差异点：
├── 数据源：医院内部文档 vs 公开医学指南
├── 检索架构：两阶段 ANNOY vs 单阶段向量检索  
├── 嵌入模型：BGE-Large-Medical vs PubMedBERT
├── 优化目标：医院特定性 vs 通用医学知识
└── 评估重点：本地化适应性 vs 标准医学质量
```

---

**Jeff 医院定制化系统评估指南完成。请根据此指南实施定制化系统评估实验。**
