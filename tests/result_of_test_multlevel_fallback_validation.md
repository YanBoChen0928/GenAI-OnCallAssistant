🏥 OnCall.ai Multilevel Fallback Validation Test
============================================================
🔧 Initializing Components for Multilevel Fallback Test...
------------------------------------------------------------
1. Initializing Llama3-Med42-70B Client...
2025-07-31 07:12:17,625 - llm_clients - INFO - Medical LLM client initialized with model: m42-health/Llama3-Med42-70B
2025-07-31 07:12:17,626 - llm_clients - WARNING - Medical LLM Model: Research tool only. Not for professional medical diagnosis.
   ✅ LLM client initialized
2. Initializing Retrieval System...
2025-07-31 07:12:17,626 - retrieval - INFO - Initializing retrieval system...
2025-07-31 07:12:17,637 - sentence_transformers.SentenceTransformer - INFO - Use pytorch device_name: mps
2025-07-31 07:12:17,637 - sentence_transformers.SentenceTransformer - INFO - Load pretrained SentenceTransformer: NeuML/pubmedbert-base-embeddings
2025-07-31 07:12:20,936 - retrieval - INFO - Embedding model loaded successfully
2025-07-31 07:12:22,314 - retrieval - INFO - Chunks loaded successfully
2025-07-31 07:12:22,418 - retrieval - INFO - Embeddings loaded successfully
2025-07-31 07:12:22,419 - retrieval - INFO - Loaded existing emergency index
2025-07-31 07:12:22,420 - retrieval - INFO - Loaded existing treatment index
2025-07-31 07:12:22,420 - retrieval - INFO - Retrieval system initialized successfully
   ✅ Retrieval system initialized
3. Initializing User Prompt Processor...
2025-07-31 07:12:22,420 - sentence_transformers.SentenceTransformer - INFO - Use pytorch device_name: mps
2025-07-31 07:12:22,420 - sentence_transformers.SentenceTransformer - INFO - Load pretrained SentenceTransformer: NeuML/pubmedbert-base-embeddings
2025-07-31 07:12:24,622 - user_prompt - INFO - UserPromptProcessor initialized
   ✅ User prompt processor initialized

🎉 All components initialized successfully!

🚀 Starting Multilevel Fallback Test Suite
Total test cases: 13
Test started at: 2025-07-31 07:12:17
================================================================================

🔍 level1_001: Level 1: Direct predefined condition match
Query: 'acute myocardial infarction treatment'
Expected Level: 1
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:12:24,623 - user_prompt - INFO - Matched predefined condition: acute myocardial infarction
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
2025-07-31 07:12:24,623 - user_prompt - INFO - Matched predefined condition: acute stroke
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
2025-07-31 07:12:24,623 - user_prompt - INFO - Matched predefined condition: pulmonary embolism
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
2025-07-31 07:12:24,623 - llm_clients - INFO - Calling Medical LLM with query: patient with severe crushing chest pain radiating to left arm
2025-07-31 07:12:47,629 - llm_clients - INFO - Raw LLM Response: Acute Myocardial Infarction (STEMI) - considering "severe crushing chest pain" and radiation to the left arm, which are classic symptoms of a heart attack specifically involving ST-elevation (STEMI type), indicating complete blockage of a coronary artery. However, please note that as an AI assistant, I don't diagnose; this interpretation is based on common clinical presentation. A healthcare provider should perform an ECG and other tests for confirmation.
2025-07-31 07:12:47,630 - llm_clients - INFO - Query Latency: 23.0064 seconds
2025-07-31 07:12:47,630 - llm_clients - INFO - Extracted Condition: acute myocardial infarction
   ✅ Detected Level: 1
   Condition: acute myocardial infarction
   Emergency Keywords: MI|chest pain|cardiac arrest
   Treatment Keywords: aspirin|nitroglycerin|thrombolytic|PCI
   Execution Time: 23.008s
   🎉 Test PASSED - Expected behavior achieved

🔍 level2_002: Level 2: Neurological symptoms requiring LLM
Query: 'sudden onset weakness on right side with speech difficulty'
Expected Level: 2
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:12:47,631 - llm_clients - INFO - Calling Medical LLM with query: sudden onset weakness on right side with speech difficulty
2025-07-31 07:12:56,760 - llm_clients - INFO - Raw LLM Response: Cerebrovascular Accident (CVA), or Acute Ischemic Stroke (specifically, with right hemiparesis and aphasia) 

