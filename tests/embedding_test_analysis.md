# Embedding Test Analysis Report

## 1. Dataset Overview

### 1.1 Data Dimensions
- Emergency Dataset: 27,493 chunks × 768 dimensions
- Treatment Dataset: 82,378 chunks × 768 dimensions
- Total Chunks: 109,871

### 1.2 Embedding Statistics

**Emergency Embeddings:**
- Value Range: -3.246 to 3.480
- Mean: -0.017
- Standard Deviation: 0.462

**Treatment Embeddings:**
- Value Range: -3.686 to 3.505
- Mean: -0.017
- Standard Deviation: 0.472

**Analysis:**
- Both datasets have similar statistical properties
- Mean values are centered around zero (-0.017)
- Standard deviations are comparable (0.462 vs 0.472)
- Treatment dataset has slightly wider range (-3.686 to 3.505 vs -3.246 to 3.480)

## 2. Model Performance

### 2.1 Self-Retrieval Test
- Test Size: 20 random samples
- Success Rate: 19/20 (95%)
- Failed Case: Index 27418
- Average Response Time: ~5ms per search

**Observations:**
- High success rate in self-retrieval (95%)
- One failure case needs investigation
- Search operations are consistently fast

### 2.2 Cross-Dataset Search Performance

**Test Queries:**
1. "What is the treatment protocol for acute myocardial infarction?"
2. "How to manage severe chest pain with difficulty breathing?"
3. "What are the emergency procedures for anaphylactic shock?"

**Key Findings:**
- Each query returns top-5 results from both datasets
- Results show semantic understanding (not just keyword matching)
- First sentences provide good context for relevance assessment

## 3. System Performance

### 3.1 Response Times
- Model Loading: ~3 seconds
- Embedding Validation: ~0.5 seconds
- Search Operations: 0.1-0.2 seconds per query

### 3.2 Resource Usage
- Model loaded on MPS (Metal Performance Shaders)
- Efficient memory usage for large datasets
- Fast vector operations

## 4. Recommendations

### 4.1 Immediate Improvements
1. Investigate failed self-retrieval case (index 27418)
2. Consider caching frequently accessed embeddings
3. Add more diverse test queries

### 4.2 Future Enhancements
1. Implement hybrid search (combine with BM25)
2. Add relevance scoring mechanism
3. Consider domain-specific test cases

## 5. Log Analysis

### 5.1 Log Structure
```
timestamp - level - message
```

### 5.2 Log Levels Used
- DEBUG: Detailed operation info
- INFO: General progress and results
- WARNING: Non-critical issues
- ERROR: Critical failures

### 5.3 Key Log Categories
1. **Initialization Logs:**
   - Path configurations
   - Model loading
   - Dataset loading

2. **Performance Logs:**
   - Search operations
   - Response times
   - Success/failure counts

3. **Error Logs:**
   - Failed searches
   - Validation errors
   - Connection issues

### 5.4 Notable Log Patterns
- Regular HTTPS connections to HuggingFace
- Consistent search operation timing
- Clear error messages for failures


<!-- split -->


# 🧪 Embedding Test Analysis Report | 向量嵌入測試分析報告

## 1. Dataset Overview | 資料集總覽

### 1.1 Data Dimensions | 資料維度
- **Emergency Dataset**: 27,493 chunks × 768 dimensions
- **Treatment Dataset**: 82,378 chunks × 768 dimensions
- **Total Chunks**: 109,871

### 1.2 Embedding Statistics | 向量統計
**Emergency Embeddings 緊急資料集嵌入向量:**
- Value Range 範圍: -3.246 ~ 3.480
- Mean 平均值: -0.017
- Std 標準差: 0.462

**Treatment Embeddings 治療資料集嵌入向量:**
- Value Range 範圍: -3.686 ~ 3.505
- Mean 平均值: -0.017
- Std 標準差: 0.472

**Analysis 分析：**
- 兩組資料集中向量分布接近，平均值均接近 0
- Treatment 資料集範圍稍寬，可能涵蓋更廣語意

---

## 2. Model Performance | 模型檢索表現

### 2.1 Self-Retrieval Test | 自我召回測試
- 測試數量 Test Size: 20
- 成功率 Success Rate: **95% (19/20)**
- 失敗案例 Failed Index: `27418`
- 平均搜尋時間 Avg Search Time: ~5ms

**Observation 觀察：**
- 自我召回成功率高，顯示索引構建準確
- 可進一步針對失敗樣本檢查切 chunk 是否過短


<!-- Details -->

# 🔍 Embedding Search Analysis Report (Emergency vs Treatment)

## 📊 Overall Summary

