import src.core.env as env
import src.core.llm as llm
import agents.services as services
import src.core.prompts as prompts
import src.core.artifacts as artifacts

from src.repository.chat_repository import ChatRepository
from google.genai import types
from loguru import logger

class LeadAgent:
    def __init__(self):
        # Gemini
        self.gemini_client = llm.get_gemini_client()

        # Agent
        self.tools = [
            services.skill_type_classification,
            services.evaluate_writing,
            services.get_learning_tip,
        ]

        # Chat repository
        self.chat_repository = ChatRepository()

        # Lead agent instruction
        self.lead_agent_instruction = prompts.load_instruction("agent-lead")
        logger.debug(f"[LOG]: {self.lead_agent_instruction}")

    def _load_history(self, user_id: int):
        """Mengambil history chat dari Supabase, kemudian diubah ke format Gemini"""

        response = self.chat_repository.load_history_by_user_id(user_id=user_id)

        # List comprehension
        return [
            types.Content(
                role=row["role"],
                parts=[
                    types.Part(
                        text=row["message_text"]
                    )
                ]
            )
            for row in response.data
        ]

    def handle_send_message(self, user_id: int, message_text: str):
        self.chat_repository.save_message(
            user_id=user_id,
            role="user",
            message_text=message_text
        )

        contents = self._load_history(user_id=user_id)

        # Siapkan keranjang artifact untuk setiap request
        artifacts.start()

        response = self.gemini_client.models.generate_content(
            model=env.GEMINI_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=self.lead_agent_instruction,
                tools=self.tools
            ),
            contents=contents
        )

        answer = response.text
        artifacts_data = artifacts.collect()

        # Handle artifact
        for item in artifacts_data:
            self.chat_repository.save_artifact(
                user_id=user_id,
                artifact_path=item["path"]
            )

        self.chat_repository.save_message(
            role="model",
            user_id=user_id,
            message_text=answer
        )

        collected_artifacts = self.chat_repository.get_last_artifact_by_user_id(user_id=user_id)

        return {"text":answer, "artifacts":collected_artifacts}

    def handle_send_voice(self, user_id: int, voice_file_path: str):
        self.chat_repository.save_message(
            user_id=user_id,
            role="user",
            message_text="[voice note]"
        )

        evaluation_speaking_result = services.evaluate_speaking(
            voice_file_path = voice_file_path
        )

        self.chat_repository.save_message(
            user_id=user_id,
            role="model",
            message_text=evaluation_speaking_result
        )

        return evaluation_speaking_result

    def handle_report(self, user_id: int, username: str, start_date: str, end_date: str):
        self.chat_repository.save_message(
            user_id=user_id,
            role="user",
            message_text=f"[generate learning report: {start_date} - {end_date}]"
        )

        history = self._load_history(user_id=user_id)

        report_file_path = services.generate_report(
            conversation_history=history,
            start_date=start_date,
            end_date=end_date,
            username=username
        )

        self.chat_repository.save_message(
            user_id=user_id,
            role="model",
            message_text=f"[generate learning report: {start_date} - {end_date} sudah selesai dicetak]"
        )

        return report_file_path