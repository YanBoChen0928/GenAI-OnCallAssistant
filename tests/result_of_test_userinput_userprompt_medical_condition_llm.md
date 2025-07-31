🏥 OnCall.ai Medical Query Processing Pipeline Test
============================================================
🔧 Initializing Pipeline Components...
--------------------------------------------------
1. Initializing Llama3-Med42-70B Client...
2025-07-31 06:38:22,609 - llm_clients - INFO - Medical LLM client initialized with model: m42-health/Llama3-Med42-70B
2025-07-31 06:38:22,609 - llm_clients - WARNING - Medical LLM Model: Research tool only. Not for professional medical diagnosis.
   ✅ LLM client initialized successfully
2. Initializing Retrieval System...
2025-07-31 06:38:22,609 - retrieval - INFO - Initializing retrieval system...
2025-07-31 06:38:22,621 - sentence_transformers.SentenceTransformer - INFO - Use pytorch device_name: mps
2025-07-31 06:38:22,621 - sentence_transformers.SentenceTransformer - INFO - Load pretrained SentenceTransformer: NeuML/pubmedbert-base-embeddings
2025-07-31 06:38:26,965 - retrieval - INFO - Embedding model loaded successfully
2025-07-31 06:38:28,444 - retrieval - INFO - Chunks loaded successfully
2025-07-31 06:38:28,532 - retrieval - INFO - Embeddings loaded successfully
2025-07-31 06:38:28,533 - retrieval - INFO - Loaded existing emergency index
2025-07-31 06:38:28,534 - retrieval - INFO - Loaded existing treatment index
2025-07-31 06:38:28,534 - retrieval - INFO - Retrieval system initialized successfully
   ✅ Retrieval system initialized successfully
3. Initializing User Prompt Processor...
2025-07-31 06:38:28,534 - sentence_transformers.SentenceTransformer - INFO - Use pytorch device_name: mps
2025-07-31 06:38:28,534 - sentence_transformers.SentenceTransformer - INFO - Load pretrained SentenceTransformer: NeuML/pubmedbert-base-embeddings
2025-07-31 06:38:30,716 - user_prompt - INFO - UserPromptProcessor initialized
   ✅ User prompt processor initialized successfully

🎉 All components initialized successfully!

🚀 Starting Comprehensive Pipeline Test
Total test cases: 6
Test started at: 2025-07-31 06:38:22
================================================================================

🔍 test_001: Classic acute myocardial infarction query
Query: 'how to treat acute MI?'
------------------------------------------------------------
Step 1: Extracting medical condition and keywords...
2025-07-31 06:38:30,716 - llm_clients - INFO - Calling Medical LLM with query: how to treat acute MI?
2025-07-31 06:39:12,449 - llm_clients - INFO - Raw LLM Response: The most representative condition: Acute Myocardial Infarction (AMI, or Heart Attack)

For treatment guidance: Acute myocardial infarction is managed by cardiologists and emergency medical teams, not medical assistants. However, for informational purposes, primary treatments include:
1. Reperfusion therapy: This may involve fibrinolysis (clot-busting medications) or percutaneous coronary intervention (PCI, such as angioplasty and stenting).
2. Antiplatelet therapy
2025-07-31 06:39:12,450 - llm_clients - INFO - Query Latency: 41.7327 seconds
2025-07-31 06:39:12,450 - llm_clients - INFO - Extracted Condition: acute myocardial infarction
   Condition: acute myocardial infarction
   Emergency keywords: MI|chest pain|cardiac arrest
   Treatment keywords: aspirin|nitroglycerin|thrombolytic|PCI
   Source: predefined_mapping
   Duration: 41.734s

Step 2: User confirmation process...
   Confirmation type: confirmation_needed

