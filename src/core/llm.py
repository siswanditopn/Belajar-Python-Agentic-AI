import src.core.env as env
from functools import lru_cache
from google import genai

@lru_cache(maxsize=1)
def get_gemini_client():
    gemini_client = genai.Client(
        api_key=env.GEMINI_API_KEY
    )

    return gemini_client