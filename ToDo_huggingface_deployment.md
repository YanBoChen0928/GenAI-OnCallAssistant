# OnCall.ai 智慧分離部署方案 B - 詳細實施步驟

## 📋 相關檔案列表

### 需要修改的檔案：

- `src/retrieval.py` - 修改 models/ 路徑邏輯
- `app.py` - 修改 customization 載入邏輯
- `customization/src/indexing/storage.py` - 修改資料檔案路徑
- `customization/src/indexing/annoy_manager.py` - 修改索引檔案路徑
- `customization/customization_pipeline.py` - 修改處理資料路徑

### 新增的檔案：

- `src/cloud_loader.py` - 雲端資料載入器
- `customization/src/cloud_config.py` - customization 雲端配置

---

## 🏗️ 方案 B 架構總覽

### **HuggingFace Spaces (應用+程式碼, <1GB):**

```
oncall-guide-ai/
├── app.py ✅
├── src/ ✅
│   ├── user_prompt.py
│   ├── retrieval.py (修改)
│   ├── generation.py
│   ├── llm_clients.py
│   ├── medical_conditions.py
│   └── cloud_loader.py (新增)
├── customization/ ✅ (只保留程式碼)
│   ├── src/ (20個 .py 檔案，部分修改)
│   │   ├── cloud_config.py (新增)
│   │   ├── indexing/storage.py (修改)
│   │   └── indexing/annoy_manager.py (修改)
│   ├── customization_pipeline.py (修改)
│   ├── generate_embeddings.py
│   └── test/
├── requirements.txt ✅
├── README.md ✅
└── .gitattributes ✅
```

### **HuggingFace Dataset (純資料, >1.5GB):**

```
oncall-guide-ai-data/
├── models/ (1.5GB)
│   ├── embeddings/
│   │   ├── emergency_embeddings.npy
│   │   ├── emergency_chunks.json
│   │   ├── treatment_embeddings.npy
│   │   └── treatment_chunks.json
│   ├── indices/annoy/
│   │   ├── emergency.ann
│   │   ├── emergency_index.ann
│   │   ├── treatment.ann
│   │   └── treatment_index.ann
│   └── data_validation_report.json
└── customization_data/
    └── processing/ (約100MB)
        ├── indices/
        │   ├── annoy_metadata.json
        │   ├── chunk_embeddings.ann
        │   ├── chunk_mappings.json
        │   ├── tag_embeddings.ann
        │   └── tag_mappings.json
        ├── embeddings/
        │   ├── chunk_embeddings.json
        │   ├── document_index.json
        │   ├── document_tag_mapping.json
        │   └── tag_embeddings.json
        └── mapping.json
```

---

## Phase 1: 準備 Dataset Repository

### Step 1.1: 創建 Dataset Repository

```bash
# 在 HuggingFace 網站創建
https://huggingface.co/new-dataset
Dataset name: oncall-guide-ai-data
Visibility: Public
License: MIT
```

### Step 1.2: Clone 和設置 Dataset Repository

```bash
# 在工作目錄外創建
cd ~/Documents
git clone https://huggingface.co/datasets/ybchen928/oncall-guide-ai-data
cd oncall-guide-ai-data

# 設置 Git LFS
git lfs install
git lfs track "*.npy"
git lfs track "*.ann"
git lfs track "*.json"
```

### Step 1.3: 複製資料到 Dataset Repository

```bash
# 複製 models 資料夾 (完整)
cp -r /Users/yanbochen/Documents/Life_in_Canada/CS_study_related/Student_Course_Guide/CS7180_GenAI/GenAI-OnCallAssistant/models ./

# 只複製 customization/processing 資料夾
mkdir -p customization_data
cp -r /Users/yanbochen/Documents/Life_in_Canada/CS_study_related/Student_Course_Guide/CS7180_GenAI/GenAI-OnCallAssistant/customization/processing ./customization_data/

# 提交到 Dataset Repository
git add .
git commit -m "Add OnCall.ai model data and customization data"
git push origin main
```

---

## Phase 2: 修改主系統檔案

### Step 2.1: 新增雲端載入器

**新增檔案：`src/cloud_loader.py`**

