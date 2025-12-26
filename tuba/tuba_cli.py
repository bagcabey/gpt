import argparse
from dataclasses import asdict

from .stt import STTClient, Transcript
from .preprocess import preprocess
from .classifier import classify
from .decision import decide, Decision
from .executor import execute
from .tts import speak


def handle_confirmation(
    transcript: Transcript, pending: Decision | None
) -> tuple[Decision | None, bool]:
    if not pending:
        return None, False
    text = transcript.text.lower()
    if text in {"evet", "onay", "tamam", "uygula"}:
        confirmed = Decision(
            action=pending.parameters.get("action", pending.action),
            parameters=pending.parameters.get("parameters", pending.parameters),
            response="Onaylandı, işlem yapılıyor.",
        )
        return confirmed, True
    if text in {"hayır", "iptal"}:
        return None, True
    return None, False


def main() -> None:
    parser = argparse.ArgumentParser(description="TUBA sesli asistan")
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Mikrofon yerine stdin’den satırları oku (test için).",
    )
    args = parser.parse_args()

    print("TUBA sesli asistan başladı. Çıkmak için Ctrl+C.")
    stt = STTClient()
    pending: Decision | None = None
    try:
        source = None
        if args.stdin:
            import sys

            source = sys.stdin
        for transcript in stt.stream(source=source):
            # Onay bekleyen işlemi kontrol et
            confirmed_decision, handled = handle_confirmation(transcript, pending)
            if handled:
                pending = None
                if confirmed_decision:
                    payload = asdict(confirmed_decision)
                    result = execute(payload)
                    spoken = speak(result)
                    print(f"[Eylem] {spoken}")
                else:
                    print("[Bilgi] İşlem iptal edildi.")
                continue

            clean_text = preprocess(transcript.text)
            classification = classify(clean_text)
            decision = decide(clean_text, classification)
            decision_payload = asdict(decision)

            if decision.pending_confirmation:
                pending = decision
                spoken = speak(decision.response)
                print(f"[Onay] {decision.response}")
                continue

            result = execute(decision_payload)
            spoken = speak(result)
            print(f"[Karar] {decision_payload}")
            print(f"[Eylem] {spoken}")
    except KeyboardInterrupt:
        print("\nÇıkış yapılıyor...")


if __name__ == "__main__":
    main()
