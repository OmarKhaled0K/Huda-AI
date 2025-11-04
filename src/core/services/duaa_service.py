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
import re
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
        await self.vector_db.create_collection(collection_name=self.settings.DUAA_COLLECTION_NAME)
                
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
                        embedding = await self.embedding_model.embed_query(dua.arabic)

                        # Insert into vector store (Qdrant)
                        res = await self.vector_db.insert_duaa(

                            duaa_id=dua.id,
                            feeling=batch_obj.feeling,
                            url=batch_obj.url,
                            arabic=dua.arabic,
                            transliteration=dua.transliteration,
                            translation=dua.translation,
                            source=dua.source,
                            embedding=embedding,
                            duas_count=batch_obj.duas_count,
                        )
                        inserted_ids.append(res["id"])
                        logger.debug("Inserted duaa id=%s dua_id=%s batch_index=%d", res["id"], dua.id, batch_index)
                    except Exception as e:
                        logger.exception("Failed to insert dua id=%s in batch_index=%d", dua.id, batch_index)
                        failures.append({"batch_index": batch_index, "dua_id": getattr(dua, 'id', None), "error": str(e)})
                        # continue to next dua
                        continue
            # END
            logger.info(f"Successfully populated {len(duaa_data)} duaa entries into vector DB.")
        except Exception as e:
            logger.error(f"Failed to populate duaa entries: {e}")
            raise HTTPException(status_code=500, detail="Error initializing duaa service")

    async def add_duaa(
        self,
        duaa_id: str,
        feeling: str,
        url: str,
        arabic: str,
        transliteration: str,
        translation: str,
        source: str,
        duas_count: int = None,
    ) -> str:
        embedding = await self.embedding_model.embed_query(arabic)
        res = await self.vector_db.insert_duaa(
            duaa_id=duaa_id,
            feeling=feeling,
            url=url,
            arabic=arabic,
            transliteration=transliteration,
            translation=translation,
            source=source,
            embedding=embedding,
            duas_count=duas_count
        )
        return res["id"]

    async def delete_duaa(self, duaa_id: str) -> bool:
        """
        Delete a duaa from the vector database based on its duaa_id.
        
        Args:
            duaa_id (str): The ID of the duaa to delete
            
        Returns:
            bool: True if the duaa was successfully deleted, False otherwise
            
        Raises:
            HTTPException: If the duaa is not found or if there's an error during deletion
        """
        try:
            # First, search for the duaa using metadata filters to get its document ID
            results = await self.vector_db.search_by_metadata(
                collection=self.settings.DUAA_COLLECTION_NAME,
                metadata_filters={"duaa_id": duaa_id},
                limit=1
            )
            
            if not results:
                raise HTTPException(
                    status_code=404,
                    detail=f"Duaa with ID {duaa_id} not found"
                )
            
            # Get the document ID from the search results
            doc_id = results[0]["id"]
            print(f"Document ID to delete: {doc_id}")
            
            # Delete the document using its ID
            success = await self.vector_db.delete_by_id(
                collection=self.settings.DUAA_COLLECTION_NAME,
                doc_id=doc_id
            )
            
            if success:
                logger.info(f"Successfully deleted duaa with ID {duaa_id}")
                return True
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to delete duaa with ID {duaa_id}"
                )
                
        except HTTPException as he:
            # Re-raise HTTP exceptions
            raise he
        except Exception as e:
            logger.error(f"Error deleting duaa with ID {duaa_id}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting duaa: {str(e)}"
            )
        


    def clean_duaa_object(self, duaa: dict) -> dict:
        """
        Clean and standardize a duaa object fetched from an external API.
        
        Args:
            duaa (dict): The raw duaa object from the API.
        Returns:
            dict: The cleaned duaa object with standardized fields.
        """
        cleaned = {
            "id": duaa.get("duaa_id", ""),  # Add ID field for referencing
            # "feeling": duaa.get("feeling", "general"),
            "arabic": duaa.get("text", ""),
            "transliteration": duaa.get("transliteration", ""),
            "translation": duaa.get("translation", ""),
            "source": duaa.get("source", ""),
        }
        return cleaned
    def replace_duaa_tags(self,text: str, context: list[dict]) -> str:
        def replacer(match):
            duaa_id = match.group(1)
            # Find the duaa in context with matching ID
            for item in context:
                if item.get("id") == duaa_id:
                    return item.get("arabic", "")
            return f"[Unknown duaa: {duaa_id}]"
        return re.sub(r"<duaa>(.*?)</duaa>", replacer, text)

    async def generate_duaa_llm(self, feeling: str) -> str:
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
            f"💬 'May Allah ease your worries and bless you with peace. Repeat after me or say the duaa: <duaa>duaa123</duaa>.'\n\n"
            f"---\n"
        )
        results = await self.vector_db.search_by_metadata(collection="duaas",
                                                       metadata_filters={"feeling": feeling},
                                                       limit=10)
        payloads = [item["payload"] for item in results if "payload" in item]
        context = [self.clean_duaa_object(payload) for payload in payloads]

        if context:
            prompt += "Here are the available duaas:\n"
            for item in context:
                prompt += (
                    f"- ID: {item['id']}\n"
                    # f"  Feeling: {cleaned['feeling']}\n"
                    f"  Arabic: {item['arabic']}\n"
                    f"  Transliteration: {item['transliteration']}\n"
                    f"  Translation: {item['translation']}\n"
                    f"  Source: {item['source']}\n\n"
                )

        prompt += (
            "---\nNow, write a short, warm, and faith-inspired message addressing the user's feeling.\n"
            "Do not return or describe any duaa text directly — only reference duaas using <duaa></duaa> tags where appropriate.\n"
        )

        logger.info(f"Generating friendly Islamic message for feeling '{feeling}' with {len(context)} context items.")

        try:
            response, metadata = await self.llm.generate(prompt)
            response = self.replace_duaa_tags(response, context)
            print(f"LLM Response:\n{response}")
            logger.info("Message generation successful.")
            return response
        except Exception as e:
            logger.error(f"Message generation failed: {e}")
            raise HTTPException(status_code=500, detail="Error generating message")


