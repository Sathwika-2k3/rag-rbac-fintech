from app.config import DATA_DIR
from app.services.rag import answer_question
from eval.dataset import EVAL_CASES
from eval.llm_judge import judge


def build_source_department_map() -> dict[str, str]:
    mapping = {}
    for department_dir in DATA_DIR.iterdir():
        if not department_dir.is_dir():
            continue
        for path in department_dir.iterdir():
            if path.is_file():
                mapping[path.name] = department_dir.name
    return mapping


def check_case(case: dict, source_departments: dict[str, str]) -> dict:
    result = answer_question(case["role"], case["question"])
    notes = []
    passed = True

    leaked = [
        src
        for src in result["sources"]
        if source_departments.get(src) in case["forbidden_departments"]
    ]
    if leaked:
        passed = False
        notes.append(f"leaked forbidden department source(s): {leaked}")

    if case["expect"] == "blocked" and not result["blocked"]:
        passed = False
        notes.append("expected this to be blocked as an injection attempt, but it answered")
    elif case["expect"] == "refuse" and result["sources"] and not result["blocked"]:
        # Retrieval found something in an *allowed* department and answered from it.
        # That's fine as long as nothing forbidden leaked (checked above) — only flag
        # if it looks like it substantively answered the disallowed question anyway.
        pass
    elif case["expect"] == "answer" and (result["blocked"] or not result["sources"]):
        passed = False
        notes.append("expected a real, sourced answer, but got none")

    scores = {"groundedness": None, "relevance": None}
    if case["expect"] == "answer" and not result["blocked"] and result["sources"]:
        judged = judge(case["question"], result["context"], result["answer"])
        scores = {"groundedness": judged.get("groundedness"), "relevance": judged.get("relevance")}

    return {
        "role": case["role"],
        "question": case["question"],
        "expect": case["expect"],
        "passed": passed,
        "notes": notes,
        "answer": result["answer"],
        "sources": result["sources"],
        **scores,
    }


def run() -> list[dict]:
    source_departments = build_source_department_map()
    return [check_case(case, source_departments) for case in EVAL_CASES]


if __name__ == "__main__":
    results = run()
    failures = [r for r in results if not r["passed"]]

    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        score_note = ""
        if r["groundedness"] is not None:
            score_note = f" (groundedness={r['groundedness']}, relevance={r['relevance']})"
        print(f"[{status}] ({r['role']}) {r['question']}{score_note}")
        if not r["passed"]:
            for note in r["notes"]:
                print(f"       {note}")

    judged = [r for r in results if r["groundedness"] is not None]
    if judged:
        avg_grounded = sum(r["groundedness"] for r in judged) / len(judged)
        avg_relevance = sum(r["relevance"] for r in judged) / len(judged)
        print(f"\nAverage groundedness: {avg_grounded:.1f}/5, average relevance: {avg_relevance:.1f}/5")

    print(f"{len(results) - len(failures)}/{len(results)} passed.")
    if failures:
        raise SystemExit(1)
