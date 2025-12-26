import re
from typing import List

FILLERS = {"ıı", "ii", "şey", "yani", "hımm", "hmm", "hım"}


def normalize(text: str) -> str:
    lowered = text.lower()
    # Noktalama sadeleştirme.
    cleaned = re.sub(r"[^\w%çğıöşü\s]", " ", lowered)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def drop_fillers(tokens: List[str]) -> List[str]:
    return [tok for tok in tokens if tok not in FILLERS]


def preprocess(text: str) -> str:
    normalized = normalize(text)
    tokens = normalized.split()
    tokens = drop_fillers(tokens)
    return " ".join(tokens)
