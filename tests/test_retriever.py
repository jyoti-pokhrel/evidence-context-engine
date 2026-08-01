from context_engine.retriever import retrieve, Document


def test_retrieve_basic():
    documents = [
        Document(
            doc_id="doc1.md",
            content="This document discusses authentication and JWT tokens",
            source_type="readme",
            timestamp="2026-01-10T00:00:00"
        ),
        Document(
            doc_id="doc2.md",
            content="This document is about rate limiting configuration",
            source_type="architecture_docs",
            timestamp="2026-01-10T00:00:00"
        )
    ]
    
    results = retrieve(["authentication", "jwt"], documents)
    
    assert len(results) > 0
    assert results[0].doc_id == "doc1.md"


def test_retrieve_empty_documents():
    results = retrieve(["test"], [])
    
    assert len(results) == 0
