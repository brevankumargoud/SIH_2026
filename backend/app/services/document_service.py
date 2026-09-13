import os
import uuid
import pypdf
from typing import BinaryIO
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.models.knowledge_base import KnowledgeBase
from app.services.chunking_service import ChunkingService
from app.services.embedding_service import EmbeddingService

class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.storage_path = os.getenv("RAG_STORAGE_PATH", "/tmp/rag_storage")
        os.makedirs(self.storage_path, exist_ok=True)
        self.chunking_svc = ChunkingService()
        self.embedding_svc = EmbeddingService()

    def process_file(self, kb_id: uuid.UUID, user_id: uuid.UUID, filename: str, file_obj: BinaryIO) -> Document:
        kb = self.db.get(KnowledgeBase, kb_id)
        if not kb:
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        ext = filename.split(".")[-1].lower()
        if ext not in ["txt", "md", "pdf", "png", "jpg", "jpeg", "webp"]:
            raise HTTPException(status_code=400, detail="Unsupported file format")

        file_bytes = file_obj.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="Empty file")

        doc_id = uuid.uuid4()
        storage_file = os.path.join(self.storage_path, f"{doc_id}_{filename}")
        
        with open(storage_file, "wb") as f:
            f.write(file_bytes)

        doc = Document(
            id=doc_id,
            knowledge_base_id=kb_id,
            uploaded_by=user_id,
            filename=filename,
            file_type=ext,
            mime_type="application/octet-stream",
            file_size_bytes=len(file_bytes),
            storage_path=storage_file,
            checksum="dummy",
            processing_status="processing"
        )
        self.db.add(doc)
        self.db.commit()

        try:
            from app.services.multimodal_processor import MultimodalProcessor
            processor = MultimodalProcessor(db=self.db)
            extracted_pages = processor.process_file(storage_file, ext)
            
            # Reconstruct text and chunks per page to preserve page_number
            chunk_index = 0
            for page in extracted_pages:
                if not page.text.strip():
                    continue
                chunks = self.chunking_svc.chunk_text(page.text)
                for chunk_text in chunks:
                    emb = self.embedding_svc.generate_embedding(chunk_text)
                    chunk_record = DocumentChunk(
                        document_id=doc.id,
                        chunk_index=chunk_index,
                        content=chunk_text,
                        page_number=page.page_number,
                        embedding=emb
                    )
                    self.db.add(chunk_record)
                    chunk_index += 1

            doc.processing_status = "completed"
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            doc.processing_status = "failed"
            doc.metadata_ = {"error": str(e)}
            self.db.add(doc)
            self.db.commit()

        self.db.refresh(doc)
        return doc

    def delete_document(self, document_id: uuid.UUID):
        doc = self.db.get(Document, document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        if os.path.exists(doc.storage_path):
            os.remove(doc.storage_path)
        self.db.delete(doc)
        self.db.commit()
