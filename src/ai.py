import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


# Load .env from the main project directory
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE, override=True)


def _get_secret(name, default=""):
    """Read configuration from environment or Streamlit secrets."""
    value = os.getenv(name, "").strip()

    if value:
        return value

    try:
        import streamlit as st
        return str(st.secrets.get(name, default)).strip()
    except Exception:
        return default


API_KEY = _get_secret("GEMINI_API_KEY")
MODEL = _get_secret("GEMINI_MODEL", "gemini-3.1-flash-lite")

client = genai.Client(api_key=API_KEY) if API_KEY else None


def _error_message(error, image=False):
    message = str(error)
    lower = message.lower()

    if "api_key_invalid" in lower or "invalid api key" in lower or "unauthorized" in lower:
        return "GEMINI AUTHENTICATION ERROR: Please check your Gemini API key."

    if any(x in lower for x in ["429", "resource_exhausted", "quota", "rate limit"]):
        return (
            "GEMINI API LIMIT REACHED: Check your API quota, "
            "billing and rate limits in Google AI Studio."
        )

    if any(x in lower for x in ["connection", "timeout", "network"]):
        return "CONNECTION ERROR: Check your internet connection."

    if "404" in lower or "not found" in lower:
        return (
            f"GEMINI MODEL ERROR: Model '{MODEL}' is unavailable "
            "or not enabled for your API key. Check your model selection."
        )

    prefix = "GEMINI IMAGE ERROR" if image else "GEMINI API ERROR"
    return f"{prefix}: {type(error).__name__}: {message[:1000]}"


def generate(prompt: str):
    """Generate text using Google Gemini."""

    if not API_KEY or client is None:
        return (
            "GEMINI API KEY NOT FOUND!\n\n"
            "Please add GEMINI_API_KEY to your project's .env file."
        )

    if not prompt or not prompt.strip():
        return "Please enter a question for Robo."

    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt
        )

        answer = response.text

        if not answer or not answer.strip():
            return (
                "The AI returned an empty response. "
                "Please try asking your question again."
            )

        return answer.strip()

    except Exception as e:
        return _error_message(e)


def tutor_fallback(prompt: str):
    """Offline fallback if Gemini is unavailable."""

    return (
        "Robo is currently in offline mode.\n\n"
        "Please check your Gemini API configuration and try again.\n\n"
        f"Your question: {prompt[:500]}"
    )


def generate_with_image(
    prompt: str,
    image_bytes: bytes,
    mime_type: str = "image/png"
):
    """Read, understand and explain uploaded study images using Gemini."""

    if not API_KEY or client is None:
        return (
            "GEMINI API KEY NOT CONFIGURED: "
            "Add GEMINI_API_KEY to your .env file or Streamlit Secrets."
        )

    if not image_bytes:
        return "Please upload an image first."

    try:
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )

        response = client.models.generate_content(
            model=MODEL,
            contents=[prompt, image_part]
        )

        answer = response.text

        if not answer or not answer.strip():
            return "The AI returned an empty response. Please try again."

        return answer.strip()

    except Exception as e:
        return _error_message(e, image=True)
