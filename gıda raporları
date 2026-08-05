#!/usr/bin/env python3
"""
Günlük Gıda Sektörü Sinyal Ajanı — Gemini API sürümü
------------------------------------------------------
Claude API yerine Google Gemini API'sini (Google Search grounding aracıyla
birlikte) kullanır. Mantık aynı: dış kaynakları tarar, analiz eder, tarihli
bir Markdown rapor olarak kaydeder.

KURULUM:
  1. pip install google-genai
  2. Google AI Studio'dan (aistudio.google.com) ÜCRETSİZ bir API anahtarı al.
     Not: Bu anahtar Gemini Pro (chat) aboneliğinden AYRI bir şeydir -
     ayrıca almak gerekiyor, ama küçük ölçekli günlük kullanım için Google'ın
     ücretsiz kotası genelde yeterli olur (güncel limitleri ai.google.dev
     üzerinden kontrol et).
  3. Ortam değişkeni olarak tanımla:
       export GEMINI_API_KEY="AIza..."      (Mac/Linux)
       setx GEMINI_API_KEY "AIza..."        (Windows, kalıcı)
  4. Aşağıdaki SECTOR_FOCUS ve EXPORT_MARKETS listelerini kendi işine göre düzenle.

ÇALIŞTIRMA:
  python3 daily_food_signal_agent_gemini.py

OTOMATİK GÜNLÜK ÇALIŞTIRMA:
  - Mac/Linux (cron):   crontab -e
        0 8 * * *  cd /path/to/script && /usr/bin/python3 daily_food_signal_agent_gemini.py
  - Windows: Görev Zamanlayıcısı -> "Temel Görev Oluştur" -> Günlük -> Program:
        python.exe   Argümanlar: C:\\path\\to\\daily_food_signal_agent_gemini.py

NOT: Model adı zamanla değişebilir (Google sık sık yeni sürüm çıkarıyor).
     Güncel model listesi: https://ai.google.dev/gemini-api/docs/models
"""

import os
import sys
import datetime
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit("Hata: 'google-genai' paketi kurulu değil. Önce çalıştır: pip install google-genai")

# ---------------------------------------------------------------------------
# AYARLAR — kendi işine göre burayı düzenle
# ---------------------------------------------------------------------------

SECTOR_FOCUS = [
    "gıda mevzuatı ve yönetmelik değişiklikleri (Resmi Gazete, Tarım ve Orman Bakanlığı)",
    "yeni gıda üretim tesisi yatırımları, IPARD/teşvik haberleri",
    "yaklaşan gıda fuarları ve katılımcı duyuruları",
    "ihracat pazarlarındaki gıda güvenliği mevzuat değişiklikleri",
]

EXPORT_MARKETS = ["Avrupa Birliği", "Orta Doğu", "Körfez Ülkeleri"]

OUTPUT_DIR = Path("./gunluk_raporlar")
MODEL = "gemini-2.5-flash"  # güncel model adını ai.google.dev/gemini-api/docs/models'dan teyit et
LOOKBACK_DAYS = 7

# ---------------------------------------------------------------------------


def build_prompt() -> str:
    focus_list = "\n".join(f"{i+1}. {item}" for i, item in enumerate(SECTOR_FOCUS))
    markets = ", ".join(EXPORT_MARKETS)
    return f"""Türkiye'deki gıda sektörünü ilgilendiren şu alanlarda son {LOOKBACK_DAYS} gün
içindeki güncel gelişmeleri web'de tara ve özetle:

{focus_list}

İhracat pazarı mevzuatı için özellikle şu bölgelere odaklan: {markets}.

Her bulgu için:
- Kısa başlık
- 2-3 cümlelik özet (kendi cümlelerinle, alıntı yapma)
- Kaynak adı ve tarih
- Bu bilginin bir gıda analiz laboratuvarı satış mühendisi için neden bir
  fırsat/sinyal olduğuna dair 1 cümlelik yorum

Sadece gerçekten yeni ve somut gelişmeleri getir; genel/bilinen bilgileri tekrarlama.
Eğer bir kategoride yeni bir şey bulamazsan, o kategoriyi 'bu dönemde yeni gelişme yok'
diyerek kısaca geç. Türkçe yaz."""


def run_agent() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Hata: GEMINI_API_KEY ortam değişkeni tanımlı değil.")

    client = genai.Client(api_key=api_key)

    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(tools=[grounding_tool])

    response = client.models.generate_content(
        model=MODEL,
        contents=build_prompt(),
        config=config,
    )

    return (response.text or "").strip()


def save_report(text: str) -> Path:
    OUTPUT_DIR.mkdir(exist_ok=True)
    today = datetime.date.today().isoformat()
    out_path = OUTPUT_DIR / f"sinyal_raporu_{today}.md"
    header = f"# Günlük Gıda Sektörü Sinyal Raporu (Gemini) — {today}\n\n"
    out_path.write_text(header + text, encoding="utf-8")
    return out_path


def main():
    print("Sinyal taraması başlatılıyor (Gemini)...")
    report_text = run_agent()
    out_path = save_report(report_text)
    print(f"Rapor kaydedildi: {out_path.resolve()}")


if __name__ == "__main__":
    main()
