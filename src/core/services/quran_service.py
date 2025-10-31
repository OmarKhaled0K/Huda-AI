import requests
from fastapi import HTTPException
from schemas.holy_quraan_schema import AyahAudioResponse
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
    @staticmethod
    def fetch_ayah_text(surah_number: int, ayah_number: int,
               arabic_edition: str = "quran-uthmani",
               english_edition: str = "en.asad") -> dict:
        """
        Fetches a single Ayah with both Arabic and English text and Surah info.
        """
        BASE_URL = "https://api.alquran.cloud/v1"
        reference = f"{surah_number}:{ayah_number}"

        # Arabic edition
        arabic_resp = requests.get(f"{BASE_URL}/ayah/{reference}/{arabic_edition}")
        if arabic_resp.status_code != 200:
            raise HTTPException(status_code=arabic_resp.status_code, detail="Failed to fetch Arabic text.")
        arabic_data = arabic_resp.json()
        if arabic_data["status"] != "OK":
            raise HTTPException(status_code=500, detail=f"Arabic API error: {arabic_data}")

        # English edition
        english_resp = requests.get(f"{BASE_URL}/ayah/{reference}/{english_edition}")
        if english_resp.status_code != 200:
            logger.error(f"Failed to fetch English text: Status code {english_resp.status_code}")
            raise HTTPException(status_code=english_resp.status_code, detail="Failed to fetch English text.")
        english_data = english_resp.json()
        if english_data["status"] != "OK":
            logger.error(f"English API error: {english_data}")
            raise HTTPException(status_code=500, detail=f"English API error: {english_data}")

        # Combine and return as dict
        ayah = {
            "surah_number": arabic_data["data"]["surah"]["number"],
            "surah_name_ar": arabic_data["data"]["surah"]["name"],
            "surah_name_en": arabic_data["data"]["surah"]["englishName"],
            "ayah_number": arabic_data["data"]["numberInSurah"],
            "ayah_text_ar": arabic_data["data"]["text"],
            "ayah_text_en": english_data["data"]["text"]
        }
        return ayah