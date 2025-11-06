from fastapi import FastAPI, Depends
from api.routers.v1.conversation_history import conversation_history_router
from core.db import get_db
from fastapi.middleware.cors import CORSMiddleware
from core.settings import get_settings

settings = get_settings()
app = FastAPI(title=settings.APP_NAME,
             description="API for Huda AI conversation history management",
             version=settings.APP_VERSION)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def read_root():
    return {
        "status": "healthy",
        "message": "Huda AI API is running"
    }

app.include_router(conversation_history_router)