- This diagnosis represents the most likely condition given the sudden onset of right-sided weakness (hemiparesis) and speech difficulty (aphasia). An ischemic stroke occurs when blood flow to a part of the brain is blocked, typically by a thrombus or embolus, causing damage to brain tissue and resulting in neurological deficits. Immediate medical
2025-07-31 07:12:56,760 - llm_clients - INFO - Query Latency: 9.1288 seconds
2025-07-31 07:12:56,760 - llm_clients - INFO - Extracted Condition: Cerebrovascular Accident (CVA), or Acute Ischemic Stroke (specifically, with right hemiparesis and aphasia)
2025-07-31 07:12:56,760 - user_prompt - INFO - Starting semantic search fallback for query: 'sudden onset weakness on right side with speech difficulty'
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  1.66it/s]
2025-07-31 07:12:58,013 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:12:58,023 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.88it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.77it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.88it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.68it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.51it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.08it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.75it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 63.98it/s]
2025-07-31 07:12:58,342 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:12:58,342 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:12:58,342 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:12:58,342 - llm_clients - INFO - Calling Medical LLM with query: sudden onset weakness on right side with speech difficulty
2025-07-31 07:13:09,255 - llm_clients - INFO - Raw LLM Response: Cerebrovascular Accident (CVA), or Acute Ischemic Stroke (specifically, with right hemiparesis and aphasia) 

- This diagnosis represents the most likely condition given the sudden onset of right-sided weakness (hemiparesis) and speech difficulty (aphasia), which are classic symptoms of an ischemic stroke affecting the dominant hemisphere (assuming the patient is right-handed).

Please note that only a qualified physician can confirm a diagnosis after a thorough evaluation, including imaging studies
2025-07-31 07:13:09,255 - llm_clients - INFO - Query Latency: 10.9129 seconds
2025-07-31 07:13:09,255 - llm_clients - INFO - Extracted Condition: Cerebrovascular Accident (CVA), or Acute Ischemic Stroke (specifically, with right hemiparesis and aphasia)
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  8.55it/s]
2025-07-31 07:13:09,844 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 22.223s
   ⚠️  Test PARTIAL - ⚠️ Level 5 != expected 2. ⚠️ Condition 'generic medical query' != expected ['acute stroke', 'cerebrovascular accident']. 

🔍 level3_001: Level 3: Generic medical terms requiring semantic search
Query: 'emergency management of cardiovascular crisis'
Expected Level: 3
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:13:09,854 - llm_clients - INFO - Calling Medical LLM with query: emergency management of cardiovascular crisis
2025-07-31 07:13:20,094 - llm_clients - INFO - Raw LLM Response: Cardiac Arrest (or, in context of crisis not yet arrest: Acute Cardiogenic Emergency, e.g., STEMI) 

- Note: As a text-based AI assistant, not a clinician, I don't provide medical advice. The term given here represents the most critical cardiovascular crisis requiring immediate emergency intervention. Cardiac arrest implies the heart has stopped pumping, while acute cardiogenic emergency (e.g., ST-elevation myocardial infarction, or STEMI) signifies severe heart
2025-07-31 07:13:20,095 - llm_clients - INFO - Query Latency: 10.2402 seconds
2025-07-31 07:13:20,095 - llm_clients - INFO - Extracted Condition: Cardiac Arrest (or, in context of crisis not yet arrest: Acute Cardiogenic Emergency, e.g., STEMI)
2025-07-31 07:13:20,095 - user_prompt - INFO - Starting semantic search fallback for query: 'emergency management of cardiovascular crisis'
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.11it/s]
2025-07-31 07:13:20,681 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:13:20,713 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.75it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.28it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 56.29it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.79it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 65.12it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.44it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.88it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.20it/s]
2025-07-31 07:13:20,905 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:13:20,905 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:13:20,905 - user_prompt - INFO - No suitable condition found in semantic search
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.96it/s]
2025-07-31 07:13:21,492 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 11.647s
   ⚠️  Test PARTIAL - ⚠️ Level 5 != expected 3. ⚠️ Condition 'generic medical query' != expected []. 

