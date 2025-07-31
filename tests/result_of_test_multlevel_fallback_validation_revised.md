🏥 OnCall.ai Multilevel Fallback Validation Test
============================================================
🔧 Initializing Components for Multilevel Fallback Test...
------------------------------------------------------------
1. Initializing Llama3-Med42-70B Client...
2025-07-31 07:51:06,059 - llm_clients - INFO - Medical LLM client initialized with model: m42-health/Llama3-Med42-70B
2025-07-31 07:51:06,059 - llm_clients - WARNING - Medical LLM Model: Research tool only. Not for professional medical diagnosis.
   ✅ LLM client initialized
2. Initializing Retrieval System...
2025-07-31 07:51:06,059 - retrieval - INFO - Initializing retrieval system...
2025-07-31 07:51:06,073 - sentence_transformers.SentenceTransformer - INFO - Use pytorch device_name: mps
2025-07-31 07:51:06,073 - sentence_transformers.SentenceTransformer - INFO - Load pretrained SentenceTransformer: NeuML/pubmedbert-base-embeddings
2025-07-31 07:51:09,264 - retrieval - INFO - Embedding model loaded successfully
2025-07-31 07:51:10,711 - retrieval - INFO - Chunks loaded successfully
2025-07-31 07:51:10,824 - retrieval - INFO - Embeddings loaded successfully
2025-07-31 07:51:10,825 - retrieval - INFO - Loaded existing emergency index
2025-07-31 07:51:10,826 - retrieval - INFO - Loaded existing treatment index
2025-07-31 07:51:10,826 - retrieval - INFO - Retrieval system initialized successfully
   ✅ Retrieval system initialized
3. Initializing User Prompt Processor...
2025-07-31 07:51:10,826 - sentence_transformers.SentenceTransformer - INFO - Use pytorch device_name: mps
2025-07-31 07:51:10,826 - sentence_transformers.SentenceTransformer - INFO - Load pretrained SentenceTransformer: NeuML/pubmedbert-base-embeddings
2025-07-31 07:51:12,702 - user_prompt - INFO - UserPromptProcessor initialized
   ✅ User prompt processor initialized

🎉 All components initialized successfully!

🚀 Starting Multilevel Fallback Test Suite
Total test cases: 13
Test started at: 2025-07-31 07:51:06
================================================================================

🔍 level1_001: Level 1: Direct predefined condition match
Query: 'acute myocardial infarction treatment'
Expected Level: 1
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:51:12,702 - user_prompt - INFO - Matched predefined condition: acute myocardial infarction
   ✅ Detected Level: 1
   Condition: acute myocardial infarction
   Emergency Keywords: MI|chest pain|cardiac arrest
   Treatment Keywords: aspirin|nitroglycerin|thrombolytic|PCI
   Execution Time: 0.000s
   🎉 Test PASSED - Expected behavior achieved

🔍 level1_002: Level 1: Predefined stroke condition
Query: 'how to manage acute stroke?'
Expected Level: 1
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:51:12,702 - user_prompt - INFO - Matched predefined condition: acute stroke
   ✅ Detected Level: 1
   Condition: acute stroke
   Emergency Keywords: stroke|neurological deficit|sudden weakness
   Treatment Keywords: tPA|thrombolysis|stroke unit care
   Execution Time: 0.000s
   🎉 Test PASSED - Expected behavior achieved

🔍 level1_003: Level 1: Predefined PE condition
Query: 'pulmonary embolism emergency protocol'
Expected Level: 1
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:51:12,702 - user_prompt - INFO - Matched predefined condition: pulmonary embolism
   ✅ Detected Level: 1
   Condition: pulmonary embolism
   Emergency Keywords: chest pain|shortness of breath|sudden dyspnea
   Treatment Keywords: anticoagulation|heparin|embolectomy
   Execution Time: 0.000s
   🎉 Test PASSED - Expected behavior achieved

🔍 level2_001: Level 2: Symptom-based query requiring LLM analysis
Query: 'patient with severe crushing chest pain radiating to left arm'
Expected Level: 2
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:51:12,702 - llm_clients - INFO - Calling Medical LLM with query: patient with severe crushing chest pain radiating to left arm
2025-07-31 07:51:55,277 - llm_clients - INFO - Raw LLM Response: Medical: "Acute Myocardial Infarction" (Heart Attack)
Explanation: The described symptoms of severe crushing chest pain radiating to the left arm are highly indicative of an acute myocardial infarction, commonly known as a heart attack. This is a medical emergency caused by blockage of coronary arteries, disrupting blood supply to the heart muscle.