```python
"""Cloud Data Loader - Downloads model data from HuggingFace Dataset"""

import os
from pathlib import Path
from huggingface_hub import hf_hub_download
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class CloudDataLoader:
    """HuggingFace Dataset data loader"""
    
    def __init__(self):
        self.dataset_repo = "ybchen928/oncall-guide-ai-models"
        self.use_cloud = os.getenv('USE_CLOUD_DATA', 'true').lower() == 'true'
    
    def get_model_file_path(self, filename: str) -> str:
        """Get model file path for General Pipeline"""
        if self.use_cloud:
            return hf_hub_download(
                repo_id=self.dataset_repo,
                filename=filename,
                repo_type="dataset"
            )
        else:
            # Local development mode
            return str(Path(__file__).parent.parent / filename)
    
    def get_customization_file_path(self, filename: str) -> str:
        """Get customization data file path for Customization Pipeline"""
        if self.use_cloud:
            return hf_hub_download(
                repo_id=self.dataset_repo,
                filename=f"customization_data/{filename}",
                repo_type="dataset"
            )
        else:
            # Local development mode - correct path to processing folder
            return str(Path(__file__).parent.parent / "customization" / "processing" / filename)

# Global instance
cloud_loader = CloudDataLoader()
```

### Step 2.2: 修改 src/retrieval.py

**修改區域：第 60-65 行附近的路徑設置**

```python
# 原始程式碼 (修改前):
# current_file = Path(__file__)
# project_root = current_file.parent.parent  # from src to root
# base_path = project_root / "models"

# 修改後的程式碼:
from .cloud_loader import cloud_loader

def _initialize_system(self) -> None:
    """Initialize embeddings, indices and chunks"""
    try:
        logger.info("Initializing retrieval system...")

        # Initialize embedding model
        self.embedding_model = SentenceTransformer("NeuML/pubmedbert-base-embeddings")
        logger.info("Embedding model loaded successfully")

        # Initialize Annoy indices
        self.emergency_index = AnnoyIndex(self.embedding_dim, 'angular')
        self.treatment_index = AnnoyIndex(self.embedding_dim, 'angular')

        # Load data using cloud loader
        self._load_chunks_from_cloud()
        self._load_embeddings_from_cloud()
        self._build_or_load_indices_from_cloud()

        logger.info("Retrieval system initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize retrieval system: {e}")
        raise

def _load_chunks_from_cloud(self) -> None:
    """Load chunk data from cloud or local files"""
    try:
        # Load emergency chunks
        emergency_chunks_path = cloud_loader.get_model_file_path("models/embeddings/emergency_chunks.json")
        with open(emergency_chunks_path, 'r', encoding='utf-8') as f:
            emergency_data = json.load(f)
            self.emergency_chunks = {i: chunk for i, chunk in enumerate(emergency_data)}

        # Load treatment chunks
        treatment_chunks_path = cloud_loader.get_model_file_path("models/embeddings/treatment_chunks.json")
        with open(treatment_chunks_path, 'r', encoding='utf-8') as f:
            treatment_data = json.load(f)
            self.treatment_chunks = {i: chunk for i, chunk in enumerate(treatment_data)}

        logger.info(f"Loaded {len(self.emergency_chunks)} emergency and {len(self.treatment_chunks)} treatment chunks")

    except Exception as e:
        logger.error(f"Failed to load chunks: {e}")
        raise

def _load_embeddings_from_cloud(self) -> None:
    """Load embeddings from cloud or local files"""
    try:
        # Load emergency embeddings
        emergency_embeddings_path = cloud_loader.get_model_file_path("models/embeddings/emergency_embeddings.npy")
        self.emergency_embeddings = np.load(emergency_embeddings_path)

        # Load treatment embeddings
        treatment_embeddings_path = cloud_loader.get_model_file_path("models/embeddings/treatment_embeddings.npy")
        self.treatment_embeddings = np.load(treatment_embeddings_path)

        logger.info("Embeddings loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load embeddings: {e}")
        raise

def _build_or_load_indices_from_cloud(self) -> None:
    """Build or load Annoy indices from cloud or local files"""
    try:
        # Load emergency index
        emergency_index_path = cloud_loader.get_model_file_path("models/indices/annoy/emergency.ann")
        self.emergency_index.load(emergency_index_path)

        # Load treatment index
        treatment_index_path = cloud_loader.get_model_file_path("models/indices/annoy/treatment.ann")
        self.treatment_index.load(treatment_index_path)

        logger.info("Annoy indices loaded successfully")

    except Exception as e:
        logger.error(f"Failed to load indices: {e}")
        raise
```

---

## Phase 3: 修改 Customization 系統檔案

### Step 3.1: 新增 customization 雲端配置

**新增檔案：`customization/src/cloud_config.py`**