Step 3: Executing retrieval...
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  1.46it/s]
2025-07-31 06:39:13,227 - retrieval - INFO - Search results: Emergency=5, Treatment=5
2025-07-31 06:39:13,228 - retrieval - INFO - Deduplication: Processing 10 results using text matching
2025-07-31 06:39:13,228 - retrieval - INFO - Deduplication summary: 10 → 9 results (removed 1)
   Search query: 'MI|chest pain|cardiac arrest aspirin|nitroglycerin|thrombolytic|PCI'
   Total results: 9
   Emergency results: 4
   Treatment results: 5
   Duration: 0.778s

   Top 3 results:
      1. Type: treatment, Distance: 0.6740
         Text preview: ong term management abbreviations : ace : angiotensin converting enzyme ; arb : angiotensin receptor...
      2. Type: treatment, Distance: 0.6792
         Text preview: on ; pci : percutaneous coronary intervention ; po : per os ; stemi : st elevation myocardial infarc...
      3. Type: treatment, Distance: 0.6904
         Text preview: receptor blocker ; mi : myocardial infarction # do ' s - a pre - hospital ecg is recommended. if ste...

✅ Test test_001 completed successfully (42.511s)

🔍 test_002: Symptoms-based query requiring LLM analysis
Query: 'patient with severe chest pain and shortness of breath'
------------------------------------------------------------
Step 1: Extracting medical condition and keywords...
2025-07-31 06:39:13,228 - llm_clients - INFO - Calling Medical LLM with query: patient with severe chest pain and shortness of breath
2025-07-31 06:39:31,525 - llm_clients - INFO - Raw LLM Response: Acute Coronary Syndrome (specifically, possible ST-Elevation Myocardial Infarction - STEMI, given severe chest pain, or non-STEMI/NST-Elevation Acute Coronary Syndrome if ST segments not elevated, based on ECG; shortness of breath indicates potential cardiac ischemia complication or concurrent pulmonary issue like cardiogenic pulmonary edema)

Note: This response is for informational purposes only and should not replace immediate medical evaluation and diagnosis by a licensed physician. The patient needs
2025-07-31 06:39:31,525 - llm_clients - INFO - Query Latency: 18.2971 seconds
2025-07-31 06:39:31,525 - llm_clients - INFO - Extracted Condition: Acute Coronary Syndrome (specifically, possible ST-Elevation Myocardial Infarction - STEMI, given severe chest pain, or non-STEMI/NST-Elevation Acute Coronary Syndrome if ST segments not elevated, based on ECG; shortness of breath indicates potential cardiac ischemia complication or concurrent pulmonary issue like cardiogenic pulmonary edema)
2025-07-31 06:39:31,525 - user_prompt - INFO - Starting semantic search fallback for query: 'patient with severe chest pain and shortness of breath'
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  7.70it/s]
2025-07-31 06:39:32,392 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 06:39:32,402 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.86it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.53it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.22it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 57.51it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 17.23it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.05it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.09it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 60.88it/s]
2025-07-31 06:39:32,729 - user_prompt - INFO - Inferred condition: None
2025-07-31 06:39:32,729 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 06:39:32,729 - user_prompt - INFO - No suitable condition found in semantic search
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.77it/s]
2025-07-31 06:39:33,251 - retrieval - INFO - Sliding window search: Found 5 results
   Condition: generic medical query
   Emergency keywords: medical|emergency
   Treatment keywords: treatment|management
   Source: generic_search
   Duration: 20.033s

Step 2: User confirmation process...
   Confirmation type: confirmation_needed

Step 3: Executing retrieval...
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.28it/s]
2025-07-31 06:39:33,404 - retrieval - INFO - Search results: Emergency=5, Treatment=5
2025-07-31 06:39:33,404 - retrieval - INFO - Deduplication: Processing 10 results using text matching
2025-07-31 06:39:33,404 - retrieval - INFO - Deduplication summary: 10 → 9 results (removed 1)
   Search query: 'medical|emergency treatment|management'
   Total results: 9
   Emergency results: 5
   Treatment results: 4
   Duration: 0.143s

   Top 3 results:
      1. Type: treatment, Distance: 0.7708
         Text preview: and nurse practitioners who may or may not be formally trained in emergency medicine. they offer pri...
      2. Type: emergency, Distance: 0.8056
         Text preview: organization of emergency medical assistance emergency medical assistance is the first aid that is g...
      3. Type: emergency, Distance: 0.8321
         Text preview: ion to the emergency room ; - urgent situation that requires advanced medical care before transporta...

