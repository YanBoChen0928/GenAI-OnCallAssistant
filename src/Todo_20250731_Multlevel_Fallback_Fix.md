太棒了！讓我們一起分析這個詳細的測試結果，這些數據很有價值！

## 📊 **測試結果深度分析**

### **✅ 成功的部分 (53.8% 成功率)**

**Level 1 - 預定義映射**: 💯 **完美表現**
- 3/3 測試通過，平均 0.000s（瞬間響應）
- `acute myocardial infarction`, `acute stroke`, `pulmonary embolism` 都直接命中

**Level 4b→5 - 冷門醫療查詢**: 💯 **完美表現**  
- 3/3 測試通過，正確進入 generic search
- 罕見血液疾病、ITP、壞死性筋膜炎都正確處理

### **🔍 發現的關鍵問題**

#### **問題1: Level 4 驗證機制失效** ❌
**現象**: 非醫療查詢（烹飪、編程、天氣）都被當作醫療查詢處理
```
- "how to cook pasta properly?" → Level 5 (應該被拒絕)
- "programming language" → Level 5 (應該被拒絕)  
- "weather forecast" → Level 5 (應該被拒絕)
```

**根本原因**: `validate_medical_query` 邏輯有問題
- LLM 雖然說"這不是醫療查詢"，但函數仍然返回 `None`（表示通過驗證）
- 應該檢查 LLM 回應中是否明確說明"非醫療"

#### **問題2: Level 3 語義搜索邏輯問題** ⚠️
**現象**: 期望 Level 3 的查詢都跳到了 Level 5
```
- "emergency management of cardiovascular crisis" → Level 5 (期望 Level 3)
- "urgent neurological intervention protocols" → Level 5 (期望 Level 3)
```

**原因**: `_infer_condition_from_text` 方法可能過於嚴格，無法推斷出有效條件

#### **問題3: Level 2 行為不一致** ⚠️
**現象**: 
- `level2_001` 成功，但被 Level 1 攔截了（LLM 提取了已知條件）
- `level2_002` 失敗，LLM 提取了條件但驗證失敗

## 🛠️ **需要修正的優先順序**

### **Priority 1: 修正 validate_medical_query**
```python
def validate_medical_query(self, user_query: str) -> Optional[Dict[str, Any]]:
    # 檢查 LLM 回應是否明確說明非醫療
    if llama_result.get('extracted_condition'):
        response_text = llama_result.get('raw_response', '').lower()
        
        # 檢查是否明確拒絕醫療查詢
        rejection_phrases = [
            "not a medical condition", 
            "outside my medical scope",
            "unrelated to medical conditions",
            "do not address"
        ]
        
        if any(phrase in response_text for phrase in rejection_phrases):
            return self._generate_invalid_query_response()
        
        return None  # 通過驗證
```

### **Priority 2: 改進語義搜索條件推斷**
`_infer_condition_from_text` 的相似度閾值可能太高(0.7)，建議降低到 0.5

### **Priority 3: 優化 Level 2 LLM 提取驗證**
確保 `validate_condition` 能正確處理 LLM 的複雜回應

## 🎯 **整體評估**

### **速度表現**: ⭐⭐⭐⭐⭐
- Level 1: 瞬間響應 (0.000s)
- 平均: 14.4s（主要是 LLM 調用造成的）

### **準確性**: ⭐⭐⭐
- 預定義條件: 100% 準確
- 冷門醫療: 100% 準確  
- 非醫療拒絕: 0% 準確 ← **需要立即修正**

你希望我先修正 `validate_medical_query` 的邏輯嗎？這是最關鍵的問題，解決後整體成功率應該能提升到 80%+。