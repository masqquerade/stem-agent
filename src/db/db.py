import chromadb
from dataclasses import dataclass

@dataclass
class Document:
    content: str
    source: str

@dataclass
class QueryResult:
    id: str
    document: str
    metadata: dict
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

    def query(self, query_texts: list[str]) -> list[QueryResult]:
        results = []

        raw = self.collection.query(
            query_texts=query_texts
        )

        for batch_ids, batch_docs, batch_metas, batch_dists in zip(raw["ids"], raw["documents"]):
            batch = [
                QueryResult(id=_id, document=doc, metadata=meta, distance=dist)
                for _id, doc, meta, dist in zip(batch_ids, batch_docs, batch_metas, batch_dists)
            ]

            results.append(batch)

        return results
