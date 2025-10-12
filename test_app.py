from __future__ import annotations
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database import connect_to_mongo, close_mongo_connection
from app.api.routes.cliente import router as cliente_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting MongoDB connection...")
    await connect_to_mongo()
    print("MongoDB connected successfully!")
    yield
    # Shutdown  
    print("Closing MongoDB connection...")
    await close_mongo_connection()
    print("MongoDB connection closed!")

app = FastAPI(
    title="Test Harmonização API", 
    version="1.0.0",
    lifespan=lifespan
)

if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Only include cliente router for testing
app.include_router(cliente_router)

@app.get("/")
async def root():
    return {"message": "Test API is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)