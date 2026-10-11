# GeM Tender Assistant

A local desktop assistant for preparing and reviewing Government e-Marketplace tenders.

## Easy setup (Windows)

1. Install Python 3.11+ from https://www.python.org/downloads/ (tick **Add Python to PATH**).
2. Download this repository as a ZIP and extract it, or clone it with Git.
3. Double-click **`setup_and_run.bat`**. It creates a virtual environment, installs dependencies, and launches the app. The next run reuses the installed environment.

## Start manually

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python desktop_app.py
```

## What it does

- Embedded Chromium/GeM browser on the left (~70%) and controls on the right (~30%).
- Login helper for user ID, password and the CAPTCHA that the user reads manually. It tries to fill visible form fields; review the page and click Login yourself.
- Tender preferences: location, department, supply category, EMD preference and keywords.
- Checklist for MSME/Udyam, catalogue, price quote, PAN, Aadhaar/authorised signatory ID, GST, turnover, ITR/CA, experience, OEM authorisation, bank details and DSC readiness.
- Optional AI document-analysis workbench using Gemini/Groq (`streamlit run app.py`).

## API keys in the UI

Open the desktop app and paste Gemini and/or Groq API keys into **AI API keys**. Click **Save API keys securely** once. The app stores keys in the operating system credential store via Python keyring (for example, Windows Credential Manager); it does not write them into this repository or a plaintext settings file. Saved keys are automatically loaded for the optional AI workbench on later runs. Empty fields leave previously saved keys unchanged. You can replace a key by entering a new one.

- Gemini: https://aistudio.google.com/apikey
- Groq: https://console.groq.com/keys

If the operating-system credential store is unavailable or locked, the app will report that it could not save the keys.

## Safe-use boundaries

- CAPTCHA must be solved by the user. No CAPTCHA bypass.
- The login helper uses heuristic field detection, so it may not match every portal layout. You can enter details directly in Chromium.
- The app does not automatically sign declarations or submit bids. Review and final submission remain with the user.
- Tender text sent to a cloud AI provider leaves your computer. Upload only data you are authorised to share.
- Never commit portal credentials, API keys, bid documents or certificates.
- A checked document is not proof it is required or valid for a specific bid. Verify the official bid document and amendments.

## AI workbench

```bash
streamlit run app.py
```

It extracts text from PDF, DOCX, XLSX, XLS, CSV, TXT and Markdown files and can ask the configured provider to summarise requirements. Scanned PDFs may need OCR.

## Official resources

- [GeM](https://gem.gov.in/)
- [GeM Seller User Manual](https://assets-bg.gem.gov.in/resources/pdf/seller-user-manual.pdf)
- [Gemini API limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Groq API limits](https://console.groq.com/docs/rate-limits)
