# Next Steps: Deploy to HuggingFace Spaces - Phase 5

## 📋 當前狀態確認

### ✅ 已完成的階段：
- **階段 1**: 雲端載入器基礎功能 ✅ 
- **階段 2**: General Pipeline 雲端載入 ✅
- **階段 3**: Customization Pipeline 雲端載入 ✅
- **階段 4**: 完整整合測試 ✅

### 📊 雲端載入驗證：
- **Dataset Repository**: `ybchen928/oncall-guide-ai-models` 
- **總資料大小**: ~1.6GB (models/ + customization_data/)
- **下載性能**: 首次 ~2分鐘，後續使用快取
- **功能完整性**: 兩條 Pipeline 都正常運作

---

## Phase 5: 部署到 HuggingFace Spaces

### 🎯 部署目標
**將不含大檔案的程式碼推送到 Spaces，實現雲端資料載入**

---

## Step 5.1: 準備部署檔案

### 檢查當前 Git 狀態
```bash
# 確認在正確的 branch
git branch
# 應該顯示: * HuggingFace_space_dataset_deployment

# 檢查檔案狀態
git status
```

### 確認要部署的檔案清單
**✅ 必須包含的檔案：**
```
├── README.md ✅ (Spaces 配置)
├── app.py ✅ (主應用程式)
├── requirements.txt ✅ (依賴清單)
├── .gitattributes ✅ (Git 配置)
└── src/ ✅ (核心程式碼)
    ├── user_prompt.py
    ├── retrieval.py (已修改支援雲端載入)
    ├── generation.py
    ├── llm_clients.py
    ├── medical_conditions.py
    ├── data_processing.py
    └── cloud_loader.py (新增)
```

**✅ Customization 程式碼：**
```
└── customization/ ✅ (只保留程式碼)
    ├── customization_pipeline.py (已修改支援雲端載入)
    ├── generate_embeddings.py
    ├── test/
    └── src/ (20個 .py 檔案)
        ├── cloud_config.py (新增)
        ├── indexing/storage.py
        ├── indexing/annoy_manager.py
        └── 其他程式碼檔案
```

**❌ 不要包含的檔案：**
```
❌ models/ (已移至 Dataset)
❌ customization/processing/ (已移至 Dataset)  
❌ evaluation/, tests/, docs/ (開發用)
❌ dataset/, onCallGuideAIvenv/ (本地環境)
❌ .env (敏感資訊)
❌ test_stage*.py (測試腳本)
```

---

## Step 5.2: 確認配置檔案

### 檢查 requirements.txt
```bash
grep "huggingface-hub" requirements.txt
# 確保包含: huggingface-hub>=0.33,<0.35
```

### 檢查 README.md YAML frontmatter
```yaml
---
title: OnCall.ai - Medical Emergency Assistant
emoji: 🏥
colorFrom: red
colorTo: blue
sdk: gradio
sdk_version: "5.38.0"
app_file: app.py
python_version: "3.11"
pinned: false
license: mit
tags:
  - medical
  - healthcare
  - RAG
  - emergency
  - clinical-guidance
  - gradio
---
```

### 檢查環境變數設置
**在 Spaces Settings 中確認：**
- `HF_TOKEN`: 你的 HuggingFace API token ✅ (已設置)
- `USE_CLOUD_DATA`: `true` (自動使用雲端模式)

---

## Step 5.3: Git 提交準備

### 暫時移除本地大檔案資料夾
```bash
# 備份本地 processing 資料夾 (如果存在)
if [ -d "customization/processing" ]; then
    mv customization/processing customization_processing_backup
    echo "✅ 已備份 customization/processing"
fi

# 確認大檔案不在 Git 追蹤中
git status | grep "models\|processing"
# 不應該看到任何 models/ 或 processing/ 相關檔案
```

### 添加修改的程式碼檔案
```bash
# 添加所有程式碼修改
git add src/cloud_loader.py
git add src/retrieval.py  
git add customization/src/cloud_config.py
git add customization/customization_pipeline.py
git add requirements.txt
git add README.md
git add app.py
git add .gitattributes

# 檢查 staging area
git status
```

---

## Step 5.4: 提交並推送到 Spaces

### Git 提交
```bash
git commit -m "Implement cloud data loading for HuggingFace Spaces deployment

- Add cloud_loader.py for core system data loading
- Add customization cloud_config.py for hospital-specific data
- Modify retrieval.py to use cloud data loading
- Modify customization_pipeline.py to use preloading
- Support both local and cloud deployment modes
- Tested with full integration verification"
```

### 檢查推送目標
```bash
# 確認 remote 設置
git remote -v
# 應該看到: hf git@hf.co:spaces/ybchen928/oncall-guide-ai

# 檢查要推送的檔案大小
du -sh src/ customization/src/ *.py *.txt *.md
# 確保總大小 < 1GB
```

