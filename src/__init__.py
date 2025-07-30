"""
OnCall.ai src package

This package contains the core implementation of the OnCall.ai system.
"""

# Version
__version__ = '0.1.0'

# import key modules
from .llm_clients import llm_Med42_70BClient
from .user_prompt import UserPromptProcessor
from .retrieval import BasicRetrievalSystem
from .medical_conditions import (
    CONDITION_KEYWORD_MAPPING,
    get_condition_keywords,
    validate_condition
) 