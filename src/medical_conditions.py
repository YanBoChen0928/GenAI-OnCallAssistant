"""
OnCall.ai Medical Conditions Configuration

This module provides centralized configuration for:
1. Predefined medical conditions
2. Condition-to-keyword mappings
3. Fallback condition keywords

Author: OnCall.ai Team
Date: 2025-07-29
"""

from typing import Dict, Optional

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
    Check if a condition exists in our predefined mapping
    
    Args:
        condition: Medical condition to validate
    
    Returns:
        Boolean indicating condition validity
    """
    return condition.lower() in {k.lower() for k in CONDITION_KEYWORD_MAPPING.keys()}

def get_condition_details(condition: str) -> Optional[Dict[str, str]]:
    """
    Retrieve detailed information for a specific condition
    
    Args:
        condition: Medical condition name
    
    Returns:
        Dict with emergency and treatment keywords, or None
    """
    normalized_condition = condition.lower()
    for key, value in CONDITION_KEYWORD_MAPPING.items():
        if key.lower() == normalized_condition:
            return value
    return None 