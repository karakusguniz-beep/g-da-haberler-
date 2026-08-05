import os
import sys
import datetime
from pathlib import Path

try:
    from google import genai
    from google.genai import types
except ImportError:
    sys.exit("Hata: 'google-genai' paketi kurulu degil.")

# ---------------------------------------------------------------------------
# SEKTÖREL ODAK ALANLARI VE HEDEF PAZARLAR
# ---------------------------------------------------------------------------

SECTOR_FOCUS = [
    "gida mevzuati ve yonetmelik degisiklikleri (Resmi Gazete, Tarim ve Orman Bakanligi)",
    "yeni gida uretim tesisi yatirimlari, IPARD/tesvik haberleri",
    "yaklasan gida fuarlari ve katilimci duyurulari",
    "ihracat pazarlarindaki gida guvenligi mevzuat degisiklikleri",
]

EXPORT_MARKETS = ["Avrupa Birligi", "Orta Dogu", "Korfez Ulkeleri"]
OUTPUT_DIR = Path("./gunluk_raporlar")
MODEL = "gemini-2.0-flash"
LOOKBACK_DAYS = 7

# ---------------------------------------------------------------------------


def build_prompt() -> str:
    focus_list = "\n".join(f"{i+1}. {item}" for i, item in enumerate(SECTOR_FOCUS))
    markets = ", ".join(EXPORT_MARKETS)
    return f"""Turkiye'deki gida sektorunu ilgilendiren su alanlarda son {LOOKBACK_DAYS} gun
icindeki guncel gelismeleri web'de tara ve ozetle:

{focus_list}

Ihracat pazari mevzuati icin ozellikle su bolgelere odaklan: {markets}.

Her bulgu icin:
- Kisa baslik
- 2-3 cumlelik ozet (kendi cumlelerinle, alinti yapma)
- Kaynak adi ve tarih
- Bu bilginin bir gida analiz laboratuvari satis muhendisi icin neden bir firsat/sinyal olduguna dair 1 cumlelik yorum

Sadece gercekten yeni ve somut gelismeleri getir; genel/bilinen bilgileri tekrarlama.
Eger bir kategoride yeni bir sey bulamazsan, o kategoriyi 'bu donemde yeni gelisme yok' diyerek kisaca gec. Turkce yaz."""


def run_agent() -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        sys.exit("Hata: GEMINI_API_KEY ortam degiskeni tanimli degil.")

    client = genai.Client(api_key=api_key)

    # Grounding (Google Search) konfigürasyonu
    config = types.GenerateContentConfig(
        tools=[{"google_search": {}}]
    )

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
    header = f"# Gunluk Gida Sektoru Sinyal Raporu — {today}\n\n"
    out_path.write_text(header + text, encoding="utf-8")
    return out_path


def main():
    print("Sinyal taramasi baslatiliyor (Gemini)...")
    report_text = run_agent()
    out_path = save_report(report_text)
    print(f"Rapor basariyla kaydedildi: {out_path.resolve()}")


if __name__ == "__main__":
    main()
