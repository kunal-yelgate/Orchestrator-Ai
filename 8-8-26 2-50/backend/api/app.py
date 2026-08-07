from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router

app = FastAPI(
    title="Agentic AI Orchestrator API",
    description="Multi-Agent AI Orchestrator built using LangGraph and FastAPI",
    version="1.0.0",
)

# -----------------------------
# CORS Configuration
# -----------------------------
origins = [
    "http://localhost:5173",      # Vite
    "http://127.0.0.1:5173",
    "http://localhost:3000",      # React/Next.js
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(router)


@app.get("/ping")
def ping():
    return {
        "message": "API is running successfully 🚀"
    }