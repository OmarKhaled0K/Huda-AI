from fastapi import FastAPI
from routers import basic_chat
app = FastAPI(title="Huda AI")
app.include_router(basic_chat.router)
# Healthy check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)