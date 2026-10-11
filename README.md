# GeM Tender Assistant

A local-first starter for preparing and reviewing Government e-Marketplace (GeM) tenders.

- **Desktop workspace** (`desktop_app.py`): embedded Chromium on the left (~70%) and controls on the right (~30%).
- **Tender preferences**: location/delivery area, department, supply category, EMD preference, keywords.
- **Document readiness checklist**: MSME/Udyam, catalogue, pricing, PAN, Aadhaar/authorised-signatory ID, GST, turnover, ITR/CA, experience, OEM authorisation, bank details, DSC readiness.
- **Login helper**: lets you type credentials and the CAPTCHA you read yourself, then fills detected fields in the visible browser. Credentials are not saved by the desktop app.
- **AI workbench** (`app.py`): document extraction and AI-assisted tender review using Gemini/Groq.
- **Provider routing** (`ai_router.py`): fallback/cooldown support for AI calls.

> **Human-in-the-loop boundary:** CAPTCHA must be solved by the user. The app does not bypass CAPTCHA or portal controls. Login field detection is heuristic. Review the browser after filling. It does not automatically submit bids, sign declarations, or make binding procurement decisions. Final review and submission stay with the user.

## Install

Python 3.10+ and a desktop environment with Qt WebEngine are recommended.

### macOS / Linux
```bash
git clone https://github.com/crtl-gif/GeM.git
cd GeM
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Windows PowerShell
```powershell
git clone https://github.com/crtl-gif/GeM.git
cd GeM
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Start the embedded Chromium workspace

```bash
python desktop_app.py
```

The window opens GeM in a Chromium view with approximately 70% browser and 30% controls.

1. Navigate to the correct GeM login page in the browser on the left.
2. Enter your user ID, password, and the CAPTCHA visible in the browser into the right panel.
3. Click **Fill login fields in browser**, inspect the browser, and click the portal's Login button yourself. If field detection fails, type directly into the portal.
4. Choose location, department, supply category, EMD preference, and keywords. Use **Prepare search terms** and apply criteria in the portal.
5. Tick documents only when available and valid. **Copy tender plan** copies a summary without credentials.
6. Verify the exact bid document and perform final portal actions manually.

The app clears ID/password/CAPTCHA fields from its own panel after trying to fill the browser. It does not persist them in a file, database, or audit log. The website receives credentials when you fill and submit its login form. The embedded browser may retain website cookies/session data, so sign out when finished.

## Optional AI tender-analysis workbench

Copy `.env.example` to `.env` and add one or both keys:
```dotenv
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
```
Then run:
```bash
streamlit run app.py
```
Get keys from [Google AI Studio](https://aistudio.google.com/apikey) and [Groq Console](https://console.groq.com/keys). Do not commit `.env`. Tender text sent to a cloud AI provider leaves your computer; upload confidential files only if authorised.

## Security and accuracy

- Never commit `.env`, portal credentials, CAPTCHA values, bid documents, certificates, or private tender files.
- Login field matching is heuristic and may not work on every GeM page version.
- A checked document is not proof that the tender requires it or that it meets bid conditions.
- AI can miss eligibility clauses, exemptions, amendments, or deadlines. Verify against the official bid document.
- The current desktop app prepares search criteria but does not scrape tenders or automatically submit a bid.
- Scanned PDFs may need OCR.

## Official resources

- [GeM](https://gem.gov.in/)
- [Government Services Portal: GeM overview](https://services.india.gov.in/service/detail/government-e-marketplace-gem)
- [GeM Seller User Manual (PDF)](https://assets-bg.gem.gov.in/resources/pdf/seller-user-manual.pdf)
- [Gemini API rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Groq API rate limits](https://console.groq.com/docs/rate-limits)

No undocumented bid-submission API is assumed. Confirm current portal rules and obtain written authorisation before adding deeper integrations.
