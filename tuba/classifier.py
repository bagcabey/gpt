from dataclasses import dataclass
from typing import Literal

Intent = Literal["command", "chat"]


COMMAND_KEYWORDS = {
    "aç",
    "kapat",
    "açık",
    "kapalı",
    "ses",
    "tıkla",
    "yaz",
    "başlat",
    "duraklat",
    "oynat",
    "kaydet",
}


CHAT_KEYWORDS = {"nasılsın", "selam", "merhaba", "naber", "duygu", "üzgün", "mutlu"}


@dataclass
class ClassificationResult:
    intent: Intent
    confidence: float


def classify(text: str) -> ClassificationResult:
    words = set(text.split())
    if words & COMMAND_KEYWORDS:
        return ClassificationResult(intent="command", confidence=0.8)
    if words & CHAT_KEYWORDS:
        return ClassificationResult(intent="chat", confidence=0.6)
    # Varsayılanı komut yaparak eylem tarafını tetikte tutuyoruz; gerçek LLM burada devreye girecek.
    return ClassificationResult(intent="command", confidence=0.5)
