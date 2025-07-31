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


      Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.37it/s]
2025-07-31 09:50:06,551 - retrieval - INFO - Search results: Emergency=5, Treatment=5
2025-07-31 09:50:06,551 - retrieval - INFO - Deduplication: Processing 10 results using text matching
2025-07-31 09:50:06,551 - retrieval - INFO - Deduplication summary: 10 → 9 results (removed 1)
      Search Query: 'medical|emergency treatment|management'
      Results: 9 total (5 emergency, 4 treatment)
      Time: 0.146s
   🧠 Step 4: Medical advice generation...
2025-07-31 09:50:06,552 - generation - INFO - Generating medical advice for query: 'Patient presenting with severe chest pain and shor...'
2025-07-31 09:50:06,552 - generation - INFO - Classified chunks: Emergency=5, Treatment=4
2025-07-31 09:50:06,552 - generation - INFO - Generating prompt with intention: diagnosis
2025-07-31 09:50:06,552 - generation - INFO - Selected chunks by intention 'diagnosis': 6 total
2025-07-31 09:50:06,552 - generation - INFO - Generated prompt with 6 chunks, 7931 chars
2025-07-31 09:50:06,552 - generation - INFO - Calling Med42-70B for medical advice generation
2025-07-31 09:50:06,552 - llm_clients - INFO - Calling Medical LLM with query: You are an experienced attending physician providing guidance to a junior clinician in an emergency setting. A colleague is asking for your expert medical opinion.

Clinical Question:
Patient presenting with severe chest pain and shortness of breath

Relevant Medical Guidelines:
[Guideline 1] (Source: Emergency, Relevance: 0.194)
organization of emergency medical assistance emergency medical assistance is the first aid that is given to victims of accidents ( casualties ) or of the acute effects of diseases. the basis of emergency medical assistance is the " chain of rescue " : this system is based on the collaboration of different actors. the most advanced cares can only be performed by physicians and surgeons with the appropriate environment ( medical imaging, biochemistry analysis laboratory, emergency room, operating room ), but the acute event often happens outside the hospital ( prehospital cares ) : at home, in the street, at work, in a public building … the other actors involved are : - the first witness of the event, who will call for help and possibly provide first aid ( see also emergency action principles ) ; - the medical regulation service that will receive the call and provide advice, and decide the action required ; - the general practitioner that will come and see the person, in case the situation is not too urgent and the person is in a safe environment ; - the ambulance that will take th

[Guideline 2] (Source: Emergency, Relevance: 0.168)
ion to the emergency room ; - urgent situation that requires advanced medical care before transportation. these categories are not so clearly separated, and depend not only on the medical condition of the casualty, but also on the organization of the health system and on the social impact. for example, a deceased person is not a medical emergency ( there is no care to perform ), but in some societies, it is a social emergency ( the people would not understand nothing is being done ) especially in the case of a child ' s death ; and it is not obvious to decide whether the person is dead or can be saved through advanced care ( e. g. case of cardiac arrest and of cardiopulmonary resuscitation ). in general, pain is usually not a life - threatening situation, but the situation is often unbearable from the point of view of the casualty. two things must thus be considered : - the perceived emergency, and - the " real " emergency. the distinction requires assessment ; assessment by the witness who calls ( importance of first aid education ) and remote assessment by the dispatcher ( medical regulation ). the confidence in the emergency assistance system warrants the efficiency of the system ; otherwise, the probable reaction would be to drive the casualty to the closest hospital, making the flow o

[Guideline 3] (Source: Emergency, Relevance: 0.129)
een by a physician more rapidly than those with less severe symptoms or injuries. after initial assessment and treatment, patients are either admitted to the hospital, stabilized and transferred to another hospital for various reasons, or discharged. the staff in emergency departments not only includes doctors, but physician assistants ( pas ) and nurses with specialized training in emergency medicine and in house emergency medical technicians, respiratory therapists, radiology technicians, healthcare assistants ( hcas ), volunteers, and other support staff who all work as a team to treat emergency patients and provide support to anxious family members. the emergency departments of most hospitals operate around the clock, although staffing levels are usually much lower at night. since a diagnosis must be made by an attending physician, the patient is initially assigned a chief complaint rather than a diagnosis. this is usually a symptom : headache, nausea, loss of consciousness. the chief complaint remains a primary fact until the attending physician makes a diagnosis. # department layout a typical emergency department has several different areas, each specialized for patients with particular severities or types of illness. in the triage area, patients are seen by a triage nurse who completes a preliminary evaluation, before transferring care to another area of the ed or a different department in the hospital. patients with l

[Guideline 4] (Source: Emergency, Relevance: 0.124)
skills, and should be left to the professionals of the emergency medical and fire service. # clinical response within hospital settings, an adequate staff is generally present to deal with the average emergency situation. emergency medicine physicians have training to deal with most medical emergencies, and maintain cpr and acls certifications. in disasters or complex emergencies, most hospitals have protocols to summon on - site and off - site staff rapidly. both emergency room and inpatient medical emergencies follow the basic protocol of advanced cardiac life support. irrespective of the nature of the emergency, adequate blood pressure and oxygenation are required before the cause of the emergency can be eliminated. possible exceptions include the clamping of arteries in severe hemorrhage.

[Guideline 5] (Source: Treatment, Relevance: 0.229)
and nurse practitioners who may or may not be formally trained in emergency medicine. they offer primary care treatment to patients who desire or require immediate care, but who do not reach the acuity that requires care in an emergency department. emergency medicine encompasses a large amount of general medicine but involves virtually all fields of medicine including the surgical sub - specialties. emergency physicians are tasked with seeing a large number of patients, treating their illnesses and arranging for disposition - either admitting them to the hospital or releasing them after treatment as necessary. the emergency physician requires a broad field of knowledge and advanced procedural skills often including surgical procedures, trauma resuscitation, advanced cardiac life support and advanced airway management. emergency physicians ideally have the skills of many specialists - the ability to manage a difficult airway ( anesthesia ), suture a complex laceration ( plastic surgery ), reduce ( set ) a fractured bone or dislocated joint ( orthopedic surgery ), treat a heart attack ( internist ), work - up a pregnant patient with vaginal bleeding ( obstetrics and gynecology ), and stop a bad nosebleed ( ent ). # definition " emergency medicine is a medical specialty - - a field of practice based on the knowledge and skills required for the prevention, diagnosis and management of acute and urgent aspects of illness and injury affecting patients of all age gro

[Guideline 6] (Source: Treatment, Relevance: 0.114)
an attending physician, the patient is initially assigned a chief complaint rather than a diagnosis. this is usually a symptom : headache, nausea, loss of consciousness. the chief complaint remains a primary fact until the attending physician makes a diagnosis. # department layout a typical emergency department has several different areas, each specialized for patients with particular severities or types of illness. in the triage area, patients are seen by a triage nurse who completes a preliminary evaluation, before transferring care to another area of the ed or a different department in the hospital. patients with life or limb - threatening conditions may bypass triage and to be seen directly by a physician. the resuscitation area is a key area of an emergency department. it usually contains several individual resuscitation bays, usually with one specially equipped for paediatric resuscitation. each bay is equipped with a defibrillator, airway equipment, oxygen, intravenous lines and fluids, and emergency drugs. resuscitation areas also have ecg machines, and often limited x - ray facilities to perform chest and pelvis films. other equipment may include non - invasive ventilation ( niv ) and portable ultrasound devices. the majors, or general medical, area is for stable patients who still need to be confined to bed ( note that a " bed " in the ed context is almost always a gurney or trolley rather than a full hospital bed ). this area is ofte

Instructions:
Focus on differential diagnosis, diagnostic criteria, and assessment approaches.

Please provide a clear, actionable response that:
1. Addresses the specific clinical question asked
2. References relevant evidence from the provided guidelines
3. Offers practical, step-by-step guidance when appropriate
4. Maintains appropriate medical caution and emphasizes the need for clinical judgment

Your response should be concise but comprehensive, suitable for immediate clinical application.
2025-07-31 09:50:44,403 - llm_clients - INFO - Raw LLM Response: For a patient presenting with severe chest pain and shortness of breath in an emergency setting, our primary focus is on identifying potentially life-threatening conditions.

Based on the given guidelines, particularly Guideline 5 (Treatment, Relevance: 0.229) and Guideline 4 (Emergency, Relevance: 0.124), which emphasize the broad knowledge base and advanced procedural skills required in emergency medicine, we should consider the following differential diagnoses:

