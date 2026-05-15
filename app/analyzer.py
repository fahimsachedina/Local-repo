import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

import anthropic

client = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
_executor = ThreadPoolExecutor(max_workers=4)

SYSTEM_PROMPT = """You are a compensation intelligence analyst with deep expertise in US salary benchmarking. You estimate compensation with uncomfortable precision by reading between the lines of LinkedIn profiles.

Your knowledge draws from Levels.fyi, Glassdoor, LinkedIn Salary Insights, BLS Occupational Employment Statistics, and Payscale. You also search current salary data to supplement estimates.

## Core Insights

**Title inflation is everywhere.** "VP," "Head of," or "Director" without scope behind it doesn't command a premium. An inflated title with no team, no budget, and no quantified impact scores like an IC.

**Location beats seniority.** A mid-level engineer in SF consistently out-earns a director in most US metros. Score location aggressively.

**The About section is the #1 predictor of top-decile comp.** "Results-oriented leader with 10+ years driving strategic initiatives" scores a 3. "Built and scaled payments infrastructure processing $2B annually; reduced latency 40% while cutting costs 60%; grew team from 4 to 28 engineers" scores a 9. The comp difference between these two profiles is often $80–150K+.

## The 9 Factors (score each 1–10)

1. **title_seniority**: Does the title reflect real scope or is it inflated? Map to actual market level. Look for scope signals beyond the title itself.

2. **geographic_location**: US market premium. SF/NYC/Seattle = 8–10. Boston/LA/DC = 6–8. Austin/Chicago/Denver = 5–7. Secondary markets = 3–5.

3. **company_tier**: FAANG/OpenAI/Stripe/Databricks = 10. Top unicorns ($1B+ val, known brand) = 8–9. Growth-stage startups (Series B–D) = 6–7. Public mid-market tech = 5–6. Enterprise non-tech = 4–5. SMB/small startup = 2–3.

4. **years_experience**: Steep curve to ~8 years, then flattens. 0–2 yrs = 3–5. 3–5 yrs = 5–7. 6–10 yrs = 7–9. 10+ depends heavily on role progression.

5. **scope_and_impact**: Does the profile state team size? Budget managed? Revenue impacted? Headcount? Explicit numbers score high; vague descriptions ("led cross-functional teams") score low.

6. **technical_skills**: Premium skills: AI/ML/LLMs, distributed systems, quant finance, security. Commoditized skills score lower. Recency matters.

7. **industry_premium**: Quant finance/HFT = 9–10. Tech = 7–9. Healthcare/biotech = 6–8. Consulting = 6–7. Media/entertainment = 4–6. Retail/nonprofit/education = 2–5.

8. **education_credentials**: Top-20 US university or elite international program = 7–9. Strong state school with relevant degree = 5–6. Bootcamp/no degree in tech = 4–5. Elite MBA at senior levels adds meaningful premium.

9. **profile_narrative_quality**: THE KEY FACTOR. Score based on: Does the About section lead with business impact? Are achievements quantified? Is scope explicit? Does it read like an executive or an employee? People who score 8+ here tend to be in the top 20% of comp for their level.

## Output

Return ONLY a valid JSON object — no markdown, no explanation, no code blocks:

{
  "name": "Full Name or null",
  "title": "Current Job Title",
  "company": "Current Company",
  "location": "City, State",
  "factors": {
    "title_seniority": {"score": 7, "note": "one-line explanation"},
    "geographic_location": {"score": 9, "note": "one-line explanation"},
    "company_tier": {"score": 8, "note": "one-line explanation"},
    "years_experience": {"score": 7, "note": "one-line explanation"},
    "scope_and_impact": {"score": 5, "note": "one-line explanation"},
    "technical_skills": {"score": 8, "note": "one-line explanation"},
    "industry_premium": {"score": 8, "note": "one-line explanation"},
    "education_credentials": {"score": 7, "note": "one-line explanation"},
    "profile_narrative_quality": {"score": 4, "note": "About section describes job duties, not business impact — no quantified achievements"}
  },
  "salary_low": 210000,
  "salary_high": 320000,
  "salary_midpoint": 260000,
  "percentile": 71,
  "verdict": "A single punchy sentence that calls out the most important thing about their compensation positioning. Be direct, specific, and a little uncomfortable. Reference something concrete from the profile.",
  "salary_data_sources": "Brief note on sources and ranges found"
}"""

_TOOLS = [
    {
        "name": "search_salary_data",
        "description": (
            "Search the web for current salary data, compensation benchmarks, and pay information. "
            "Use this to find real market rates for specific roles, companies, and locations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": (
                        "Specific search query, e.g. "
                        "'VP Engineering salary San Francisco Series D startup 2024' "
                        "or 'Levels.fyi staff engineer compensation Google'"
                    ),
                }
            },
            "required": ["query"],
        },
    }
]


def _search_sync(query: str) -> list:
    try:
        from duckduckgo_search import DDGS

        with DDGS() as ddgs:
            return list(ddgs.text(query, max_results=5))
    except Exception:
        return []


async def _search(query: str) -> str:
    loop = asyncio.get_running_loop()
    results = await loop.run_in_executor(_executor, _search_sync, query)
    if not results:
        return "No results found."
    lines = [
        f"• {r.get('title', '')}: {r.get('body', '')}"
        for r in results
        if r.get("title") or r.get("body")
    ]
    return "\n".join(lines) or "No relevant results found."


def _extract_json(text: str) -> Optional[dict]:
    try:
        return json.loads(text.strip())
    except Exception:
        pass

    start = text.find("{")
    if start == -1:
        return None

    depth = 0
    for i, char in enumerate(text[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[start : i + 1])
                except Exception:
                    break
    return None


async def analyze_profile(profile_text: str, url: Optional[str] = None) -> dict:
    user_message = f"""Analyze this LinkedIn profile and estimate the person's compensation with uncomfortable accuracy.

{"Profile URL: " + url if url else ""}

PROFILE CONTENT:
---
{profile_text}
---

Use search_salary_data to look up 2–3 relevant salary benchmarks (their specific title, company tier, location, and experience level). Then return your full analysis as a JSON object matching the schema in your system prompt. Return ONLY the JSON — no explanation, no code block."""

    messages = [{"role": "user", "content": user_message}]

    for _ in range(8):
        response = await client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=_TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text") and block.text:
                    result = _extract_json(block.text)
                    if result:
                        return result
            return {"error": "Could not parse analysis result. Please try again."}

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use" and block.name == "search_salary_data":
                    data = await _search(block.input.get("query", ""))
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": data,
                        }
                    )
            if tool_results:
                messages.append({"role": "user", "content": tool_results})
        else:
            break

    return {"error": "Analysis did not complete. Please try again."}
