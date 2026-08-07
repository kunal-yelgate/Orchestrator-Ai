from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="Agentic AI Orchestrator API",
    description="Multi-Agent AI Orchestrator built using LangGraph and FastAPI",
    version="1.0.0"
)

# Include all API routes
app.include_router(router)

# Optional root endpoint (if not already defined in routes.py)
@app.get("/ping")
def ping():
    return {
        "message": "API is running successfully 🚀"
    }