(Not providing advice, just categorizing the condition)
2025-07-31 07:51:55,278 - llm_clients - INFO - Query Latency: 42.5747 seconds
2025-07-31 07:51:55,278 - llm_clients - INFO - Extracted Condition: acute myocardial infarction
   ✅ Detected Level: 1
   Condition: acute myocardial infarction
   Emergency Keywords: MI|chest pain|cardiac arrest
   Treatment Keywords: aspirin|nitroglycerin|thrombolytic|PCI
   Execution Time: 42.576s
   🎉 Test PASSED - Expected behavior achieved

🔍 level2_002: Level 2: Neurological symptoms requiring LLM
Query: 'sudden onset weakness on right side with speech difficulty'
Expected Level: 2
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:51:55,279 - llm_clients - INFO - Calling Medical LLM with query: sudden onset weakness on right side with speech difficulty
2025-07-31 07:52:06,165 - llm_clients - INFO - Raw LLM Response: Medical: "Acute Ischemic Stroke" (or Cerebrovascular Accident, specifically involving right hemispheric damage causing contralateral weakness and speech impairment)

Explanation: The symptoms described - sudden onset weakness on the right side (implying left brain hemisphere involvement due to contralateral motor control) and speech difficulty - are classic indicators of an acute ischemic stroke. This condition occurs when blood flow to a region of the brain is blocked, depriving it of oxygen and nutrients,
2025-07-31 07:52:06,165 - llm_clients - INFO - Query Latency: 10.8864 seconds
2025-07-31 07:52:06,165 - llm_clients - INFO - Extracted Condition: Medical: "Acute Ischemic Stroke" (or Cerebrovascular Accident, specifically involving right hemispheric damage causing contralateral weakness and speech impairment)
2025-07-31 07:52:06,166 - user_prompt - INFO - Starting semantic search fallback for query: 'sudden onset weakness on right side with speech difficulty'
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  1.61it/s]
2025-07-31 07:52:07,568 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:52:07,575 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.70it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.71it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.64it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.46it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.59it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.61it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.26it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 56.86it/s]
2025-07-31 07:52:07,896 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:52:07,896 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:52:07,896 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:52:07,897 - llm_clients - INFO - Calling Medical LLM with query: sudden onset weakness on right side with speech difficulty
2025-07-31 07:52:16,923 - llm_clients - INFO - Raw LLM Response: Medical: "Cerebrovascular Accident (CVA) - Ischemic Stroke" (or simply "Ischemic Stroke" for brevity, as it's the most specific diagnosis here)
  - Explanation: The symptoms described, sudden right-sided weakness and speech difficulty, are classic indicators of an ischemic stroke, which occurs when blood flow to the brain is blocked by a clot or narrowed blood vessels.

Note: While hemorrhagic stroke is another type of CVA, the given symptoms
2025-07-31 07:52:16,923 - llm_clients - INFO - Query Latency: 9.0264 seconds
2025-07-31 07:52:16,923 - llm_clients - INFO - Extracted Condition: Medical: "Cerebrovascular Accident (CVA) - Ischemic Stroke" (or simply "Ischemic Stroke" for brevity, as it's the most specific diagnosis here)
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  1.89it/s]
2025-07-31 07:52:17,964 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 22.751s
   ⚠️  Test PARTIAL - ⚠️ Level 5 != expected 2. ⚠️ Condition 'generic medical query' != expected ['acute stroke', 'cerebrovascular accident']. 

🔍 level3_001: Level 3: Generic medical terms requiring semantic search
Query: 'emergency management of cardiovascular crisis'
Expected Level: 3
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:52:18,030 - llm_clients - INFO - Calling Medical LLM with query: emergency management of cardiovascular crisis
2025-07-31 07:52:27,145 - llm_clients - INFO - Raw LLM Response: Medical: "Cardiovascular crisis" in this context (emergency management) is best represented by "Acute Myocardial Infarction (AMI)" or "ST-Elevation Myocardial Infarction (STEMI)," as both terms describe severe, time-critical cardiac events requiring immediate intervention. However, if considering a broader "cardiovascular crisis" that's not limited to infarction, "Cardiogenic Shock" might also be applicable, as it represents a severe, life
2025-07-31 07:52:27,145 - llm_clients - INFO - Query Latency: 9.1143 seconds
2025-07-31 07:52:27,145 - llm_clients - INFO - Extracted Condition: acute myocardial infarction
   ✅ Detected Level: 1
   Condition: acute myocardial infarction
   Emergency Keywords: MI|chest pain|cardiac arrest
   Treatment Keywords: aspirin|nitroglycerin|thrombolytic|PCI
   Execution Time: 9.115s
   ⚠️  Test PARTIAL - ⚠️ Level 1 != expected 3. ⚠️ Condition 'acute myocardial infarction' != expected []. 

🔍 level3_002: Level 3: Medical terminology requiring semantic fallback
Query: 'urgent neurological intervention protocols'
Expected Level: 3
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:52:27,145 - llm_clients - INFO - Calling Medical LLM with query: urgent neurological intervention protocols
2025-07-31 07:52:37,615 - llm_clients - INFO - Raw LLM Response: Medical: "Acute Ischemic Stroke" (representing a condition requiring urgent neurological intervention, specifically thrombectomy or thrombolysis protocols)

Explanation: Acute ischemic stroke necessitates rapid medical response, as timely interventions like mechanical thrombectomy or intravenous thrombolysis can significantly improve patient outcomes. The term "urgent neurological intervention protocols" in this context likely refers to these treatments for stroke, making "Acute Ischemic Stroke" the most representative medical condition.
2025-07-31 07:52:37,615 - llm_clients - INFO - Query Latency: 10.4695 seconds
2025-07-31 07:52:37,615 - llm_clients - INFO - Extracted Condition: Medical: "Acute Ischemic Stroke" (representing a condition requiring urgent neurological intervention, specifically thrombectomy or thrombolysis protocols)
2025-07-31 07:52:37,616 - user_prompt - INFO - Starting semantic search fallback for query: 'urgent neurological intervention protocols'
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  3.45it/s]
2025-07-31 07:52:38,539 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:52:38,549 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 49.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 52.73it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 64.13it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 51.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.40it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.10it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.29it/s]
2025-07-31 07:52:38,759 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:52:38,759 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:52:38,759 - user_prompt - INFO - No suitable condition found in semantic search
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.09it/s]
2025-07-31 07:52:39,345 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 12.249s
   ⚠️  Test PARTIAL - ⚠️ Level 5 != expected 3. ⚠️ Condition 'generic medical query' != expected []. 

