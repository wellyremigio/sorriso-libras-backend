from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.config import get_settings
from app.database.mongodb import close_mongo_connection, connect_to_mongo
from app.routes.video_routes import router as video_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Sorriso Libras API",
    description="API do aplicativo Sorriso Libras",
    version= "1.0.0",
    lifespan=lifespan
)

app.include_router(video_router)

@app.get("/")
def read_root():
    return {
        "message": "API Sorriso libras funcionando!"
    }
    
    
@app.get("/health")
def health_check():
    return {
        "status": "ok"
    }