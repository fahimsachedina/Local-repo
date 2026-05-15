import os
import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

from .analyzer import analyze_profile
from .fetcher import fetch_linkedin_profile

app = FastAPI(title="LinkedIn Salary Estimator")

# ALLOWED_ORIGINS env var: comma-separated list of allowed frontend origins,
# or "*" (default) to allow all — set this in production to your frontend URL.
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "*")
_origins = ["*"] if _raw_origins.strip() == "*" else [o.strip() for o in _raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

_HTML = pathlib.Path(__file__).parent / "templates" / "index.html"


class AnalyzeRequest(BaseModel):
    url: Optional[str] = None
    profile_text: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def index():
    return _HTML.read_text()


@app.post("/api/analyze")
async def analyze(request: AnalyzeRequest):
    profile_text = request.profile_text

    if not profile_text and request.url:
        profile_text = await fetch_linkedin_profile(request.url)
        if not profile_text:
            return JSONResponse(
                status_code=422,
                content={
                    "error": "profile_required",
                    "message": "LinkedIn blocked the request. Please paste your profile text.",
                },
            )

    if not profile_text:
        return JSONResponse(
            status_code=422,
            content={
                "error": "profile_required",
                "message": "Please provide a LinkedIn URL or paste your profile text.",
            },
        )

    result = await analyze_profile(profile_text, request.url)
    return result
