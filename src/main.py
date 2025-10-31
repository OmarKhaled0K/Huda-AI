from fastapi import FastAPI
from api.routers import basic_chat
from utils.logging.logger_setup import setup_logger
app = FastAPI(title="Huda AI",
              version="1.0.0",
              description="An AI-powered application for various tasks.")



logger = setup_logger()
logger.info("🚀 Huda AI logger initialized successfully.")

app.include_router(basic_chat.router,
                   prefix="/api/v1")
# Healthy check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)