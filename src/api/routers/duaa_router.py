from fastapi import APIRouter, HTTPException

from ai.vector_db.qdrant_db import QdrantVectorStore
from utils.logging import setup_logger
import time
from core.services.duaa_service import DuaaService
from schemas.holy_quraan_schema import (
    DuaaBatch,
)
from ai.embeddings.embedding_manager import get_embedding
duaa_router = APIRouter(prefix="/chat", tags=["Duaa Router"])
logger = setup_logger("app.db_endpoint")




@duaa_router.get("/initialize-duaa-service", summary="Initialize Duaa Service and populate vector DB if empty")
async def initialize_duaa_service():
    start_ts = time.perf_counter()
    logger.info("initialize_duaa_service called")
    duaa_service = DuaaService()
    await duaa_service.initialize_duaa_service()
    duration = time.perf_counter() - start_ts
    logger.info("initialize_duaa_service completed duration=%.3fs", duration)
    return {"status": "ok", "message": "Duaa Service initialized"}




@duaa_router.get("/get_duaa", summary="get quaa based on feeling")
async def get_duaa(feeling: str):

    start_ts = time.perf_counter()
    vector_store = QdrantVectorStore()
    logger.info("get_duaa called", extra={"feeling": feeling})

    try:
        results = await vector_store.search_by_metadata(collection="duaas",
                                                       metadata_filters={"feeling": feeling},
                                                       limit=10)
        
    except Exception as e:
        logger.exception("Failed to get duaa for feeling=%s", feeling)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    duration = time.perf_counter() - start_ts
    logger.info("get_duaa completed feeling=%s results=%d duration=%.3fs", feeling, len(results), duration)

    return {"status": "ok", "results": results}

@duaa_router.post("/generate_duaa", summary="Generate a duaa based on feeling and context")
async def generate_duaa(feeling: str, ):
    start_ts = time.perf_counter()
    
    duaa_service = DuaaService()
    duaa_text = await duaa_service.generate_duaa_llm(feeling=feeling)
    duration = time.perf_counter() - start_ts
    logger.info("generate_duaa completed feeling=%s duration=%.3fs", feeling, duration)

    return {"status": "ok", "duaa": duaa_text}

@duaa_router.post("/add_duaa", summary="Add a Duaa")
async def add_duaa(duaa: DuaaBatch):
    duaa_service = DuaaService()
    res_list = []
    for d in duaa.duas:
        res = await duaa_service.add_duaa(
            duaa_id=d.duaa_id,
            feeling=duaa.feeling,
            url=duaa.url,
            arabic=d.arabic,
            transliteration=d.transliteration,
            translation=d.translation,
            source=d.source,
            duas_count=duaa.duas_count
        )
        res_list.append(res)
    return {"status": "ok", "id": res_list}



@duaa_router.delete("/delete_duaa", summary="Delete a Duaa by ID")
async def delete_duaa(duaa_id: str):
    duaa_service = DuaaService()
    success = await duaa_service.delete_duaa(duaa_id)
    if not success:
        raise HTTPException(status_code=404, detail="Duaa not found")
    return {"status": "ok", "message": "Duaa deleted successfully"}
