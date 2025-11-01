from fastapi import APIRouter, UploadFile, File, HTTPException
from schemas.holy_quraan_schema import (
    DuaaBatch,

)
import json
from ai.vector_db.qdrant_db import QdrantVectorStore
from utils.logging import setup_logger
from typing import List
batch_database_router = APIRouter(prefix="/chat", tags=["Batch Database Upload"])
logger = setup_logger("app.db_endpoint")


vector_store = QdrantVectorStore()
#TODO: Replace with actual embedding function
def embed_text(text: str, size: int = 1536) -> List[float]:
    # simple placeholder vector
    return [0.0] * size


@batch_database_router.post("/upload-duaas", summary="Upload multiple duas from JSON")
async def upload_duaas(file: UploadFile = File(...)):
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="File must be a JSON file")

    # Load JSON from uploaded file
    content = await file.read()
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")

    # Support both single batch or a list of batches
    batches = data if isinstance(data, list) else [data]
    inserted_ids = []

    for batch in batches:
        batch_obj = DuaaBatch(**batch)  # validate and parse

        for dua in batch_obj.duas:
            # Compute embedding for each dua
            embedding = embed_text(dua.arabic)

            # Insert into vector store (Qdrant)
            res = await vector_store.insert_duaa(
                duaa_id=None,
                feeling=batch_obj.feeling,
                url=batch_obj.url,
                dua_number=dua.number,
                arabic=dua.arabic,
                transliteration=dua.transliteration,
                translation=dua.translation,
                source=dua.source,
                embedding=embedding,
                duas_count=batch_obj.duas_count
            )
            inserted_ids.append(res["id"])

    return {"status": "ok", "inserted_ids": inserted_ids, "total_inserted": len(inserted_ids)}