| Query                                                   | Emergency Results     | Treatment Results     | Summary Comment                              |
|---------------------------------------------------------|------------------------|------------------------|-----------------------------------------------|
| 1️⃣ Treatment for Acute Myocardial Infarction           | ✅ Matched well         | ✅ Highly relevant      | Relevant guidelines retrieved from both sets |
| 2️⃣ Management of Severe Chest Pain with Dyspnea        | ⚠️ Redundant, not focused | ⚠️ Vague and general    | Lacks actionable steps, contains repetition   |
| 3️⃣ Emergency Procedures for Anaphylactic Shock         | ⚠️ Off-topic           | ✅ Precise and relevant | Emergency off-topic, but Treatment is strong  |

---

## 🧪 Detailed Query Analysis

### ✅ 1. `What is the treatment protocol for acute myocardial infarction?`

#### 📌 Emergency Dataset:
- `E-2 ~ E-4` mention guidelines, STEMI, PCI.
- Distances range from `0.833 ~ 0.842` → valid.
- `E-3` is a long guideline chunk → ideal RAG candidate.

✅ Conclusion: Emergency subset performs well, keyword chunking effective.

#### 📌 Treatment Dataset:
- `T-1` and `T-2` directly address the question with guideline phrases.
- `distance ~0.813` → strong semantic match.
- `T-5` is shorter but still contains “AMI”.

✅ Conclusion: Treatment retrieval is highly effective.

---

### ⚠️ 2. `How to manage severe chest pain with difficulty breathing?`

#### 📌 Emergency Dataset:
- `E-1 ~ E-3` are identical dyspnea passages; no actionable steps.
- `E-4 ~ E-5` are general symptom overviews, not acute response protocols.

⚠️ Issue: Semantic match exists, but lacks procedural content.  
⚠️ Repetition indicates Annoy might be over-focused on a narrow cluster.

#### 📌 Treatment Dataset:
- `T-1 ~ T-3` mention dyspnea and chest pain but are mostly patient descriptions.
- `T-4` hints at emergency care for asthma but still lacks clarity.

⚠️ Conclusion: This query needs better symptom-action co-occurrence modeling.

---

### ⚠️ 3. `What are the emergency procedures for anaphylactic shock?`

#### 📌 Emergency Dataset:
- `E-1 ~ E-2`: irrelevant or truncated.
- `E-3`: mentions management during anesthesia → partial match.
- `E-4 ~ E-5`: just list multiple shock types; no protocol info.

❌ Emergency dataset lacks focused content on this topic.

#### 📌 Treatment Dataset:
- `T-1`: explicitly lists epinephrine, oxygen, IV fluids, corticosteroids → ✅ ideal
- `T-2`: confirms emergency drug prep
- `T-3 ~ T-5`: all recognize anaphylactic shock

✅ Conclusion: Treatment subset captures this case very accurately.

---

## 📏 Distance Threshold Reference

| Distance Value Range | Interpretation                            |
|----------------------|--------------------------------------------|
| `< 0.80`             | Very strong match (almost identical)       |
| `0.80 ~ 0.86`        | Acceptable semantic match                  |
| `> 0.90`             | Weak relevance, possibly off-topic chunks  |

---

## 🧰 Recommendations Based on Findings

| Issue Type                     | Suggested Solution                                                       |


(genAIvenv) yanbochen@YanBos-MacBook-Pro tests % python test_embedding_validation.py


=== Query: What is the treatment protocol for acute myocardial infarction? ===
Batches: 100%|██████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  6.65it/s]

Emergency Dataset Results:

E-1 (distance: 0.826):
myocardial infarction, white [ / bib _ ref ].

E-2 (distance: 0.833):
the management of acute myocardial infarction : guidelines and audit standards successful management of acute myocardial infarction depends in the first instance on the patient recognising the symptoms and seeking help as quickly as possible.

E-3 (distance: 0.836):
sandbox : stemi # 2017 esc guidelines for the management of acute myocardial infarction in patients presenting with st - segment elevation # # changes in recommendations # # what is new in 2017 guidelines on ami - stemi? # # ami - stemi - 2017 new recommendations # acc / aats / aha / ase / asnc / scai / scct / sts 2016 appropriate use criteria for coronary revascularization in patients with acute coronary syndromes # # stemi — immediate revascularization by pci # # stemi — initial treatment by fibrinolytic therapy # # stemi — revascularization of nonculprit artery during the initial hospitalization # 2017 aha / acc clinical performance and quality measures for adults with st - elevation and non – st - elevation myocardial infarction # # revised stemi and nstemi measures # # revised stemi and nstemi measures.

E-4 (distance: 0.842):
stemi resident survival guide # overview st elevation myocardial infarction ( stemi ) is a syndrome characterized by the presence of symptoms of myocardial ischemia associated with persistent st elevation on electrocardiogram and elevated cardiac enzymes.

