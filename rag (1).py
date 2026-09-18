"""
Simple RAG implementation using Ollama embeddings.
"""

import os
from pathlib import Path

import numpy as np
import requests

from config import (
    OLLAMA_BASE_URL,
    EMBEDDING_MODEL,
    KNOWLEDGE_BASE_DIR,
    TOP_K_RESULTS,
)


class KnowledgeBase:
    """Manages documents and semantic retrieval."""

    def __init__(self):
        self.documents = []

    def load_documents(self):
        """Load text documents from the knowledge-base directory."""

        folder = Path(KNOWLEDGE_BASE_DIR)

        if not folder.exists():
            raise FileNotFoundError(
                f"Knowledge base directory not found: {folder}"
            )

        self.documents.clear()

        for file_path in sorted(folder.glob("*.txt")):
            text = file_path.read_text(encoding="utf-8").strip()

            if text:
                self.documents.append(
                    {
                        "filename": file_path.name,
                        "text": text,
                        "embedding": None,
                    }
                )

        if not self.documents:
            raise RuntimeError(
                "No .txt files were found in the knowledge_base folder."
            )

    def _get_embedding(self, text: str):
        """Generate an embedding using Ollama."""

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text,
            },
            timeout=60,
        )

        response.raise_for_status()

        data = response.json()

        if "embedding" not in data:
            raise RuntimeError(
                "Ollama did not return an embedding."
            )

        return np.array(data["embedding"], dtype=np.float32)

    @staticmethod
    def _cosine_similarity(vector_a, vector_b):
        """Calculate cosine similarity."""

        denominator = (
            np.linalg.norm(vector_a) *
            np.linalg.norm(vector_b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(vector_a, vector_b) / denominator
        )

    def create_embeddings(self):
        """Create embeddings for all loaded documents."""

        for document in self.documents:
            document["embedding"] = self._get_embedding(
                document["text"]
            )

    def search(self, query: str, top_k: int = TOP_K_RESULTS):
        """Retrieve the most relevant documents."""

        if not self.documents:
            self.load_documents()

        if any(
            document["embedding"] is None
            for document in self.documents
        ):
            self.create_embeddings()

        query_embedding = self._get_embedding(query)

        scored_documents = []

        for document in self.documents:

            score = self._cosine_similarity(
                query_embedding,
                document["embedding"],
            )

            scored_documents.append(
                {
                    "filename": document["filename"],
                    "text": document["text"],
                    "score": score,
                }
            )

        scored_documents.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return scored_documents[:top_k]

    def format_results(self, results):
        """Convert retrieval results into prompt-ready text."""

        if not results:
            return "No relevant knowledge-base information found."

        sections = []

        for result in results:
            sections.append(
                f"Source: {result['filename']}\n"
                f"Relevance score: {result['score']:.3f}\n"
                f"{result['text']}"
            )

        return "\n\n---\n\n".join(sections)