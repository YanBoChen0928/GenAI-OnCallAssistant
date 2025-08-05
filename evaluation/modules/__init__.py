"""
Evaluation modules for OnCall.ai system testing.

This package contains modular evaluation components for testing
the OnCall.ai medical query processing pipeline.
"""

from .query_executor import QueryExecutor

__version__ = "1.0.0"
__all__ = ["QueryExecutor", "query_executor"]