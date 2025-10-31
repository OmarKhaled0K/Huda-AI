from fastapi import APIRouter, HTTPException,Query
from utils.logging.logger_setup import setup_logger
from schemas.ayah_audio_schema import  AyahAudioResponse
from core.services.quran_audio_service import QuranService
from fastapi.responses import StreamingResponse
import requests

ayah_audio_router = APIRouter(prefix="/ayah_audio", tags=["Ayah Audio"])
logger = setup_logger()

@ayah_audio_router.get("/get_ayah_audio", response_model=AyahAudioResponse)
async def get_ayah_audio(
    surah: int = Query(..., ge=1, le=114, description="Surah number (1–114)"),
    ayah: int = Query(..., ge=1, description="Ayah number"),
    reciter_id: int = Query(1, ge=1, le=10, description="Reciter ID (1–5 usually)")   
    ):
    """
    Return the audio URL of a specific Ayah given Surah, Ayah, and Reciter ID.
    
    Args:
        surah (int): Surah number
        ayah (int): Ayah number
        reciter_id (int): ID of the reciter
        
    Returns:
        AyahAudioResponse: Audio metadata including URLs and reciter information
    """
    logger.info(f"Received request for Surah {surah}, Ayah {ayah}, Reciter {reciter_id}")
    result = QuranService.fetch_ayah_audio(surah, ayah, reciter_id)
    response = AyahAudioResponse(
            surah=result['surah'],
            ayah=result['ayah'],
            reciter_id=reciter_id,
            reciter_name=result['reciter_name'],
            audio_url=result['audio_url'],
            original_url=result['original_url']
        )
    return response

@ayah_audio_router.get("/stream_ayah_audio", responses={200: {"content": {"audio/mpeg": {}}}})
def stream_ayah_audio(
    surah: int = Query(..., ge=1, le=114, description="Surah number (1–114)"),
    ayah: int = Query(..., ge=1, description="Ayah number"),
    reciter_id: int = Query(1, ge=1, le=5, description="Reciter ID (1–5 usually)")
):
    """
    🎧 Stream the audio file of a specific Ayah directly.
    You can press ▶️ in Swagger UI to listen.
    """
    meta = QuranService.fetch_ayah_audio(surah, ayah, reciter_id)
    try:
        audio_resp = requests.get(meta['audio_url'], stream=True, timeout=15)
        audio_resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch audio file: {e}")

    # Stream audio to user
    return StreamingResponse(
        audio_resp.iter_content(chunk_size=8192),
        media_type="audio/mpeg",
        headers={
            "Content-Disposition": f'inline; filename="surah{surah}_ayah{ayah}.mp3"',
            "Cache-Control": "public, max-age=3600"
        }
    )
