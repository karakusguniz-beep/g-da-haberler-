name: Gunluk Gida Sinyal Raporu

on:
  schedule:
    - cron: '0 5 * * *'
  workflow_dispatch:

jobs:
  run-report:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # Projeye raporu kaydetme iznini doğrudan buradan veriyoruz

    steps:
      - name: Kodu Cek
        uses: actions/checkout@v4.2.2

      - name: Python Kur
        uses: actions/setup-python@v5.3.0
        with:
          python-version: '3.10'

      - name: Kutuphaneleri Yukle
        run: pip install google-genai

      - name: Raporu Uret
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python daily_food_signal_agent_gemini.py

      - name: Raporu Kaydet
        run: |
          git config --global user.name "Sinyal Botu"
          git config --global user.email "bot@github.com"
          git add gunluk_raporlar/
          git commit -m "Gunluk rapor eklendi: $(date +'%Y-%m-%d')" || exit 0
          git push