✅ Test test_002 completed successfully (20.176s)

🔍 test_003: Neurological emergency query
Query: 'sudden neurological symptoms suggesting stroke'
------------------------------------------------------------
Step 1: Extracting medical condition and keywords...
2025-07-31 06:39:33,404 - llm_clients - INFO - Calling Medical LLM with query: sudden neurological symptoms suggesting stroke
2025-07-31 06:39:49,400 - llm_clients - INFO - Raw LLM Response: Cerebrovascular Accident (CVA), or Acute Ischemic Stroke

(As a medical assistant, I'm limited to providing condition labels, not advice. In this case, the description given—sudden neurological symptoms suggestive of stroke—points to an acute ischemic stroke, also known as cerebrovascular accident (CVA). This diagnosis implies a blockage of blood flow to the brain, resulting in sudden neurological deficits.)

**Please consult a qualified healthcare professional for evaluation and management.
2025-07-31 06:39:49,403 - llm_clients - INFO - Query Latency: 15.9960 seconds
2025-07-31 06:39:49,404 - llm_clients - INFO - Extracted Condition: Cerebrovascular Accident (CVA), or Acute Ischemic Stroke
2025-07-31 06:39:49,405 - user_prompt - INFO - Starting semantic search fallback for query: 'sudden neurological symptoms suggesting stroke'
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  8.53it/s]
2025-07-31 06:39:50,205 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 06:39:50,214 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 13.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.19it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.05it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.50it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.67it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.14it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.27it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.62it/s]
2025-07-31 06:39:50,417 - user_prompt - INFO - Inferred condition: None
2025-07-31 06:39:50,418 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 06:39:50,418 - user_prompt - INFO - No suitable condition found in semantic search
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.16it/s]
2025-07-31 06:39:50,938 - retrieval - INFO - Sliding window search: Found 5 results
   Condition: generic medical query
   Emergency keywords: medical|emergency
   Treatment keywords: treatment|management
   Source: generic_search
   Duration: 17.544s

Step 2: User confirmation process...
   Confirmation type: confirmation_needed

Step 3: Executing retrieval...
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 46.02it/s]
2025-07-31 06:39:50,972 - retrieval - INFO - Search results: Emergency=5, Treatment=5
2025-07-31 06:39:50,972 - retrieval - INFO - Deduplication: Processing 10 results using text matching
2025-07-31 06:39:50,972 - retrieval - INFO - Deduplication summary: 10 → 9 results (removed 1)
   Search query: 'medical|emergency treatment|management'
   Total results: 9
   Emergency results: 5
   Treatment results: 4
   Duration: 0.025s

   Top 3 results:
      1. Type: treatment, Distance: 0.7708
         Text preview: and nurse practitioners who may or may not be formally trained in emergency medicine. they offer pri...
      2. Type: emergency, Distance: 0.8056
         Text preview: organization of emergency medical assistance emergency medical assistance is the first aid that is g...
      3. Type: emergency, Distance: 0.8321
         Text preview: ion to the emergency room ; - urgent situation that requires advanced medical care before transporta...

✅ Test test_003 completed successfully (17.569s)

🔍 test_004: Protocol-specific stroke query
Query: 'acute stroke management protocol'
------------------------------------------------------------
Step 1: Extracting medical condition and keywords...
2025-07-31 06:39:50,973 - user_prompt - INFO - Matched predefined condition: acute stroke
   Condition: acute stroke
   Emergency keywords: stroke|neurological deficit|sudden weakness
   Treatment keywords: tPA|thrombolysis|stroke unit care
   Source: predefined_mapping
   Duration: 0.000s

Step 2: User confirmation process...
   Confirmation type: confirmation_needed

