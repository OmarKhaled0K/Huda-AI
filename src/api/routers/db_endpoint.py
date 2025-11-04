from fastapi import APIRouter, HTTPException
from schemas.holy_quraan_schema import (
    AyahCreate,
    TafsirCreate,
    HadithCreate,
)
from ai.vector_db.qdrant_db import QdrantVectorStore
from utils.logging import setup_logger
from typing import List
vector_database_router = APIRouter(prefix="/chat", tags=["Basic Chat"])
logger = setup_logger("app.db_endpoint")


vector_store = QdrantVectorStore()
#TODO: Replace with actual embedding function
def embed_text(text: str, size: int = 1536) -> List[float]:
    # simple placeholder vector
    return [0.0] * size
@vector_database_router.post("/ayahs", summary="Add a Surah/Ayah")
async def add_ayah(ayah: AyahCreate):
    embedding = embed_text(ayah.text)
    res = await vector_store.insert_ayah(
        ayah_id=None,
        surah_number=ayah.surah_number,
        ayah_number=ayah.ayah_number,
        juz_number=ayah.juz_number,
        text=ayah.text,
        transliteration=ayah.transliteration,
        translation=ayah.translation,
        ayah_type=ayah.ayah_type,
        feelings=ayah.feelings,
        embedding=embedding
    )
    return {"status": "ok", "id": res["id"]}

@vector_database_router.post("/tafseers", summary="Add a Tafsir")
async def add_tafseer(tafseer: TafsirCreate):
    embedding = embed_text(tafseer.text)
    res = await vector_store.insert_tafseer(
        tafseer_id=None,
        referenced_ayahs=tafseer.referenced_ayahs,
        text=tafseer.text,
        tafseer_type=tafseer.tafseer_type,
        translation=tafseer.translation,
        feelings=tafseer.feelings,
        embedding=embedding
    )
    return {"status": "ok", "id": res["id"]}

@vector_database_router.post("/hadiths", summary="Add a Hadith")
async def add_hadith(hadith: HadithCreate):
    embedding = embed_text(hadith.text)
    res = await vector_store.insert_hadith(
        hadith_id=None,
        hadith_number=hadith.hadith_number,
        source_collection=hadith.source_collection,
        text=hadith.text,
        transliteration=hadith.transliteration,
        translation=hadith.translation,
        explanation=hadith.explanation,
        feelings=hadith.feelings,
        embedding=embedding
    )
    return {"status": "ok", "id": res["id"]}