🔍 level3_002: Level 3: Medical terminology requiring semantic fallback
Query: 'urgent neurological intervention protocols'
Expected Level: 3
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:13:21,501 - llm_clients - INFO - Calling Medical LLM with query: urgent neurological intervention protocols
2025-07-31 07:13:30,536 - llm_clients - INFO - Raw LLM Response: The most representative condition: Acute Ischemic Stroke (requiring urgent neurointervention, such as thrombectomy)

Explanation: The phrase "urgent neurological intervention protocols" typically refers to time-critical situations in neurology, and among these, acute ischemic stroke is a prime example. Acute ischemic stroke necessitates rapid evaluation and intervention, including thrombectomy, to restore blood flow and minimize brain damage. This condition demands urgent action due to its narrow therapeutic window, typically within 
2025-07-31 07:13:30,537 - llm_clients - INFO - Query Latency: 9.0352 seconds
2025-07-31 07:13:30,537 - llm_clients - INFO - Extracted Condition: The most representative condition: Acute Ischemic Stroke (requiring urgent neurointervention, such as thrombectomy)
2025-07-31 07:13:30,537 - user_prompt - INFO - Starting semantic search fallback for query: 'urgent neurological intervention protocols'
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  7.94it/s]
2025-07-31 07:13:31,115 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:13:31,123 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.96it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.55it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.09it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.23it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 48.16it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 65.05it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.42it/s]
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 63.08it/s]
2025-07-31 07:13:31,334 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:13:31,334 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:13:31,334 - user_prompt - INFO - No suitable condition found in semantic search
Batches: 100%|██████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.31it/s]
2025-07-31 07:13:31,889 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 10.398s
   ⚠️  Test PARTIAL - ⚠️ Level 5 != expected 3. ⚠️ Condition 'generic medical query' != expected []. 

🔍 level4a_001: Level 4a: Non-medical query should be rejected
Query: 'how to cook pasta properly?'
Expected Level: 4
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:13:31,899 - llm_clients - INFO - Calling Medical LLM with query: how to cook pasta properly?
2025-07-31 07:13:41,038 - llm_clients - INFO - Raw LLM Response: As a medical assistant, I do not address cooking techniques, only medical conditions. However, for context (not advice): This query doesn't represent a medical condition; it's about culinary practice. In this case, "properly" cooking pasta typically means achieving al dente texture (not overly soft) by boiling in adequately salted water for the recommended time on the package, then draining well. This is unrelated to any health condition unless discussing, hypothetically, gastrointestinal tolerance in specific patients (e
2025-07-31 07:13:41,038 - llm_clients - INFO - Query Latency: 9.1386 seconds
2025-07-31 07:13:41,038 - llm_clients - INFO - Extracted Condition: As a medical assistant, I do not address cooking techniques, only medical conditions. However, for context (not advice): This query doesn't represent a medical condition; it's about culinary practice. In this case, "properly" cooking pasta typically means achieving al dente texture (not overly soft) by boiling in adequately salted water for the recommended time on the package, then draining well. This is unrelated to any health condition unless discussing, hypothetically, gastrointestinal tolerance in specific patients (e
2025-07-31 07:13:41,038 - user_prompt - INFO - Starting semantic search fallback for query: 'how to cook pasta properly?'
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.02it/s]
2025-07-31 07:13:42,156 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:13:42,165 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  9.34it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 52.88it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.97it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.95it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.63it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.07it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.84it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.43it/s]
2025-07-31 07:13:42,407 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:13:42,407 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:13:42,407 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:13:42,407 - llm_clients - INFO - Calling Medical LLM with query: how to cook pasta properly?
2025-07-31 07:13:51,634 - llm_clients - INFO - Raw LLM Response: As a medical assistant, I don't address cooking techniques, but for context (not medical advice): In terms of relevance to health, the key aspect here isn't "proper" cooking per se, but rather avoiding overcooking that can reduce nutrient content. For whole-grain pasta, aim for al dente texture (firm, not mushy) to preserve fiber and other nutrients. However, this query is not about a medical condition but a culinary practice.
 Representative (non-medical) term
