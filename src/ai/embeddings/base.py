from abc import ABC, abstractmethod
from typing import List, Union
import numpy as np

class BaseEmbedding(ABC):
    """Base class for embedding implementations."""
    
    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        """
        Embed a single text query into a vector.
        
        Args:
            text (str): The text to embed.
            
        Returns:
            List[float]: The embedding vector.
        """
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts in parallel.
        
        Args:
            texts (List[str]): List of texts to embed.
            
        Returns:
            List[List[float]]: List of embedding vectors.
        """
        pass

    @staticmethod
    def create_dummy_embedding(dimension: int = 1536) -> List[float]:
        """
        Create a dummy embedding vector for testing or placeholder purposes.
        Uses normal distribution to create a vector that somewhat mimics real embeddings.
        
        Args:
            dimension (int): The dimension of the embedding vector. Defaults to 1536 (OpenAI's dimension).
            
        Returns:
            List[float]: A dummy embedding vector.
        """
        return list(np.random.normal(0, 0.1, dimension).astype(float))
    
    @staticmethod
    def compute_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec1 (List[float]): First vector.
            vec2 (List[float]): Second vector.
            
        Returns:
            float: Cosine similarity score between -1 and 1.
        """
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return float(np.dot(vec1, vec2) / (norm1 * norm2)) if norm1 > 0 and norm2 > 0 else 0.0
    
    @staticmethod
    def normalize_embedding(vector: List[float]) -> List[float]:
        """
        Normalize an embedding vector to unit length.
        
        Args:
            vector (List[float]): Vector to normalize.
            
        Returns:
            List[float]: Normalized vector.
        """
        norm = np.linalg.norm(vector)
        return list(np.array(vector) / norm) if norm > 0 else vector
