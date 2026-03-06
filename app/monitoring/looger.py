import logging
import json
import os
from datetime import datetime



os.makedirs("logs", exist_ok=True)


log_filename = f"logs/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


class JsonFormatter(logging.Formatter):

    def format(self, record):

        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),

          
            "file": record.filename,
            "function": record.funcName,
            "line": record.lineno,

            "question": getattr(record, "question", None),
            "user_role": getattr(record, "user_role", None),

            "retrieved_docs": getattr(record, "retrieved_docs", None),
            "retrieval_latency": getattr(record, "retrieval_latency", None),

            "llm_latency": getattr(record, "llm_latency", None),
            "answer_length": getattr(record, "answer_length", None),

            "grounded": getattr(record, "grounded", None),

            "total_latency": getattr(record, "total_latency", None),
            "error": getattr(record, "error", None)
        }

        return json.dumps(log_record,indent=4)


logger = logging.getLogger("rag_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:

    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.INFO)

    formatter = JsonFormatter()
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)


    logger.propagate = False