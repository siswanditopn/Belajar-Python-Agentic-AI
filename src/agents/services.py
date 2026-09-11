import random
import json
import wave
import time

import src.core.env as env
import src.core.llm as llm
import src.core.prompts as prompts
import src.core.artifacts as artifacts

from datetime import datetime
from pathlib import Path
from google.genai import types
from markdown_pdf import MarkdownPdf, Section
from typing import Literal
from loguru import logger

from src.core.schemas import (
    LearningReportSchema,
    ListeningExerciseSchema,
    EvaluateUserIntentionSchema,
    EvaluateSpeakingSchema,
)

gemini_client = llm.get_gemini_client()
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")


def generate_exercise(
    text: str, skill_types: Literal["reading", "speaking", "listening", "writing"]
):
    logger.info(f"tools: generate_exercise - {skill_types}")

    match skill_types:
        case "writing":
            return writing_exercise(text=text)
        case "speaking":
            return speaking_exercise(text=text)
        case "listening":
            return listening_exercise(text=text)
        case "reading":
            return reading_exercise(text=text)


def writing_exercise(text: str):
    model = env.GEMINI_MODEL
    system_instruction = prompts.load_instruction("agent-writing-exercise")
    prompt = (
        f"Buatkan latihan writing berdasarkan permintaan user berikut ini: \n{text}"
    )

    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction),
    )

    logger.info("success generate writing exercise")

    return response.text


def speaking_exercise(text: str):
    model = env.GEMINI_MODEL
    system_instruction = prompts.load_instruction("agent-speaking-exercise")
    prompt = (
        f"Buatkan latihan speaking berdasarkan permintaan user berikut ini: \n{text}"
    )

    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction),
    )

    logger.info("success generate speaking exercise")

    return response.text


def reading_exercise(text: str):
    model = env.GEMINI_MODEL
    system_instruction = prompts.load_instruction("agent-reading-exercise")
    prompt = (
        f"Buatkan latihan reading berdasarkan permintaan user berikut ini: \n{text}"
    )

    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=system_instruction),
    )

    logger.info("success generate reading exercise")

    return response.text


def _listening_generate_script(text: str):
    model = env.GEMINI_MODEL
    system_instruction = prompts.load_instruction("agent-generate-script")
    prompt = f"Buatkan 1 latihan listening berdasarkan permintaan peserta berikut ini: \n{text}"

    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_json_schema=ListeningExerciseSchema.model_json_schema(),
        ),
    )

    data = ListeningExerciseSchema.model_validate(json.loads(response.text))

    return data


def _listening_generate_audio_script(generate_script: ListeningExerciseSchema):
    model = env.GEMINI_MODEL_TTS

    script = generate_script.script
    speaker_one = generate_script.speaker_one
    speaker_two = generate_script.speaker_two

    prompt = f"Buatkan audio (text-to-speech) dari percakapan antara dua orang pada script berikut ini: \n{script}"

    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
                    speaker_voice_configs=[
                        types.SpeakerVoiceConfig(
                            speaker=speaker_one,
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Puck"
                                )
                            ),
                        ),  # speaker_one -> laki - laki -> Puck
                        types.SpeakerVoiceConfig(
                            speaker=speaker_two,
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name="Kore"
                                )
                            ),
                        ),  # speaker_two -> perempuan -> Kore
                    ]
                )
            ),
        ),
    )

    candidates = response.candidates or []
    for candidate in candidates:
        parts = candidate.content.parts if candidate.content else []
        for part in parts:
            if part.inline_data and part.inline_data.data:
                return part.inline_data.data