2025-07-31 07:13:51,634 - llm_clients - INFO - Query Latency: 9.2269 seconds
2025-07-31 07:13:51,634 - llm_clients - INFO - Extracted Condition: As a medical assistant, I don't address cooking techniques, but for context (not medical advice): In terms of relevance to health, the key aspect here isn't "proper" cooking per se, but rather avoiding overcooking that can reduce nutrient content. For whole-grain pasta, aim for al dente texture (firm, not mushy) to preserve fiber and other nutrients. However, this query is not about a medical condition but a culinary practice.
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.02it/s]
2025-07-31 07:13:52,790 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 20.900s
   ⚠️  Test PARTIAL - ⚠️ Level 5 != expected 4. ⚠️ Query should have been rejected. 

🔍 level4a_002: Level 4a: Technology query should be rejected
Query: 'best programming language to learn in 2025'
Expected Level: 4
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:13:52,799 - llm_clients - INFO - Calling Medical LLM with query: best programming language to learn in 2025
2025-07-31 07:14:02,339 - llm_clients - INFO - Raw LLM Response: As a medical assistant, I do not address technology or education preferences like "best programming language" (which is non-medical context); however, for clarity, this query is outside my biomedical scope. In 2025 or any current year, the choice of "best" programming language is subjective and depends on industry trends, personal goals, and specific use cases (e.g., web development, mobile apps, or data science). Popular choices include Python, JavaScript, and Java, but it's crucial
2025-07-31 07:14:02,339 - llm_clients - INFO - Query Latency: 9.5400 seconds
2025-07-31 07:14:02,339 - llm_clients - INFO - Extracted Condition: As a medical assistant, I do not address technology or education preferences like "best programming language" (which is non-medical context); however, for clarity, this query is outside my biomedical scope. In 2025 or any current year, the choice of "best" programming language is subjective and depends on industry trends, personal goals, and specific use cases (e.g., web development, mobile apps, or data science). Popular choices include Python, JavaScript, and Java, but it's crucial
2025-07-31 07:14:02,339 - user_prompt - INFO - Starting semantic search fallback for query: 'best programming language to learn in 2025'
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  6.45it/s]
2025-07-31 07:14:02,974 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:14:02,986 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  3.16it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.42it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.06it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.97it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 40.41it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.85it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.99it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.63it/s]
2025-07-31 07:14:03,457 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:14:03,457 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:14:03,457 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:14:03,457 - llm_clients - INFO - Calling Medical LLM with query: best programming language to learn in 2025
2025-07-31 07:14:13,766 - llm_clients - INFO - Raw LLM Response: As a medical assistant, I don't analyze technology trends or recommend programming languages; however, for clarity's sake (though out of my medical scope), in 2021 (not 2025's future prediction, as I'm bound by current data), popular choices for learning include Python, JavaScript, and Java due to their versatility, wide adoption, and job market demand. Keep in mind this information is not medical advice but rather a layman's interpretation of tech trends.

Representative Condition (not
2025-07-31 07:14:13,766 - llm_clients - INFO - Query Latency: 10.3088 seconds
2025-07-31 07:14:13,767 - llm_clients - INFO - Extracted Condition: As a medical assistant, I don't analyze technology trends or recommend programming languages; however, for clarity's sake (though out of my medical scope), in 2021 (not 2025's future prediction, as I'm bound by current data), popular choices for learning include Python, JavaScript, and Java due to their versatility, wide adoption, and job market demand. Keep in mind this information is not medical advice but rather a layman's interpretation of tech trends.
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.00it/s]
2025-07-31 07:14:14,884 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 22.107s
   ⚠️  Test PARTIAL - ⚠️ Level 5 != expected 4. ⚠️ Query should have been rejected. 

🔍 level4a_003: Level 4a: Weather query should be rejected
Query: 'weather forecast for tomorrow'
Expected Level: 4
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:14:14,905 - llm_clients - INFO - Calling Medical LLM with query: weather forecast for tomorrow
2025-07-31 07:14:24,069 - llm_clients - INFO - Raw LLM Response: As a medical assistant, I do not address weather forecasts; however, for context clarification, this query is unrelated to medical conditions. The requested information here is about meteorology (weather prediction) rather than health or disease. There's no representative medical condition to provide in this case.

