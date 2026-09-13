import os
import sys
import uuid
import io
import pytest
from dotenv import load_dotenv

# Ensure environment is loaded from backend/.env
load_dotenv()

from fastapi.testclient import TestClient
from sqlalchemy import text
from app.main import app
from app.db.database import SessionLocal
from app.models.user import User
from app.models.workspace import Workspace
from app.models.knowledge_base import KnowledgeBase
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.core.security import create_access_token

client = TestClient(app)

def run_test():
    print("--- 1. Checking Environment Variables ---")
    print("EMBEDDING_PROVIDER:", os.getenv("EMBEDDING_PROVIDER"))
    print("OLLAMA_BASE_URL:", os.getenv("OLLAMA_BASE_URL"))
    print("EMBEDDING_MODEL:", os.getenv("EMBEDDING_MODEL"))
    assert os.getenv("EMBEDDING_PROVIDER") == "ollama", "EMBEDDING_PROVIDER must be 'ollama'"
    assert "10.151.15.220" in os.getenv("OLLAMA_BASE_URL", ""), "OLLAMA_BASE_URL must point to Laptop-3"

    db = SessionLocal()
    try:
        # Fetch or create dev_user
        user = db.query(User).filter_by(username="dev_user").first()
        assert user is not None, "dev_user must exist in database"
        
        # Create auth token
        token = create_access_token(user.id)
        headers = {"Authorization": f"Bearer {token}"}
        
        # Fetch default workspace or create one
        ws_res = client.get("/workspaces/default", headers=headers)
        assert ws_res.status_code == 200, f"Failed to get default workspace: {ws_res.text}"
        workspace_id = ws_res.json()["id"]
        print(f"Using Workspace ID: {workspace_id}")

        # Get or create default Knowledge Base
        kb_res = client.get("/knowledge-bases/default", headers=headers)
        assert kb_res.status_code == 200, f"Failed to get default KB: {kb_res.text}"
        kb = kb_res.json()
        kb_id = kb["id"]
        print(f"Using Knowledge Base ID: {kb_id} (Name: {kb.get('name')})")

        # Prepare test document
        doc_content = (
            "Industrial Boiler Operation Guide:\n"
            "Document ID: BOILER-SPEC-9092\n"
            "The thermal cracking furnace operates at an optimal supercritical pressure of 22.1 megapascals.\n"
            "The high-pressure turbine steam bypass valve opens automatically whenever emergency cooldown protocol Alpha-7 is engaged.\n"
            "Lubrication for the primary circulation impeller requires synthetic polyalphaolefin ISO VG 460 lubricant replaced every 4000 operational hours.\n"
        ).encode("utf-8")

        print("\n--- 2. Uploading Document to Knowledge Base ---")
        files = {
            "file": ("boiler_operating_spec.txt", io.BytesIO(doc_content), "text/plain")
        }
        upload_res = client.post(f"/knowledge-bases/{kb_id}/documents", headers=headers, files=files)
        print("Upload Status Code:", upload_res.status_code)
        assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
        doc_data = upload_res.json()
        doc_id = doc_data["id"]
        print(f"Document Uploaded: ID={doc_id}, Status={doc_data['processing_status']}")
        assert doc_data["processing_status"] == "completed", f"Processing failed: {doc_data}"

        print("\n--- 3. Verifying Database Chunks & Vector Dimensions in PostgreSQL ---")
        chunks = db.query(DocumentChunk).filter(DocumentChunk.document_id == uuid.UUID(doc_id)).all()
        print(f"Number of chunks created: {len(chunks)}")
        assert len(chunks) > 0, "No chunks were created!"

        for c in chunks:
            print(f"Chunk Index {c.chunk_index}: length={len(c.content)} chars")
            # Query vector dimension from PostgreSQL pgvector
            vec_dim = db.execute(
                text("SELECT vector_dims(embedding) FROM document_chunks WHERE id = :cid"),
                {"cid": c.id}
            ).scalar()
            print(f"Chunk ID {c.id} -> pgvector dimension in PostgreSQL: {vec_dim}")
            assert vec_dim == 768, f"Expected vector dimension 768, got {vec_dim}"

        print("\n--- 4. Testing Semantic Retrieval (Zero Exact Keyword Matches) ---")
        semantic_query = "At what pressure does the thermal cracking system function at its best?"
        print(f"Semantic Query: '{semantic_query}'")
        search_res = client.post(
            f"/knowledge-bases/{kb_id}/search",
            headers=headers,
            json={
                "knowledge_base_id": kb_id,
                "query": semantic_query,
                "top_k": 3
            }
        )
        print("Search Status Code:", search_res.status_code)
        assert search_res.status_code == 200, f"Search failed: {search_res.text}"
        results = search_res.json()
        print(f"Number of retrieved results: {len(results)}")
        assert len(results) > 0, "Semantic search returned 0 results!"
        
        for idx, r in enumerate(results):
            print(f"Result {idx+1}: Score={r['score']:.4f}, Document={r['filename']}")
            print(f"Excerpt: {r['content'][:120]}...")
            assert r['score'] >= 0.5, f"Similarity score {r['score']} was below threshold 0.5"
            assert "22.1 megapascals" in r['content']

        print("\n--- 5. Testing Second Semantic Query ---")
        semantic_query_2 = "What fluid should be applied to lubricate the main circulation pump components?"
        print(f"Semantic Query 2: '{semantic_query_2}'")
        search_res_2 = client.post(
            f"/knowledge-bases/{kb_id}/search",
            headers=headers,
            json={
                "knowledge_base_id": kb_id,
                "query": semantic_query_2,
                "top_k": 3
            }
        )
        assert search_res_2.status_code == 200, f"Search 2 failed: {search_res_2.text}"
        results_2 = search_res_2.json()
        assert len(results_2) > 0, "Semantic search 2 returned 0 results!"
        print(f"Result: Score={results_2[0]['score']:.4f}, Excerpt: {results_2[0]['content'][:120]}...")
        assert "polyalphaolefin" in results_2[0]['content']
        assert results_2[0]['score'] >= 0.5

        print("\nALL INGESTION AND SEMANTIC RETRIEVAL CHECKS PASSED SUCCESSFULLY!")

    finally:
        db.close()

if __name__ == "__main__":
    run_test()
