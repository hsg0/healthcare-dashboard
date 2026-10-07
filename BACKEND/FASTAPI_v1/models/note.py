# WHAT — The clinical notes table.
# WHY — A patient record needs the written notes a clinician adds over time.
# HOW — main.py creates this table on startup. Each row points at one patient.
# IMPORTANT — Notes are patient data. Deleting a patient deletes that patient's notes through the cascade, so no note is left pointing at a patient who is gone. There is no seed here: notes start empty.

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from config.database import DatabaseBase


class Note(DatabaseBase):
    __tablename__ = "notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), index=True
    )
    note_text: Mapped[str] = mapped_column(Text)
    written_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