1. Acute Coronary Syndrome (ACS): Chest pain, especially if described as squeezing, pressure, or heaviness, and accompanied by shortness of breath, is highly suggestive of ACS. We should assess for electrocardiogram (ECG) changes indicative of ischemia or infarction and consider troponin levels for confirmation.
2. Pulmonary Embolism (PE): Sudden onset of severe chest pain and dyspnea could indicate PE. We should evaluate for risk factors, perform a D-dimer assay, and consider computed tomography pulmonary angiography (CTPA) for confirmation if indicated.
3. Cardiac Tamponade: Rapidly worsening dyspnea and chest pain could suggest cardiac tamponade. We should assess for signs of shock, evaluate jugular venous distension, and consider echocardiography to confirm.
4. Aortic Dissection: Severe, tearing chest pain, especially if radiating to the back, could indicate aortic dissection. We should evaluate for hypertension, widened mediastinum on chest X-ray, and consider computed tomography angiography (CTA) for confirmation.

Practical, step-by-step guidance:
1. Obtain a detailed history, focusing on pain characteristics, onset, duration, and radiation.
2. Perform a thorough physical examination, including vital signs, cardiac and lung auscultation, and assessment for jugular venous distension or pedal edema.
3. Order an ECG immediately to evaluate for signs of ischemia or infarction.
4. Obtain blood for cardiac biomarkers (troponin) and D-dimer assay.
5. Consider CTPA or CTA if PE or aortic dissection is suspected.
6. Perform bedside echocardiography if cardiac tamponade is suspected.
7. Administer oxygen and initiate pain management with nitroglycerin or morphine, as appropriate, while awaiting further diagnostic results.
8. Consult cardiology, pulmonary, or vascular surgery services as indicated based on diagnostic
2025-07-31 09:50:44,404 - llm_clients - INFO - Query Latency: 37.8510 seconds
2025-07-31 09:50:44,404 - llm_clients - INFO - Extracted Condition: pulmonary embolism
2025-07-31 09:50:44,404 - generation - INFO - Medical advice generated successfully in 37.852s
      Intention: diagnosis
      Confidence: 0.90
      Advice Length: 18 chars
      Chunks Used: 9
      Time: 37.852s

   ✅ Pipeline completed successfully!
   📊 Total Time: 50.365s
   🩺 Medical Advice Preview:
      pulmonary embolism...

🧪 e2e_003: Neurological emergency with protocol focus
Query: 'What are the emergency protocols for acute stroke management?'
Expected: treatment intention
----------------------------------------------------------------------
   🎯 Step 1: Condition extraction and validation...
2025-07-31 09:50:44,404 - user_prompt - INFO - Matched predefined condition: acute stroke
      Condition: acute stroke
      Keywords: Emergency='stroke|neurological deficit|sudden weakness', Treatment='tPA|thrombolysis|stroke unit care'
      Time: 0.000s
   🤝 Step 2: User confirmation (simulated as 'yes')...
   🔍 Step 3: Medical guideline retrieval...
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  1.46it/s]
2025-07-31 09:50:45,207 - retrieval - INFO - Search results: Emergency=5, Treatment=5
2025-07-31 09:50:45,208 - retrieval - INFO - Deduplication: Processing 10 results using text matching
2025-07-31 09:50:45,208 - retrieval - INFO - Deduplication summary: 10 → 9 results (removed 1)
      Search Query: 'stroke|neurological deficit|sudden weakness tPA|thrombolysis|stroke unit care'
      Results: 9 total (5 emergency, 4 treatment)
      Time: 0.804s
   🧠 Step 4: Medical advice generation...
2025-07-31 09:50:45,208 - generation - INFO - Generating medical advice for query: 'What are the emergency protocols for acute stroke ...'
2025-07-31 09:50:45,208 - generation - INFO - Classified chunks: Emergency=5, Treatment=4
2025-07-31 09:50:45,208 - generation - INFO - Generating prompt with intention: treatment
2025-07-31 09:50:45,208 - generation - INFO - Selected chunks by intention 'treatment': 6 total
2025-07-31 09:50:45,209 - generation - INFO - Generated prompt with 6 chunks, 8335 chars
2025-07-31 09:50:45,209 - generation - INFO - Calling Med42-70B for medical advice generation
2025-07-31 09:50:45,209 - llm_clients - INFO - Calling Medical LLM with query: You are an experienced attending physician providing guidance to a junior clinician in an emergency setting. A colleague is asking for your expert medical opinion.

Clinical Question:
What are the emergency protocols for acute stroke management?

Relevant Medical Guidelines:
[Guideline 1] (Source: Emergency, Relevance: 0.232)
mproved outcomes for a broad spectrum of carefully selected clients who can be treated within three hours of the onset of stroke. early treatment ( within 90 minutes ) may be more likely to result in positive outcomes at three months post stroke, however later treatment ( 90 - 180 minutes ) is also beneficial ( adams et al., 2003 ). it is important to note that there are non - cerebrovascular conditions that may present with symptoms similar to stroke - a " stroke mimic ". some of the conditions that mimic stroke include : seizures ; systemic infection ; brain tumor ; toxic - metabolic ; positional vertigo ; cardiac ; syncope ; and trauma ( libman, wirkowski, alvir & rao, 1995 ). # level of evidence = iv nursing best practice guideline # discussion of evidence performing a neurological assessment at initial presentation and monitoring throughout the continuum of care provides a standardized method to detect neurological change. although many factors influence the rate and degree of recovery after stroke, the single most important variable is the severity of the initial neurological deficit ( heinemann, 1989 ). monitoring of neurological status helps to identify emerging neurological deterioration that could lead to early

[Guideline 2] (Source: Emergency, Relevance: 0.187)
ortive care ( physiotherapy and occupational therapy ) and secondary prevention with antiplatelet drugs ( aspirin and often dipyridamole ), blood pressure control, statins and anticoagulation ( in selected patients ). # treatment of ischemic stroke an ischemic stroke is due to a thrombus ( blood clot ) occluding a cerebral artery, a patient is given antiplatelet medication ( aspirin, clopidogrel, dipyridamole ), or anticoagulant medication ( warfarin ), dependent on the cause, when this type of stroke has been found. hemorrhagic stroke must be ruled out with medical imaging, since this therapy would be harmful to patients with that type of stroke. whether thrombolysis is performed or not, the following investigations are required : - stroke symptoms are documented, often using scoring systems such as the national institutes of health stroke scale, the cincinnati stroke scale, and the los angeles prehospital stroke screen. the cincinnati stroke scale is used by emergency medical technicians ( emts ) to determine whether a patient needs trans

[Guideline 3] (Source: Treatment, Relevance: 0.261)
hree hours of the onset of stroke. early treatment ( within 90 minutes ) may be more likely to result in positive outcomes at three months post stroke, however later treatment ( 90 - 180 minutes ) is also beneficial ( adams et al., 2003 ). it is important to note that there are non - cerebrovascular conditions that may present with symptoms similar to stroke - a " stroke mimic ". some of the conditions that mimic stroke include : seizures ; systemic infection ; brain tumor ; toxic - metabolic ; positional vertigo ; cardiac ; syncope ; and trauma ( libman, wirkowski, alvir & rao, 1995 ). # level of evidence = iv nursing best practice guideline # discussion of evidence performing a neurological assessment at initial presentation and monitoring throughout the continuum of care provides a standardized method to detect neurological change. although many factors influence the rate and degree of recovery after stroke, the single most important variable is the severity of the initial neurological deficit ( heinemann, 1989 ). monitoring of neurological status helps to identify emerging neurological deterioration that could lead to early intervention ( hachinski & norris, 1980 ). prompt early assessment, both globally and a neurological assessment, can influence client outcomes. included in the assessment should be vital signs and a baseline blood glucose level. the agency for health care policy and research post - stroke rehabilitation panel ( ahcpr, 1995 ) reco

[Guideline 4] (Source: Treatment, Relevance: 0.260)
hree hours of the onset of stroke. early treatment ( within 90 minutes ) may be more likely to result in positive outcomes at three months post stroke, however later treatment ( 90 - 180 minutes ) is also beneficial ( adams et al., 2003 ). it is important to note that there are non - cerebrovascular conditions that may present with symptoms similar to stroke - a " stroke mimic ". some of the conditions that mimic stroke include : seizures ; systemic infection ; brain tumor ; toxic - metabolic ; positional vertigo ; cardiac ; syncope ; and trauma ( libman, wirkowski, alvir & rao, 1995 ). # level of evidence = iv nursing best practice guideline # discussion of evidence performing a neurological assessment at initial presentation and monitoring throughout the continuum of care provides a standardized method to detect neurological change. although many factors influence the rate and degree of recovery after stroke, the single most important variable is the severity of the initial neurological deficit ( heinemann, 1989 ). monitoring of neurological status helps to identify emerging neurological deterioration that could lead to early intervention ( hachinski & norris, 1980 ). prompt early assessment, both globally and a neurological assessment, can influence client outcomes. included in the assessment should be vital signs and a baseline blood glucose level. the agency for health care policy and research post - stroke rehabilitation panel ( ahcpr, 1995 ) r

