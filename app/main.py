from fastapi import FastAPI
from app.api.generation import router as generation_router

app = FastAPI(
    title="Evidence Graph",
    version="0.1.0",
    description="Minimal embedding → retrieval → generation pipeline.",
)

app.include_router(generation_router, prefix="/api")

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
