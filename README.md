# LinkedIn Salary Estimator

An AI tool that reads your LinkedIn profile and estimates how much you make — with uncomfortable accuracy.

Paste a LinkedIn URL. An AI agent reads your profile, searches live salary databases, scores you on 9 compensation factors, and hands you back an estimated salary band, a percentile, and a one-line verdict.

## How it works

1. You paste your LinkedIn URL (or profile text directly)
2. An AI agent searches current salary databases for your role, company tier, and location
3. It scores you on 9 compensation factors
4. You get a salary band, your market percentile, and a direct verdict

## The 9 compensation factors

| Factor | What it measures |
|---|---|
| **Title & Seniority** | Is the title substantive or inflated? |
| **Geographic Location** | SF/NYC/Seattle vs. secondary markets |
| **Company Tier** | FAANG to SMB — the biggest comp determinant after location |
| **Years of Experience** | Relevant experience curve, not just tenure |
| **Scope & Impact** | Team size, budget, revenue — explicit numbers earn points |
| **Technical Skills** | In-demand (AI/ML, distributed systems) vs. commoditized |
| **Industry Premium** | Finance/tech vs. retail/nonprofit |
| **Education & Credentials** | Elite programs add premium at senior levels |
| **Profile Narrative Quality** | **The key factor.** Quantified achievements vs. job description language |

---

## Running locally (monolith mode)

Backend serves the frontend — one command, everything works.

```bash
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
python run.py          # → http://localhost:8000
```

---

## Deploying: frontend + backend separately

### 1. Deploy the backend

**Option A — Docker (Railway, Fly.io, Render, etc.)**

```bash
docker build -t salary-estimator .
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key \
  -e ALLOWED_ORIGINS=https://your-frontend.netlify.app \
  salary-estimator
```

Most platforms (Railway, Render, Fly.io) will auto-detect the `Dockerfile`. Set these environment variables in your platform's dashboard:

| Variable | Value |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `ALLOWED_ORIGINS` | Your frontend URL, e.g. `https://your-app.netlify.app` |

**Option B — Run directly on a VPS**

```bash
pip install -r requirements.txt
ANTHROPIC_API_KEY=your_key ALLOWED_ORIGINS=https://your-frontend.netlify.app \
  uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

### 2. Deploy the frontend

The standalone frontend lives in `frontend/`. It's two files: `index.html` and `config.js`.

**Before deploying**, edit `frontend/config.js` and set your backend URL:

```js
window.API_URL = 'https://your-backend.railway.app';
```

**Option A — Netlify**

1. Drag and drop the `frontend/` folder at [app.netlify.com](https://app.netlify.com) → "Deploy manually"
2. Done. No build step needed.

Or via CLI:
```bash
npx netlify-cli deploy --dir frontend --prod
```

**Option B — Vercel**

```bash
npx vercel frontend/
```

**Option C — GitHub Pages**

Push the `frontend/` folder contents to a `gh-pages` branch, or configure GitHub Pages to serve from the `frontend/` directory.

---

## Note on LinkedIn scraping

LinkedIn actively blocks automated profile access. If the URL fetch fails, the tool prompts you to paste your profile text. Copy everything visible on your LinkedIn page — headline, About section, all experience entries, education — for the most accurate estimate.

---

Built by Valley.
