from langchain_ollama import ChatOllama



def get_llm(
    temperature: float = 0,
    max_tokens: int = 256,
    model_name: str = "phi",):
    
    return ChatOllama(
        model=model_name,
        temperature=temperature,
        num_predict=max_tokens,
        streaming=True,
        
    )