[Guideline 5] (Source: Treatment, Relevance: 0.223)
stroke ischemic treatment # overview treatment of stroke is occasionally with thrombolysis ( " clot buster " ), but usually with supportive care ( physiotherapy and occupational therapy ) and secondary prevention with antiplatelet drugs ( aspirin and often dipyridamole ), blood pressure control, statins and anticoagulation ( in selected patients ). # treatment of ischemic stroke an ischemic stroke is due to a thrombus ( blood clot ) occluding a cerebral artery, a patient is given antiplatelet medication ( aspirin, clopidogrel, dipyridamole ), or anticoagulant medication ( warfarin ), dependent on the cause, when this type of stroke has been found. hemorrhagic stroke must be ruled out with medical imaging, since this therapy would be harmful to patients with that type of stroke. whether thrombolysis is performed or not, the following investigations are required : - stroke symptoms are documented, often using scoring systems such as the national institutes of health stroke scale, the cincinnati stroke scale, and the los angeles prehospital stroke screen. the cincinnati stroke scale is used by emergency medical technicians ( emts ) to determine whether a patient needs transport to a stroke cent

[Guideline 6] (Source: Treatment, Relevance: 0.221)
ent for signs and symptoms of stroke as part of monitoring for possible stroke transformation. this should include screening tools such as fast ( face, arms, speech, time ) 15 and protocols for inhospital actions to be taken if signs and symptoms of stroke are identified. additional education and support may be required for hcp caring for patients with intracerebral hemorrhage ( ich ) and subarachnoid hemorrhage ( sah ). after patients receive hyperacute reperfusion treatment ( thrombolysis and / or evt ), care is optimally provided in an intensively monitored unit or critical care bed. where access to critical care beds becomes limited, this care could be provided in a ward bed with appropriate supports. broadly speaking, this would include measures for enhanced patient monitoring particularly within the first 24 h post - hyperacute treatment, education of the interdisciplinary team regarding all aspects of care for thrombolysis and evt patients, and clear communication between team members regarding patient clinical status. patients should be cared for in an area with high visibility from the hall and ideally with cardiac telemetry. # key messages - stroke patients should continue to be cared for in specialized acute stroke units where possible. 2. education and basic skills training may be required for nonstroke experts caring for stroke patients to ensure patient safety and optimizing recovery. 3. where access to critical care beds becomes limited, this care could be provided in a ward bed with appropriate supports. # stroke r

Instructions:
Focus on providing specific treatment protocols, management steps, and therapeutic interventions.

Please provide a clear, actionable response that:
1. Addresses the specific clinical question asked
2. References relevant evidence from the provided guidelines
3. Offers practical, step-by-step guidance when appropriate
4. Maintains appropriate medical caution and emphasizes the need for clinical judgment

Your response should be concise but comprehensive, suitable for immediate clinical application.
2025-07-31 09:50:45,488 - llm_clients - ERROR - Medical LLM query error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee5-36e27354785df215721995f7;6c789243-f499-4fb4-99aa-632b46b748d0)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
2025-07-31 09:50:45,488 - llm_clients - ERROR - Error Type: HfHubHTTPError
2025-07-31 09:50:45,489 - llm_clients - ERROR - Detailed Error: HfHubHTTPError('402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee5-36e27354785df215721995f7;6c789243-f499-4fb4-99aa-632b46b748d0)\n\nYou have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.')
2025-07-31 09:50:45,489 - llm_clients - ERROR - Query Latency (on error): 0.2794 seconds
2025-07-31 09:50:45,489 - llm_clients - ERROR - Query that caused error: You are an experienced attending physician providing guidance to a junior clinician in an emergency setting. A colleague is asking for your expert medical opinion.

Clinical Question:
What are the emergency protocols for acute stroke management?

Relevant Medical Guidelines:
[Guideline 1] (Source: Emergency, Relevance: 0.232)
mproved outcomes for a broad spectrum of carefully selected clients who can be treated within three hours of the onset of stroke. early treatment ( within 90 minutes ) may be more likely to result in positive outcomes at three months post stroke, however later treatment ( 90 - 180 minutes ) is also beneficial ( adams et al., 2003 ). it is important to note that there are non - cerebrovascular conditions that may present with symptoms similar to stroke - a " stroke mimic ". some of the conditions that mimic stroke include : seizures ; systemic infection ; brain tumor ; toxic - metabolic ; positional vertigo ; cardiac ; syncope ; and trauma ( libman, wirkowski, alvir & rao, 1995 ). # level of evidence = iv nursing best practice guideline # discussion of evidence performing a neurological assessment at initial presentation and monitoring throughout the continuum of care provides a standardized method to detect neurological change. although many factors influence the rate and degree of recovery after stroke, the single most important variable is the severity of the initial neurological deficit ( heinemann, 1989 ). monitoring of neurological status helps to identify emerging neurological deterioration that could lead to early

[Guideline 2] (Source: Emergency, Relevance: 0.187)
ortive care ( physiotherapy and occupational therapy ) and secondary prevention with antiplatelet drugs ( aspirin and often dipyridamole ), blood pressure control, statins and anticoagulation ( in selected patients ). # treatment of ischemic stroke an ischemic stroke is due to a thrombus ( blood clot ) occluding a cerebral artery, a patient is given antiplatelet medication ( aspirin, clopidogrel, dipyridamole ), or anticoagulant medication ( warfarin ), dependent on the cause, when this type of stroke has been found. hemorrhagic stroke must be ruled out with medical imaging, since this therapy would be harmful to patients with that type of stroke. whether thrombolysis is performed or not, the following investigations are required : - stroke symptoms are documented, often using scoring systems such as the national institutes of health stroke scale, the cincinnati stroke scale, and the los angeles prehospital stroke screen. the cincinnati stroke scale is used by emergency medical technicians ( emts ) to determine whether a patient needs trans

[Guideline 3] (Source: Treatment, Relevance: 0.261)
hree hours of the onset of stroke. early treatment ( within 90 minutes ) may be more likely to result in positive outcomes at three months post stroke, however later treatment ( 90 - 180 minutes ) is also beneficial ( adams et al., 2003 ). it is important to note that there are non - cerebrovascular conditions that may present with symptoms similar to stroke - a " stroke mimic ". some of the conditions that mimic stroke include : seizures ; systemic infection ; brain tumor ; toxic - metabolic ; positional vertigo ; cardiac ; syncope ; and trauma ( libman, wirkowski, alvir & rao, 1995 ). # level of evidence = iv nursing best practice guideline # discussion of evidence performing a neurological assessment at initial presentation and monitoring throughout the continuum of care provides a standardized method to detect neurological change. although many factors influence the rate and degree of recovery after stroke, the single most important variable is the severity of the initial neurological deficit ( heinemann, 1989 ). monitoring of neurological status helps to identify emerging neurological deterioration that could lead to early intervention ( hachinski & norris, 1980 ). prompt early assessment, both globally and a neurological assessment, can influence client outcomes. included in the assessment should be vital signs and a baseline blood glucose level. the agency for health care policy and research post - stroke rehabilitation panel ( ahcpr, 1995 ) reco

[Guideline 4] (Source: Treatment, Relevance: 0.260)
hree hours of the onset of stroke. early treatment ( within 90 minutes ) may be more likely to result in positive outcomes at three months post stroke, however later treatment ( 90 - 180 minutes ) is also beneficial ( adams et al., 2003 ). it is important to note that there are non - cerebrovascular conditions that may present with symptoms similar to stroke - a " stroke mimic ". some of the conditions that mimic stroke include : seizures ; systemic infection ; brain tumor ; toxic - metabolic ; positional vertigo ; cardiac ; syncope ; and trauma ( libman, wirkowski, alvir & rao, 1995 ). # level of evidence = iv nursing best practice guideline # discussion of evidence performing a neurological assessment at initial presentation and monitoring throughout the continuum of care provides a standardized method to detect neurological change. although many factors influence the rate and degree of recovery after stroke, the single most important variable is the severity of the initial neurological deficit ( heinemann, 1989 ). monitoring of neurological status helps to identify emerging neurological deterioration that could lead to early intervention ( hachinski & norris, 1980 ). prompt early assessment, both globally and a neurological assessment, can influence client outcomes. included in the assessment should be vital signs and a baseline blood glucose level. the agency for health care policy and research post - stroke rehabilitation panel ( ahcpr, 1995 ) r

[Guideline 5] (Source: Treatment, Relevance: 0.223)
stroke ischemic treatment # overview treatment of stroke is occasionally with thrombolysis ( " clot buster " ), but usually with supportive care ( physiotherapy and occupational therapy ) and secondary prevention with antiplatelet drugs ( aspirin and often dipyridamole ), blood pressure control, statins and anticoagulation ( in selected patients ). # treatment of ischemic stroke an ischemic stroke is due to a thrombus ( blood clot ) occluding a cerebral artery, a patient is given antiplatelet medication ( aspirin, clopidogrel, dipyridamole ), or anticoagulant medication ( warfarin ), dependent on the cause, when this type of stroke has been found. hemorrhagic stroke must be ruled out with medical imaging, since this therapy would be harmful to patients with that type of stroke. whether thrombolysis is performed or not, the following investigations are required : - stroke symptoms are documented, often using scoring systems such as the national institutes of health stroke scale, the cincinnati stroke scale, and the los angeles prehospital stroke screen. the cincinnati stroke scale is used by emergency medical technicians ( emts ) to determine whether a patient needs transport to a stroke cent

