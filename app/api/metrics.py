from prometheus_client import generate_latest
from fastapi.responses import Response
from fastapi import  APIRouter
met=APIRouter()
@met.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")