If, however, you were referring indirectly to weather-sensitive health conditions (e.g., heat exhaustion, cold-induced asthma exacerbation), the specific condition would depend on the actual weather forecast details (temperature, humidity, etc.)
2025-07-31 07:14:24,069 - llm_clients - INFO - Query Latency: 9.1634 seconds
2025-07-31 07:14:24,069 - llm_clients - INFO - Extracted Condition: As a medical assistant, I do not address weather forecasts; however, for context clarification, this query is unrelated to medical conditions. The requested information here is about meteorology (weather prediction) rather than health or disease. There's no representative medical condition to provide in this case.
2025-07-31 07:14:24,070 - user_prompt - INFO - Starting semantic search fallback for query: 'weather forecast for tomorrow'
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.17it/s]
2025-07-31 07:14:25,222 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:14:25,234 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.71it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.65it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.87it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.21it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 21.32it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.77it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 53.42it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 56.34it/s]
2025-07-31 07:14:25,491 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:14:25,491 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:14:25,491 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:14:25,491 - llm_clients - INFO - Calling Medical LLM with query: weather forecast for tomorrow
2025-07-31 07:14:35,356 - llm_clients - INFO - Raw LLM Response: As a medical assistant, I do not address weather forecasts; however, for this context (to maintain representativeness in terms unrelated to diagnosis), the phrase here isn't indicative of a medical condition. Instead, it's about environmental information—specifically, a request for meteorological data (tomorrow's weather). In medical terminology, we wouldn't classify this as a condition, but for representation's sake in a non-medical context, it can be labeled as "meteorological inquiry" or simply
2025-07-31 07:14:35,356 - llm_clients - INFO - Query Latency: 9.8645 seconds
2025-07-31 07:14:35,356 - llm_clients - INFO - Extracted Condition: As a medical assistant, I do not address weather forecasts; however, for this context (to maintain representativeness in terms unrelated to diagnosis), the phrase here isn't indicative of a medical condition. Instead, it's about environmental information—specifically, a request for meteorological data (tomorrow's weather). In medical terminology, we wouldn't classify this as a condition, but for representation's sake in a non-medical context, it can be labeled as "meteorological inquiry" or simply
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.19it/s]
2025-07-31 07:14:36,024 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 21.128s
   ⚠️  Test PARTIAL - ⚠️ Level 5 != expected 4. ⚠️ Query should have been rejected. 

🔍 level4b_001: Level 4b→5: Obscure medical query passing validation to generic search
Query: 'rare hematologic malignancy treatment approaches'
Expected Level: 5
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:14:36,033 - llm_clients - INFO - Calling Medical LLM with query: rare hematologic malignancy treatment approaches
2025-07-31 07:14:45,301 - llm_clients - INFO - Raw LLM Response: The most representative condition: Myelofibrosis (or, in context of "rare" reference, could be an even less common variant like BCR-ABL1-negative atypical CML or unclassifiable myeloproliferative neoplasm) 

- For myelofibrosis, primary treatment approaches include JAK2 inhibitors (e.g., ruxolitinib), supportive care (transfusions, erythropoiesis-stimulating agents), and allog
2025-07-31 07:14:45,302 - llm_clients - INFO - Query Latency: 9.2678 seconds
2025-07-31 07:14:45,302 - llm_clients - INFO - Extracted Condition: The most representative condition: Myelofibrosis (or, in context of "rare" reference, could be an even less common variant like BCR-ABL1-negative atypical CML or unclassifiable myeloproliferative neoplasm)
2025-07-31 07:14:45,302 - user_prompt - INFO - Starting semantic search fallback for query: 'rare hematologic malignancy treatment approaches'
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.00it/s]
2025-07-31 07:14:46,428 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:14:46,436 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.59it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 38.61it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.66it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.40it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.09it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.42it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.98it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 66.70it/s]
2025-07-31 07:14:46,672 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:14:46,672 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:14:46,672 - user_prompt - INFO - No suitable condition found in semantic search
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.28it/s]
2025-07-31 07:14:47,160 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 11.137s
   🎉 Test PASSED - Expected behavior achieved

🔍 level4b_002: Level 4b→5: Rare condition requiring generic medical search
Query: 'idiopathic thrombocytopenic purpura management guidelines'
Expected Level: 5
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:14:47,170 - llm_clients - INFO - Calling Medical LLM with query: idiopathic thrombocytopenic purpura management guidelines
2025-07-31 07:14:56,483 - llm_clients - INFO - Raw LLM Response: The primary medical condition: Idiopathic Thrombocytopenic Purpura (ITP)