```python
"""Customization 系統雲端配置"""

import os
from pathlib import Path
from huggingface_hub import hf_hub_download
import logging

logger = logging.getLogger(__name__)

class CustomizationCloudLoader:
    """Customization 專用雲端載入器"""

    def __init__(self):
        self.dataset_repo = "ybchen928/oncall-guide-ai-data"
        self.use_cloud = os.getenv('USE_CLOUD_DATA', 'true').lower() == 'true'

    def get_processing_file_path(self, relative_path: str) -> str:
        """獲取 processing 檔案路徑"""
        if self.use_cloud:
            return hf_hub_download(
                repo_id=self.dataset_repo,
                filename=f"customization_data/processing/{relative_path}",
                repo_type="dataset"
            )
        else:
            # 本地開發模式
            base_path = Path(__file__).parent.parent.parent / "customization" / "processing"
            return str(base_path / relative_path)

# 全域實例
customization_loader = CustomizationCloudLoader()
```

### Step 3.2: 修改 customization/src/indexing/storage.py

**修改區域：檔案路徑設置部分**

```python
# 在檔案頂部添加導入
from ..cloud_config import customization_loader

# 修改路徑相關函數 (大約第 45 行附近)
def get_processing_path(filename: str) -> str:
    """獲取處理檔案的路徑"""
    return customization_loader.get_processing_file_path(filename)

# 修改所有使用處理檔案的地方
def load_chunk_mappings():
    """載入 chunk mappings"""
    mappings_path = get_processing_path("indices/chunk_mappings.json")
    with open(mappings_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_tag_mappings():
    """載入 tag mappings"""
    mappings_path = get_processing_path("indices/tag_mappings.json")
    with open(mappings_path, 'r', encoding='utf-8') as f:
        return json.load(f)
```

### Step 3.3: 修改 customization/src/indexing/annoy_manager.py

**修改區域：索引檔案載入部分**

```python
# 在檔案頂部添加導入
from ..cloud_config import customization_loader

# 修改索引載入函數 (大約第 134 行附近)
class AnnoyIndexManager:
    def load_chunk_index(self):
        """載入 chunk 索引"""
        index_path = customization_loader.get_processing_file_path("indices/chunk_embeddings.ann")
        self.chunk_index = AnnoyIndex(self.embedding_dim, 'angular')
        self.chunk_index.load(index_path)
        return self.chunk_index

    def load_tag_index(self):
        """載入 tag 索引"""
        index_path = customization_loader.get_processing_file_path("indices/tag_embeddings.ann")
        self.tag_index = AnnoyIndex(self.embedding_dim, 'angular')
        self.tag_index.load(index_path)
        return self.tag_index
```

### Step 3.4: 修改 customization/customization_pipeline.py

**修改區域：主要處理流程的檔案路徑**

```python
# 在檔案頂部添加 (大約第 12 行之後)
from src.cloud_config import customization_loader

# 修改資料載入函數 (大約第 31 行附近)
def load_processing_data():
    """載入處理所需的資料檔案"""
    try:
        # 載入文檔索引
        doc_index_path = customization_loader.get_processing_file_path("embeddings/document_index.json")
        with open(doc_index_path, 'r', encoding='utf-8') as f:
            document_index = json.load(f)

        # 載入對應關係
        mapping_path = customization_loader.get_processing_file_path("mapping.json")
        with open(mapping_path, 'r', encoding='utf-8') as f:
            mapping_data = json.load(f)

        return document_index, mapping_data

    except Exception as e:
        logger.error(f"Failed to load processing data: {e}")
        raise
```

---

## Phase 4: 更新配置檔案

### Step 4.1: 更新 requirements.txt

**新增必要依賴：**

```text
# 在現有 requirements.txt 中確保包含：
huggingface-hub>=0.33,<0.35
```

### Step 4.2: 更新 .gitattributes

**確保 Git LFS 設置：**

```text
*.npy filter=lfs diff=lfs merge=lfs -text
*.ann filter=lfs diff=lfs merge=lfs -text
*.json filter=lfs diff=lfs merge=lfs -text
```

---

## Phase 5: 本地測試

### Step 5.1: 測試雲端資料載入

**創建測試腳本：`test_cloud_integration.py`**

