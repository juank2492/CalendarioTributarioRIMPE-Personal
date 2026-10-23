from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.middleware.logging_lopdp import LoggingLOPDPMiddleware
from backend.routers.calendario_router import router as calendario_router
from backend.routers.obligaciones_router import router as obligaciones_router

app = FastAPI(
    title="Calendario Tributario RIMPE - API",
    description="Motor determinista y explicaciones RAG con Google Gemini Flash",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingLOPDPMiddleware)

app.include_router(calendario_router)
app.include_router(obligaciones_router)

@app.get("/health", tags=["Salud"])
def health_check():
    return {"status": "healthy", "service": "RIMPE Compliance Core"}