(As a medical assistant, I do not provide advice, but here's the relevant condition with context for a knowledge reference.)
In this case, the most representative condition is Idiopathic Thrombocytopenic Purpura (ITP), an autoimmune disorder characterized by low platelet count (thrombocytopenia) without identifiable underlying causes. Management guidelines typically involve
2025-07-31 07:14:56,484 - llm_clients - INFO - Query Latency: 9.3136 seconds
2025-07-31 07:14:56,484 - llm_clients - INFO - Extracted Condition: The primary medical condition: Idiopathic Thrombocytopenic Purpura (ITP)
2025-07-31 07:14:56,484 - user_prompt - INFO - Starting semantic search fallback for query: 'idiopathic thrombocytopenic purpura management guidelines'
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.14it/s]
2025-07-31 07:14:57,082 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:14:57,090 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 12.83it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 51.94it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.06it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 65.59it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.81it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.78it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.76it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.14it/s]
2025-07-31 07:14:57,296 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:14:57,296 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:14:57,296 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:14:57,296 - llm_clients - INFO - Calling Medical LLM with query: idiopathic thrombocytopenic purpura management guidelines
2025-07-31 07:15:06,621 - llm_clients - INFO - Raw LLM Response: The primary medical condition: Idiopathic Thrombocytopenic Purpura (ITP)

(As a medical assistant, I don't provide advice, but describe the condition and point to standard guidelines. For ITP management, refer to professional sources like the American Society of Hematology [ASH] or National Institutes of Health [NIH].)

Idiopathic Thrombocytopenic Purpura (ITP) is an autoimmune disorder characterized by low platelet count
2025-07-31 07:15:06,621 - llm_clients - INFO - Query Latency: 9.3245 seconds
2025-07-31 07:15:06,621 - llm_clients - INFO - Extracted Condition: The primary medical condition: Idiopathic Thrombocytopenic Purpura (ITP)
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 11.12it/s]
2025-07-31 07:15:07,391 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 20.228s
   🎉 Test PASSED - Expected behavior achieved

🔍 level4b_003: Level 4b→5: Rare emergency condition → generic search
Query: 'necrotizing fasciitis surgical intervention protocols'
Expected Level: 5
----------------------------------------------------------------------
🎯 Executing multilevel fallback...
2025-07-31 07:15:07,398 - llm_clients - INFO - Calling Medical LLM with query: necrotizing fasciitis surgical intervention protocols
2025-07-31 07:15:16,625 - llm_clients - INFO - Raw LLM Response: The primary medical condition: Necrotizing Fasciitis

In this context, the key condition is Necrotizing Fasciitis, a severe bacterial infection characterized by rapid destruction of subcutaneous tissue and fascia. The term provided, "surgical intervention protocols," refers to the treatment approach rather than a distinct medical condition. However, for clarity in this answer, I'll address it as it pertains to managing Necrotizing Fasciitis.

In Necrotizing Fasciitis, surgical
2025-07-31 07:15:16,625 - llm_clients - INFO - Query Latency: 9.2271 seconds
2025-07-31 07:15:16,625 - llm_clients - INFO - Extracted Condition: The primary medical condition: Necrotizing Fasciitis
2025-07-31 07:15:16,625 - user_prompt - INFO - Starting semantic search fallback for query: 'necrotizing fasciitis surgical intervention protocols'
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.01it/s]
2025-07-31 07:15:17,212 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 07:15:17,222 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 12.01it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.04it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.57it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.92it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 48.15it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.28it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.83it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.38it/s]
2025-07-31 07:15:17,449 - user_prompt - INFO - Inferred condition: None
2025-07-31 07:15:17,449 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 07:15:17,449 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 07:15:17,449 - llm_clients - INFO - Calling Medical LLM with query: necrotizing fasciitis surgical intervention protocols
2025-07-31 07:15:24,511 - llm_clients - INFO - Raw LLM Response: The most representative condition: Necrotizing Fasciitis

(As a medical assistant, I do not provide advice, only identify conditions. For necrotizing fasciitis, surgical intervention typically involves aggressive debridement—removing dead tissue—and may require repeated procedures until healthy margins are achieved. This is accompanied by supportive care and antibiotics.)