🔍 level4a_001: Level 4a: Non-medical query should be rejected
Query: 'how to cook pasta properly?'
Expected Level: 4
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:52:39,395 - llm_clients - INFO - Calling Medical LLM with query: how to cook pasta properly?
2025-07-31 07:52:45,753 - llm_clients - INFO - Raw LLM Response: NON_MEDICAL_QUERY. This inquiry is about culinary technique (cooking pasta) and not related to medical conditions or health issues. It does not represent a medical topic for diagnosis or advice. Instead, it's a question of food preparation, typically addressed in cookbooks or culinary resources.
2025-07-31 07:52:45,753 - llm_clients - INFO - Query Latency: 6.3575 seconds
2025-07-31 07:52:45,753 - llm_clients - INFO - Extracted Condition: 
2025-07-31 07:52:45,753 - user_prompt - INFO - Starting semantic search fallback for query: 'how to cook pasta properly?'
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  1.47it/s]
2025-07-31 07:52:47,084 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:52:47,091 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.54it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.37it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 43.26it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.35it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.17it/s]
2025-07-31 07:52:47,305 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:52:47,305 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:52:47,305 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:52:47,305 - llm_clients - INFO - Calling Medical LLM with query: how to cook pasta properly?
2025-07-31 07:52:53,999 - llm_clients - INFO - Raw LLM Response: NON_MEDICAL_QUERY. This inquiry is about culinary technique (cooking pasta) and not related to any medical condition or health issue. It involves instructions on food preparation rather than addressing a disease, symptom, or medical concern.
2025-07-31 07:52:53,999 - llm_clients - INFO - Query Latency: 6.6933 seconds
2025-07-31 07:52:53,999 - llm_clients - INFO - Extracted Condition: 
   ✅ Detected Level: 4
   Condition: None
   Emergency Keywords: None
   Treatment Keywords: None
   Execution Time: 14.604s
   🎉 Test PASSED - Expected behavior achieved