E-5 (distance: 0.879):
# pre - discharge care abbreviations : ace : angiotensin converting enzyme ; lvef : left ventricular ejection fraction ; mi : myocardial infarction ; pci : percutaneous coronary intervention ; po : per os ; stemi : st elevation myocardial infarction ; vf : ventricular fibrillation ; vt : ventricular tachycardia # long term management abbreviations : ace : angiotensin converting enzyme ; arb : angiotensin receptor blocker ; mi : myocardial infarction # do ' s - a pre - hospital ecg is recommended.

Treatment Dataset Results:

T-1 (distance: 0.813):
intain the standard of care and timely access of patients with ACS, including acute myocardial infarction (AMI), to reperfusion therapy.

T-2 (distance: 0.825):
The Management of Acute Myocardial Infarction: Guidelines and Audit Standards

Successful management of acute myocardial infarction.

T-3 (distance: 0.854):
fined as STEMI, NSTEMI or unstable angina.

T-4 (distance: 0.869):
Japan, there are no clear guidelines focusing on procedural aspect of the standardized care.

T-5 (distance: 0.879):
ients with acute myocardial infarction (AMI).


=== Query: How to manage severe chest pain with difficulty breathing? ===
Batches: 100%|██████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.76it/s]

Emergency Dataset Results:

E-1 (distance: 0.848):
shortness of breath resident survival guide # overview dyspnea is a symptom, it must generally be distinguished from signs that clinicians typically invoke as evidence of respiratory distress, such as tachypnea, use of accessory muscles, and intercostal retractions.

E-2 (distance: 0.849):
shortness of breath resident survival guide # overview dyspnea is a symptom, it must generally be distinguished from signs that clinicians typically invoke as evidence of respiratory distress, such as tachypnea, use of accessory muscles, and intercostal retractions.

E-3 (distance: 0.852):
shortness of breath resident survival guide # overview dyspnea is a symptom, it must generally be distinguished from signs that clinicians typically invoke as evidence of respiratory distress, such as tachypnea, use of accessory muscles, and intercostal retractions.

E-4 (distance: 0.879):
sandbox : milan # overview dyspnea is the uncomfortable awareness of one ' s own breathing.

E-5 (distance: 0.879):
sandbox : milan # overview dyspnea is the uncomfortable awareness of one ' s own breathing.

Treatment Dataset Results:

T-1 (distance: 0.827):
lly cyanotic and clammy, and may experience dyspnea or chest pain from underperfusion 13 .

T-2 (distance: 0.868):
acterized by a worsening of the patient’s respiratory symptoms (baseline dyspnea, cough, and/or sputum production) that is beyond normal day-to-day variations and leads to a change in medication.

T-3 (distance: 0.872):
ally cyanotic and clammy, and may experience dyspnea or chest pain from underperfusion 13.

T-4 (distance: 0.898):
ce used to test breathing) results show your breathing problems are worsening
- you need to go to the emergency room for asthma treatment.

T-5 (distance: 0.898):
breathlessness in a person in the last days of life.


=== Query: What are the emergency procedures for anaphylactic shock? ===
Batches: 100%|██████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.16it/s]

Emergency Dataset Results:

E-1 (distance: 0.924):
the other.

E-2 (distance: 0.943):
ic defibrillation.

E-3 (distance: 0.946):
suspected anaphylactic reactions associated with anaesthesia # # summary ( 1 ) the aagbi has published guidance on management of anaphylaxis during anaesthesia in.

E-4 (distance: 0.952):
- gastrointestinal bleeding - perforated peptic ulcer - post - procedural or post - surgical - retroperitoneal hemorrhage - rupture ovarian cyst - trauma - distributive shock - sepsis - toxic shock syndrome - anaphylactic or anaphylactoid reaction - neurogenic shock - adrenal crisis # fire : focused initial rapid evaluation a focused initial rapid evaluation ( fire ) should be performed to identify patients in need of immediate intervention.

E-5 (distance: 0.954):
- surgical - retroperitoneal hemorrhage - rupture ovarian cyst - trauma - distributive shock - sepsis - toxic shock syndrome - anaphylactic or anaphylactoid reaction - neurogenic shock - adrenal crisis # fire : focused initial rapid evaluation a focused initial rapid evaluation ( fire ) should be performed to identify patients in need of immediate intervention.

Treatment Dataset Results:

T-1 (distance: 0.813):
ensitivity (anaphylactic) reactions require emergency treatment with epinephrine and other emergency measures, that may include airway management, oxygen, intravenous fluids, antihistamines, corticosteroids, and vasopressors as clinically indicated.

T-2 (distance: 0.833):
ave standard emergency treatments for hypersensitivity or anaphylactic reactions readily available in the operating room (e.

T-3 (distance: 0.838):
e, or systemic inflammation (anaphylactic shock).

T-4 (distance: 0.843):
ED AND APPROPRIATE THERAPY INSTITUTED.

T-5 (distance: 0.844):
UED AND APPROPRIATE THERAPY INSTITUTED.