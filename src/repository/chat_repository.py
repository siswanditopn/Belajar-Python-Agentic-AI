import src.core.supabase as supabase

from typing import Literal
from loguru import logger


class ChatRepository:
    def __init__(self):
        self.supabase = supabase.get_supabase_client()

    def save_message(
        self, user_id: int, role: Literal["user", "model"], message_text: str
    ):
        self.supabase.table("chat_histories").insert(
            {"user_id": user_id, "role": role, "message_text": message_text}
        ).execute()

    def load_history_by_user_id(self, user_id: int):
        result = (
            self.supabase.table("chat_histories")
            .select("role", "message_text")
            .eq("user_id", user_id)
            .order("created_at", desc=False)
            .execute()
        )

        return result

    def save_user(self, user_id: int, username: str, chat_id: int):
        exist_user = (
            self.supabase.table("chat_users")
            .select("user_id")
            .eq("user_id", user_id)
            .execute()
        )

        if len(exist_user.data) > 0:
            logger.debug(f"user {user_id} sudah terdaftar")
            return  # berhenti

        result = (
            self.supabase.table("chat_users")
            .insert({"user_id": user_id, "username": username, "chat_id": chat_id})
            .execute()
        )

        return result

    def save_artifact(self, user_id: int, artifact_path):
        self.supabase.table("chat_histories").insert(
            {
                "user_id": user_id,
                "role": "model",
                "message_text": "[audio]",
                "artifact": str(artifact_path),
            }
        ).execute()

    def get_last_artifact_by_user_id(self, user_id: int):
        result = (
            self.supabase.table("chat_histories")
            .select("artifact")
            .eq("user_id", user_id)
            .not_.is_("artifact", "null")  # artifact yang tidak kosong (null)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        return result

    def get_users(self):
        return self.supabase.table("chat_users").select("user_id").execute()