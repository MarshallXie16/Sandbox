"""
VaultAI Integration Layer - Database Models
"""

from app.models.prompt_template import PromptTemplate
from app.models.llm_log import LLMLog
from app.models.document import Document
from app.models.embedding import Embedding

__all__ = [
    "PromptTemplate",
    "LLMLog",
    "Document",
    "Embedding",
]
