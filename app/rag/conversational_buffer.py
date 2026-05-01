from collections import deque


class RollingChatMemory:
    def __init__(self, k: int = 5):
        self.messages = deque(maxlen=k * 2)

    def load_memory_variables(self, _inputs):
        return {
            "chat_history": list(self.messages)
        }

    def save_context(self, inputs, outputs):
        self.messages.append({
            "role": "user",
            "content": inputs.get("input", "")
        })
        self.messages.append({
            "role": "assistant",
            "content": outputs.get("result", "")
        })

def buffer_memory():
    return RollingChatMemory(k=5)

