from langchain_core.callbacks import BaseCallbackHandler
from prometheus_client import Counter
from app.monitoring.mertics import PROMPT_TOKENS, COMPLETION_TOKENS


class TokenUsageCallback(BaseCallbackHandler):

    def on_llm_end(self, response, **kwargs):

        if "token_usage" in response.llm_output:

            usage = response.llm_output["token_usage"]

            PROMPT_TOKENS.inc(usage.get("prompt_tokens", 0))
            COMPLETION_TOKENS.inc(usage.get("completion_tokens", 0))