Step 3: Executing retrieval...
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.92it/s]
2025-07-31 06:39:51,110 - retrieval - INFO - Search results: Emergency=5, Treatment=5
2025-07-31 06:39:51,110 - retrieval - INFO - Deduplication: Processing 10 results using text matching
2025-07-31 06:39:51,110 - retrieval - INFO - Deduplication summary: 10 → 9 results (removed 1)
   Search query: 'stroke|neurological deficit|sudden weakness tPA|thrombolysis|stroke unit care'
   Total results: 9
   Emergency results: 5
   Treatment results: 4
   Duration: 0.137s

   Top 3 results:
      1. Type: treatment, Distance: 0.7389
         Text preview: hree hours of the onset of stroke. early treatment ( within 90 minutes ) may be more likely to resul...
      2. Type: treatment, Distance: 0.7401
         Text preview: hree hours of the onset of stroke. early treatment ( within 90 minutes ) may be more likely to resul...
      3. Type: emergency, Distance: 0.7685
         Text preview: mproved outcomes for a broad spectrum of carefully selected clients who can be treated within three ...

✅ Test test_004 completed successfully (0.137s)

🔍 test_005: General symptom requiring LLM analysis
Query: 'patient presenting with acute abdominal pain'
------------------------------------------------------------
Step 1: Extracting medical condition and keywords...
2025-07-31 06:39:51,110 - llm_clients - INFO - Calling Medical LLM with query: patient presenting with acute abdominal pain
2025-07-31 06:40:00,096 - llm_clients - INFO - Raw LLM Response: Acute Appendicitis

(As a medical assistant, I identify the most representative condition here as acute appendicitis, given the patient's symptom of acute abdominal pain, particularly if localized in the right lower quadrant and accompanied by other typical signs like nausea, vomiting, fever, or guarding. However, this is not a definitive diagnosis and should be confirmed by a physician through clinical evaluation, imaging, or surgical findings.)
2025-07-31 06:40:00,096 - llm_clients - INFO - Query Latency: 8.9862 seconds
2025-07-31 06:40:00,097 - llm_clients - INFO - Extracted Condition: Acute Appendicitis
2025-07-31 06:40:00,097 - user_prompt - INFO - Starting semantic search fallback for query: 'patient presenting with acute abdominal pain'
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.49it/s]
2025-07-31 06:40:00,664 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 06:40:00,673 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.57it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 50.55it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.08it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 62.74it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.91it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.25it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.38it/s]
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 64.09it/s]
2025-07-31 06:40:00,876 - user_prompt - INFO - Inferred condition: None
2025-07-31 06:40:00,876 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 06:40:00,876 - user_prompt - INFO - No suitable condition found in semantic search
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.32it/s]
2025-07-31 06:40:01,399 - retrieval - INFO - Sliding window search: Found 5 results
   Condition: generic medical query
   Emergency keywords: medical|emergency
   Treatment keywords: treatment|management
   Source: generic_search
   Duration: 10.298s

Step 2: User confirmation process...
   Confirmation type: confirmation_needed

Step 3: Executing retrieval...
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.41it/s]
2025-07-31 06:40:01,432 - retrieval - INFO - Search results: Emergency=5, Treatment=5
2025-07-31 06:40:01,432 - retrieval - INFO - Deduplication: Processing 10 results using text matching
2025-07-31 06:40:01,432 - retrieval - INFO - Deduplication summary: 10 → 9 results (removed 1)
   Search query: 'medical|emergency treatment|management'
   Total results: 9
   Emergency results: 5
   Treatment results: 4
   Duration: 0.025s

   Top 3 results:
      1. Type: treatment, Distance: 0.7708
         Text preview: and nurse practitioners who may or may not be formally trained in emergency medicine. they offer pri...
      2. Type: emergency, Distance: 0.8056
         Text preview: organization of emergency medical assistance emergency medical assistance is the first aid that is g...
      3. Type: emergency, Distance: 0.8321
         Text preview: ion to the emergency room ; - urgent situation that requires advanced medical care before transporta...