2025-07-31 07:15:24,511 - llm_clients - INFO - Query Latency: 7.0619 seconds
2025-07-31 07:15:24,511 - llm_clients - INFO - Extracted Condition: The most representative condition: Necrotizing Fasciitis
Batches: 100%|██████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.83it/s]
2025-07-31 07:15:25,078 - retrieval - INFO - Sliding window search: Found 5 results
   ✅ Detected Level: 5
   Condition: generic medical query
   Emergency Keywords: medical|emergency
   Treatment Keywords: treatment|management
   Execution Time: 17.692s
   🎉 Test PASSED - Expected behavior achieved

================================================================================
📊 MULTILEVEL FALLBACK TEST REPORT
================================================================================
🕐 Execution Summary:
   Total duration: 187.465s
   Average per test: 14.420s

📈 Test Results:
   Total tests: 13
   Passed: 7 ✅
   Partial: 6 ⚠️
   Failed: 6 ❌
   Success rate: 53.8%

🎯 Level Distribution Analysis:
   Level 1 (Predefined Mapping): 4 tests, avg 5.752s
   Level 5 (Generic Search): 9 tests, avg 17.495s

📋 Category Analysis:
   level1_predefined: 3/3 (100.0%)
   level2_llm: 1/2 (50.0%)
   level3_semantic: 0/2 (0.0%)
   level4a_rejection: 0/3 (0.0%)
   level4b_to_5: 3/3 (100.0%)

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
      Time: 23.008s
      Validation: ⚠️ Level 1 != expected 2. ✅ Condition 'acute myocardial infarction' matches expected. 

   level2_002: ⚠️ PARTIAL
      Query: 'sudden onset weakness on right side with speech difficulty'
      Expected Level: 2
      Detected Level: 5
      Condition: generic medical query
      Time: 22.223s
      Validation: ⚠️ Level 5 != expected 2. ⚠️ Condition 'generic medical query' != expected ['acute stroke', 'cerebrovascular accident']. 

   level3_001: ⚠️ PARTIAL
      Query: 'emergency management of cardiovascular crisis'
      Expected Level: 3
      Detected Level: 5
      Condition: generic medical query
      Time: 11.647s
      Validation: ⚠️ Level 5 != expected 3. ⚠️ Condition 'generic medical query' != expected []. 

   level3_002: ⚠️ PARTIAL
      Query: 'urgent neurological intervention protocols'
      Expected Level: 3
      Detected Level: 5
      Condition: generic medical query
      Time: 10.398s
      Validation: ⚠️ Level 5 != expected 3. ⚠️ Condition 'generic medical query' != expected []. 

   level4a_001: ⚠️ PARTIAL
      Query: 'how to cook pasta properly?'
      Expected Level: 4
      Detected Level: 5
      Condition: generic medical query
      Time: 20.900s
      Validation: ⚠️ Level 5 != expected 4. ⚠️ Query should have been rejected. 

   level4a_002: ⚠️ PARTIAL
      Query: 'best programming language to learn in 2025'
      Expected Level: 4
      Detected Level: 5
      Condition: generic medical query
      Time: 22.107s
      Validation: ⚠️ Level 5 != expected 4. ⚠️ Query should have been rejected. 

   level4a_003: ⚠️ PARTIAL
      Query: 'weather forecast for tomorrow'
      Expected Level: 4
      Detected Level: 5
      Condition: generic medical query
      Time: 21.128s
      Validation: ⚠️ Level 5 != expected 4. ⚠️ Query should have been rejected. 

   level4b_001: ✅ PASS
      Query: 'rare hematologic malignancy treatment approaches'
      Expected Level: 5
      Detected Level: 5
      Condition: generic medical query
      Time: 11.137s
      Validation: ✅ Level 5 as expected. ✅ Generic medical search triggered. 

   level4b_002: ✅ PASS
      Query: 'idiopathic thrombocytopenic purpura management guidelines'
      Expected Level: 5
      Detected Level: 5
      Condition: generic medical query
      Time: 20.228s
      Validation: ✅ Level 5 as expected. ✅ Generic medical search triggered. 

   level4b_003: ✅ PASS
      Query: 'necrotizing fasciitis surgical intervention protocols'
      Expected Level: 5
      Detected Level: 5
      Condition: generic medical query
      Time: 17.692s
      Validation: ✅ Level 5 as expected. ✅ Generic medical search triggered. 