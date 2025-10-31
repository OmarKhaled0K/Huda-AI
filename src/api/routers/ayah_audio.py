from fastapi import APIRouter, HTTPException
from ai.llms.llm_manager import get_llm
from utils.logging.logger_setup import setup_logger
from schemas.ayah_audio_schema import AyahAudioRequest, AyahAudioResponse
from core.services.quran_audio_service import QuranService

ayah_audio_router = APIRouter(prefix="/ayah_audio", tags=["Ayah Audio"])
logger = setup_logger()

@ayah_audio_router.post("/get_ayah_audio", response_model=AyahAudioResponse)
async def get_ayah_audio(req: AyahAudioRequest):
    """
    Return the audio URL of a specific Ayah given Surah, Ayah, and Reciter ID.
    
    Args:
        req (AyahAudioRequest): Request containing surah, ayah, and reciter_id
        
    Returns:
        AyahAudioResponse: Audio metadata including URLs and reciter information
    """
    logger.info(f"Received request for Surah {req.surah}, Ayah {req.ayah}, Reciter {req.reciter_id}")
    result = QuranService.fetch_ayah_audio(req.surah, req.ayah, req.reciter_id)
    response = AyahAudioResponse(
            surah=result['surah'],
            ayah=result['ayah'],
            reciter_id=req.reciter_id,
            reciter_name=result['reciter_name'],
            audio_url=result['audio_url'],
            original_url=result['original_url']
        )
    return response