[Guideline 6] (Source: Treatment, Relevance: 0.221)
ent for signs and symptoms of stroke as part of monitoring for possible stroke transformation. this should include screening tools such as fast ( face, arms, speech, time ) 15 and protocols for inhospital actions to be taken if signs and symptoms of stroke are identified. additional education and support may be required for hcp caring for patients with intracerebral hemorrhage ( ich ) and subarachnoid hemorrhage ( sah ). after patients receive hyperacute reperfusion treatment ( thrombolysis and / or evt ), care is optimally provided in an intensively monitored unit or critical care bed. where access to critical care beds becomes limited, this care could be provided in a ward bed with appropriate supports. broadly speaking, this would include measures for enhanced patient monitoring particularly within the first 24 h post - hyperacute treatment, education of the interdisciplinary team regarding all aspects of care for thrombolysis and evt patients, and clear communication between team members regarding patient clinical status. patients should be cared for in an area with high visibility from the hall and ideally with cardiac telemetry. # key messages - stroke patients should continue to be cared for in specialized acute stroke units where possible. 2. education and basic skills training may be required for nonstroke experts caring for stroke patients to ensure patient safety and optimizing recovery. 3. where access to critical care beds becomes limited, this care could be provided in a ward bed with appropriate supports. # stroke r

Instructions:
Focus on providing specific treatment protocols, management steps, and therapeutic interventions.

Please provide a clear, actionable response that:
1. Addresses the specific clinical question asked
2. References relevant evidence from the provided guidelines
3. Offers practical, step-by-step guidance when appropriate
4. Maintains appropriate medical caution and emphasizes the need for clinical judgment

Your response should be concise but comprehensive, suitable for immediate clinical application.
2025-07-31 09:50:45,489 - generation - ERROR - Med42-70B generation failed: Med42-70B generation error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee5-36e27354785df215721995f7;6c789243-f499-4fb4-99aa-632b46b748d0)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
2025-07-31 09:50:45,489 - generation - ERROR - Medical advice generation failed: Med42-70B generation error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee5-36e27354785df215721995f7;6c789243-f499-4fb4-99aa-632b46b748d0)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
      Intention: treatment
      Confidence: 0.00
      Advice Length: 164 chars
      Chunks Used: 0
      Time: 0.281s

   ✅ Pipeline completed successfully!
   📊 Total Time: 1.085s
   🩺 Medical Advice Preview:
      I apologize, but I encountered an error while processing your medical query. Please try rephrasing your question or contact technical support if the i...

🧪 e2e_004: Diagnostic reasoning query
Query: 'Differential diagnosis for sudden onset chest pain in young adult'
Expected: diagnosis intention
----------------------------------------------------------------------
   🎯 Step 1: Condition extraction and validation...
2025-07-31 09:50:45,490 - llm_clients - INFO - Calling Medical LLM with query: Differential diagnosis for sudden onset chest pain in young adult
2025-07-31 09:50:45,608 - llm_clients - ERROR - Medical LLM query error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee5-4f3715827fdc8cfb54613652;c3a6c20b-b542-4055-b18b-778f97a50c3b)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
2025-07-31 09:50:45,608 - llm_clients - ERROR - Error Type: HfHubHTTPError
2025-07-31 09:50:45,608 - llm_clients - ERROR - Detailed Error: HfHubHTTPError('402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee5-4f3715827fdc8cfb54613652;c3a6c20b-b542-4055-b18b-778f97a50c3b)\n\nYou have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.')
2025-07-31 09:50:45,608 - llm_clients - ERROR - Query Latency (on error): 0.1180 seconds
2025-07-31 09:50:45,608 - llm_clients - ERROR - Query that caused error: Differential diagnosis for sudden onset chest pain in young adult
2025-07-31 09:50:45,608 - user_prompt - INFO - Starting semantic search fallback for query: 'Differential diagnosis for sudden onset chest pain in young adult'
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 10.94it/s]
2025-07-31 09:50:46,613 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 09:50:46,619 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 26.73it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 41.98it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 39.92it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.33it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 44.23it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.58it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 54.78it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 59.50it/s]
2025-07-31 09:50:46,809 - user_prompt - INFO - Inferred condition: None
2025-07-31 09:50:46,809 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 09:50:46,809 - user_prompt - INFO - No suitable condition found in semantic search
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.94it/s]
2025-07-31 09:50:47,401 - retrieval - INFO - Sliding window search: Found 5 results
      Condition: generic medical query
      Keywords: Emergency='medical|emergency', Treatment='treatment|management'
      Time: 1.925s
   🤝 Step 2: User confirmation (simulated as 'yes')...
   🔍 Step 3: Medical guideline retrieval...
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 38.54it/s]
2025-07-31 09:50:47,445 - retrieval - INFO - Search results: Emergency=5, Treatment=5
2025-07-31 09:50:47,445 - retrieval - INFO - Deduplication: Processing 10 results using text matching
2025-07-31 09:50:47,445 - retrieval - INFO - Deduplication summary: 10 → 9 results (removed 1)
      Search Query: 'medical|emergency treatment|management'
      Results: 9 total (5 emergency, 4 treatment)
      Time: 0.030s
   🧠 Step 4: Medical advice generation...
2025-07-31 09:50:47,445 - generation - INFO - Generating medical advice for query: 'Differential diagnosis for sudden onset chest pain...'
2025-07-31 09:50:47,445 - generation - INFO - Classified chunks: Emergency=5, Treatment=4
2025-07-31 09:50:47,445 - generation - INFO - Generating prompt with intention: diagnosis
2025-07-31 09:50:47,445 - generation - INFO - Selected chunks by intention 'diagnosis': 6 total
2025-07-31 09:50:47,445 - generation - INFO - Generated prompt with 6 chunks, 7931 chars
2025-07-31 09:50:47,445 - generation - INFO - Calling Med42-70B for medical advice generation
2025-07-31 09:50:47,445 - llm_clients - INFO - Calling Medical LLM with query: You are an experienced attending physician providing guidance to a junior clinician in an emergency setting. A colleague is asking for your expert medical opinion.

Clinical Question:
Differential diagnosis for sudden onset chest pain in young adult

Relevant Medical Guidelines:
[Guideline 1] (Source: Emergency, Relevance: 0.194)
organization of emergency medical assistance emergency medical assistance is the first aid that is given to victims of accidents ( casualties ) or of the acute effects of diseases. the basis of emergency medical assistance is the " chain of rescue " : this system is based on the collaboration of different actors. the most advanced cares can only be performed by physicians and surgeons with the appropriate environment ( medical imaging, biochemistry analysis laboratory, emergency room, operating room ), but the acute event often happens outside the hospital ( prehospital cares ) : at home, in the street, at work, in a public building … the other actors involved are : - the first witness of the event, who will call for help and possibly provide first aid ( see also emergency action principles ) ; - the medical regulation service that will receive the call and provide advice, and decide the action required ; - the general practitioner that will come and see the person, in case the situation is not too urgent and the person is in a safe environment ; - the ambulance that will take th

[Guideline 2] (Source: Emergency, Relevance: 0.168)
ion to the emergency room ; - urgent situation that requires advanced medical care before transportation. these categories are not so clearly separated, and depend not only on the medical condition of the casualty, but also on the organization of the health system and on the social impact. for example, a deceased person is not a medical emergency ( there is no care to perform ), but in some societies, it is a social emergency ( the people would not understand nothing is being done ) especially in the case of a child ' s death ; and it is not obvious to decide whether the person is dead or can be saved through advanced care ( e. g. case of cardiac arrest and of cardiopulmonary resuscitation ). in general, pain is usually not a life - threatening situation, but the situation is often unbearable from the point of view of the casualty. two things must thus be considered : - the perceived emergency, and - the " real " emergency. the distinction requires assessment ; assessment by the witness who calls ( importance of first aid education ) and remote assessment by the dispatcher ( medical regulation ). the confidence in the emergency assistance system warrants the efficiency of the system ; otherwise, the probable reaction would be to drive the casualty to the closest hospital, making the flow o

