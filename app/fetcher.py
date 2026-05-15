import re
from typing import Optional

import httpx
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Upgrade-Insecure-Requests": "1",
}

_BLOCKED_SIGNALS = [
    "Join LinkedIn",
    "Sign in to LinkedIn",
    "Create your free account",
    "authwall",
    "Sign in",
]


async def fetch_linkedin_profile(url: str) -> Optional[str]:
    """
    Attempt to fetch a public LinkedIn profile page.
    LinkedIn aggressively blocks scrapers, so this frequently returns None.
    The caller should fall back to asking the user to paste their profile text.
    """
    if not url or "linkedin.com" not in url:
        return None

    if not url.startswith("http"):
        url = "https://" + url

    try:
        async with httpx.AsyncClient(
            follow_redirects=True, timeout=20.0, headers=_HEADERS
        ) as client:
            response = await client.get(url)

        final_url = str(response.url)
        if any(x in final_url for x in ["login", "authwall", "signup", "checkpoint"]):
            return None

        if response.status_code in [401, 403, 429]:
            return None

        soup = BeautifulSoup(response.text, "lxml")

        for tag in soup.find_all(["script", "style", "nav", "footer", "header", "meta", "link"]):
            tag.decompose()

        body = soup.find("main") or soup.find("body")
        if not body:
            return None

        text = body.get_text(separator="\n", strip=True)
        text = re.sub(r"\n{3,}", "\n\n", text)

        if len(text) < 300:
            return None

        if any(signal in text for signal in _BLOCKED_SIGNALS):
            return None

        return text[:20_000]

    except Exception:
        return None