✅ Test test_005 completed successfully (10.322s)

🔍 test_006: Specific condition with treatment focus
Query: 'pulmonary embolism treatment guidelines'
------------------------------------------------------------
Step 1: Extracting medical condition and keywords...
2025-07-31 06:40:01,432 - user_prompt - INFO - Matched predefined condition: pulmonary embolism
   Condition: pulmonary embolism
   Emergency keywords: chest pain|shortness of breath|sudden dyspnea
   Treatment keywords: anticoagulation|heparin|embolectomy
   Source: predefined_mapping
   Duration: 0.000s

Step 2: User confirmation process...
   Confirmation type: confirmation_needed

Step 3: Executing retrieval...
Batches: 100%|███████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 16.27it/s]
2025-07-31 06:40:01,562 - retrieval - INFO - Search results: Emergency=5, Treatment=5
2025-07-31 06:40:01,562 - retrieval - INFO - Deduplication: Processing 10 results using text matching
2025-07-31 06:40:01,562 - retrieval - INFO - Deduplication summary: 10 → 8 results (removed 2)
   Search query: 'chest pain|shortness of breath|sudden dyspnea anticoagulation|heparin|embolectomy'
   Total results: 8
   Emergency results: 5
   Treatment results: 3
   Duration: 0.130s

   Top 3 results:
      1. Type: emergency, Distance: 0.8949
         Text preview: algesics ( e. g. morphine, pethidine ) facilities for defibrillation ( df ) aspirin / anticoagulant ...
      2. Type: treatment, Distance: 0.9196
         Text preview: y proximal deep vein thrombosis leading to acute pulmonary embolism # # common causes of peripheral ...
      3. Type: emergency, Distance: 0.9216
         Text preview: ed or discolored skin in the affected leg - visible surface veins dvt usually involves the deep vein...

✅ Test test_006 completed successfully (0.130s)

================================================================================
📊 COMPREHENSIVE TEST REPORT
================================================================================
🕐 Execution Summary:
   Start time: 2025-07-31 06:38:22
   End time: 2025-07-31 06:40:01
   Total duration: 98.954s
   Average per test: 16.492s

📈 Test Results:
   Total tests: 6
   Successful: 6 ✅
   Failed: 0 ❌
   Success rate: 100.0%

✅ Successful Tests Analysis:
   Condition extraction sources:
     - predefined_mapping: 3 tests
     - generic_search: 3 tests
   Performance metrics:
     - Avg condition extraction: 14.935s
     - Avg retrieval time: 0.206s

   📋 test_001: Classic acute myocardial infarction query
      Query: 'how to treat acute MI?'
      Condition: acute myocardial infarction
      Source: predefined_mapping
      Results: 9 total (4 emergency, 5 treatment)
      Duration: 42.511s

   📋 test_002: Symptoms-based query requiring LLM analysis
      Query: 'patient with severe chest pain and shortness of breath'
      Condition: generic medical query
      Source: generic_search
      Results: 9 total (5 emergency, 4 treatment)
      Duration: 20.176s

   📋 test_003: Neurological emergency query
      Query: 'sudden neurological symptoms suggesting stroke'
      Condition: generic medical query
      Source: generic_search
      Results: 9 total (5 emergency, 4 treatment)
      Duration: 17.569s

   📋 test_004: Protocol-specific stroke query
      Query: 'acute stroke management protocol'
      Condition: acute stroke
      Source: predefined_mapping
      Results: 9 total (5 emergency, 4 treatment)
      Duration: 0.137s

   📋 test_005: General symptom requiring LLM analysis
      Query: 'patient presenting with acute abdominal pain'
      Condition: generic medical query
      Source: generic_search
      Results: 9 total (5 emergency, 4 treatment)
      Duration: 10.322s

   📋 test_006: Specific condition with treatment focus
      Query: 'pulmonary embolism treatment guidelines'
      Condition: pulmonary embolism
      Source: predefined_mapping
      Results: 8 total (5 emergency, 3 treatment)
      Duration: 0.130s