### 推送到 Spaces
```bash
git push hf HuggingFace_space_dataset_deployment:main --force
```

---

## Step 5.5: 監控部署過程

### 檢查建置狀態
1. **前往 Spaces**: https://huggingface.co/spaces/ybchen928/oncall-guide-ai
2. **點擊 "App" 標籤**查看建置進度
3. **觀察 Logs**:
   - 依賴安裝進度
   - 雲端檔案下載進度
   - 系統初始化狀態

### 預期建置過程
```
Phase 1: Installing dependencies (2-3 minutes)
├── Installing Python packages from requirements.txt
├── Setting up Gradio environment
└── Configuring Python 3.11 environment

Phase 2: Application startup (3-5 minutes)  
├── Downloading models/ from Dataset (1.5GB)
├── Downloading customization_data/ from Dataset (150MB)
├── Initializing retrieval systems
└── Starting Gradio interface

Phase 3: Ready for use
├── App status: "Running" 🟢
├── Interface accessible
└── All features available
```

---

## 🚨 故障排除指南

### 常見問題與解決方案

#### 1. 依賴安裝失敗
**症狀**: 建置卡在 "Installing dependencies"
**解決**:
```bash
# 檢查 requirements.txt 語法
pip check

# 確認版本相容性
pip install --dry-run -r requirements.txt
```

#### 2. 雲端檔案下載失敗
**症狀**: "404 Not Found" 或 "Access denied"
**解決**:
- 確認 Dataset Repository 是 Public
- 檢查 `HF_TOKEN` 環境變數設置
- 驗證 Dataset 中的檔案路徑

#### 3. 記憶體不足
**症狀**: "Out of memory" 或建置超時
**解決**:
- 考慮升級 Spaces 硬體 (CPU basic → CPU upgrade)
- 或實施懶載入 (需要時才載入大檔案)

#### 4. Gradio 介面無法啟動
**症狀**: 建置成功但無法存取
**解決**:
- 檢查 app.py 中的 launch() 配置
- 確認沒有硬編碼的 port/host 設定

#### 5. Customization 功能失效
**症狀**: Hospital Only 模式無法運作
**解決**:
- 檢查 customization/src/cloud_config.py 的 dataset_repo 名稱
- 確認所有 processing 檔案都在 Dataset 中

---

## Step 5.6: 功能驗證

### 線上測試清單
**部署成功後進行的驗證：**

#### 基本功能測試
- [ ] **General Mode**: 測試基本醫療查詢
- [ ] **Hospital Mode**: 測試 customization 功能  
- [ ] **Combined Mode**: 測試混合功能

#### 性能測試
- [ ] **首次載入時間**: 記錄冷啟動時間
- [ ] **查詢響應時間**: 測試熱啟動性能
- [ ] **記憶體使用**: 監控系統資源

#### 錯誤處理測試
- [ ] **無效查詢**: 測試非醫療查詢的拒絕機制
- [ ] **網路錯誤**: 模擬檔案下載失敗的處理
- [ ] **資料不一致**: 測試部分檔案缺失的容錯性

---

## 📊 部署成功指標

### 技術指標
- **建置時間**: < 10 分鐘
- **首次載入**: < 5 分鐘  
- **查詢響應**: < 3 秒
- **記憶體使用**: < 4GB (免費額度內)

### 功能指標  
- **General Pipeline**: 正常返回醫療建議
- **Hospital Pipeline**: 正常返回院所特定建議
- **Combined Mode**: 整合結果正確
- **錯誤處理**: 適當的錯誤訊息和回退機制

---

## 🎯 部署後的後續步驟

### 文檔更新
- [ ] 更新 README.md 說明雲端部署架構
- [ ] 創建使用指南
- [ ] 記錄已知限制和注意事項

### 監控和維護
- [ ] 設置 Spaces 的使用監控
- [ ] 定期檢查 Dataset Repository 狀態
- [ ] 監控建置和執行 logs

### 擴展計畫
- [ ] 考慮實施檔案版本控制
- [ ] 評估硬體升級需求
- [ ] 規劃額外功能的雲端化

---

## ⚠️ 重要注意事項

1. **首次使用者體驗**: 第一個使用者需要等待檔案下載 (2-5分鐘)
2. **快取共享**: 所有使用者共享 HuggingFace 的檔案快取
3. **成本考量**: 免費 Spaces 有使用時間限制，考慮升級計畫
4. **資料同步**: Dataset 更新時，Spaces 需要清除快取重新下載
5. **備份策略**: 保持本地開發環境的完整性，以備緊急回退

---

## 🚀 執行檢查清單

部署前確認：
- [ ] 階段 4 整合測試通過
- [ ] Git 狀態乾淨 (無大檔案)
- [ ] Requirements.txt 包含所有依賴
- [ ] README.md YAML 配置正確
- [ ] 環境變數已設置
- [ ] Dataset Repository 可正常存取

準備就緒後，執行 Phase 5 部署步驟！
