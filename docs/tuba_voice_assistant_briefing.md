# TUBA – Sesli Asistan Sistemi

Bu belge, TUBA’nın çevrimdışı çalışan sesli asistan sisteminin uçtan uca akışını ve ana bileşenlerini özetler.

## 1. Amaç

Kullanıcının mikrofondan konuşarak bilgisayarla etkileşim kurmasını sağlar:

- Doğal Türkçe konuşmayı anlama.
- Komutları ayırt etme ve eyleme dönüştürme.
- Yanıtı sesli olarak iletme.
- İnternetsiz ve kesintisiz çalışma.

## 2. Genel Ses Akışı

1. **Kullanıcı konuşur** → Mikrofon.
2. **Speech to Text** → Vosk.
3. **Metin ön işleme** → Temizleme/normalleştirme.
4. **Karar motoru + LLM** → Yapılandırılmış karar.
5. **Eylem (C# / Windows)** → Uygulama, tıklama vb.
6. **Yanıt metni** → TTS ile seslendirme.

### Bileşen Haritası (Özet)

- **Ses yakalama**: Windows varsayılan mikrofonu, buffer’lı stream.
- **STT**: Vosk (Türkçe küçük model).
- **Ön işleme**: Normalizasyon, durak kelime temizleme.
- **Karar**: Kural motoru + TinyLLaMA (yerel), risk/onay katmanı.
- **Eylem**: C# komut yürütücüsü, input emülasyonu, pencere/ses kontrolü.
- **TTS**: pyttsx3, sadece kullanıcıya söylenecek cümle.

## 3. Ses Girişi (Mic → Metin)

- Varsayılan Windows mikrofonu sürekli veya tetikleyiciyle dinlenir.
- Buffer’lı ses akışı kullanılır.
- STT motoru: **vosk-model-small-tr-0.3** (hafif, hızlı, komut odaklı).
- Örnek: “WhatsApp aç” → `whatsapp aç`.

## 4. Metin Ön İşleme

- Küçük harfe çevirme.
- Dolgu kelimeleri silme (ıı, şey, yani, hımm).
- Noktalama sadeleştirme.
- Gereksiz boşlukları temizleme.

Amaç: Karar motoru için net ve temiz girdi sağlamak.

## 5. Komut mu, Sohbet mi?

- **Komut** örnekleri: “chrome aç”, “sesi %50 yap”, “kaydol yazısına tıkla”.
- **Sohbet** örnekleri: “nasılsın”, “bugün nasılsın”, “canım sıkkın”.
- Ayrım: kural motoru, bağlam, anahtar kelimeler.

Karar ağacı (basitleştirilmiş):

1. **Öncelikli kural eşleşmeleri**: Aç/kapat, ses ayarı, medya, tıklama/yazma.
2. **Sohbet/duygu tespiti**: Selamlaşma, duygu anahtarları, bağlam.
3. **LLM yorumu**: Serbest form komutlar; yapılandırılmış çıktıya dönüştürme.
4. **Güvenlik filtresi**: Silme/kapatma gibi kritik işlemler için onay.

## 6. Karar Verme

Çok katmanlı karar akışı:

1. **Güvenlik kontrolü**: tehlikeli ifadeler, kapatma/silme için önlemler.
2. **Kural tabanlı eşleşme**: önceden tanımlı komutlar, en hızlı yol.
3. **Bağlam & hafıza**: önceki konuşmalar, alışkanlıklar, duygu durumu.
4. **Yerel dil modeli (TinyLLaMA)**: serbest ifadeleri yorumlar, yapılandırılmış karar üretir.
5. **Risk/onay**: gerektiğinde sözlü onay ister.

### Karar çıktısı formatı

```json
{
  "action": "open_app",
  "parameters": {"app_name": "chrome"},
  "response": "Chrome açılıyor."
}
```

Bu yapı C# tarafınca kolayca uygulanır.

### Karar Motoru İpuçları

- Kural tabanlı sözlükte uygulama adları ve eşanlamlıları tutulur (örn. “edge”, “microsoft edge”, “tarayıcı”).
- Sayısal değerler normalize edilir: “yüzde elli” → `%50`; “otuz” → `30`.
- Bağlam saklama: Son açılan uygulama, son tıklanan metin, duygu etiketi.
- Onay gerektiren işlemler için `action` alanına `pending_confirmation: true` gibi bayrak eklenebilir.

## 7. Eylemin Uygulanması (C#)

- `open_app` → uygulama açılır.
- `set_volume` → sistem sesi ayarlanır.
- `click_xy` → ekranda tıklama yapılır.
- `type_text` → klavye yazısı.
- `media_play_pause` → medya kontrolü.

Gerçek donanım kontrolü: mouse, klavye, pencere, ses aygıtları.

### Uygulama Koşulları

- Çalışma ortamı: Windows 10/11, mikrofon erişimi açık.
- İzinler: Input emülasyonu ve pencere kontrolü için gerekli API izinleri.
- Stabilite: Uzun süreli dinleme oturumlarında bellek sızıntısı testleri yapılmalı.
- Hata yönetimi: Eylem katmanından dönen hatalar sesli olarak kısaca raporlanabilir (örn. “Chrome açılamadı, tekrar deneyeyim mi?”).

## 8. OCR Destekli Komutlar

Komut örnekleri: “Ayarlar butonuna tıkla”, “Kaydol yazısını bul”, “Mail adresimi yaz”.

Akış:

1. Konuşma alınır.
2. Ekran görüntüsü alınır.
3. OCR ile metin çıkarılır.
4. Hedef bulunur.
5. Tıklama/yazma uygulanır.

Başarı kriterleri:

- Hedef metin birden fazla kez bulunursa en görünür/merkeze en yakın olan seçilir.
- Bulunamazsa kullanıcıya sözlü geri bildirim verilir ve alternatif sorulur.

## 9. Yanıtın Seslendirilmesi (TTS)

- Motor: **pyttsx3** (yerel).
- Kurallar: sadece `response` alanı okunur; JSON/teknik metin okunmaz.
- Kısa ve doğal cümleler: “WhatsApp açılıyor.”, “Ses %30’a ayarlandı.”, “Kaydol bulundu, tıklıyorum.”

## 10. Duyguya Dayalı Davranış

- Örnek: Kullanıcı “Canım çok sıkkın” dediğinde duygu = üzgün.
- Tepki: yumuşak ton, sohbet odaklı yanıt, gerekirse öneri.

## 11. Sesli Onay Mekanizması

- Kritik komutlar (ör. bilgisayarı kapat, dosya sil) için doğrulama sorusu: “Emin misin?”
- Yanıt: “Evet” → işlem yapılır, “Hayır” → iptal edilir.

## 12. Yetenek Özeti

- Konuşmayı algılar, metne çevirir, anlamlandırır.
- Windows’u kontrol eder; tıklar, yazar, sesi yönetir, ekranı okur.
- Yanıtları seslendirir.
- Gerçek bir masaüstü ajan olarak konuşmayı eyleme dönüştürür.

## 13. Test ve Devreye Alma İpuçları

- **Mikrofon testi**: STT kanalını tek başına çalıştırıp gecikme ve doğruluk ölçün.
- **Komut senaryoları**: Aç/kapat, ses, medya, tıklama/yazma, OCR, onay gerektiren eylemler için ayrı test listeleri oluşturun.
- **Çevrimdışı teyit**: İnternet bağlantısı olmadan STT ve LLM çıktılarının sürekliliğini doğrulayın.
- **Günlükleme**: Her aşamada hafif log tutun (girdi metni, karar JSON’u, eylem sonucu) ve PII içermemesine dikkat edin.
- **Performans**: STT + karar + TTS toplam süresini <1.5 sn hedefleyin; gecikme artarsa buffer ve model boyutlarını optimize edin.
