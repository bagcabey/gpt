# gpt

Bu depo, TUBA sesli asistanı için çalışan bir metin-tabanlı simülasyon içerir. Amaç,
çevrimdışı mimariyi gerçek zamanlı akışa benzer şekilde uçtan uca test edebilmektir.

## Nasıl çalıştırılır (tam akış)

1. Python 3.10+ kurulu olmalı.
2. Sistemde Tesseract kurulu olmalı (OCR için). Windows’ta `choco install tesseract`, Ubuntu’da `sudo apt install tesseract-ocr tesseract-ocr-tur`.
3. Bağımlılıkları kurun:

   ```bash
   pip install -r requirements.txt
   ```

4. CLI’yi başlatın (mikrofon dinler):

   ```bash
   python -m tuba.tuba_cli
   ```

   Yalnızca metinle test etmek için `--stdin` ekleyin.

5. Komut örnekleri: `whatsapp aç`, `sesi %50 yap`, `kaydol tıkla`, `merhaba nasılsın`.
6. Kritik işlemler (kapatma/silme vb.) için sistem onay isteyecektir.
7. Çıkmak için `Ctrl+C`.

> LLaMA modeli ilk çalıştırmada `models/` klasörüne otomatik indirilir (TinyLlama GGUF). Farklı bir model kullanmak için `TUBA_LLAMA_MODEL` ortam değişkeniyle yolu belirtin.

## Mimari (özet)

- `tuba/stt.py`: Mikrofon yerine stdin’den metin alan mock STT.
- `tuba/preprocess.py`: Normalizasyon ve dolgu kelime temizleme.
- `tuba/classifier.py`: Komut/sohbet ayrımı.
- `tuba/decision.py`: Yapılandırılmış aksiyon üretimi, kural + LLaMA hibrit.
- `tuba/llm.py`: Yerel GGUF LLaMA yükleyicisi (llama-cpp-python).
- `tuba/ocr.py`: Ekran görüntüsü alır, Tesseract ile metin arar.
- `tuba/executor.py`: Uygulama açma, OCR tıklaması, koordinat tıklaması, yazma, ses ayarı (hotkey ile).
- `tuba/tts.py`: TTS yerine düz metin döndürür.

## Belgeler

- [TUBA – Sesli Asistan Sistemi Brifingi](docs/tuba_voice_assistant_briefing.md): Çevrimdışı mimari, karar akışı, eylem katmanı ve test önerilerinin özetleri.
