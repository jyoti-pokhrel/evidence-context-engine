from rank_bm25 import BM25Okapi
from dataclasses import dataclass
from typing import Optional


@dataclass
class Document:
    doc_id: str
    content: str
    source_type: str
    timestamp: str


@dataclass
class RetrievalResult:
    doc_id: str
    score: float
    document: Document


def retrieve(required_context: list[str], documents: list[Document], top_k: int = 100) -> list[RetrievalResult]:
    if not documents:
        return []
    
    corpus = [doc.content for doc in documents]
    tokenized_corpus = [doc.lower().split() for doc in corpus]
    
    bm25 = BM25Okapi(tokenized_corpus)
    
    query_terms = []
    for term in required_context:
        query_terms.extend(term.split('_'))
    query = " ".join(query_terms).lower()
    tokenized_query = query.split()
    
    scores = bm25.get_scores(tokenized_query)
    
    scored_docs = []
    for i, doc in enumerate(documents):
        scored_docs.append(RetrievalResult(
            doc_id=doc.doc_id,
            score=float(scores[i]),
            document=doc
        ))
    
    scored_docs.sort(key=lambda x: x.score, reverse=True)
    
    return scored_docs[:top_k]
