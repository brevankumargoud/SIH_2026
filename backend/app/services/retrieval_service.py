from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid
from typing import List
from app.models.document_chunk import DocumentChunk
from app.models.document import Document
from app.schemas.rag import SearchResult
from app.services.embedding_service import EmbeddingService

class RetrievalService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()

    def search(self, knowledge_base_id: uuid.UUID, query: str, top_k: int = 5, threshold: float = 0.5) -> List[SearchResult]:
        query_embedding = self.embedding_service.generate_embedding(query)
        
        distance_col = DocumentChunk.embedding.cosine_distance(query_embedding).label('distance')
        
        stmt = (
            select(DocumentChunk, distance_col, Document.filename)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.knowledge_base_id == knowledge_base_id)
            .order_by(distance_col)
            .limit(top_k)
        )
        
        results = self.db.execute(stmt).all()
        
        search_results = []
        for chunk, distance, filename in results:
            score = 1.0 - distance
            if score >= threshold:
                search_results.append(SearchResult(
                    chunk_id=chunk.id,
                    document_id=chunk.document_id,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    score=score,
                    filename=filename
                ))
        return search_results
