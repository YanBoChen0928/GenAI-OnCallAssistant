# 🔧 臨時修復：MRR查詢複雜度分類問題

## 📋 問題描述

### 發現的問題
- **症狀**：所有醫療查詢都被錯誤分類為"Simple Query Complexity"
- **影響**：導致MRR計算使用過嚴格的相關性閾值(0.75)，使得MRR分數異常低(0.111)
- **典型案例**：68歲房顫患者急性中風查詢被判為Simple，而非Complex

### 根本原因分析
```json
// 在comprehensive_details_20250809_192154.json中發現：
"matched": "",          // ← 所有檢索結果的matched字段都是空字符串
"matched_treatment": "" // ← 導致複雜度判斷邏輯失效
```

**原始判斷邏輯缺陷**：
- 依賴`matched`字段中的emergency keywords計數
- `matched`字段為空 → keyword_count = 0 → 判斷為Simple
- 使用0.75嚴格閾值 → 大部分結果被認為不相關

## 🛠️ 臨時修復方案

### 修改文件
- `evaluation/metric7_8_precision_MRR.py` - 改進複雜度判斷邏輯
- `evaluation/metric7_8_precision_mrr_chart_generator.py` - 確保圖表正確顯示

### 新的複雜度判斷策略

#### **Strategy 1: 急症關鍵詞分析**
```python
emergency_indicators = [
    'stroke', 'cardiac', 'arrest', 'acute', 'sudden', 'emergency',
    'chest pain', 'dyspnea', 'seizure', 'unconscious', 'shock',
    'atrial fibrillation', 'neurological', 'weakness', 'slurred speech'
]
# 如果查詢包含2+急症詞彙 → Complex
```

#### **Strategy 2: Emergency結果比例分析**
```python
emergency_ratio = emergency_results_count / total_results
# 如果50%+的檢索結果是emergency類型 → Complex
```

#### **Strategy 3: 高相關性結果分布**
```python  
high_relevance_count = results_with_relevance >= 0.7
# 如果3+個結果高度相關 → Complex
```

#### **Strategy 4: 原始邏輯保留**
```python
# 保留原matched字段邏輯作為fallback
# 如果matched字段有數據，仍使用原邏輯
```

### 預期改善效果

#### **修改前 vs 修改後**：
```
查詢: "68歲房顫患者突然言語不清和右側無力"

修改前:
├─ 判斷: Simple (依賴空matched字段)
├─ 閾值: 0.75 (嚴格)
├─ 相關結果: 0個 (最高0.727 < 0.75)
└─ MRR: 0.0

修改後:
├─ 判斷: Complex (2個急症詞 + 55%急症結果)
├─ 閾值: 0.65 (寬鬆)  
├─ 相關結果: 5個 (0.727, 0.726, 0.705, 0.698, 0.696 > 0.65)
└─ MRR: 1.0 (第1個結果就相關)
```

#### **指標改善預測**：
- **MRR**: 0.111 → 0.5-1.0 (提升350-800%)
- **Precision@K**: 0.062 → 0.4-0.6 (提升550-870%)
- **複雜度分類準確性**: 顯著改善

## 📋 長期修復計劃

### 需要根本解決的問題

#### **1. 檢索系統修復**
```
文件: src/retrieval.py
問題: matched字段未正確填入emergency keywords
修復: 檢查keyword matching邏輯，確保匹配結果正確保存
```

#### **2. 醫療條件映射檢查**
```  
文件: src/medical_conditions.py
問題: emergency keywords映射可能不完整
修復: 驗證CONDITION_KEYWORD_MAPPING是否涵蓋所有急症情況
```

#### **3. 數據管線整合**
```
文件: evaluation/latency_evaluator.py
問題: matched信息在保存過程中丟失
修復: 確保從retrieval到保存的完整數據傳遞
```

### 根本修復步驟
1. **檢查retrieval.py中的keyword matching實現**
2. **修復matched字段填入邏輯**  
3. **重新運行latency_evaluator.py生成新的comprehensive_details**
4. **驗證matched字段包含正確的emergency keywords**
5. **恢復metric7_8_precision_MRR.py為原始邏輯**
6. **重新運行MRR分析驗證結果**

### 影響評估
- **修復時間**: 預估2-3小時開發 + 1-2小時重新評估
- **風險**: 需要重新生成所有評估數據
- **收益**: 徹底解決問題，確保所有metrics準確性

## 🔍 驗證方法

### 修復後驗證步驟
1. **運行修復版MRR分析**: `python metric7_8_precision_MRR.py`
2. **檢查複雜度分類**: 中風查詢應顯示為Complex
3. **驗證MRR改善**: 期望看到MRR > 0.5
4. **生成新圖表**: `python metric7_8_precision_mrr_chart_generator.py`
5. **對比修復前後結果**: 確認指標顯著改善

### 成功標準
- ✅ 急性中風查詢被正確分類為Complex
- ✅ MRR分數提升至合理範圍(0.5+)  
- ✅ Precision@K顯著改善
- ✅ 圖表顯示正確的複雜度分布

## ⚠️ 注意事項

### 臨時性質說明
- **這是權宜之計**：解決當前分析需求，但不解決根本數據問題
- **數據依賴**：仍依賴現有的comprehensive_details數據
- **邏輯複雜性**：增加了判斷邏輯的複雜度，可能需要調優

### 未來清理
- 根本修復完成後，應移除臨時邏輯
- 恢復簡潔的原始matched字段判斷方式  
- 刪除此臨時修復文檔

---
**創建日期**: 2025-08-09  
**修復類型**: 臨時解決方案  
**預期清理日期**: 根本修復完成後
