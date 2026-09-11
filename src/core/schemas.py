from pydantic import BaseModel, Field
from typing import Literal

class ListeningExerciseSchema(BaseModel):
    speaker_one: str = Field(..., description="Nama pembicara pertama, misalnya: 'Vino'")
    speaker_two: str = Field(..., description="Nama pembicara kedua, misalnya: 'Fanny'")
    script: str = Field(..., description="Dialog yang dibacakan oleh Text-to-speech (TTS), format: 'Vino: ...\\nFanny: ...' secara bergantian")
    questions: list[str] = Field(..., description="Daftar pertanyaan untuk menguji pemahaman peserta berdasarkan 'script'")

class EvaluateUserIntentionSchema(BaseModel):
    skill_types: Literal["reading", "speaking", "writing", "listening"] = Field(..., description="Pilihan salah satu skill_types yang dibutuhkan peserta")

class LearningSkillTypesSchema(BaseModel): #Item latihan yang dilakukan peserta
    category: str = Field(..., description="Salah satu kategori skill_types: reading, speaking, writing, dan listening")
    title: str = Field(..., description="Judul latihan")
    feedback: str = Field(..., description="Penilaian objektif dengan metode sandwich feedback")
    score: int = Field(..., description="Nilai kemampuan dalam rentang 1-10")

class LearningReportSchema(BaseModel): #Laporan belajar
    start_date: str = Field(..., description="Tanggal mulai belajar")
    end_date: str = Field(..., description="Tanggal akhir belajar")
    username: str = Field(..., description="Username dari peserta")
    global_score: int = Field(..., description="Nilai keseluruhan")
    skill_types: list[LearningSkillTypesSchema] #List of LearningSkillTypesSchema
    markdown_content: str = Field(..., description="Seluruh isi laporan dalam format markdown")

class EvaluateSpeakingSchema(BaseModel):
    correction: str = Field(..., description="Catatan perbaikan pengucapan Bahasa Inggris untuk peserta")
    score: int = Field(..., description="Rentang nilai 1-10 untuk pengucapan Bahasa Inggris dari peserta")
    summary: str = Field(..., description="Gabungan antara correction dan score")