🔍 level4a_002: Level 4a: Technology query should be rejected
Query: 'best programming language to learn in 2025'
Expected Level: 4
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:52:54,000 - llm_clients - INFO - Calling Medical LLM with query: best programming language to learn in 2025
2025-07-31 07:53:00,100 - llm_clients - INFO - Raw LLM Response: NON_MEDICAL_QUERY. This inquiry is about technology (specifically, programming languages) and their future relevance, rather than a medical condition or health topic. It doesn't pertain to diagnosis, treatment, or any medical aspect. Therefore, it's not a medical query.
2025-07-31 07:53:00,100 - llm_clients - INFO - Query Latency: 6.1004 seconds
2025-07-31 07:53:00,100 - llm_clients - INFO - Extracted Condition: 
2025-07-31 07:53:00,100 - user_prompt - INFO - Starting semantic search fallback for query: 'best programming language to learn in 2025'
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.94it/s]
2025-07-31 07:53:00,968 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:53:01,048 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.26it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 56.37it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 56.33it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.62it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 56.23it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.59it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.69it/s]
2025-07-31 07:53:01,255 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:53:01,255 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:53:01,255 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:53:01,256 - llm_clients - INFO - Calling Medical LLM with query: best programming language to learn in 2025
2025-07-31 07:53:06,397 - llm_clients - INFO - Raw LLM Response: NON_MEDICAL_QUERY. This inquiry is about selecting a programming language for future learning (in 2025) and has no relation to medical conditions or healthcare. It falls under the domain of computer science and technology education.
2025-07-31 07:53:06,397 - llm_clients - INFO - Query Latency: 5.1410 seconds
2025-07-31 07:53:06,397 - llm_clients - INFO - Extracted Condition: 
   ✅ Detected Level: 4
   Condition: None
   Emergency Keywords: None
   Treatment Keywords: None
   Execution Time: 12.397s
   🎉 Test PASSED - Expected behavior achieved

🔍 level4a_003: Level 4a: Weather query should be rejected
Query: 'weather forecast for tomorrow'
Expected Level: 4
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:53:06,397 - llm_clients - INFO - Calling Medical LLM with query: weather forecast for tomorrow
2025-07-31 07:53:11,119 - llm_clients - INFO - Raw LLM Response: NON_MEDICAL_QUERY. This inquiry is about meteorological information (weather prediction) and not related to any medical condition or health topic. It falls under environmental or general information, not medicine.
2025-07-31 07:53:11,120 - llm_clients - INFO - Query Latency: 4.7219 seconds
2025-07-31 07:53:11,120 - llm_clients - INFO - Extracted Condition: 
2025-07-31 07:53:11,120 - user_prompt - INFO - Starting semantic search fallback for query: 'weather forecast for tomorrow'
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.01it/s]
2025-07-31 07:53:12,200 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:53:12,209 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.36it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 51.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 53.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 63.88it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.51it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.37it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 65.13it/s]
2025-07-31 07:53:12,415 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:53:12,415 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:53:12,415 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:53:12,415 - llm_clients - INFO - Calling Medical LLM with query: weather forecast for tomorrow
2025-07-31 07:53:17,281 - llm_clients - INFO - Raw LLM Response: NON_MEDICAL_QUERY. This inquiry is about meteorology (predicting weather conditions) and not related to medical conditions or health issues. It doesn't involve symptoms, diagnoses, or any aspect of healthcare.
2025-07-31 07:53:17,281 - llm_clients - INFO - Query Latency: 4.8653 seconds
2025-07-31 07:53:17,281 - llm_clients - INFO - Extracted Condition: 
   ✅ Detected Level: 4
   Condition: None
   Emergency Keywords: None
   Treatment Keywords: None
   Execution Time: 10.884s
   🎉 Test PASSED - Expected behavior achieved

