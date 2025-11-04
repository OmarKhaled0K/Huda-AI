from typing import List, Optional
import asyncio
from openai import AsyncOpenAI
from .base import BaseEmbedding
from config.settings import get_settings
class OpenAIEmbedding(BaseEmbedding):
    """OpenAI embedding implementation."""
    
    def __init__(self,model: str = "text-embedding-ada-002"):
        """
        Initialize OpenAI embedding.
        
        Args:
            api_key (str): OpenAI API key.
            model (str, optional): Model to use for embeddings. Defaults to "text-embedding-ada-002".
        """
        self.client = AsyncOpenAI(api_key=get_settings().OPENAI_API_KEY)
        self.model = model
        
    async def embed_query(self, text: str) -> List[float]:
        """
        Get embedding for a single text using OpenAI API.
        
        Args:
            text (str): Text to embed.
            
        Returns:
            List[float]: Embedding vector.
        """
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding
    
    
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for multiple texts in parallel using OpenAI API.
        
        Args:
            texts (List[str]): List of texts to embed.
            
        Returns:
            List[List[float]]: List of embedding vectors.
        """
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [data.embedding for data in response.data]
