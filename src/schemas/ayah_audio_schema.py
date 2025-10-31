from pydantic import BaseModel, Field

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