def _write_wave_file(
    audio_output_path: Path,
    pcm: bytes,
    channels: int = 1,
    rate: int = 24000,
    sample_width: int = 2,
):
    with wave.open(str(audio_output_path), "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


def listening_exercise(text: str):

    env.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    audio_output_path = env.OUTPUT_DIR / f"listening-{timestamp}.wav"

    # 1. "model" untuk generate script percakapan dua orang
    generate_script = _listening_generate_script(text=text)

    # 2. "model" untuk generate audio berdasarkan `generate_script`
    audio = _listening_generate_audio_script(generate_script=generate_script)

    # 3. generate wave file
    _write_wave_file(audio_output_path, audio)

    # 4. catat file audio ke channel / jalur artifacts
    artifacts.add(
        path=audio_output_path,
        kind="audio",
        caption="dengarkan audio latihan listening ini, lalu jawab pertanyaannya.",
    )

    # 5. kembalikan daftar pertanyaan
    questions_text = "\n".join(
        f"- {question}" for question in generate_script.questions
    )

    logger.info("success generate listening exercise")

    return (
        "Audio latihan listening sudah berhasil dibuat dan terlampir otomatis"
        f"Pertanyaan: {questions_text}"
    )


def skill_type_classification(text: str):  # prompt dari user
    """Menentukan kebutuhan latihan yang tepat berdasarkan pesan yang disampaikan oleh peserta"""

    logger.info("tools: skill_type_classification")

    model = env.GEMINI_MODEL
    system_instruction = prompts.load_instruction("agent-skill-type-classifier")
    prompt = f"Analisa pesan yang disampaikan oleh peserta kemudian tentukan latihan `skill_types` yang tepat: \n{text}"

    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_json_schema=EvaluateUserIntentionSchema.model_json_schema(),
            temperature=0.3,
        ),
    )

    data = EvaluateUserIntentionSchema.model_validate(json.loads(response.text))

    return generate_exercise(text=text, skill_types=data.skill_types)


def get_learning_tip():
    """Memberikan 1 tips berguna untuk belajar bahasa inggris"""

    tips = [
        "Latihan berbicara 10 menit sehari lebih efektif daripada belajar 2 jam seminggu sekali.",
        "Tonton film atau series berbahasa Inggris dengan subtitle bahasa Inggris, bukan Indonesia.",
        "Catat 5 kata baru setiap hari dan coba gunakan masing-masing dalam satu kalimat.",
        "Jangan takut salah — kesalahan adalah bagian dari proses belajar yang paling berharga.",
        "Coba berpikir dalam Bahasa Inggris saat melakukan aktivitas sehari-hari.",
    ]

    return random.choice(tips)


def evaluate_writing(text: str):
    """Melakukan evaluasi dan review terhadap grammar dan penulisan dari teks bahasa inggris yang dikirim oleh peserta"""

    model = env.GEMINI_MODEL
    system_instruction = prompts.load_instruction("agent-evaluate-writing")
    prompt = f"Periksa grammar dari tulisan bahasa inggris berikut ini: \n{text}"

    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        ),
    )

    logger.success("success evaluate writing")

    return response.text


def evaluate_speaking(voice_file_path: str):
    """Periksa pelafalan dari file voice note (.ogg) yang dikirim oleh peserta"""

    model = env.GEMINI_MODEL
    system_instruction = prompts.load_instruction("agent-evaluate-speaking")
    prompt = "Dengarkan rekaman voice note berikut ini dan berikan penilaian kamu."

    voice_file = gemini_client.files.upload(file=voice_file_path)

    while voice_file.state.name == "PROCESSING":
        logger.info("file audio sedang diproses")
        time.sleep(5)
        voice_file = gemini_client.files.get(name=voice_file.name)

    if voice_file.state.name == "FAILED":
        raise ValueError("file audio gagal diupload")

    response = gemini_client.models.generate_content(
        model=model,
        contents=[voice_file, prompt],
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_json_schema=EvaluateSpeakingSchema.model_json_schema(),
            temperature=0.3,
        ),
    )

    data = EvaluateSpeakingSchema.model_validate(json.loads(response.text))

    logger.success("success evaluate speaking")

    return data.summary


def generate_report(
    conversation_history: list[types.Content],  # tipe contents Gemini
    username: str,
    start_date: str,
    end_date: str,
):
    """Membuat laporan belajar bahasa inggris dalam rentang waktu tertentu"""

    model = env.GEMINI_MODEL
    system_instruction = prompts.load_instruction("agent-report")
    prompt = f"Buatkan laporan belajar bahasa inggris atas nama {username} dari tanggal {start_date} sampai {end_date} dengan me-analisis riwayat latihan berikut ini: \n{conversation_history}"

    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_json_schema=LearningReportSchema.model_json_schema(),
        ),
    )

    data = LearningReportSchema.model_validate(json.loads(response.text))
    report_content = data.markdown_content

    env.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report_file_path = env.OUTPUT_DIR / f"laporan-belajar-{timestamp}.pdf"

    pdf = MarkdownPdf(toc_level=2)
    pdf.add_section(Section(report_content))
    pdf.save(report_file_path)

    logger.success("success generate report")

    return str(report_file_path)