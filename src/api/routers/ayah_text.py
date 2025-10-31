
from fastapi import APIRouter, HTTPException,Query
from utils.logging.logger_setup import setup_logger
from schemas.holy_quraan_schema import  AyahTextResponse
import requests
from core.services.quran_service import QuranService

ayah_text_router = APIRouter(prefix="/ayah_text", tags=["Ayah Text"])
logger = setup_logger()

@ayah_text_router.get("/ayah/", response_model=AyahTextResponse)
def get_ayah(surah_number: int = Query(..., ge=1, le=114),
             ayah_number: int = Query(..., ge=1)):
    """
    Get a single Ayah in both Arabic and English.
    Inputs:
    - surah_number: 1-114
    - ayah_number: ayah number within the surah
    """
    logger.info(f"Received text request for Surah number {surah_number}, Ayah {ayah_number}")
    try:
        # ayah = fetch_ayah(surah_number, ayah_number)
        result = QuranService.fetch_ayah_text(surah_number=surah_number, ayah_number=ayah_number)
        ayah = AyahTextResponse(
            surah_number=result['surah_number'],
            surah_name_ar=result['surah_name_ar'],
            surah_name_en=result['surah_name_en'],
            ayah_number=result['ayah_number'],
            ayah_text_ar=result['ayah_text_ar'],
            ayah_text_en=result['ayah_text_en']
        )
        return ayah
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching Ayah text: {e}")
        raise HTTPException(status_code=500, detail=str(e))
