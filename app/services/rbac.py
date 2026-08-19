from qdrant_client.http.models import FieldCondition, Filter, MatchAny

ROLE_DEPARTMENTS: dict[str, list[str]] = {
    "general": ["general"],
    "engineering": ["engineering", "general"],
    "finance": ["finance", "general"],
    "marketing": ["marketing", "general"],
    "hr": ["hr", "general"],
    "c-level": ["engineering", "finance", "general", "hr", "marketing"],
}


def allowed_departments(role: str) -> list[str]:
    return ROLE_DEPARTMENTS.get(role, [])


def department_filter(role: str) -> Filter:
    return Filter(
        must=[FieldCondition(key="metadata.department", match=MatchAny(any=allowed_departments(role)))]
    )


# Below this relevance score, a match is treated as "not actually about this" rather than
# real context — an empirically tuned cutoff, not a precise science. Adjust if testing shows
# real answers getting dropped, or clearly irrelevant chunks still getting through.
MIN_RELEVANCE_SCORE = 0.35


def search_for_role(vectorstore, role: str, query: str, k: int = 4, min_score: float = MIN_RELEVANCE_SCORE):
    results = vectorstore.similarity_search_with_score(query, k=k, filter=department_filter(role))
    return [doc for doc, score in results if score >= min_score]
