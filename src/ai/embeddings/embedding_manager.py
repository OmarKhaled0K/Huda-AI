# app/embeddings/embedding_manager.py
from .openai_embedding import OpenAIEmbedding
from .base import BaseEmbedding
from config.settings import get_settings

def get_embedding() -> BaseEmbedding:
    """Factory that returns the appropriate embedding instance."""
    settings = get_settings()
    provider = settings.EMBEDDING_PROVIDER.lower()

    if provider == "openai":
        return OpenAIEmbedding( model=settings.OPENAI_EMBEDDING_MODEL)
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")

# Create a dummy embedding for testing purposes
def create_dummy_embedding(dimension: int = 1536) -> list[float]:
    """
    Create a dummy embedding vector using the base implementation.
    
    Args:
        dimension (int, optional): Dimension of the dummy embedding. Defaults to 1536.
        
    Returns:
        list[float]: A dummy embedding vector.
    """
    return BaseEmbedding.create_dummy_embedding(dimension)
