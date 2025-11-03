from ai.vector_db import BaseVectorStore
# qdrant_vector_store.py
import asyncio
from typing import List, Dict, Any, Optional
from abc import ABC
from uuid import uuid4

from qdrant_client import models
from qdrant_client.async_qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue, Range
from config.settings import get_settings
from utils.logging import setup_logger
logger = setup_logger("app.vector_db")  # Component-level logger


class QdrantVectorStore(BaseVectorStore):
    """
    Qdrant-backed implementation of BaseVectorStore.

    - Each collection: 'ayahs', 'tafseers', 'hadiths'
    - Each point payload includes 'text' and type-specific metadata under payload keys.
    - IDs are UUID strings by default.
    """
    #TODO: Remove those lines
    # # default vector sizes — adjust to embedding model you plan to use
    # DEFAULT_VECTOR_SIZE = 1536
    # DEFAULT_DISTANCE = models.Distance.COSINE

    def __init__(
        self,
        host: str = None,
        port: int = None,
        api_key: Optional[str] = None,
        prefer_grpc: bool = False,
        vector_size: int = 1536,
        distance: models.Distance = "cosine",
        timeout: Optional[int] = None,
    ):
        settings = get_settings()
        self._url = f"http://{host}:{port}" if host and port else settings.BASE_QDRANT_URL
        self._api_key = settings.QDRANT_API_KEY 
        self._prefer_grpc = prefer_grpc
        self._vector_size = settings.DEFAULT_VECTOR_SIZE
        self._distance = settings.DEFAULT_DISTANCE
        self._client: Optional[AsyncQdrantClient] = None

        # collections we manage
        self.collections = {
            "ayahs": {"vectors": models.VectorParams(size=self._vector_size, distance=self._distance)},
            "tafseers": {"vectors": models.VectorParams(size=self._vector_size, distance=self._distance)},
            "hadiths": {"vectors": models.VectorParams(size=self._vector_size, distance=self._distance)},
        }

        self._timeout = timeout

    async def _ensure_client(self):
        if self._client is None:
            self._client = AsyncQdrantClient(url=self._url, prefer_grpc=self._prefer_grpc, api_key=self._api_key, timeout=self._timeout)

    # -------------------------
    # Initialization / lifecycle
    # -------------------------
    async def initialize_store(self) -> None:
        """
        Create (or recreate) the collections used by this store.
        NOTE: `recreate_collection` will drop existing collection and create fresh one.
        Use create_collection if you want to keep existing data.
        """
        await self._ensure_client()

        for name, params in self.collections.items():
            # You may opt for create_collection() to preserve data.
            # recreate_collection is convenient in dev/test.
            await self._client.recreate_collection(
                collection_name=name,
                vectors_config=params["vectors"],
            )

    # -------------------------
    # Helpers
    # -------------------------
    @staticmethod
    def _new_id() -> str:
        return str(uuid4())

    @staticmethod
    def _build_payload_text_and_meta(text: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        payload = dict(metadata) if metadata else {}
        payload["text"] = text
        return payload

    @staticmethod
    def _build_filter(filters: Optional[Dict[str, Any]]) -> Optional[Filter]:
        """
        Convert simple dict filters like {"surah_number": 2, "ayah_type": "Makki"}
        into Qdrant Filter with `must` FieldConditions (exact match).
        For list values we match any (use MatchValue with list).
        Note: for advanced filters (ranges, nested, array contains) extend here.
        """
        if not filters:
            return None

        conditions = []
        for key, value in filters.items():
            if isinstance(value, dict) and ("gte" in value or "lte" in value or "gt" in value or "lt" in value):
                # Range condition
                range_cond = Range(gte=value.get("gte"), lte=value.get("lte"), gt=value.get("gt"), lt=value.get("lt"))
                conditions.append(FieldCondition(key=key, range=range_cond))
            else:
                # Match exact value or list of values
                if isinstance(value, (list, tuple, set)):
                    mv = MatchValue(value=list(value))
                else:
                    mv = MatchValue(value=value)
                conditions.append(FieldCondition(key=key, match=mv))

        if not conditions:
            return None
        return Filter(must=conditions)

    # -------------------------
    # Insert methods
    # -------------------------
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
        await self._ensure_client()
        collection = "ayahs"
        _id = ayah_id or self._new_id()
        payload = {
            "type": "ayah",
            "ayah_id": _id,
            "surah_number": surah_number,
            "ayah_number": ayah_number,
            "juz_number": juz_number,
            "transliteration": transliteration,
            "translation": translation,
            "ayah_type": ayah_type,
            "feelings": feelings or [],
            "chunk_index": chunk_index,
        }
        if extra_metadata:
            payload.update(extra_metadata)

        point = PointStruct(id=_id, vector=embedding, payload=self._build_payload_text_and_meta(text, payload))
        if self.collection_exists(collection) is False:
            logger.info(f"Collection '{collection}' does not exist. Creating it.")
            await self.create_collection(
                collection_name=collection,
                vectors=models.VectorParams(size=self._vector_size, distance=self._distance),
            )
        await self._client.upsert(collection_name=collection, points=[point])
        return {"id": _id, "status": "ok"}


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
        await self._ensure_client()
        collection = "duaas"
        _id = duaa_id or self._new_id()
        payload = {
            "type": "duaa",
            "duaa_id": _id,
            "feeling": feeling,
            "url": url,
            "dua_number": dua_number,
            "transliteration": transliteration,
            "translation": translation,
            "source": source,
            "duas_count": duas_count,
        }
        if extra_metadata:
            payload.update(extra_metadata)

        point = PointStruct(
            id=_id,
            vector=embedding,
            payload=self._build_payload_text_and_meta(arabic, payload)
        )
        if await self.collection_exists(collection) is False:
            logger.info(f"Collection '{collection}' does not exist. Creating it.")
            await self.create_collection(
                collection_name=collection,
                vectors=models.VectorParams(size=self._vector_size, distance=self._distance),
            )
        await self._client.upsert(collection_name=collection, points=[point])
        return {"id": _id, "status": "ok"}

    async def insert_tafseer(
        self,
        tafseer_id: Optional[str],
        referenced_ayahs: List[Dict[str, int]],
        text: str,
        tafseer_type: str,
        translation: Optional[str],
        feelings: Optional[List[str]],
        embedding: List[float],
        chunk_index: Optional[int] = 0,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        await self._ensure_client()
        collection = "tafseers"
        _id = tafseer_id or self._new_id()
        payload = {
            "type": "tafseer",
            "tafseer_id": _id,
            "referenced_ayahs": referenced_ayahs,
            "tafseer_type": tafseer_type,
            "translation": translation,
            "feelings": feelings or [],
            "chunk_index": chunk_index,
        }
        if extra_metadata:
            payload.update(extra_metadata)

        point = PointStruct(id=_id, vector=embedding, payload=self._build_payload_text_and_meta(text, payload))
        if self.collection_exists(collection) is False:
            logger.info(f"Collection '{collection}' does not exist. Creating it.")
            await self.create_collection(
                collection_name=collection,
                vectors=models.VectorParams(size=self._vector_size, distance=self._distance),
            )
        await self._client.upsert(collection_name=collection, points=[point])
        return {"id": _id, "status": "ok"}

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
        await self._ensure_client()
        collection = "hadiths"
        _id = hadith_id or self._new_id()
        payload = {
            "type": "hadith",
            "hadith_id": _id,
            "hadith_number": hadith_number,
            "source_collection": source_collection,
            "transliteration": transliteration,
            "translation": translation,
            "explanation": explanation,
            "feelings": feelings or [],
            "chunk_index": chunk_index,
        }
        if extra_metadata:
            payload.update(extra_metadata)

        point = PointStruct(id=_id, vector=embedding, payload=self._build_payload_text_and_meta(text, payload))
        if self.collection_exists(collection) is False:
            logger.info(f"Collection '{collection}' does not exist. Creating it.")
            await self.create_collection(
                collection_name=collection,
                vectors=models.VectorParams(size=self._vector_size, distance=self._distance),
            )
        await self._client.upsert(collection_name=collection, points=[point])
        return {"id": _id, "status": "ok"}

    # -------------------------
    # Search methods
    # -------------------------
    async def search_by_semantic_similarity(
        self,
        collection: str,
        query_embedding: List[float],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        await self._ensure_client()
        q_filter = self._build_filter(filters)
        hits = await self._client.search(
            collection_name=collection,
            query_vector=query_embedding,
            limit=limit,
            query_filter=q_filter,
            with_payload=True,
            with_vectors=False,
        )
        results = []
        for hit in hits:
            results.append({
                "id": hit.id,
                "score": hit.score,
                "payload": hit.payload,
            })
        return results

    async def search_by_embeddings(
        self,
        collection: str,
        query_embeddings: List[List[float]],
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Batch embeddings search: run searches sequentially and return combined results.
        """
        aggregated = []
        for emb in query_embeddings:
            res = await self.search_by_semantic_similarity(collection=collection, query_embedding=emb, limit=limit)
            aggregated.append(res)
        return aggregated

    async def search_by_keywords(
        self,
        collection: str,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """
        Lightweight keyword search:
        - Qdrant is not a full text/BM25 engine. For small datasets this method
          scrolls payloads and scores by substring presence & simple heuristic.
        - For production BM25 you should integrate Postgres/Elastic (store text there and use qdrant for vectors).
        """
        await self._ensure_client()
        q_filter = self._build_filter(filters)

        # naive scanning approach using scroll - stops when we collected 'limit+offset' matches
        matches: List[Dict[str, Any]] = []
        batch_size = 512
        next_cursor = None
        required = limit + offset
        collected = 0

        while True:
            scroll_resp = await self._client.scroll(
                collection_name=collection,
                limit=batch_size,
                offset=0,
                with_payload=True,
                with_vectors=False,
                scroll_filter=q_filter,
                # pagination via next_page is supported; here we use 'scroll' with 'offset' simulation
            )
            # scroll returns points up to `limit`; for simplicity we break after one page
            # (If you have many points, implement proper pagination using 'scroll' returned 'next_page' token.)
            points = scroll_resp.records
            if not points:
                break

            for p in points:
                text = (p.payload or {}).get("text", "") or ""
                score = 0
                q_lower = query.lower()
                text_lower = text.lower()

                if q_lower in text_lower:
                    # exact substring match; boost by length ratio
                    score += 100
                    score += max(0, 50 - (len(text_lower) - len(q_lower)) // 50)

                # approximate: count occurrences of tokens
                for token in q_lower.split():
                    if token and token in text_lower:
                        score += 1

                if score > 0:
                    matches.append({"id": p.id, "score": score, "payload": p.payload})

            # we only scanned one page in this simple implementation — break
            break

        # sort by our heuristic score and apply offset/limit
        matches.sort(key=lambda r: r["score"], reverse=True)
        sliced = matches[offset: offset + limit]
        return sliced

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
        Hybrid approach:
         - run semantic search (embedding)
         - run keyword heuristic search
         - normalize scores and merge
        """
        sem = await self.search_by_semantic_similarity(collection=collection, query_embedding=query_embedding, filters=filters, limit=limit * 2)
        key = await self.search_by_keywords(collection=collection, query=query, filters=filters, limit=limit * 2)

        # build maps by id
        sem_map = {r["id"]: r for r in sem}
        key_map = {r["id"]: r for r in key}

        merged = {}
        # include all ids
        for _id in set(list(sem_map.keys()) + list(key_map.keys())):
            sscore = sem_map.get(_id, {}).get("score", 0) or 0
            kscore = key_map.get(_id, {}).get("score", 0) or 0

            # Normalize sem score with a reasonable heuristic (Qdrant returns distance/similarity depending on config)
            # Here we assume larger score==more similar (Qdrant search returns "score" where larger is better for cosine)
            normalized_sem = sscore
            normalized_key = kscore

            final_score = semantic_weight * normalized_sem + keyword_weight * normalized_key

            # prefer payload from sem, then key
            payload = (sem_map.get(_id) or key_map.get(_id)).get("payload")

            merged[_id] = {"id": _id, "score": final_score, "payload": payload}

        # return top-N
        results = sorted(merged.values(), key=lambda x: x["score"], reverse=True)[:limit]
        return results

    async def search_by_metadata(
        self,
        collection: str,
        metadata_filters: Dict[str, Any],
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        await self._ensure_client()
        q_filter = self._build_filter(metadata_filters)
        # Use scroll to retrieve items that match filter; with small datasets this is fine.
        resp,_ = await self._client.scroll(collection_name=collection, limit=limit, with_payload=True, scroll_filter=q_filter)
        print(f"resp: {resp}")

        return [{"id": r.id, "payload": r.payload} for r in resp]

    # -------------------------
    # Delete / Utility
    # -------------------------
    async def delete_by_id(self, collection: str, doc_id: str) -> bool:
        await self._ensure_client()
        await self._client.delete(collection_name=collection, points=[doc_id])
        return True

    async def delete_by_ayah_reference(self, surah_number: int, ayah_number: int, collection: Optional[str] = None) -> int:
        """
        Delete points that reference a given ayah. If collection is None, only 'tafseers' is searched by default.
        Returns number of deleted points (best-effort; we gather matching ids then delete).
        """
        await self._ensure_client()
        target_collections = [collection] if collection else ["tafseers"]
        total_deleted = 0
        for col in target_collections:
            # find records referencing the ayah
            # we assume payload.referenced_ayahs is stored as a list of {"surah_number":N,"ayah_number":M}
            resp = await self._client.scroll(collection_name=col, limit=1000, with_payload=True)
            ids_to_delete = []
            for rec in resp.records:
                ref = (rec.payload or {}).get("referenced_ayahs") or []
                for r in ref:
                    if isinstance(r, dict) and r.get("surah_number") == surah_number and r.get("ayah_number") == ayah_number:
                        ids_to_delete.append(rec.id)
                        break
            if ids_to_delete:
                await self._client.delete(collection_name=col, points=ids_to_delete)
            total_deleted += len(ids_to_delete)
        return total_deleted

    async def delete_collection(self, collection: str) -> bool:
        await self._ensure_client()
        # drop the collection
        await self._client.delete_collection(collection_name=collection)
        return True

    async def get_document_by_id(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        await self._ensure_client()
        resp = await self._client.retrieve(collection_name=collection, ids=[doc_id], with_payload=True)
        if not resp:
            return None
        r = resp[0]
        return {"id": r.id, "payload": r.payload}
    
    async def count_collection_points(
        self,
        collection_name: str,
        filters: Optional[Dict[str, Any]] = None,
        exact: bool = True,
    ) -> int:
        """
        Return the number of points in `collection_name`.

        Args:
            collection_name: name of the Qdrant collection.
            filters: optional simple dict of metadata filters (same format as used elsewhere in this class).
            exact: whether to request an exact count from Qdrant (may be slower).

        Returns:
            Integer count (0 on errors or if the collection does not exist).
        """
        await self._ensure_client()
        # If collection does not exist, return 0
        try:
            if await self.collection_exists(collection_name) is False:
                return 0

            q_filter = self._build_filter(filters) if filters else None

            # Qdrant Async client `count` typically returns an object with `count` attribute.
            # Use `filter` argument name which matches qdrant-client expectations in most versions.
            resp = await self._client.count(collection_name=collection_name, filter=q_filter, exact=exact)

            # resp may be an object with `.count` or an int; handle both.
            if hasattr(resp, "count"):
                return int(getattr(resp, "count", 0) or 0)
            if isinstance(resp, int):
                return resp
            # Fallback: try to coerce
            return int(resp) if resp is not None else 0
        except Exception as e:
            logger.exception("Failed to count points in collection '%s': %s", collection_name, e)
            return 0
    #TODO: Add those two methods in base class as abstract methods
    async def collection_exists(self, collection_name: str) -> bool:
        await self._ensure_client()
        collections = await self._client.get_collections()
        return any(c.name == collection_name for c in collections.collections)

    async def create_collection(self, collection_name: str, vectors: models.VectorParams) -> None:
        await self._ensure_client()
        await self._client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors,
        )