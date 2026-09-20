from fastapi import FastAPI

from app.api.generation import router as generation_router


app = FastAPI(
    title="Evidence Graph API",
    version="0.1.0",
    description="Evidence-grounded retrieval and generation API.",
)


app.include_router(generation_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "evidence-graph",
    }