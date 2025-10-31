from fastapi import FastAPI
from api.routers import basic_chat_router
from api.routers import ayah_audio_router
from utils.logging.logger_setup import setup_logger
from config.settings import get_settings

settings = get_settings()

app = FastAPI(title=settings.APP_NAME,
              version=settings.APP_VERSION,
              description="An AI-powered application for various tasks.")



logger = setup_logger()
logger.info("🚀 Huda AI logger initialized successfully.")

app.include_router(basic_chat_router,
                   prefix="/api/v1")
app.include_router(ayah_audio_router,
                   prefix="/api/v1")
# Healthy check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "env": settings.APP_ENV,
        "debug": settings.DEBUG
    }

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)