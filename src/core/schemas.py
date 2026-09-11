from pydantic import BaseModel, Field
from typing import Literal


class ListeningExerciseSchema(BaseModel):
    speaker_one: str = Field(..., description="Nama pembicara pertama, misalnya: 'Joe'")
    speaker_two: str = Field(..., description="Nama pembicara kedua, misalnya: 'Jane'")
    script: str = Field(
        ...,
        description="Dialog yang dibacakan oleh TTS (Text-to-speech), format: 'Joe: ...\\nJane:...' bergantian",
    )
    questions: list[str] = Field(
        ...,
        description="Daftar pertanyaan untuk menguji pemahaman peserta berdasarkan `script`",
    )


class EvaluateUserIntentionSchema(BaseModel):
    skill_types: Literal["reading", "speaking", "writing", "listening"] = Field(
        ..., description="pilihan salah satu skill_types yang dibutuhkan peserta"
    )


class LearningSkillTypesSchema(BaseModel):  # item latihan yang dilakukan peserta
    category: str = Field(
        ...,
        description="salah satu category skill_types: reading, speaking, writing dan listening",
    )
    title: str = Field(..., description="judul latihan")
    feedback: str = Field(
        ..., description="penilaian objective dengan metode sandwich feedback"
    )
    score: int = Field(..., description="nilai kemampuan dalam rentang 1 - 10")


class LearningReportSchema(BaseModel):  # laporan belajar
    start_date: str = Field(..., description="tanggal mulai belajar")
    end_date: str = Field(..., description="tanggal akhir belajar")
    username: str = Field(..., description="username dari peserta")
    global_score: int = Field(..., description="nilai keseluruhan")
    skill_types: list[LearningSkillTypesSchema]  # list of LearningSkillTypesSchema
    markdown_content: str = Field(
        ..., description="seluruh isi laporan dalam format markdown"
    )


class EvaluateSpeakingSchema(BaseModel):
    correction: str = Field(
        ..., description="catatan perbaikan pengucapan bahasa inggris untuk peserta"
    )
    score: str = Field(
        ...,
        description="rentang nilai dari 1 - 10 untuk pengucapan bahasa inggris dari peserta",
    )
    summary: str = Field(..., description="gabungan antara correction dan score")