[Guideline 3] (Source: Emergency, Relevance: 0.129)
een by a physician more rapidly than those with less severe symptoms or injuries. after initial assessment and treatment, patients are either admitted to the hospital, stabilized and transferred to another hospital for various reasons, or discharged. the staff in emergency departments not only includes doctors, but physician assistants ( pas ) and nurses with specialized training in emergency medicine and in house emergency medical technicians, respiratory therapists, radiology technicians, healthcare assistants ( hcas ), volunteers, and other support staff who all work as a team to treat emergency patients and provide support to anxious family members. the emergency departments of most hospitals operate around the clock, although staffing levels are usually much lower at night. since a diagnosis must be made by an attending physician, the patient is initially assigned a chief complaint rather than a diagnosis. this is usually a symptom : headache, nausea, loss of consciousness. the chief complaint remains a primary fact until the attending physician makes a diagnosis. # department layout a typical emergency department has several different areas, each specialized for patients with particular severities or types of illness. in the triage area, patients are seen by a triage nurse who completes a preliminary evaluation, before transferring care to another area of the ed or a different department in the hospital. patients with l

[Guideline 4] (Source: Emergency, Relevance: 0.124)
skills, and should be left to the professionals of the emergency medical and fire service. # clinical response within hospital settings, an adequate staff is generally present to deal with the average emergency situation. emergency medicine physicians have training to deal with most medical emergencies, and maintain cpr and acls certifications. in disasters or complex emergencies, most hospitals have protocols to summon on - site and off - site staff rapidly. both emergency room and inpatient medical emergencies follow the basic protocol of advanced cardiac life support. irrespective of the nature of the emergency, adequate blood pressure and oxygenation are required before the cause of the emergency can be eliminated. possible exceptions include the clamping of arteries in severe hemorrhage.

[Guideline 5] (Source: Treatment, Relevance: 0.229)
and nurse practitioners who may or may not be formally trained in emergency medicine. they offer primary care treatment to patients who desire or require immediate care, but who do not reach the acuity that requires care in an emergency department. emergency medicine encompasses a large amount of general medicine but involves virtually all fields of medicine including the surgical sub - specialties. emergency physicians are tasked with seeing a large number of patients, treating their illnesses and arranging for disposition - either admitting them to the hospital or releasing them after treatment as necessary. the emergency physician requires a broad field of knowledge and advanced procedural skills often including surgical procedures, trauma resuscitation, advanced cardiac life support and advanced airway management. emergency physicians ideally have the skills of many specialists - the ability to manage a difficult airway ( anesthesia ), suture a complex laceration ( plastic surgery ), reduce ( set ) a fractured bone or dislocated joint ( orthopedic surgery ), treat a heart attack ( internist ), work - up a pregnant patient with vaginal bleeding ( obstetrics and gynecology ), and stop a bad nosebleed ( ent ). # definition " emergency medicine is a medical specialty - - a field of practice based on the knowledge and skills required for the prevention, diagnosis and management of acute and urgent aspects of illness and injury affecting patients of all age gro

[Guideline 6] (Source: Treatment, Relevance: 0.114)
an attending physician, the patient is initially assigned a chief complaint rather than a diagnosis. this is usually a symptom : headache, nausea, loss of consciousness. the chief complaint remains a primary fact until the attending physician makes a diagnosis. # department layout a typical emergency department has several different areas, each specialized for patients with particular severities or types of illness. in the triage area, patients are seen by a triage nurse who completes a preliminary evaluation, before transferring care to another area of the ed or a different department in the hospital. patients with life or limb - threatening conditions may bypass triage and to be seen directly by a physician. the resuscitation area is a key area of an emergency department. it usually contains several individual resuscitation bays, usually with one specially equipped for paediatric resuscitation. each bay is equipped with a defibrillator, airway equipment, oxygen, intravenous lines and fluids, and emergency drugs. resuscitation areas also have ecg machines, and often limited x - ray facilities to perform chest and pelvis films. other equipment may include non - invasive ventilation ( niv ) and portable ultrasound devices. the majors, or general medical, area is for stable patients who still need to be confined to bed ( note that a " bed " in the ed context is almost always a gurney or trolley rather than a full hospital bed ). this area is ofte

Instructions:
Focus on differential diagnosis, diagnostic criteria, and assessment approaches.

Please provide a clear, actionable response that:
1. Addresses the specific clinical question asked
2. References relevant evidence from the provided guidelines
3. Offers practical, step-by-step guidance when appropriate
4. Maintains appropriate medical caution and emphasizes the need for clinical judgment

Your response should be concise but comprehensive, suitable for immediate clinical application.
2025-07-31 09:50:47,565 - llm_clients - ERROR - Medical LLM query error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee7-327af85a14d8140c6b21f01e;87cf042b-f194-4556-b329-19d9da40e14f)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
2025-07-31 09:50:47,565 - llm_clients - ERROR - Error Type: HfHubHTTPError
2025-07-31 09:50:47,565 - llm_clients - ERROR - Detailed Error: HfHubHTTPError('402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee7-327af85a14d8140c6b21f01e;87cf042b-f194-4556-b329-19d9da40e14f)\n\nYou have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.')
2025-07-31 09:50:47,565 - llm_clients - ERROR - Query Latency (on error): 0.1200 seconds
2025-07-31 09:50:47,565 - llm_clients - ERROR - Query that caused error: You are an experienced attending physician providing guidance to a junior clinician in an emergency setting. A colleague is asking for your expert medical opinion.

Clinical Question:
Differential diagnosis for sudden onset chest pain in young adult

Relevant Medical Guidelines:
[Guideline 1] (Source: Emergency, Relevance: 0.194)
organization of emergency medical assistance emergency medical assistance is the first aid that is given to victims of accidents ( casualties ) or of the acute effects of diseases. the basis of emergency medical assistance is the " chain of rescue " : this system is based on the collaboration of different actors. the most advanced cares can only be performed by physicians and surgeons with the appropriate environment ( medical imaging, biochemistry analysis laboratory, emergency room, operating room ), but the acute event often happens outside the hospital ( prehospital cares ) : at home, in the street, at work, in a public building … the other actors involved are : - the first witness of the event, who will call for help and possibly provide first aid ( see also emergency action principles ) ; - the medical regulation service that will receive the call and provide advice, and decide the action required ; - the general practitioner that will come and see the person, in case the situation is not too urgent and the person is in a safe environment ; - the ambulance that will take th

[Guideline 2] (Source: Emergency, Relevance: 0.168)
ion to the emergency room ; - urgent situation that requires advanced medical care before transportation. these categories are not so clearly separated, and depend not only on the medical condition of the casualty, but also on the organization of the health system and on the social impact. for example, a deceased person is not a medical emergency ( there is no care to perform ), but in some societies, it is a social emergency ( the people would not understand nothing is being done ) especially in the case of a child ' s death ; and it is not obvious to decide whether the person is dead or can be saved through advanced care ( e. g. case of cardiac arrest and of cardiopulmonary resuscitation ). in general, pain is usually not a life - threatening situation, but the situation is often unbearable from the point of view of the casualty. two things must thus be considered : - the perceived emergency, and - the " real " emergency. the distinction requires assessment ; assessment by the witness who calls ( importance of first aid education ) and remote assessment by the dispatcher ( medical regulation ). the confidence in the emergency assistance system warrants the efficiency of the system ; otherwise, the probable reaction would be to drive the casualty to the closest hospital, making the flow o

[Guideline 3] (Source: Emergency, Relevance: 0.129)
een by a physician more rapidly than those with less severe symptoms or injuries. after initial assessment and treatment, patients are either admitted to the hospital, stabilized and transferred to another hospital for various reasons, or discharged. the staff in emergency departments not only includes doctors, but physician assistants ( pas ) and nurses with specialized training in emergency medicine and in house emergency medical technicians, respiratory therapists, radiology technicians, healthcare assistants ( hcas ), volunteers, and other support staff who all work as a team to treat emergency patients and provide support to anxious family members. the emergency departments of most hospitals operate around the clock, although staffing levels are usually much lower at night. since a diagnosis must be made by an attending physician, the patient is initially assigned a chief complaint rather than a diagnosis. this is usually a symptom : headache, nausea, loss of consciousness. the chief complaint remains a primary fact until the attending physician makes a diagnosis. # department layout a typical emergency department has several different areas, each specialized for patients with particular severities or types of illness. in the triage area, patients are seen by a triage nurse who completes a preliminary evaluation, before transferring care to another area of the ed or a different department in the hospital. patients with l

[Guideline 4] (Source: Emergency, Relevance: 0.124)
skills, and should be left to the professionals of the emergency medical and fire service. # clinical response within hospital settings, an adequate staff is generally present to deal with the average emergency situation. emergency medicine physicians have training to deal with most medical emergencies, and maintain cpr and acls certifications. in disasters or complex emergencies, most hospitals have protocols to summon on - site and off - site staff rapidly. both emergency room and inpatient medical emergencies follow the basic protocol of advanced cardiac life support. irrespective of the nature of the emergency, adequate blood pressure and oxygenation are required before the cause of the emergency can be eliminated. possible exceptions include the clamping of arteries in severe hemorrhage.

