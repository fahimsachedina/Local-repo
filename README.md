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

The profile narrative quality factor is the strongest predictor of whether someone is capturing their full market value. A profile that says "results-oriented leader" scores a 3. One that says "built payments infrastructure processing $2B annually, grew team from 4 to 28" scores a 9. The comp difference is often $80–150K.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your API key

```bash
cp .env.example .env
# Add your Anthropic API key to .env
```

Get a key at [console.anthropic.com](https://console.anthropic.com).

### 3. Run

```bash
python run.py
```

Open [http://localhost:8000](http://localhost:8000).

## Note on LinkedIn scraping

LinkedIn actively blocks automated profile access. If the URL fetch fails, the tool prompts you to paste your profile text. Copy everything visible on your LinkedIn page — headline, About section, all experience entries, education — for the most accurate estimate.

---

Built by Valley.
