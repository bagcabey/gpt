from dataclasses import dataclass
from typing import Dict, Any, Optional

from .classifier import ClassificationResult
from .llm import LLMEngine


@dataclass
class Decision:
    action: str
    parameters: Dict[str, Any]
    response: str
    pending_confirmation: bool = False
    risk_tag: str | None = None


DEFAULT_ACTION = "chat_response"
RISKY_KEYWORDS = {"kapat", "bilgisayarı", "sil", "format"}


def decide(text: str, classification: ClassificationResult) -> Decision:
    words = text.split()

    if classification.intent == "chat":
        return Decision(
            action="chat_response",
            parameters={"text": text},
            response="Seni dinliyorum.",
        )

    app_name = _extract_app(words)
    volume = _extract_volume(words)

    if app_name:
        return Decision(
            action="open_app",
            parameters={"app_name": app_name},
            response=f"{app_name} açılıyor.",
        )

    if volume is not None:
        return Decision(
            action="set_volume",
            parameters={"level": volume},
            response=f"Ses %{volume} seviyesine ayarlanıyor.",
        )

    if "tıkla" in words:
        target = _extract_target(words)
        return Decision(
            action="click_ocr",
            parameters={"target": target},
            response=f"{target or 'hedef'} bulunursa tıklıyorum.",
        )

    # LLM devreye girer
    llm = LLMEngine()
    data = llm.structured_decision(text)
    decision = Decision(
        action=data.get("action", DEFAULT_ACTION),
        parameters=data.get("parameters", {}),
        response=data.get("response", "Anladım, sohbet için hazırım."),
    )

    # Riskli mi? Onay iste.
    if _is_risky(words) or decision.action in {"shutdown", "format", "delete"}:
        return Decision(
            action="pending",
            parameters={
                "action": decision.action,
                "parameters": decision.parameters,
            },
            response="Emin misin? Bu işlem kritik olabilir.",
            pending_confirmation=True,
            risk_tag="dangerous",
        )

    return decision


def _extract_app(words: list[str]) -> Optional[str]:
    if "aç" in words:
        try:
            idx = words.index("aç")
            if idx > 0:
                return words[idx - 1]
        except ValueError:
            pass
    return None


def _extract_volume(words: list[str]) -> Optional[int]:
    for word in words:
        if word.startswith("%") and word[1:].isdigit():
            return int(word[1:])
        if word.isdigit():
            value = int(word)
            if 0 <= value <= 100 and "ses" in words:
                return value
    return None


def _extract_target(words: list[str]) -> Optional[str]:
    if not words:
        return None
    try:
        idx = words.index("tıkla")
    except ValueError:
        return None
    return words[idx - 1] if idx > 0 else None


def _is_risky(words: list[str]) -> bool:
    return bool(set(words) & RISKY_KEYWORDS)
