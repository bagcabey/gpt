import queue
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Iterable
import sys
import urllib.request

import sounddevice as sd
from vosk import KaldiRecognizer, Model

from .config import DEFAULT_VOSK_URL, VOSK_DIR, VOSK_ZIP_PATH


@dataclass
class Transcript:
    text: str
    is_final: bool = True


class STTClient:
    """
    Vosk tabanlı Türkçe STT.
    - Model yoksa indirir ve çıkarır.
    - Mikrofon dinleme (default)
    - Test için stdin kaynaklı satır akışını da destekler.
    """

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self.model = self._ensure_model()

    def _ensure_model(self) -> Model:
        if not VOSK_DIR.exists():
            VOSK_DIR.parent.mkdir(parents=True, exist_ok=True)
            print(f"Vosk modeli indiriliyor → {VOSK_ZIP_PATH}")
            urllib.request.urlretrieve(DEFAULT_VOSK_URL, VOSK_ZIP_PATH)
            print("Model indirildi, açılıyor...")
            with zipfile.ZipFile(VOSK_ZIP_PATH, "r") as zf:
                zf.extractall(VOSK_DIR.parent)
            print("Model açıldı.")
        return Model(str(VOSK_DIR))

    def stream(self, source: Optional[Iterable[str]] = None) -> Iterable[Transcript]:
        if source is not None:
            for line in source:
                text = line.strip()
                if text:
                    yield Transcript(text=text)
            return

        q: "queue.Queue[bytes]" = queue.Queue()

        def _callback(indata, frames, time, status):
            if status:
                print(status, file=sys.stderr)
            q.put(bytes(indata))

        recognizer = KaldiRecognizer(self.model, self.sample_rate)
        with sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=8000,
            device=None,
            dtype="int16",
            channels=1,
            callback=_callback,
        ):
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    res = recognizer.Result()
                    text = self._extract_text(res)
                    if text:
                        yield Transcript(text=text, is_final=True)
                else:
                    partial = recognizer.PartialResult()
                    text = self._extract_partial(partial)
                    if text:
                        yield Transcript(text=text, is_final=False)

    @staticmethod
    def _extract_text(result_json: str) -> str:
        import json

        try:
            data = json.loads(result_json)
            return data.get("text", "").strip()
        except Exception:
            return ""

    @staticmethod
    def _extract_partial(result_json: str) -> str:
        import json

        try:
            data = json.loads(result_json)
            return data.get("partial", "").strip()
        except Exception:
            return ""