🔍 level4b_001: Level 4b→5: Obscure medical query passing validation to generic search
Query: 'rare hematologic malignancy treatment approaches'
Expected Level: 5
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:53:17,282 - llm_clients - INFO - Calling Medical LLM with query: rare hematologic malignancy treatment approaches
2025-07-31 07:53:26,329 - llm_clients - INFO - Raw LLM Response: Medical: "rare hematologic malignancy treatment approaches" → "Targeted Therapy for Agnogenic Myeloid Metaplasia (or currently, 'Agnogenic/Idiopathic: Myelofibrosis' in modern classification, as part of CMML-excluded rare myeloproliferative neoplasms) or, alternatively, 'Chimeric Antigen Receptor T-Cell therapy (CAR-T) for rare B-cell lymphomas like Primary Mediastinal
2025-07-31 07:53:26,329 - llm_clients - INFO - Query Latency: 9.0470 seconds
2025-07-31 07:53:26,331 - llm_clients - INFO - Extracted Condition: Medical: "rare hematologic malignancy treatment approaches" → "Targeted Therapy for Agnogenic Myeloid Metaplasia (or currently, 'Agnogenic/Idiopathic: Myelofibrosis' in modern classification, as part of CMML-excluded rare myeloproliferative neoplasms) or, alternatively, 'Chimeric Antigen Receptor T-Cell therapy (CAR-T) for rare B-cell lymphomas like Primary Mediastinal
2025-07-31 07:53:26,331 - user_prompt - INFO - Starting semantic search fallback for query: 'rare hematologic malignancy treatment approaches'
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.05it/s]
2025-07-31 07:53:26,871 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:53:26,880 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 12.32it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.77it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.97it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.97it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.97it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.87it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.43it/s]
2025-07-31 07:53:27,089 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:53:27,089 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:53:27,089 - user_prompt - INFO - No suitable condition found in semantic search
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.43it/s]
2025-07-31 07:53:27,626 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 10.356s
   🎉 Test PASSED - Expected behavior achieved

🔍 level4b_002: Level 4b→5: Rare condition requiring generic medical search
Query: 'idiopathic thrombocytopenic purpura management guidelines'
Expected Level: 5
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:53:27,638 - llm_clients - INFO - Calling Medical LLM with query: idiopathic thrombocytopenic purpura management guidelines
2025-07-31 07:53:36,704 - llm_clients - INFO - Raw LLM Response: Medical: "Idiopathic Thrombocytopenic Purpura (ITP) Management" → "ITP Treatment Protocols" (referring to guidelines for managing this autoimmune platelet disorder, which include corticosteroids, IVIG, thrombopoietin receptor agonists, or splenectomy in certain cases)

Explanation: This query is medical because it pertains to the guidelines for treating a specific blood disorder, Idiopathic Thrombocytopenic
2025-07-31 07:53:36,704 - llm_clients - INFO - Query Latency: 9.0658 seconds
2025-07-31 07:53:36,704 - llm_clients - INFO - Extracted Condition: Medical: "Idiopathic Thrombocytopenic Purpura (ITP) Management" → "ITP Treatment Protocols" (referring to guidelines for managing this autoimmune platelet disorder, which include corticosteroids, IVIG, thrombopoietin receptor agonists, or splenectomy in certain cases)
2025-07-31 07:53:36,704 - user_prompt - INFO - Starting semantic search fallback for query: 'idiopathic thrombocytopenic purpura management guidelines'
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.61it/s]
2025-07-31 07:53:37,450 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:53:37,459 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.43it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.51it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.38it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 43.72it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.79it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.22it/s]
2025-07-31 07:53:37,691 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:53:37,691 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:53:37,691 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:53:37,691 - llm_clients - INFO - Calling Medical LLM with query: idiopathic thrombocytopenic purpura management guidelines
2025-07-31 07:53:47,836 - llm_clients - INFO - Raw LLM Response: Medical: "Idiopathic Thrombocytopenic Purpura (ITP) Management" → "ITP Treatment Protocols" (referring to guidelines for therapy in this autoimmune platelet disorder, which may include corticosteroids, intravenous immunoglobulin, or thrombopoietin receptor agonists, among other strategies).

