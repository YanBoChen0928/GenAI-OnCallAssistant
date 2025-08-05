"""
OnCall.ai Medical Conditions Configuration

This module provides centralized configuration for:
1. Predefined medical conditions
2. Condition-to-keyword mappings
3. Fallback condition keywords
4. Regular expression matching for flexible condition recognition

Author: OnCall.ai Team
Date: 2025-07-29
"""

from typing import Dict, Optional
import re

# Regular Expression Mapping for Flexible Condition Recognition
CONDITION_REGEX_MAPPING: Dict[str, str] = {
    r"acute[\s_-]*coronary[\s_-]*syndrome": "acute_coronary_syndrome",
    r"acute[\s_-]*myocardial[\s_-]*infarction": "acute myocardial infarction",
    r"acute[\s_-]*ischemic[\s_-]*stroke": "acute_ischemic_stroke",
    r"hemorrhagic[\s_-]*stroke": "hemorrhagic_stroke", 
    r"transient[\s_-]*ischemic[\s_-]*attack": "transient_ischemic_attack",
    r"pulmonary[\s_-]*embolism": "pulmonary embolism",
    # Handles variants like:
    # "Acute Coronary Syndrome", "acute_coronary_syndrome", "acute-coronary-syndrome"
}
# Comprehensive Condition-to-Keyword Mapping
CONDITION_KEYWORD_MAPPING: Dict[str, Dict[str, str]] = {
    "acute myocardial infarction": {
        "emergency": "MI|chest pain|cardiac arrest",
        "treatment": "aspirin|nitroglycerin|thrombolytic|PCI"
    },
    "acute stroke": {
        "emergency": "stroke|neurological deficit|sudden weakness", 
        "treatment": "tPA|thrombolysis|stroke unit care"
    },
    "pulmonary embolism": {
        "emergency": "chest pain|shortness of breath|sudden dyspnea",
        "treatment": "anticoagulation|heparin|embolectomy"
    },
    # extended from @20250729Test_Retrieval.md 
    "acute_ischemic_stroke": {
        "emergency": "ischemic stroke|neurological deficit",
        "treatment": "tPA|stroke unit management"
    },
    "hemorrhagic_stroke": {
        "emergency": "hemorrhagic stroke|intracranial bleeding",
        "treatment": "blood pressure control|neurosurgery"
    },
    "transient_ischemic_attack": {
        "emergency": "TIA|temporary stroke symptoms",
        "treatment": "antiplatelet|lifestyle modification"
    },
    "acute_coronary_syndrome": {
        "emergency": "ACS|chest pain|ECG changes",
        "treatment": "antiplatelet|statins|cardiac monitoring"
    },
    "acute seizure": {
    "emergency": "seizure|convulsion|epilepsy|loss of consciousness",
    "treatment": "anticonvulsant|benzodiazepine|neurologic assessment"
    },
    "seizure disorder": {
        "emergency": "seizure|status epilepticus|postictal state",
        "treatment": "antiepileptic drugs|EEG monitoring|neurology consult"
    },
    "postpartum hemorrhage": {
    "emergency": "postpartum hemorrhage|uterine atony|placental retention|vaginal laceration",
    "treatment": "uterine massage|IV oxytocin infusion|blood transfusion|surgical intervention"
    },
    "bacterial meningitis": {
    "emergency": "bacterial meningitis|fever|headache|neck stiffness|altered mental status|meningitis|meningeal signs",
    "treatment": "empiric antibiotics|ceftriaxone|vancomycin|dexamethasone|lumbar puncture"
    }
}

# Fallback Condition Keywords
FALLBACK_CONDITION_KEYWORDS: Dict[str, str] = {
    "acute_ischemic_stroke": "acute ischemic stroke treatment",
    "hemorrhagic_stroke": "hemorrhagic stroke management", 
    "transient_ischemic_attack": "TIA treatment protocol",
    "acute_coronary_syndrome": "ACS treatment guidelines",
    "stable_angina": "stable angina management",
    "non_cardiac_chest_pain": "non-cardiac chest pain evaluation",
    "witnessed_cardiac_arrest": "witnessed cardiac arrest protocol",
    "unwitnessed_cardiac_arrest": "unwitnessed cardiac arrest management",
    "post_resuscitation_care": "post-resuscitation care guidelines"
}

def get_condition_keywords(specific_condition: str) -> Optional[str]:
    """
    Retrieve fallback keywords for a specific condition
    
    Args:
        specific_condition: Medical condition name
    
    Returns:
        Corresponding keywords or the original condition
    """
    return FALLBACK_CONDITION_KEYWORDS.get(specific_condition, specific_condition)

def validate_condition(condition: str) -> bool:
    """
    Check if a condition exists in our predefined mapping with flexible regex matching
    
    Args:
        condition: Medical condition to validate
    
    Returns:
        Boolean indicating condition validity
    """
    if not condition:
        return False
    
    condition_lower = condition.lower().strip()
    
    # Level 1: Direct exact match (fastest)
    for key in CONDITION_KEYWORD_MAPPING.keys():
        if key.lower() == condition_lower:
            return True
    
    # Level 2: Regular expression matching (flexible)
    for regex_pattern, mapped_condition in CONDITION_REGEX_MAPPING.items():
        if re.search(regex_pattern, condition_lower, re.IGNORECASE):
            return True
    
    # Level 3: Partial matching for key medical terms (fallback)
    medical_keywords = ['coronary', 'syndrome', 'stroke', 'myocardial', 'embolism', 'ischemic']
    if any(keyword in condition_lower for keyword in medical_keywords):
        return True
    
    return False

def get_condition_details(condition: str) -> Optional[Dict[str, str]]:
    """
    Retrieve detailed information for a specific condition with flexible matching
    
    Args:
        condition: Medical condition name
    
    Returns:
        Dict with emergency and treatment keywords, or None
    """
    if not condition:
        return None
    
    condition_lower = condition.lower().strip()
    
    # Level 1: Direct exact match
    for key, value in CONDITION_KEYWORD_MAPPING.items():
        if key.lower() == condition_lower:
            return value
    
    # Level 2: Regular expression matching
    for regex_pattern, mapped_condition in CONDITION_REGEX_MAPPING.items():
        if re.search(regex_pattern, condition_lower, re.IGNORECASE):
            # Find the mapped condition in the keyword mapping
            for key, value in CONDITION_KEYWORD_MAPPING.items():
                if key.lower() == mapped_condition.lower():
                    return value
    
    return None 