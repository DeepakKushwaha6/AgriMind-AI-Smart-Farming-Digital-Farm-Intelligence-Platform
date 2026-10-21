# AgriMind AI — Production Backend & DevOps Guide

Digital Farm Intelligence Platform backend powering evidence-aware agronomic recommendations, weather and mandi market intelligence, BYOK API key management with polite web scraping fallback, and multi-user farm management.

---

## 1. Architecture Overview

```
                      ┌────────────────────────────────────────┐
                      │    Frontend (Tailwind CDN + Chart.js)  │
                      └──────────────────┬─────────────────────┘
                                         │ Bearer Token / HTTPS
                                         ▼
                      ┌────────────────────────────────────────┐
                      │    FastAPI Application (Port 8000)     │
                      │  - Pydantic v2 Input Validation       │
                      │  - Argon2 Password Hashing & PyJWT     │
                      │  - SlowAPI Strict Rate Limiter         │
                      └──────────────────┬─────────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        ▼                                ▼                                ▼
┌──────────────┐               ┌──────────────────┐             ┌──────────────────┐
│ KeyResolver  │               │ DecisionEngine   │             │ ScraperConnector │
│  Resolution: │               │  (Pure Python)   │             │ - robots.txt     │
│ 1. User BYOK │               │ - Irrigation     │             │ - 3s Rate Limit  │
│ 2. Shared Key│               │ - Urea Splitting │             │ - ETag / 304     │
│ 3. Free API  │               │ - Net Realisation│             │ - HTML Validator │
│ 4. Scraper   │               └──────────────────┘             └──────────────────┘
│ 5. Cache     │
└──────────────┘
```

---

## 2. Local Setup (Step-by-Step)

### Prerequisites
- Python 3.11+
- Tesseract OCR (`sudo apt install tesseract-ocr tesseract-ocr-hin` or `brew install tesseract`)

### Step 1: Clone & Virtual Environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Environment Configuration
```bash
cp .env.example .env
# Edit .env with your secrets
```

### Step 3: Run Alembic Migrations & Seed Initial Data
```bash
alembic upgrade head
python scripts/seed.py
```

### Step 4: Start Development Server
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI documentation is available at:
- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`

---

## 3. How to Obtain Each Free Key

| Category | Provider | Free Tier Limits | How to Obtain |
| :--- | :--- | :--- | :--- |
| **AI** | **OpenRouter** | 20 RPM on `:free` models | Sign up at [openrouter.ai/keys](https://openrouter.ai/keys) (No credit card required). |
| **AI** | **Google Gemini** | Free quota via AI Studio | Create key at [aistudio.google.com](https://aistudio.google.com). |
| **Mandi** | **data.gov.in** | 10,000 req/month free | Register at [data.gov.in](https://data.gov.in) and request AGMARKNET API key. |
| **Maps** | **Google Maps** | Free Demo Key or $200/mo free credit | Enable via AI Studio Google Maps setup or Google Cloud Console. |
| **Weather** | **Open-Meteo** | Free 10,000 req/day | **No API key required** (Keyless by default). |
| **Satellite** | **Copernicus** | Free Sentinel-2 L2A | Register at [dataspace.copernicus.eu](https://dataspace.copernicus.eu). |

---

## 4. Free Hosted Postgres (Neon / Supabase)

Free hosting instances such as Render have ephemeral file disks that erase SQLite on restarts. Use a free cloud Postgres:

1. **Neon Free Tier** (Serverless Postgres with scale-to-zero):
   - Sign up at [neon.tech](https://neon.tech).
   - Create a project named `agrimind-db`.
   - Copy your async connection string:
     `DATABASE_URL=postgresql+asyncpg://<user>:<password>@<ep-id>.us-east-2.aws.neon.tech/neondb?ssl=require`
2. Update `DATABASE_URL` in your Render dashboard environment variables.
3. Run `alembic upgrade head` and `python scripts/seed.py`.

---

## 5. Free Deployment on Render (API) & Vercel (Frontend)

### Deploying FastAPI on Render (Free Tier)
1. Push your repository to GitHub.
2. In [dashboard.render.com](https://dashboard.render.com), click **New Web Service** and connect your repo.
3. Settings:
   - **Root Directory:** `backend`
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt && alembic upgrade head && python scripts/seed.py`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`
4. Add environment variables from `.env.example` (set `DATABASE_URL`, `JWT_SECRET_KEY`, `APP_ENCRYPTION_KEY`, `FRONTEND_ORIGINS`).

### Free Uptime Pinger (Preventing Cold Starts)
Free Render instances spin down after 15 minutes of inactivity. To keep it awake:
1. Register on [cron-job.org](https://cron-job.org) or [uptimerobot.com](https://uptimerobot.com) (both 100% free).
2. Set up an HTTP GET monitor every 10 minutes to:
   `https://your-agrimind-api.onrender.com/health`
3. The frontend displays an automatic *"Server is waking up (up to 60s)"* banner if an initial ping takes longer than 3 seconds.

---

## 6. Embedding in Google Sites / Third-Party Iframes

Google Sites embeds web apps inside a sandboxed cross-origin iframe. Standard cookies (`SameSite=Lax` or third-party cookies) are blocked in sandboxed iframes.
- AgriMind AI stores the JWT access token in browser memory / localStorage and sends it via the `Authorization: Bearer <token>` header on every API request.
- Ensure `FRONTEND_ORIGINS` in backend config allows your Google Sites domain or `*` if needed.

---

## 7. API Keys vs. Free Fallback Policy

1. **Mode A (User Key Present):** If the farmer saves their personal API key in **Settings > API Keys**, AgriMind AI uses their private key with priority.
2. **Mode B (No Key):** If no key is configured, the system seamlessly falls back to keyless free APIs (Open-Meteo, Nominatim) and scheduled polite web scraping.
3. **Labels:** Every data card visibly discloses its provenance (e.g., *"Updated 12m ago • Source: Open-Meteo"* or *"Source: Web Scraping"*).