[Guideline 5] (Source: Treatment, Relevance: 0.229)
and nurse practitioners who may or may not be formally trained in emergency medicine. they offer primary care treatment to patients who desire or require immediate care, but who do not reach the acuity that requires care in an emergency department. emergency medicine encompasses a large amount of general medicine but involves virtually all fields of medicine including the surgical sub - specialties. emergency physicians are tasked with seeing a large number of patients, treating their illnesses and arranging for disposition - either admitting them to the hospital or releasing them after treatment as necessary. the emergency physician requires a broad field of knowledge and advanced procedural skills often including surgical procedures, trauma resuscitation, advanced cardiac life support and advanced airway management. emergency physicians ideally have the skills of many specialists - the ability to manage a difficult airway ( anesthesia ), suture a complex laceration ( plastic surgery ), reduce ( set ) a fractured bone or dislocated joint ( orthopedic surgery ), treat a heart attack ( internist ), work - up a pregnant patient with vaginal bleeding ( obstetrics and gynecology ), and stop a bad nosebleed ( ent ). # definition " emergency medicine is a medical specialty - - a field of practice based on the knowledge and skills required for the prevention, diagnosis and management of acute and urgent aspects of illness and injury affecting patients of all age gro

[Guideline 6] (Source: Treatment, Relevance: 0.114)
an attending physician, the patient is initially assigned a chief complaint rather than a diagnosis. this is usually a symptom : headache, nausea, loss of consciousness. the chief complaint remains a primary fact until the attending physician makes a diagnosis. # department layout a typical emergency department has several different areas, each specialized for patients with particular severities or types of illness. in the triage area, patients are seen by a triage nurse who completes a preliminary evaluation, before transferring care to another area of the ed or a different department in the hospital. patients with life or limb - threatening conditions may bypass triage and to be seen directly by a physician. the resuscitation area is a key area of an emergency department. it usually contains several individual resuscitation bays, usually with one specially equipped for paediatric resuscitation. each bay is equipped with a defibrillator, airway equipment, oxygen, intravenous lines and fluids, and emergency drugs. resuscitation areas also have ecg machines, and often limited x - ray facilities to perform chest and pelvis films. other equipment may include non - invasive ventilation ( niv ) and portable ultrasound devices. the majors, or general medical, area is for stable patients who still need to be confined to bed ( note that a " bed " in the ed context is almost always a gurney or trolley rather than a full hospital bed ). this area is ofte

Instructions:
Focus on differential diagnosis, diagnostic criteria, and assessment approaches.

Please provide a clear, actionable response that:
1. Addresses the specific clinical question asked
2. References relevant evidence from the provided guidelines
3. Offers practical, step-by-step guidance when appropriate
4. Maintains appropriate medical caution and emphasizes the need for clinical judgment

Your response should be concise but comprehensive, suitable for immediate clinical application.
2025-07-31 09:50:47,566 - generation - ERROR - Med42-70B generation failed: Med42-70B generation error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee7-327af85a14d8140c6b21f01e;87cf042b-f194-4556-b329-19d9da40e14f)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
2025-07-31 09:50:47,566 - generation - ERROR - Medical advice generation failed: Med42-70B generation error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee7-327af85a14d8140c6b21f01e;87cf042b-f194-4556-b329-19d9da40e14f)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
      Intention: diagnosis
      Confidence: 0.00
      Advice Length: 164 chars
      Chunks Used: 0
      Time: 0.121s

   ✅ Pipeline completed successfully!
   📊 Total Time: 2.076s
   🩺 Medical Advice Preview:
      I apologize, but I encountered an error while processing your medical query. Please try rephrasing your question or contact technical support if the i...

🧪 e2e_005: Pulmonary emergency requiring immediate intervention
Query: 'Emergency management of pulmonary embolism'
Expected: treatment intention
----------------------------------------------------------------------
   🎯 Step 1: Condition extraction and validation...
2025-07-31 09:50:47,566 - user_prompt - INFO - Matched predefined condition: pulmonary embolism
      Condition: pulmonary embolism
      Keywords: Emergency='chest pain|shortness of breath|sudden dyspnea', Treatment='anticoagulation|heparin|embolectomy'
      Time: 0.000s
   🤝 Step 2: User confirmation (simulated as 'yes')...
   🔍 Step 3: Medical guideline retrieval...
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 15.31it/s]
2025-07-31 09:50:47,699 - retrieval - INFO - Search results: Emergency=5, Treatment=5
2025-07-31 09:50:47,699 - retrieval - INFO - Deduplication: Processing 10 results using text matching
2025-07-31 09:50:47,699 - retrieval - INFO - Deduplication summary: 10 → 8 results (removed 2)
      Search Query: 'chest pain|shortness of breath|sudden dyspnea anticoagulation|heparin|embolectomy'
      Results: 8 total (5 emergency, 3 treatment)
      Time: 0.133s
   🧠 Step 4: Medical advice generation...
2025-07-31 09:50:47,699 - generation - INFO - Generating medical advice for query: 'Emergency management of pulmonary embolism...'
2025-07-31 09:50:47,699 - generation - INFO - Classified chunks: Emergency=5, Treatment=3
2025-07-31 09:50:47,699 - generation - INFO - Generating prompt with intention: treatment
2025-07-31 09:50:47,699 - generation - INFO - Selected chunks by intention 'treatment': 5 total
2025-07-31 09:50:47,699 - generation - INFO - Generated prompt with 5 chunks, 6701 chars
2025-07-31 09:50:47,699 - generation - INFO - Calling Med42-70B for medical advice generation
2025-07-31 09:50:47,699 - llm_clients - INFO - Calling Medical LLM with query: You are an experienced attending physician providing guidance to a junior clinician in an emergency setting. A colleague is asking for your expert medical opinion.

Clinical Question:
Emergency management of pulmonary embolism

Relevant Medical Guidelines:
[Guideline 1] (Source: Emergency, Relevance: 0.105)
algesics ( e. g. morphine, pethidine ) facilities for defibrillation ( df ) aspirin / anticoagulant ( heparin ) rest converting enzyme inhibitor thrombolysis iv beta blocker oxygen 60 % nitrates stool softeners # # jvp : wave form ask me atrial contraction systole ( ventricular contraction ) klosure ( closure ) of tricusps, so atrial filling maximal atrial filling emptying of atrium # # mi : basic management boomar : bed rest oxygen opiate monitor anticoagulate reduce clot size # # mi : signs and symptoms pulse : persistent chest pains upset stomach lightheadedness shortness of breath excessive sweating # # mi : therapeutic treatment o batman! oxygen beta blocker asa thrombolytics ( e. g. heparin ) morphine ace prn nitroglycerin # # mi : treatment of acute mi coag : cyclomorph oxygen aspirin glycerol trinitrate # # murmur attributes " il pqrst " ( person has ill pqrst heart waves ) : intensity location pitch quality radiation shape timing # # murmurs : innocent murmur features 8 s ' s : soft systolic short sounds ( s1 & s2 ) normal symptomless special t

[Guideline 2] (Source: Emergency, Relevance: 0.078)
ed or discolored skin in the affected leg - visible surface veins dvt usually involves the deep veins of the legs or arms. it may cause life - threatening emboli to the lungs and valvular dysfunction and chronic leg swelling. the classic symptoms of pain and swelling may be present or absent, unilateral or bilateral, mild or severe. when obstruction is high ( for example, in the pelvic veins ), edema may be bilateral. leg pain is only present in 50 % of patients and doesn ' t correspond to the location of the thrombus. when tenderness is present, it is usually confined to the calf muscles or along the deep veins in the medial thigh. warmth and erythema may be present over the area of the thrombus. the symptoms of pulmonary embolism are : - sudden onset of cough - sharp chest pain - rapid breathing or shortness of breath - lightheadedness suspicion of a dvt or pulmonary embolism is a medical emergency and requires immediate medical attention. the 2020 asco guidelines for treatment of venous thromboembolism states that initial anticoagulation may involve lmwh, ufh, fondaparinux, or rivaroxaban for cancer patients with established vte ( 2020 ). 47 the guidelines also recommend lmwh as the preferred approach for longterm anticoagulant therapy. for patients with cns malignancies, the guidelines recommend careful monitoring for hemorrhagic complications, and state that anticoagulation be avoided in the presence of active intracranial bleeding

[Guideline 3] (Source: Treatment, Relevance: 0.080)
y proximal deep vein thrombosis leading to acute pulmonary embolism # # common causes of peripheral edema - advanced kidney disease - nephrotic syndrome - systolic or diastolic heart failure - constrictive pericarditis - pulmonary hypertension - anemia - nutritional deficiency - malabsorption - refeeding edema - deep vein thrombosis - cellulitis - superficial thrombophlebitis - baker cyst - chronic venous insufficiency - lymphedema - pregnancy - menstrual cycle - hyperthyroidism - hypothyroidism - medications - obstructive sleep apnea # diagnosis shown below is an algorithm summarizing the diagnosis of edema. # treatment shown below is an algorithm summarizing the treatment of edema. # do ' s - before initiation of medical compression therapy, checking the arterial circulation is recommended. if foot pulses or ankle pulses are weak or not palpable, the ankle - brachial index ( abi ) should be measured. - in proximal deep vein thrombosis ( dvt ), using compression bandage or medical compression stockings and walking accompanied with anticoagulant therapy will lessen the pain and swelling. - in dvt, using medical compression will not increase the risk of pulmonary thromboembolism and post thrombotic syndrome. - early mobilization in acute deep vein thrombosis will not increase the risk of pulmonary thromboembolism. - in the acute phase of dvt, calf compression reduces irreversible skin alteration, edema, and pain. - in compensated heart failure nyha [UNK] and [UNK], mild compression of both

