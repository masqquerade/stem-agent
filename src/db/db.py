import chromadb
from chromadb.api.types import Metadata
from dataclasses import dataclass

@dataclass
class Document:
    content: str
    source: str

@dataclass
class QueryResult:
    id: str
    document: str
    metadata: Metadata
    distance: float

class VectorDatabase:
    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name="documents"
        )

    def add(self, docs: list[Document]):
        self.collection.add(
            ids=[
                doc.source for doc in docs
            ],
            documents=[
                doc.content for doc in docs
            ]
        )

    def query(self, query_texts: list[str], n_results: int = 3) -> list[list[QueryResult]]:
        n_results = min(n_results, self.collection.count())
        if n_results == 0:
            return [[] for _ in query_texts]
        results = []

        raw = self.collection.query(
            query_texts=query_texts,
            n_results=n_results
        )

        for batch_ids, batch_docs, batch_metas, batch_dists in zip(raw["ids"], raw["documents"], raw["metadatas"], raw["distances"]):
            batch = [
                QueryResult(id=_id, document=doc, metadata=meta, distance=dist)
                for _id, doc, meta, dist in zip(batch_ids, batch_docs, batch_metas, batch_dists)
            ]

            results.append(batch)

        return results
