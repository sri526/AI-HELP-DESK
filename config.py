"""
Configuration for the AI IT Helpdesk Agent.
"""

OLLAMA_BASE_URL = "http://localhost:11434"


LLM_MODEL = "llama3.2:3b"


EMBEDDING_MODEL = "nomic-embed-text"

KNOWLEDGE_BASE_DIR = "knowledge_base"


TOP_K_RESULTS = 3


MAX_MEMORY_MESSAGES = 10