```python
import os
os.environ['USE_CLOUD_DATA'] = 'true'

from src.retrieval import BasicRetrievalSystem
from customization.customization_pipeline import retrieve_document_chunks

def test_integration():
    print("🧪 測試雲端整合...")

    try:
        # 測試核心系統
        retrieval = BasicRetrievalSystem()
        print("✅ 核心系統初始化成功")

        # 測試 customization 系統
        results = retrieve_document_chunks("chest pain", top_k=3)
        print(f"✅ Customization 系統測試成功，返回 {len(results)} 個結果")

        print("🎉 所有整合測試通過！")
        return True

    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        return False

if __name__ == "__main__":
    success = test_integration()
    exit(0 if success else 1)
```

### Step 5.2: 執行測試

```bash
python test_cloud_integration.py
```

---

## Phase 6: 部署到 Spaces

### Step 6.1: 準備 Spaces 檔案

**確認要上傳到 Spaces 的檔案清單：**

- ✅ `app.py` (已修改)
- ✅ `src/` (包含新的 cloud_loader.py)
- ✅ `customization/` (只包含程式碼，不含 processing/)
- ✅ `requirements.txt` (已更新)
- ✅ `README.md`
- ✅ `.gitattributes`

### Step 6.2: Git 提交和推送

```bash
# 在主專案目錄
cd /Users/yanbochen/Documents/Life_in_Canada/CS_study_related/Student_Course_Guide/CS7180_GenAI/GenAI-OnCallAssistant

# 移除 customization/processing 資料夾 (暫時)
mv customization/processing customization_processing_backup

# 添加修改的檔案
git add src/cloud_loader.py
git add customization/src/cloud_config.py
git add src/retrieval.py
git add customization/src/indexing/storage.py
git add customization/src/indexing/annoy_manager.py
git add customization/customization_pipeline.py
git add requirements.txt
git add .gitattributes

# 提交變更
git commit -m "Implement cloud data loading for HuggingFace Spaces deployment"

# 推送到 Spaces (不包含大檔案)
git push hf HuggingFace-Deployment:main --force

# 恢復 processing 資料夾 (本地開發用)
mv customization_processing_backup customization/processing
```

---

## Phase 7: 驗證部署

### Step 7.1: 檢查 Spaces 建置

1. 前往：https://huggingface.co/spaces/ybchen928/oncall-guide-ai
2. 檢查 **"App"** 標籤的建置狀態
3. 查看 **"Logs"** 確認雲端資料載入成功

### Step 7.2: 測試功能

1. **General Mode**: 測試基本醫療查詢
2. **Hospital Mode**: 測試 customization 功能
3. **Combined Mode**: 測試混合功能

---

## 🚨 故障排除

### 常見問題與解決方案：

**1. 模型下載失敗**

- 檢查 Dataset Repository 是否為 Public
- 確認網路連接正常

**2. 路徑錯誤**

- 檢查 cloud_loader.py 中的檔案路徑
- 確認 Dataset 中的檔案結構正確

**3. Import 錯誤**

- 檢查所有新增的 import 語句
- 確認 requirements.txt 包含 huggingface-hub

**4. Customization 功能失效**

- 檢查 customization/src/cloud_config.py 是否正確載入
- 確認 processing 資料在 Dataset 中的路徑

---

## 📊 檔案大小估算

**Spaces Repository (~50MB):**

- app.py + src/ + customization/src/ + configs
- 完全在 1GB 限制內

**Dataset Repository (~1.6GB):**

- models/ (~1.5GB)
- customization_data/processing/ (~100MB)
- 在 300GB 免費額度內

---

## 🎯 完成檢查清單

- [ ] Dataset Repository 創建並上傳資料
- [ ] 新增 src/cloud_loader.py
- [ ] 修改 src/retrieval.py 路徑邏輯
- [ ] 新增 customization/src/cloud_config.py
- [ ] 修改 customization 相關檔案路徑
- [ ] 本地測試雲端整合功能
- [ ] 部署到 Spaces (不含大檔案)
- [ ] 驗證完整功能正常運作
## ✅ 階段測試結果更新

### 階段 1 測試 ✅ 成功
- 雲端載入器連線正常
- Dataset Repository 存取成功

### 階段 2 測試 ✅ 成功  
- 核心檢索系統雲端載入正常
- General Pipeline 完整功能驗證
- 效能: Emergency (84.5M), Treatment (331M) 檔案下載成功

### 階段 3 測試 ✅ 成功
- Customization Pipeline 雲端載入正常  
- 預載入 10 個檔案 (~150MB) 成功
- Hospital-specific 功能完整驗證
- 測試結果: "chest pain" (36 results), "emergency treatment" (59 results)
- 系統載入: 110 tags, 3,784 chunks

**當前狀態: 準備階段 4 整合測試**
