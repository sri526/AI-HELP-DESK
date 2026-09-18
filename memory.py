"""
Conversation memory for the IT Helpdesk Agent.
"""

from config import MAX_MEMORY_MESSAGES


class ConversationMemory:
    """Stores recent user and assistant messages."""

    def __init__(self):
        self.messages = []

    def add_user_message(self, message: str):
        self.messages.append(
            {
                "role": "user",
                "content": message,
            }
        )
        self._limit_memory()

    def add_assistant_message(self, message: str):
        self.messages.append(
            {
                "role": "assistant",
                "content": message,
            }
        )
        self._limit_memory()

    def get_messages(self):
        return self.messages.copy()

    def get_formatted_history(self):
        if not self.messages:
            return "No previous conversation."

        history = []

        for message in self.messages:
            role = message["role"].capitalize()
            content = message["content"]

            history.append(f"{role}: {content}")

        return "\n".join(history)

    def clear(self):
        self.messages.clear()

    def _limit_memory(self):
        self.messages = self.messages[-MAX_MEMORY_MESSAGES:]