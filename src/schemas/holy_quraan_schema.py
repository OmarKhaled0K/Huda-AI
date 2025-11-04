from pydantic import BaseModel, Field
from typing import List, Optional
class AyahTextResponse(BaseModel):
    surah_number: int
    surah_name_ar: str
    surah_name_en: str
    ayah_number: int
    ayah_text_ar: str
    ayah_text_en: str

class AyahAudioRequest(BaseModel):
    surah: int = Field(..., ge=1, le=114, description="Surah number (1–114)")
    ayah: int = Field(..., ge=1, description="Ayah number")
    reciter_id: int = Field(1, ge=1, le=10, description="Reciter ID (1–5 usually)")


class AyahAudioResponse(BaseModel):
    surah: int
    ayah: int
    reciter_id: int
    reciter_name: str
    audio_url: str | None = None
    original_url: str | None = None
class AyahCreate(BaseModel):
    surah_number: int
    ayah_number: int
    juz_number: Optional[int]
    text: str
    transliteration: Optional[str]
    translation: Optional[str]
    ayah_type: Optional[str] = Field(description="Makki or Madani")
    feelings: Optional[List[str]] = []

class TafsirCreate(BaseModel):
    referenced_ayahs: List[dict]  # [{"surah_number":1, "ayah_number":1}, ...]
    text: str
    tafseer_type: str
    translation: Optional[str]
    feelings: Optional[List[str]] = []

class HadithCreate(BaseModel):
    hadith_number: Optional[str]
    source_collection: Optional[str]
    text: str
    transliteration: Optional[str]
    translation: Optional[str]
    explanation: Optional[str]
    feelings: Optional[List[str]] = []

class DuaaCreate(BaseModel):
    feeling: str
    url: str
    dua_number: str
    arabic: str
    transliteration: Optional[str]
    translation: Optional[str]
    source: Optional[str]
    duas_count: Optional[int] = None

#TODO: Remove duplication with DuaaCreate
class DuaaItem(BaseModel):
    duaa_id: str
    arabic: str
    transliteration: str
    translation: str
    source: Optional[str]

class DuaaBatch(BaseModel):
    feeling: str
    url: str
    duas_count: int
    duas: List[DuaaItem] | DuaaItem
