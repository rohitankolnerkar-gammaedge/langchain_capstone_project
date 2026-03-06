from prometheus_client import Counter, Histogram, Gauge


REQUEST_COUNT = Counter(
    "rag_requests_total",
    "Total RAG requests"
)

REQUEST_ERRORS = Counter(
    "rag_request_errors_total",
    "Total failed RAG requests"
)


RETRIEVAL_LATENCY = Histogram(
    "rag_retrieval_latency_seconds",
    "Time spent in retrieval"
)

LLM_LATENCY = Histogram(
    "rag_llm_latency_seconds",
    "Time spent in LLM generation"
)

TOTAL_LATENCY = Histogram(
    "rag_total_latency_seconds",
    "Total request processing time"
)

PDF_LOADING_LATENCY = Histogram(
    "rag_pdf_loading_latency_seconds",
    "Time spent loading PDF"
)

PDF_SPLITTING_LATENCY = Histogram(
    "rag_pdf_splitting_latency_seconds",
    "Time spent splitting documents"
)

PDF_EMBEDDING_LATENCY = Histogram(
    "rag_pdf_embedding_latency_seconds",
    "Time spent embedding and storing vectors"
)

PDF_TOTAL_INGESTION_LATENCY = Histogram(
    "rag_pdf_total_ingestion_latency_seconds",
    "Total ingestion pipeline latency"
)
GROUNDED_ANSWERS = Counter("rag_grounded_total", "Grounded answers")
UNGROUNDED_ANSWERS = Counter("rag_ungrounded_total", "Ungrounded answers")

RETRIEVAL_ACCURACY = Gauge(
    "rag_retrieval_accuracy",
    "Current retrieval accuracy score"
)