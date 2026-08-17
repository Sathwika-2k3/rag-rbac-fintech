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


def search_for_role(vectorstore, role: str, query: str, k: int = 4):
    return vectorstore.similarity_search(query, k=k, filter=department_filter(role))
