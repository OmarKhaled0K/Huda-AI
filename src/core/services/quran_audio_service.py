import requests
from fastapi import HTTPException
from schemas.ayah_audio_schema import AyahAudioResponse
from utils.logging.logger_setup import setup_logger

logger = setup_logger()

class QuranService:
    @staticmethod
    def fetch_ayah_audio(surah: int, ayah: int, reciter_id: int) -> dict:
        """
        Fetch audio metadata for a given surah, ayah, and reciter from Quran API.
        
        Args:
            surah (int): Surah number
            ayah (int): Ayah number
            reciter_id (int): ID of the reciter
            
        Returns:
            result: Audio metadata including URLs and reciter information
            
        Raises:
            HTTPException: If API request fails or reciter is not found
        """
        base_url = f"https://quranapi.pages.dev/api/audio/{surah}/{ayah}.json"
        try:
            logger.info(f"Fetching audio for Surah {surah}, Ayah {ayah}, Reciter {reciter_id}")
            resp = requests.get(base_url, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch audio: {e}")
            raise HTTPException(status_code=502, detail=f"Error contacting Quran API: {e}")

        data = resp.json()
        reciter_key = str(reciter_id)
        if reciter_key not in data:
            logger.warning(f"Reciter {reciter_id} not found for Surah {surah}, Ayah {ayah}")
            raise HTTPException(
                status_code=404,
                detail=f"Reciter with ID {reciter_id} not found for Surah {surah}, Ayah {ayah}. "
                       f"Available reciters: {list(data.keys())}"
            )

        entry = data[reciter_key]
        logger.info(f"Successfully fetched audio for Surah {surah}, Ayah {ayah}, Reciter {reciter_id}")
        result = {"surah": surah, "ayah": ayah, "reciter_id": reciter_id, "reciter_name": entry.get("reciter", "Unknown"),
                "audio_url": entry.get("url"), "original_url": entry.get("originalUrl")}
        return result