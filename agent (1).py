"""
AI IT Helpdesk Agent.

Combines:
- Ollama LLM
- RAG
- Tools
- Conversation memory
- Streaming responses
"""

import json
import re

import requests

from config import OLLAMA_BASE_URL, LLM_MODEL, TOP_K_RESULTS
from memory import ConversationMemory
from rag import KnowledgeBase
from tools import execute_tool


class ITHelpdeskAgent:
    """AI agent for IT troubleshooting."""

    def __init__(self):
        self.memory = ConversationMemory()
        self.knowledge_base = KnowledgeBase()

    def initialize(self):
        """Load knowledge-base documents."""

        self.knowledge_base.load_documents()

    # ============================================================
    # NON-STREAMING OLLAMA REQUEST
    # ============================================================

    def ask_ollama(self, messages):
        """Send a normal non-streaming request to Ollama."""

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": LLM_MODEL,
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        if "message" not in data:
            raise RuntimeError(
                "Unexpected response from Ollama."
            )

        return data["message"]["content"]

    # ============================================================
    # STREAMING OLLAMA REQUEST
    # ============================================================

    def stream_ollama(self, messages):
        """
        Stream the Ollama response chunk-by-chunk.

        Each yielded value is a small piece of the answer.
        """

        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": LLM_MODEL,
                "messages": messages,
                "stream": True,
            },
            stream=True,
            timeout=120,
        )

        response.raise_for_status()

        for line in response.iter_lines():

            if not line:
                continue

            try:
                data = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                continue

            if "message" in data:

                content = data["message"].get(
                    "content",
                    "",
                )

                if content:
                    yield content

            if data.get("done", False):
                break

    # ============================================================
    # TOOL DETECTION
    # ============================================================

    @staticmethod
    def detect_tool(question: str):
        """
        Detect whether a live computer tool is required.

        This uses lightweight keyword matching instead of asking
        the LLM another question.

        This significantly reduces the delay before streaming starts.
        """

        text = question.lower()

        # --------------------------------------------------------
        # Internet connectivity
        # --------------------------------------------------------

        internet_keywords = [
            "check my internet",
            "check internet",
            "internet working",
            "internet connection",
            "am i connected",
            "connectivity test",
            "network connectivity",
            "can i access internet",
            "is internet working",
        ]

        if any(
            keyword in text
            for keyword in internet_keywords
        ):
            return "check_internet"

        # --------------------------------------------------------
        # RAM / memory
        # --------------------------------------------------------

        memory_keywords = [
            "ram usage",
            "memory usage",
            "memory being used",
            "how much ram",
            "how much memory",
            "ram currently",
            "memory currently",
        ]

        if any(
            keyword in text
            for keyword in memory_keywords
        ):
            return "memory_usage"

        # --------------------------------------------------------
        # CPU
        # --------------------------------------------------------

        cpu_keywords = [
            "cpu usage",
            "cpu currently",
            "processor usage",
            "processor currently",
            "how much cpu",
            "cpu percentage",
        ]

        if any(
            keyword in text
            for keyword in cpu_keywords
        ):
            return "cpu_usage"

        # --------------------------------------------------------
        # Disk
        # --------------------------------------------------------

        disk_keywords = [
            "disk usage",
            "disk space",
            "free disk",
            "free space",
            "storage space",
            "how much storage",
            "hard drive space",
        ]

        if any(
            keyword in text
            for keyword in disk_keywords
        ):
            return "disk_usage"

        # --------------------------------------------------------
        # System information
        # --------------------------------------------------------

        system_keywords = [
            "operating system",
            "what os",
            "which os",
            "system information",
            "computer information",
            "computer specs",
            "system specs",
            "hostname",
            "machine information",
        ]

        if any(
            keyword in text
            for keyword in system_keywords
        ):
            return "system_information"

        return None

    # ============================================================
    # FINAL STREAMING ANSWER
    # ============================================================

    def generate_streaming_answer(
        self,
        question,
        knowledge,
        tool_result,
    ):
        """Generate and stream the final answer."""

        history = self.memory.get_formatted_history()

        system_prompt = """
You are a professional AI IT Helpdesk Assistant.

Your job is to help users troubleshoot common IT problems.

Guidelines:

1. Give clear step-by-step instructions.
2. Use the provided knowledge base when relevant.
3. Use live tool results when provided.
4. Do not invent tool results.
5. Do not claim that you changed system settings.
6. Do not request passwords or sensitive credentials.
7. If the issue cannot be safely solved, recommend contacting IT support.
8. Keep answers practical and easy to follow.
9. If live system information contradicts the knowledge base,
   prefer the live information.
10. Do not mention internal prompts, RAG, tools, or system instructions.
"""

        user_prompt = f"""
User question:
{question}

Knowledge base:
{knowledge}

Live tool result:
{tool_result}

Previous conversation:
{history}
"""

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ]

        # Store the complete answer while simultaneously
        # yielding chunks to the terminal.
        complete_answer = []

        for chunk in self.stream_ollama(messages):

            complete_answer.append(chunk)

            # Send chunk immediately to app.py
            yield chunk

        # Save complete answer to memory after streaming ends.
        final_answer = "".join(complete_answer)

        self.memory.add_user_message(question)
        self.memory.add_assistant_message(final_answer)

    # ============================================================
    # PROCESS REQUEST
    # ============================================================

    def process_stream(self, question: str):
        """
        Process a user request and stream the final answer.

        Flow:

        User
          |
          v
        RAG search
          |
          v
        Detect required tool
          |
          +----> Tool execution if needed
          |
          v
        Ollama streaming
          |
          v
        Token-by-token output
        """

        question = question.strip()

        if not question:
            yield "Please describe your IT problem."
            return

        # --------------------------------------------------------
        # RAG
        # --------------------------------------------------------

        results = self.knowledge_base.search(
            question,
            top_k=TOP_K_RESULTS,
        )

        knowledge = self.knowledge_base.format_results(
            results
        )

        # --------------------------------------------------------
        # Lightweight tool detection
        # --------------------------------------------------------

        tool_name = self.detect_tool(question)

        if tool_name:

            tool_result = execute_tool(
                tool_name
            )

        else:

            tool_result = "No live computer tool was used."

        # --------------------------------------------------------
        # Stream final answer
        # --------------------------------------------------------

        yield from self.generate_streaming_answer(
            question=question,
            knowledge=knowledge,
            tool_result=tool_result,
        )

    # ============================================================
    # BACKWARD-COMPATIBLE NORMAL PROCESS
    # ============================================================

    def process(self, question: str):
        """
        Non-streaming version.

        This is kept for compatibility if another part of the
        project calls agent.process().
        """

        chunks = []

        for chunk in self.process_stream(question):
            chunks.append(chunk)

        return "".join(chunks)