Explanation: This query is medical because it discusses guidelines for managing a specific blood disorder, idiopathic thrombocytopenic purpura
2025-07-31 07:53:47,836 - llm_clients - INFO - Query Latency: 10.1445 seconds
2025-07-31 07:53:47,836 - llm_clients - INFO - Extracted Condition: Medical: "Idiopathic Thrombocytopenic Purpura (ITP) Management" → "ITP Treatment Protocols" (referring to guidelines for therapy in this autoimmune platelet disorder, which may include corticosteroids, intravenous immunoglobulin, or thrombopoietin receptor agonists, among other strategies).
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.06it/s]
2025-07-31 07:53:48,812 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 21.183s
   🎉 Test PASSED - Expected behavior achieved

🔍 level4b_003: Level 4b→5: Rare emergency condition → generic search
Query: 'necrotizing fasciitis surgical intervention protocols'
Expected Level: 5
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:53:48,821 - llm_clients - INFO - Calling Medical LLM with query: necrotizing fasciitis surgical intervention protocols
2025-07-31 07:53:57,799 - llm_clients - INFO - Raw LLM Response: Medical: "Necrotizing Fasciitis" - In this context, the primary medical condition is Necrotizing Fasciitis, a severe soft tissue infection characterized by rapid progression and tissue death. The phrase "surgical intervention protocols" refers to the medical procedures and guidelines for surgically managing this condition, typically involving debridement (removal of dead tissue) and sometimes amputation.

Explanation: This query is medical because it pertains to a specific infectious disease (Necrotizing
2025-07-31 07:53:57,799 - llm_clients - INFO - Query Latency: 8.9777 seconds
2025-07-31 07:53:57,800 - llm_clients - INFO - Extracted Condition: Medical: "Necrotizing Fasciitis" - In this context, the primary medical condition is Necrotizing Fasciitis, a severe soft tissue infection characterized by rapid progression and tissue death. The phrase "surgical intervention protocols" refers to the medical procedures and guidelines for surgically managing this condition, typically involving debridement (removal of dead tissue) and sometimes amputation.
2025-07-31 07:53:57,800 - user_prompt - INFO - Starting semantic search fallback for query: 'necrotizing fasciitis surgical intervention protocols'
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.58it/s]
2025-07-31 07:53:58,405 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:53:58,414 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.81it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 48.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.49it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.11it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.81it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.57it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.03it/s]
Batches: 100%|███████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.29it/s]
2025-07-31 07:53:58,638 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:53:58,638 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:53:58,638 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:53:58,638 - llm_clients - INFO - Calling Medical LLM with query: necrotizing fasciitis surgical intervention protocols
2025-07-31 07:53:58,758 - llm_clients - ERROR - Medical LLM query error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b8386-259e81a24556b80a163e3d17;5ec89b2d-e0da-4255-90b6-f0c7e9577b38)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
2025-07-31 07:53:58,758 - llm_clients - ERROR - Error Type: HfHubHTTPError
2025-07-31 07:53:58,758 - llm_clients - ERROR - Detailed Error: HfHubHTTPError('402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b8386-259e81a24556b80a163e3d17;5ec89b2d-e0da-4255-90b6-f0c7e9577b38)\n\nYou have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.')
2025-07-31 07:53:58,758 - llm_clients - ERROR - Query Latency (on error): 0.1196 seconds
2025-07-31 07:53:58,758 - llm_clients - ERROR - Query that caused error: necrotizing fasciitis surgical intervention protocols
   ✅ Detected Level: 4
   Condition: None
   Emergency Keywords: None
   Treatment Keywords: None
   Execution Time: 9.937s
   ⚠️  Test PARTIAL - ⚠️ Level 4 != expected 5. ⚠️ Should trigger generic medical search. 

================================================================================
📊 MULTILEVEL FALLBACK TEST REPORT
================================================================================
🕐 Execution Summary:
   Total duration: 172.699s
   Average per test: 13.285s

📈 Test Results:
   Total tests: 13
   Passed: 9 ✅
   Partial: 4 ⚠️
   Failed: 4 ❌
   Success rate: 69.2%

🎯 Level Distribution Analysis:
   Level 1 (Predefined Mapping): 5 tests, avg 10.338s
   Level 4 (Validation Rejection): 4 tests, avg 11.956s
   Level 5 (Generic Search): 4 tests, avg 16.635s

