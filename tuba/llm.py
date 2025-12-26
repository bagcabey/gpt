import json
from pathlib import Path
from typing import Any, Dict
import urllib.request

from llama_cpp import Llama

from .config import DEFAULT_MODEL_URL, DEFAULT_MODEL_PATH, LLAMA_MODEL_ENV, MODELS_DIR


class LLMEngine:
    """
    Yerel LLaMA (GGUF) modeliyle çalışan basit karar üretici.
    Model eksikse otomatik indirir, ardından llama-cpp ile yükler.
    """

    def __init__(self, model_path: str | None = None):
        self.model_path = Path(model_path or LLAMA_MODEL_ENV)
        self._model: Llama | None = None

    def ensure_model(self) -> None:
        if self.model_path.exists():
            return
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        print(f"Model indiriliyor → {self.model_path} ...")
        urllib.request.urlretrieve(DEFAULT_MODEL_URL, self.model_path)
        print("Model indirildi.")

    def load(self) -> None:
        if self._model is not None:
            return
        self.ensure_model()
        self._model = Llama(model_path=str(self.model_path), n_ctx=2048, embedding=False)

    def structured_decision(self, user_text: str) -> Dict[str, Any]:
        """
        Kullanıcı metninden yapılandırılmış aksiyon JSON'u üretmeye çalışır.
        Başarısız olursa chat_response döner.
        """
        self.load()
        assert self._model is not None

        system_prompt = (
            "Sen bir masaüstü sesli asistanısın. ÇIKTIYI SADECE JSON OLARAK VER.\n"
            "Şema: {\"action\": string, \"parameters\": object, \"response\": string}\n"
            "Desteklenen eylemler: open_app(app_name), set_volume(level 0-100), "
            "click_ocr(target), type_text(text), chat_response(text).\n"
            "Güvensiz bir işlem ise chat_response ile uyar.\n"
        )
        prompt = f"<|system|>\n{system_prompt}\n<|user|>\n{user_text}\n<|assistant|>\n"
        completion = self._model(
            prompt,
            max_tokens=256,
            stop=["<|user|>", "<|system|>"],
            temperature=0.2,
        )
        text = completion["choices"][0]["text"]
        try:
            data = json.loads(text)
            if not isinstance(data, dict):
                raise ValueError("non-dict json")
            return {
                "action": data.get("action", "chat_response"),
                "parameters": data.get("parameters", {}) or {},
                "response": data.get("response", "Anladım."),
            }
        except Exception:
            return {
                "action": "chat_response",
                "parameters": {"text": user_text},
                "response": "Anladım.",
            }