[Guideline 4] (Source: Treatment, Relevance: 0.071)
. sensitivity and specificity are both thought to be 98 %, and the site of entry can be visualized in 85 % of cases. # 2. pulmonary embolism - supportive symptoms include : shortness of breath chest pain dyspnea anxiety pleuritic chest pain - shortness of breath - chest pain - dyspnea - anxiety - pleuritic chest pain - supportive laboratory studies include : d - dimers are formed by the degradation of fibrin clot. almost all patients with pe have some endogenous fibrinolysis, and therefore have elevated levels of d - dimer. many other processes, such as pneumonia, congestive heart failure ( chf ), myocardial infarction ( mi ), malignancy, and surgery, are also associated with a mild degree of fibrinolysis, and hence an elevated d - dimer is not specific for pulmonary embolism. its negative predictive value, however, is 91 – 94 % - d - dimers are formed by the degradation of fibrin clot. - almost all patients with pe have some endogenous fibrinolysis, and therefore have elevated levels of d - dimer. - many other processes, such as pneumonia, congestive heart failure ( chf ), myocardial infarction ( mi ), malignancy, and surgery, are also associated with a mild degree of fibrinolysis, and hence an elevated d - dimer is not specific for pulmonary embolism. - its negative predictive value, howe

[Guideline 5] (Source: Treatment, Relevance: 0.053)
l impact in a cohort of patients with..., cote [ / bib _ ref ]. the risk of pe in this setting is also unclear [ bib _ ref ] prevalence of venous thromboembolism in patients with secondary polycythemia, nadeem [ / bib _ ref ] as an increased hct in the general population is also associated with increased vte risk [ bib _ ref ] hematocrit and risk of venous thromboembolism in a general population. the tromso..., braekkan [ / bib _ ref ]. a recent study suggests that patients with copd at low risk of vte had increased incidence of pulmonary embolism if they had concurrent erythrocytosis [ bib _ ref ] relationship between polycythemia and in - hospital mortality in chronic obstructive pulmonary disease patients..., guo [ / bib _ ref ]. additional risk factors affecting circulatory compromise and tissue oxygen delivery include carbon monoxide in smokers, extent of hypercapnia, renal blood flow, acid - base balance ( ph ), capacity of the bone marrow to respond to erythropoietic drive, position on the oxygen dissociation curve and changes in the peripheral vascular cir

Instructions:
Focus on providing specific treatment protocols, management steps, and therapeutic interventions.

Please provide a clear, actionable response that:
1. Addresses the specific clinical question asked
2. References relevant evidence from the provided guidelines
3. Offers practical, step-by-step guidance when appropriate
4. Maintains appropriate medical caution and emphasizes the need for clinical judgment

Your response should be concise but comprehensive, suitable for immediate clinical application.
2025-07-31 09:50:47,821 - llm_clients - ERROR - Medical LLM query error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee7-1003161902752f57369eec15;8b59401d-09cb-4ee0-98c8-c23b86cdc19f)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
2025-07-31 09:50:47,821 - llm_clients - ERROR - Error Type: HfHubHTTPError
2025-07-31 09:50:47,821 - llm_clients - ERROR - Detailed Error: HfHubHTTPError('402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee7-1003161902752f57369eec15;8b59401d-09cb-4ee0-98c8-c23b86cdc19f)\n\nYou have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.')
2025-07-31 09:50:47,821 - llm_clients - ERROR - Query Latency (on error): 0.1224 seconds
2025-07-31 09:50:47,821 - llm_clients - ERROR - Query that caused error: You are an experienced attending physician providing guidance to a junior clinician in an emergency setting. A colleague is asking for your expert medical opinion.

Clinical Question:
Emergency management of pulmonary embolism

Relevant Medical Guidelines:
[Guideline 1] (Source: Emergency, Relevance: 0.105)
algesics ( e. g. morphine, pethidine ) facilities for defibrillation ( df ) aspirin / anticoagulant ( heparin ) rest converting enzyme inhibitor thrombolysis iv beta blocker oxygen 60 % nitrates stool softeners # # jvp : wave form ask me atrial contraction systole ( ventricular contraction ) klosure ( closure ) of tricusps, so atrial filling maximal atrial filling emptying of atrium # # mi : basic management boomar : bed rest oxygen opiate monitor anticoagulate reduce clot size # # mi : signs and symptoms pulse : persistent chest pains upset stomach lightheadedness shortness of breath excessive sweating # # mi : therapeutic treatment o batman! oxygen beta blocker asa thrombolytics ( e. g. heparin ) morphine ace prn nitroglycerin # # mi : treatment of acute mi coag : cyclomorph oxygen aspirin glycerol trinitrate # # murmur attributes " il pqrst " ( person has ill pqrst heart waves ) : intensity location pitch quality radiation shape timing # # murmurs : innocent murmur features 8 s ' s : soft systolic short sounds ( s1 & s2 ) normal symptomless special t

[Guideline 2] (Source: Emergency, Relevance: 0.078)
ed or discolored skin in the affected leg - visible surface veins dvt usually involves the deep veins of the legs or arms. it may cause life - threatening emboli to the lungs and valvular dysfunction and chronic leg swelling. the classic symptoms of pain and swelling may be present or absent, unilateral or bilateral, mild or severe. when obstruction is high ( for example, in the pelvic veins ), edema may be bilateral. leg pain is only present in 50 % of patients and doesn ' t correspond to the location of the thrombus. when tenderness is present, it is usually confined to the calf muscles or along the deep veins in the medial thigh. warmth and erythema may be present over the area of the thrombus. the symptoms of pulmonary embolism are : - sudden onset of cough - sharp chest pain - rapid breathing or shortness of breath - lightheadedness suspicion of a dvt or pulmonary embolism is a medical emergency and requires immediate medical attention. the 2020 asco guidelines for treatment of venous thromboembolism states that initial anticoagulation may involve lmwh, ufh, fondaparinux, or rivaroxaban for cancer patients with established vte ( 2020 ). 47 the guidelines also recommend lmwh as the preferred approach for longterm anticoagulant therapy. for patients with cns malignancies, the guidelines recommend careful monitoring for hemorrhagic complications, and state that anticoagulation be avoided in the presence of active intracranial bleeding

[Guideline 3] (Source: Treatment, Relevance: 0.080)
y proximal deep vein thrombosis leading to acute pulmonary embolism # # common causes of peripheral edema - advanced kidney disease - nephrotic syndrome - systolic or diastolic heart failure - constrictive pericarditis - pulmonary hypertension - anemia - nutritional deficiency - malabsorption - refeeding edema - deep vein thrombosis - cellulitis - superficial thrombophlebitis - baker cyst - chronic venous insufficiency - lymphedema - pregnancy - menstrual cycle - hyperthyroidism - hypothyroidism - medications - obstructive sleep apnea # diagnosis shown below is an algorithm summarizing the diagnosis of edema. # treatment shown below is an algorithm summarizing the treatment of edema. # do ' s - before initiation of medical compression therapy, checking the arterial circulation is recommended. if foot pulses or ankle pulses are weak or not palpable, the ankle - brachial index ( abi ) should be measured. - in proximal deep vein thrombosis ( dvt ), using compression bandage or medical compression stockings and walking accompanied with anticoagulant therapy will lessen the pain and swelling. - in dvt, using medical compression will not increase the risk of pulmonary thromboembolism and post thrombotic syndrome. - early mobilization in acute deep vein thrombosis will not increase the risk of pulmonary thromboembolism. - in the acute phase of dvt, calf compression reduces irreversible skin alteration, edema, and pain. - in compensated heart failure nyha [UNK] and [UNK], mild compression of both

