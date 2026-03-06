from langchain_classic.memory import ConversationBufferWindowMemory

def buffer_memory():
    memory = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True,output_key="result", k=5)
    return memory


