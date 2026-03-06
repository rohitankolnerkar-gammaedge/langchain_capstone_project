from fastapi import FastAPI
from app.api.user_input import input_query
from app.api.input_document import input_doc
from app.api.metrics import met
from app.api.evaluate import eval_router 
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
app = FastAPI()


app.include_router(input_query, prefix="/api")
app.include_router(input_doc, prefix="/api")
app.include_router(met )
app.include_router(eval_router, prefix="/api")
FastAPIInstrumentor.instrument_app(app)
@app.get("/")
def read_root():
    return {"hello": "world"}