[Guideline 4] (Source: Treatment, Relevance: 0.071)
. sensitivity and specificity are both thought to be 98 %, and the site of entry can be visualized in 85 % of cases. # 2. pulmonary embolism - supportive symptoms include : shortness of breath chest pain dyspnea anxiety pleuritic chest pain - shortness of breath - chest pain - dyspnea - anxiety - pleuritic chest pain - supportive laboratory studies include : d - dimers are formed by the degradation of fibrin clot. almost all patients with pe have some endogenous fibrinolysis, and therefore have elevated levels of d - dimer. many other processes, such as pneumonia, congestive heart failure ( chf ), myocardial infarction ( mi ), malignancy, and surgery, are also associated with a mild degree of fibrinolysis, and hence an elevated d - dimer is not specific for pulmonary embolism. its negative predictive value, however, is 91 – 94 % - d - dimers are formed by the degradation of fibrin clot. - almost all patients with pe have some endogenous fibrinolysis, and therefore have elevated levels of d - dimer. - many other processes, such as pneumonia, congestive heart failure ( chf ), myocardial infarction ( mi ), malignancy, and surgery, are also associated with a mild degree of fibrinolysis, and hence an elevated d - dimer is not specific for pulmonary embolism. - its negative predictive value, howe

[Guideline 5] (Source: Treatment, Relevance: 0.053)
l impact in a cohort of patients with..., cote [ / bib _ ref ]. the risk of pe in this setting is also unclear [ bib _ ref ] prevalence of venous thromboembolism in patients with secondary polycythemia, nadeem [ / bib _ ref ] as an increased hct in the general population is also associated with increased vte risk [ bib _ ref ] hematocrit and risk of venous thromboembolism in a general population. the tromso..., braekkan [ / bib _ ref ]. a recent study suggests that patients with copd at low risk of vte had increased incidence of pulmonary embolism if they had concurrent erythrocytosis [ bib _ ref ] relationship between polycythemia and in - hospital mortality in chronic obstructive pulmonary disease patients..., guo [ / bib _ ref ]. additional risk factors affecting circulatory compromise and tissue oxygen delivery include carbon monoxide in smokers, extent of hypercapnia, renal blood flow, acid - base balance ( ph ), capacity of the bone marrow to respond to erythropoietic drive, position on the oxygen dissociation curve and changes in the peripheral vascular cir

Instructions:
Focus on providing specific treatment protocols, management steps, and therapeutic interventions.

Please provide a clear, actionable response that:
1. Addresses the specific clinical question asked
2. References relevant evidence from the provided guidelines
3. Offers practical, step-by-step guidance when appropriate
4. Maintains appropriate medical caution and emphasizes the need for clinical judgment

Your response should be concise but comprehensive, suitable for immediate clinical application.
2025-07-31 09:50:47,822 - generation - ERROR - Med42-70B generation failed: Med42-70B generation error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee7-1003161902752f57369eec15;8b59401d-09cb-4ee0-98c8-c23b86cdc19f)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
2025-07-31 09:50:47,822 - generation - ERROR - Medical advice generation failed: Med42-70B generation error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee7-1003161902752f57369eec15;8b59401d-09cb-4ee0-98c8-c23b86cdc19f)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
      Intention: treatment
      Confidence: 0.00
      Advice Length: 164 chars
      Chunks Used: 0
      Time: 0.123s

   ✅ Pipeline completed successfully!
   📊 Total Time: 0.256s
   🩺 Medical Advice Preview:
      I apologize, but I encountered an error while processing your medical query. Please try rephrasing your question or contact technical support if the i...

🧪 e2e_006: Non-medical query - should be rejected
Query: 'How to cook pasta properly?'
Expected: None intention
----------------------------------------------------------------------
   🎯 Step 1: Condition extraction and validation...
2025-07-31 09:50:47,822 - llm_clients - INFO - Calling Medical LLM with query: How to cook pasta properly?
2025-07-31 09:50:47,934 - llm_clients - ERROR - Medical LLM query error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee7-16bc1514374962a27a55d595;0e7a3848-8d8c-4c57-9ee8-0e26dfc6b209)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
2025-07-31 09:50:47,934 - llm_clients - ERROR - Error Type: HfHubHTTPError
2025-07-31 09:50:47,934 - llm_clients - ERROR - Detailed Error: HfHubHTTPError('402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee7-16bc1514374962a27a55d595;0e7a3848-8d8c-4c57-9ee8-0e26dfc6b209)\n\nYou have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.')
2025-07-31 09:50:47,934 - llm_clients - ERROR - Query Latency (on error): 0.1120 seconds
2025-07-31 09:50:47,934 - llm_clients - ERROR - Query that caused error: How to cook pasta properly?
2025-07-31 09:50:47,934 - user_prompt - INFO - Starting semantic search fallback for query: 'How to cook pasta properly?'
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.37it/s]
2025-07-31 09:50:48,507 - retrieval - INFO - Sliding window search: Found 5 results
2025-07-31 09:50:48,514 - user_prompt - INFO - Semantic search returned 5 results
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 14.06it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.55it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 47.00it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.21it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 45.97it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 55.83it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 58.52it/s]
Batches: 100%|██████████████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00, 61.10it/s]
2025-07-31 09:50:48,729 - user_prompt - INFO - Inferred condition: None
2025-07-31 09:50:48,729 - user_prompt - WARNING - Condition validation failed for: None
2025-07-31 09:50:48,729 - user_prompt - INFO - No suitable condition found in semantic search
2025-07-31 09:50:48,729 - llm_clients - INFO - Calling Medical LLM with query: How to cook pasta properly?
2025-07-31 09:50:48,846 - llm_clients - ERROR - Medical LLM query error: 402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee8-570085dc663fa9df5c617c04;c8f719c8-3f2c-40f9-934b-d3455abcb6f2)

You have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.
2025-07-31 09:50:48,846 - llm_clients - ERROR - Error Type: HfHubHTTPError
2025-07-31 09:50:48,846 - llm_clients - ERROR - Detailed Error: HfHubHTTPError('402 Client Error: Payment Required for url: https://router.huggingface.co/featherless-ai/v1/chat/completions (Request ID: Root=1-688b9ee8-570085dc663fa9df5c617c04;c8f719c8-3f2c-40f9-934b-d3455abcb6f2)\n\nYou have exceeded your monthly included credits for Inference Providers. Subscribe to PRO to get 20x more monthly included credits.')
2025-07-31 09:50:48,846 - llm_clients - ERROR - Query Latency (on error): 0.1173 seconds
2025-07-31 09:50:48,846 - llm_clients - ERROR - Query that caused error: How to cook pasta properly?
      Condition: None
      Keywords: Emergency='None', Treatment='None'
      Time: 1.025s
      🚫 Non-medical query correctly rejected

================================================================================
📊 END-TO-END PIPELINE TEST REPORT
================================================================================
🕐 Execution Summary:
   Test session duration: 100.488s
   Average per test: 16.748s

📈 Pipeline Results:
   Total tests: 6
   Successful: 6 ✅
   Failed: 0 ❌
   Success rate: 100.0%

⚡ Performance Analysis:
   Condition Extraction: 2.553s average
   Retrieval: 0.279s average
   Generation: 15.425s average
   Complete Pipeline: 15.469s average

📝 Detailed Test Results:

   📋 e2e_001: ✅ PASS
      Query: 'How to treat acute myocardial infarction in emergency department?'
      Category: cardiac_emergency
      Total Time: 39.031s
      Condition Extracted: acute myocardial infarction
      Generation: 0.90 confidence, 9 chunks
      Advice Preview: acute myocardial infarction...

   📋 e2e_002: ✅ PASS
      Query: 'Patient presenting with severe chest pain and shortness of breath'
      Category: multi_symptom
      Total Time: 50.365s
      Condition Extracted: generic medical query
      Generation: 0.90 confidence, 9 chunks
      Advice Preview: pulmonary embolism...

   📋 e2e_003: ✅ PASS
      Query: 'What are the emergency protocols for acute stroke management?'
      Category: neurological_emergency
      Total Time: 1.085s
      Condition Extracted: acute stroke
      Generation: 0.00 confidence, 0 chunks
      Advice Preview: I apologize, but I encountered an error while processing your medical query. Please try rephrasing y...

   📋 e2e_004: ✅ PASS
      Query: 'Differential diagnosis for sudden onset chest pain in young adult'
      Category: differential_diagnosis
      Total Time: 2.076s
      Condition Extracted: generic medical query
      Generation: 0.00 confidence, 0 chunks
      Advice Preview: I apologize, but I encountered an error while processing your medical query. Please try rephrasing y...

   📋 e2e_005: ✅ PASS
      Query: 'Emergency management of pulmonary embolism'
      Category: pulmonary_emergency
      Total Time: 0.256s
      Condition Extracted: pulmonary embolism
      Generation: 0.00 confidence, 0 chunks
      Advice Preview: I apologize, but I encountered an error while processing your medical query. Please try rephrasing y...

   📋 e2e_006: ✅ PASS
      Query: 'How to cook pasta properly?'
      Category: non_medical
      Total Time: 0.000s
      Condition Extracted: None

================================================================================
📁 End-to-end test results saved to: /Users/yanbochen/Documents/Life in Canada/CS study related/*Student Course, Guide/CS7180 GenAI/FinalProject_git_copy/tests/end_to_end_pipeline_results_20250731_095048.json

🎯 End-to-end testing completed!
Next step: Create Gradio interface for interactive testing