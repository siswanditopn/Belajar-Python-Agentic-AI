import src.core.env as env
from functools import lru_cache
from supabase import Client, create_client

@lru_cache
def get_supabase_client():
    supabase: Client = create_client(
        supabase_url=env.SUPABASE_URL,
        supabase_key=env.SUPABASE_KEY
    )

    return supabase