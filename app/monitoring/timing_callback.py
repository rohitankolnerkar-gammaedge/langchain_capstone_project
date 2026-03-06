import time
from langchain_core.callbacks import BaseCallbackHandler
from .mertics import LLM_LATENCY

class TimingCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        self.retriever_start = None
        self.llm_start = None


    def on_llm_start(self, *args, **kwargs):
        self.llm_start = time.perf_counter()

    def on_llm_end(self, *args, **kwargs):
        latency = (time.perf_counter() - self.llm_start) * 1000
        print(f"[METRIC] LLM latency: {latency:.2f} ms")
        LLM_LATENCY.observe(latency / 1000)