📋 Category Analysis:
   level1_predefined: 3/3 (100.0%)
   level2_llm: 1/2 (50.0%)
   level3_semantic: 0/2 (0.0%)
   level4a_rejection: 3/3 (100.0%)
   level4b_to_5: 2/3 (66.7%)

📝 Detailed Test Results:

   level1_001: ✅ PASS
      Query: 'acute myocardial infarction treatment'
      Expected Level: 1
      Detected Level: 1
      Condition: acute myocardial infarction
      Time: 0.000s
      Validation: ✅ Level 1 as expected. ✅ Condition 'acute myocardial infarction' matches expected. 

   level1_002: ✅ PASS
      Query: 'how to manage acute stroke?'
      Expected Level: 1
      Detected Level: 1
      Condition: acute stroke
      Time: 0.000s
      Validation: ✅ Level 1 as expected. ✅ Condition 'acute stroke' matches expected. 

   level1_003: ✅ PASS
      Query: 'pulmonary embolism emergency protocol'
      Expected Level: 1
      Detected Level: 1
      Condition: pulmonary embolism
      Time: 0.000s
      Validation: ✅ Level 1 as expected. ✅ Condition 'pulmonary embolism' matches expected. 

   level2_001: ✅ PASS
      Query: 'patient with severe crushing chest pain radiating to left arm'
      Expected Level: 2
      Detected Level: 1
      Condition: acute myocardial infarction
      Time: 42.576s
      Validation: ⚠️ Level 1 != expected 2. ✅ Condition 'acute myocardial infarction' matches expected. 

   level2_002: ⚠️ PARTIAL
      Query: 'sudden onset weakness on right side with speech difficulty'
      Expected Level: 2
      Detected Level: 5
      Condition: generic medical query
      Time: 22.751s
      Validation: ⚠️ Level 5 != expected 2. ⚠️ Condition 'generic medical query' != expected ['acute stroke', 'cerebrovascular accident']. 

   level3_001: ⚠️ PARTIAL
      Query: 'emergency management of cardiovascular crisis'
      Expected Level: 3
      Detected Level: 1
      Condition: acute myocardial infarction
      Time: 9.115s
      Validation: ⚠️ Level 1 != expected 3. ⚠️ Condition 'acute myocardial infarction' != expected []. 

   level3_002: ⚠️ PARTIAL
      Query: 'urgent neurological intervention protocols'
      Expected Level: 3
      Detected Level: 5
      Condition: generic medical query
      Time: 12.249s
      Validation: ⚠️ Level 5 != expected 3. ⚠️ Condition 'generic medical query' != expected []. 

   level4a_001: ✅ PASS
      Query: 'how to cook pasta properly?'
      Expected Level: 4
      Detected Level: 4
      Condition: None
      Time: 14.604s
      Validation: ✅ Level 4 as expected. ✅ Query correctly rejected. 

   level4a_002: ✅ PASS
      Query: 'best programming language to learn in 2025'
      Expected Level: 4
      Detected Level: 4
      Condition: None
      Time: 12.397s
      Validation: ✅ Level 4 as expected. ✅ Query correctly rejected. 

   level4a_003: ✅ PASS
      Query: 'weather forecast for tomorrow'
      Expected Level: 4
      Detected Level: 4
      Condition: None
      Time: 10.884s
      Validation: ✅ Level 4 as expected. ✅ Query correctly rejected. 

   level4b_001: ✅ PASS
      Query: 'rare hematologic malignancy treatment approaches'
      Expected Level: 5
      Detected Level: 5
      Condition: generic medical query
      Time: 10.356s
      Validation: ✅ Level 5 as expected. ✅ Generic medical search triggered. 

   level4b_002: ✅ PASS
      Query: 'idiopathic thrombocytopenic purpura management guidelines'
      Expected Level: 5
      Detected Level: 5
      Condition: generic medical query
      Time: 21.183s
      Validation: ✅ Level 5 as expected. ✅ Generic medical search triggered. 

   level4b_003: ⚠️ PARTIAL
      Query: 'necrotizing fasciitis surgical intervention protocols'
      Expected Level: 5
      Detected Level: 4
      Condition: None
      Time: 9.937s
      Validation: ⚠️ Level 4 != expected 5. ⚠️ Should trigger generic medical search. 