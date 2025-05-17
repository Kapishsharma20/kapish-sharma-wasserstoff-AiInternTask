from fastapi import FastAPI
from app.api.endpoints import router as api_router
from app.core.database import database
from app.config import settings

app = FastAPI(title="Document Analyzer")

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    try:
        await database.execute("SELECT 1")
        return {"status": "OK", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": str(e)}
