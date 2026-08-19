import re

MAX_MESSAGE_LENGTH = 1000

INJECTION_PATTERNS = [
    re.compile(r"ignore (all|any|previous|prior) instructions", re.IGNORECASE),
    re.compile(r"disregard (all|any|previous|prior) instructions", re.IGNORECASE),
    re.compile(r"reveal (your|the) system prompt", re.IGNORECASE),
    re.compile(r"act as (an?|the)? ?(admin|administrator|developer|root)", re.IGNORECASE),
    re.compile(r"jailbreak", re.IGNORECASE),
]

PII_PATTERNS = {
    "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "employee_id": re.compile(r"\bFINEMP\d+\b"),
}


def check_input(message: str) -> str | None:
    if not message or not message.strip():
        return "Message cannot be empty."
    if len(message) > MAX_MESSAGE_LENGTH:
        return f"Message is too long (max {MAX_MESSAGE_LENGTH} characters)."
    for pattern in INJECTION_PATTERNS:
        if pattern.search(message):
            return "This message looks like an attempt to override the assistant's instructions and was blocked."
    return None


def check_output(answer: str, allowed_departments: list[str]) -> str:
    if "hr" in allowed_departments:
        return answer
    for pattern in PII_PATTERNS.values():
        if pattern.search(answer):
            return "[Response withheld: it referenced personal employee data outside your access level.]"
    return answer
