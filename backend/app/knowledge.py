import re
from dataclasses import dataclass

from .models import Citation


@dataclass(frozen=True)
class KnowledgeChunk:
    business_id: str
    title: str
    content: str
    page: int | None = None


class KnowledgeBase:
    def __init__(self) -> None:
        self._chunks: list[KnowledgeChunk] = []

    def add(self, chunk: KnowledgeChunk) -> None:
        self._chunks.append(chunk)

    def search(self, business_id: str, query: str, limit: int = 3) -> list[tuple[KnowledgeChunk, float]]:
        query_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        if not query_terms:
            return []
        matches: list[tuple[KnowledgeChunk, float]] = []
        for chunk in self._chunks:
            if chunk.business_id != business_id:
                continue
            terms = set(re.findall(r"[a-z0-9]+", f"{chunk.title} {chunk.content}".lower()))
            score = len(query_terms & terms) / len(query_terms)
            if score > 0:
                matches.append((chunk, score))
        return sorted(matches, key=lambda item: item[1], reverse=True)[:limit]

    def citations(self, results: list[tuple[KnowledgeChunk, float]]) -> list[Citation]:
        return [
            Citation(document=chunk.title, page=chunk.page, excerpt=chunk.content[:300])
            for chunk, _ in results
        ]
