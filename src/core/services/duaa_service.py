import requests
from fastapi import HTTPException
from utils.logging.logger_setup import setup_logger
from config.settings import get_settings
from ai.llms.llm_manager import get_llm
from ai.embeddings.embedding_manager import (
    get_embedding,
    create_dummy_embedding,
)
from typing import List
import json
from ai.vector_db import QdrantVectorStore
from schemas.holy_quraan_schema import (
    DuaaBatch,
)
import uuid
logger = setup_logger("app.duaa_service")

class DuaaService:
    def __init__(self):
        self.settings = get_settings()
        self.llm = get_llm()
        self.vector_db = QdrantVectorStore()
        self.embedding_model = get_embedding()
        

    async def initialize_duaa_service(self):
        """
        Initialize the Duaa Service by searching for existing duaa entries in the vector database.
        If not exist fetch the data from `iam_feeling.json` file and populate the vector database.
        """
        count_duaas = await self.vector_db.count_collection_points(self.settings.DUAA_COLLECTION_NAME)
        if count_duaas == 0:
            logger.info("No duaa entries found in vector DB. Populating from iam_feeling.json...")
            try:
                with open(self.settings.DUAA_PATH, "r", encoding="utf-8") as f:
                    duaa_data = json.load(f)
                
                # START
                inserted_ids: List[str] = []
                failures: List[dict] = []

                for batch_index, batch in enumerate(duaa_data, start=1):
                    logger.debug("Processing batch %d: %s", batch_index, {k: v for k, v in (batch.items() if isinstance(batch, dict) else [])})
                    try:
                        batch_obj = DuaaBatch(**batch)  # validate and parse
                    except Exception as e:
                        logger.exception("Batch validation failed index=%d", batch_index)
                        failures.append({"batch_index": batch_index, "error": str(e)})
                        # skip this batch and continue with others
                        continue

                    for dua in batch_obj.duas:
                        try:
                            # Compute embedding for each dua
                            embedding = self.embedding_model.embed_query(dua.arabic)
                            duaa_id = str(uuid.uuid4())

                            # Insert into vector store (Qdrant)
                            res = await self.vector_db.insert_duaa(
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
                            logger.exception("Failed to insert dua number=%s in batch_index=%d", dua.number, batch_index)
                            failures.append({"batch_index": batch_index, "dua_number": getattr(dua, 'number', None), "error": str(e)})
                            # continue to next dua
                            continue
                # END
                logger.info(f"Successfully populated {len(duaa_data)} duaa entries into vector DB.")
            except Exception as e:
                logger.error(f"Failed to populate duaa entries: {e}")
                raise HTTPException(status_code=500, detail="Error initializing duaa service")
            
        return True
    


    def clean_duaa_object(self, duaa: dict) -> dict:
        """
        Clean and standardize a duaa object fetched from an external API.
        
        Args:
            duaa (dict): The raw duaa object from the API.
        Returns:
            dict: The cleaned duaa object with standardized fields.
        """
        cleaned = {
            "id": duaa.get("id", ""),  # Add ID field for referencing
            "feeling": duaa.get("feeling", "general"),
            "arabic": duaa.get("text", ""),
            "transliteration": duaa.get("transliteration", ""),
            "translation": duaa.get("translation", ""),
        }
        return cleaned


    async def generate_duaa_llm(self, feeling: str, context: List[dict]) -> str:
        """
        Generate a friendly Islamic message based on the provided feeling and context,
        using an LLM. The LLM must not generate or include actual duaas, only reference
        them by their ID using <duaa></duaa> tags.
        
        Args:
            feeling (str): The feeling or emotion to base the message on.
            context (List[dict]): List of related duaas with metadata.
        Returns:
            str: The generated Islamic message (no duaa text, only duaa IDs).
        """
        prompt = (
            f"You are an assistant that writes compassionate, Islamic-friendly messages.\n"
            f"The user is feeling '{feeling}'.\n\n"
            f"Use the following existing duaas as references to inspire your message.\n"
            f"Each duaa has an ID. When you want to reference or embed a duaa, "
            f"DO NOT write or paraphrase it — just include its ID inside <duaa></duaa> tags.\n\n"
            f"For example:\n"
            f"💬 'May Allah ease your worries and bless you with peace. You might reflect on <duaa>duaa123</duaa>.'\n\n"
            f"---\n"
        )

        if context:
            prompt += "Here are the available duaas:\n"
            for item in context:
                cleaned = self.clean_duaa_object(item)
                prompt += (
                    f"- ID: {cleaned['id']}\n"
                    f"  Feeling: {cleaned['feeling']}\n"
                    f"  Translation: {cleaned['translation']}\n\n"
                )

        prompt += (
            "---\nNow, write a short, warm, and faith-inspired message addressing the user's feeling.\n"
            "Do not return or describe any duaa text directly — only reference duaas using <duaa></duaa> tags where appropriate.\n"
        )

        logger.info(f"Generating friendly Islamic message for feeling '{feeling}' with {len(context)} context items.")
        print(f"Prompt for LLM:\n{prompt}")

        try:
            response, metadata = await self.llm.generate(prompt)
            logger.info("Message generation successful.")
            return response
        except Exception as e:
            logger.error(f"Message generation failed: {e}")
            raise HTTPException(status_code=500, detail="Error generating message")
