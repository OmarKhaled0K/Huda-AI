from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseVectorStore(ABC):
    """
    Abstract interface for a vector store tailored to:
      - Ayahs
      - Tafseers
      - Hadiths

    This version removes company_id and department_id for a single-tenant setup.
    """

    # --- lifecycle / setup ----------------------------------------------
    @abstractmethod
    async def initialize_store(self) -> None:
        """
        Initialize collections/indices.
        Ensure the following collections exist: 'ayahs', 'tafseers', 'hadiths'
        """
        raise NotImplementedError

    # --- inserts ---------------------------------------------------------
    @abstractmethod
    async def insert_ayah(
        self,
        ayah_id: Optional[str],
        surah_number: int,
        ayah_number: int,
        juz_number: Optional[int],
        text: str,
        transliteration: Optional[str],
        translation: Optional[str],
        ayah_type: Optional[str],
        feelings: Optional[List[str]],
        embedding: List[float],
        chunk_index: Optional[int] = 0,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Insert a single ayah (or ayah chunk) into the 'ayahs' collection.
        """
        raise NotImplementedError
    
    @abstractmethod
    async def insert_duaa(
        self,
        duaa_id: Optional[str],
        feeling: str,
        url: str,
        dua_number: str,
        arabic: str,
        transliteration: Optional[str],
        translation: Optional[str],
        source: Optional[str],
        embedding: List[float],
        duas_count: Optional[int] = None,
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Insert a single duaa into the 'duaas' collection.
        Returns a dict containing stored id and status.
        """
        raise NotImplementedError

    @abstractmethod
    async def insert_tafseer(
        self,
        tafseer_id: Optional[str],
        referenced_ayahs: List[Dict[str, int]],  # e.g. [{"surah_number":2,"ayah_number":255}, ...]
        text: str,
        tafseer_type: str,
        translation: Optional[str],
        feelings: Optional[List[str]],
        embedding: List[float],
        chunk_index: Optional[int] = 0,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Insert a tafseer entry (or chunk) into the 'tafseers' collection.
        """
        raise NotImplementedError

    @abstractmethod
    async def insert_hadith(
        self,
        hadith_id: Optional[str],
        hadith_number: Optional[str],
        source_collection: Optional[str],
        text: str,
        transliteration: Optional[str],
        translation: Optional[str],
        explanation: Optional[str],
        feelings: Optional[List[str]],
        embedding: List[float],
        chunk_index: Optional[int] = 0,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Insert a hadith entry (or chunk) into the 'hadiths' collection.
        """
        raise NotImplementedError

    # --- search primitives ----------------------------------------------
    @abstractmethod
    async def search_by_keywords(
        self,
        collection: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Keyword/BM25 search over `collection` ("ayahs"|"tafseers"|"hadiths").
        `filters` can be used to filter by metadata (e.g., {"surah_number": 2}).
        """
        raise NotImplementedError

    @abstractmethod
    async def search_by_semantic_similarity(
        self,
        collection: str,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Vector nearest-neighbor search in `collection`.
        Returns results ordered by similarity (score/distance).
        """
        raise NotImplementedError

    @abstractmethod
    async def search_hybrid(
        self,
        collection: str,
        query: str,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        keyword_weight: float = 0.5,
        semantic_weight: float = 0.5,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Combine keyword and embedding search (hybrid ranking).
        Implementations should merge and normalize scores.
        """
        raise NotImplementedError

    @abstractmethod
    async def search_by_metadata(
        self,
        collection: str,
        metadata_filters: Dict[str, Any],
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        Search documents based purely on metadata attributes.
        """
        raise NotImplementedError

    @abstractmethod
    async def search_by_embeddings(
        self,
        collection: str,
        query_embeddings: List[List[float]],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Batch embedding search; useful for multi-vector queries.
        """
        raise NotImplementedError

    # --- maintenance / delete ------------------------------------------
    @abstractmethod
    async def delete_by_id(
        self,
        collection: str,
        doc_id: str,
    ) -> bool:
        """
        Delete a single document/chunk by id from `collection`.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_by_ayah_reference(
        self,
        surah_number: int,
        ayah_number: int,
        collection: Optional[str] = None,
    ) -> int:
        """
        Delete entries referencing a specific ayah (used mainly for Tafseer).
        Returns the number of deleted records.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_collection(self, collection: str) -> bool:
        """
        Delete or purge all entries of a given collection (use carefully).
        """
        raise NotImplementedError

    # --- utility --------------------------------------------------------
    @abstractmethod
    async def get_document_by_id(
        self,
        collection: str,
        doc_id: str,
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve a stored document by id (returns None if not found).
        """
        raise NotImplementedError
