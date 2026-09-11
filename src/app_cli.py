from src.agents.lead import LeadAgent
from loguru import logger

lead_agent = LeadAgent()


def run():
    print(
        "Mentor Bahasa Inggris Virtual \n"
        "Coba tulis pesan: \n"
        "- buatkan soal reading \n"
        "- periksa: I goes to school \n"
        "- berikan saya tips belajar \n"
        "atau ngobrol bebas"
    )

    while True:
        prompt = input("[user]: ")

        if prompt.lower() == "/exit":
            break

        response = lead_agent.handle_send_message(user_id=101010, message_text=prompt)
        logger.debug(response)

        print(f"[AI]: {response["text"]}")

        if response["artifacts"]:
            artifacts_data = response["artifacts"].data
            for item in artifacts_data:
                logger.info(f"lokasi artifact: {item["artifact"]}")