from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.user_input import input_query
from app.api.input_document import input_doc
from app.api.metrics import met
from app.api.evaluate import eval_router 
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
app = FastAPI()

STATIC_DIR = Path(__file__).resolve().parent / "static"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(input_query, prefix="/api")
app.include_router(input_doc, prefix="/api")
app.include_router(met )
app.include_router(eval_router, prefix="/api")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
FastAPIInstrumentor.instrument_app(app)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def read_root():
    return FileResponse(STATIC_DIR / "index.html")
