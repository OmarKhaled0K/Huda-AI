from fastapi import APIRouter, UploadFile, File, HTTPException
from schemas.holy_quraan_schema import (
    DuaaBatch,

)
import json
from ai.vector_db.qdrant_db import QdrantVectorStore
from utils.logging import setup_logger
from typing import List
import time
import uuid
from core.services.duaa_service import DuaaService
batch_database_router = APIRouter(prefix="/chat", tags=["Batch Database"])
logger = setup_logger("app.db_endpoint")


vector_store = QdrantVectorStore()
#TODO: Replace with actual embedding function
def embed_text(text: str, size: int = 1536) -> List[float]:
    # simple placeholder vector
    return [0.0] * size


@batch_database_router.post("/upload-duaas", summary="Upload multiple duas from JSON")
async def upload_duaas(file: UploadFile = File(...)):
    start_ts = time.perf_counter()
    logger.info("upload_duaas called", extra={"filename": file.filename})

    if not file.filename.endswith(".json"):
        logger.warning("Uploaded file rejected - not a JSON file: %s", file.filename)
        raise HTTPException(status_code=400, detail="File must be a JSON file")

    # Load JSON from uploaded file
    content = await file.read()
    logger.debug("Read uploaded file bytes=%d filename=%s", len(content or b""), file.filename)
    try:
        data = json.loads(content)
    except json.JSONDecodeError as e:
        logger.warning("Invalid JSON file uploaded: %s error=%s", file.filename, e)
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    # Support both single batch or a list of batches
    batches = data if isinstance(data, list) else [data]
    logger.info("Parsed upload into %d batch(es) from file=%s", len(batches), file.filename)

    inserted_ids: List[str] = []
    failures: List[dict] = []

    for batch_index, batch in enumerate(batches, start=1):
        logger.debug("Processing batch %d: %s", batch_index, {k: v for k, v in (batch.items() if isinstance(batch, dict) else [])})
        try:
            batch_obj = DuaaBatch(**batch)  # validate and parse
        except Exception as e:
            logger.exception("Batch validation failed index=%d file=%s", batch_index, file.filename)
            failures.append({"batch_index": batch_index, "error": str(e)})
            # skip this batch and continue with others
            continue

        for dua in batch_obj.duas:
            try:
                # Compute embedding for each dua
                embedding = embed_text(dua.arabic)
                duaa_id = str(uuid.uuid4())

                # Insert into vector store (Qdrant)
                res = await vector_store.insert_duaa(
                    duaa_id=duaa_id,
                    feeling=batch_obj.feeling,
                    url=batch_obj.url,
                    dua_number=dua.number,
                    arabic=dua.arabic,
                    transliteration=dua.transliteration,
                    translation=dua.translation,
                    source=dua.source,
                    embedding=embedding,
                    duas_count=batch_obj.duas_count,
                )
                inserted_ids.append(res["id"])
                logger.debug("Inserted duaa id=%s dua_number=%s batch_index=%d", res["id"], dua.number, batch_index)
            except Exception as e:
                logger.exception("Failed to insert dua number=%s in batch_index=%d file=%s", dua.number, batch_index, file.filename)
                failures.append({"batch_index": batch_index, "dua_number": getattr(dua, 'number', None), "error": str(e)})
                # continue to next dua
                continue

    duration = time.perf_counter() - start_ts
    logger.info("upload_duaas completed file=%s inserted=%d failed=%d duration=%.3fs", file.filename, len(inserted_ids), len(failures), duration)

    return {"status": "ok", "inserted_ids": inserted_ids, "total_inserted": len(inserted_ids), "failures": failures}

@batch_database_router.get("/get_duaa", summary="get quaa based on feeling")
async def get_duaa(feeling: str):
    start_ts = time.perf_counter()
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

@batch_database_router.post("/generate_duaa", summary="Generate a duaa based on feeling and context")
async def generate_duaa(feeling: str, ):
    start_ts = time.perf_counter()
    try:
        results = await vector_store.search_by_metadata(collection="duaas",
                                                       metadata_filters={"feeling": feeling},
                                                       limit=10)
        payloads = [item["payload"] for item in results if "payload" in item]
        
    except Exception as e:
        logger.exception("Failed to get duaa for feeling=%s", feeling)
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
    duaa_service = DuaaService()
    duaa_text = await duaa_service.generate_duaa_llm(feeling=feeling, context=payloads)
    duration = time.perf_counter() - start_ts
    logger.info("generate_duaa completed feeling=%s duration=%.3fs", feeling, duration)

    return {"status": "ok", "duaa": duaa_text}