# WHAT — The clinical note URLs for one patient, plus the chart summary.
# WHY — The patient detail screen needs to read, add, and remove notes, and to show a readable summary of the chart.
# HOW — main.py attaches this router. Every URL starts by checking the patient exists, then reads or writes the notes table.
# IMPORTANT — The summary is a plain template built from stored fields. There is no LLM here, and it is not a diagnosis or a treatment recommendation. Never trust the browser: the note text and timestamp are checked again with Pydantic.

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Path, status as http_status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import database_session
from models.note import Note
from models.patient import Patient
from routes.patients import calculate_age_in_years, find_patient_or_404

note_router = APIRouter(prefix="/patients/{patient_id}", tags=["notes"])

# A browser clock can run a little ahead of the server clock, so allow a small gap.
ALLOWED_CLOCK_DRIFT = timedelta(minutes=5)

# Stored chart fields use these phrases to mean "nothing on file".
EMPTY_FIELD_PHRASES = {"", "none", "none known", "none recorded"}

# Shown with every summary so nobody reads it as medical advice.
SUMMARY_NOTICE = (
    "This is a readable summary of the chart. It is not a diagnosis "
    "or a treatment recommendation."
)


# --------------------------------- request and response shapes ---------------------------------


class NoteRequest(BaseModel):
    """What the browser must send to add a note."""

    # No min_length here on purpose: the check below rejects blank text with a
    # sentence a person can read, instead of Pydantic's wording about characters.
    note_text: str = Field(max_length=4000)
    written_at: datetime

    @field_validator("note_text")
    @classmethod
    def reject_blank_text(cls, note_text: str) -> str:
        trimmed_text = note_text.strip()
        if not trimmed_text:
            raise ValueError("A note cannot be empty.")
        return trimmed_text

    @field_validator("written_at")
    @classmethod
    def reject_time_too_far_ahead(cls, written_at: datetime) -> datetime:
        # A note without a timezone is read as UTC so every stored time can be compared.
        if written_at.tzinfo is None:
            written_at = written_at.replace(tzinfo=timezone.utc)
        if written_at > datetime.now(timezone.utc) + ALLOWED_CLOCK_DRIFT:
            raise ValueError("A note cannot be written in the future.")
        return written_at


class NoteResponse(BaseModel):
    """One stored note."""

    id: int
    patient_id: int
    note_text: str
    written_at: datetime


class NoteListResponse(BaseModel):
    """Every note for one patient, newest first."""

    notes: list[NoteResponse]
    total_count: int


class PatientSummaryResponse(BaseModel):
    """A readable chart summary built from what is already stored."""

    patient_id: int
    patient_name: str
    patient_age: int
    blood_type: str
    conditions: str
    allergies: str
    note_count: int
    summary_text: str
    notice: str


def to_note_response(note: Note) -> NoteResponse:
    return NoteResponse(
        id=note.id,
        patient_id=note.patient_id,
        note_text=note.note_text,
        written_at=note.written_at,
    )


# --------------------------------- helpers ---------------------------------


async def read_notes_newest_first(session: AsyncSession, patient_id: int) -> list[Note]:
    """Every note for one patient, newest written_at first."""
    notes_query = (
        select(Note)
        .where(Note.patient_id == patient_id)
        .order_by(Note.written_at.desc(), Note.id.desc())
    )
    return list((await session.scalars(notes_query)).all())


def has_recorded_value(stored_text: str) -> bool:
    """The seed rows use phrases like "None known" to mean the field is empty."""
    return stored_text.strip().lower() not in EMPTY_FIELD_PHRASES


def build_summary_text(patient: Patient, notes_oldest_first: list[Note]) -> str:
    """Join the stored chart fields into sentences. This is a template, not a diagnosis."""
    patient_name = f"{patient.first_name} {patient.last_name}"
    patient_age = calculate_age_in_years(patient.date_of_birth)

    sentences = [
        f"{patient_name} is {patient_age} years old, blood type {patient.blood_type}, "
        f"and is marked {patient.status} on the chart."
    ]

    if has_recorded_value(patient.conditions):
        sentences.append(f"Recorded conditions: {patient.conditions}.")
    else:
        sentences.append("No conditions are recorded.")

    if has_recorded_value(patient.allergies):
        sentences.append(f"Recorded allergies: {patient.allergies}.")
    else:
        sentences.append("No allergies are recorded.")

    sentences.append(f"The last recorded visit was {patient.last_visit}.")

    if not notes_oldest_first:
        sentences.append("No clinical notes are on file.")
        return " ".join(sentences)

    note_word = "note" if len(notes_oldest_first) == 1 else "notes"
    sentences.append(
        f"There {'is' if len(notes_oldest_first) == 1 else 'are'} "
        f"{len(notes_oldest_first)} clinical {note_word} on file, oldest first."
    )
    for note in notes_oldest_first:
        sentences.append(f"On {note.written_at.date()}: {note.note_text}")

    return " ".join(sentences)


# --------------------------------- routes ---------------------------------


@note_router.get("/notes", response_model=NoteListResponse)
async def list_notes(
    patient_id: int = Path(ge=1),
    session: AsyncSession = Depends(database_session),
) -> NoteListResponse:
    """All notes for one patient, or 404 when that patient is missing."""
    await find_patient_or_404(session, patient_id)
    notes = await read_notes_newest_first(session, patient_id)
    return NoteListResponse(
        notes=[to_note_response(note) for note in notes],
        total_count=len(notes),
    )


@note_router.get("/summary", response_model=PatientSummaryResponse)
async def get_patient_summary(
    patient_id: int = Path(ge=1),
    session: AsyncSession = Depends(database_session),
) -> PatientSummaryResponse:
    """A template chart summary for one patient, or 404 when that patient is missing."""
    patient = await find_patient_or_404(session, patient_id)
    notes_newest_first = await read_notes_newest_first(session, patient_id)
    notes_oldest_first = list(reversed(notes_newest_first))

    return PatientSummaryResponse(
        patient_id=patient.id,
        patient_name=f"{patient.first_name} {patient.last_name}",
        patient_age=calculate_age_in_years(patient.date_of_birth),
        blood_type=patient.blood_type,
        conditions=patient.conditions,
        allergies=patient.allergies,
        note_count=len(notes_oldest_first),
        summary_text=build_summary_text(patient, notes_oldest_first),
        notice=SUMMARY_NOTICE,
    )


@note_router.post(
    "/notes", response_model=NoteResponse, status_code=http_status.HTTP_201_CREATED
)
async def create_note(
    submitted_note: NoteRequest,
    patient_id: int = Path(ge=1),
    session: AsyncSession = Depends(database_session),
) -> NoteResponse:
    """Attach one note to an existing patient, or 404 when that patient is missing."""
    await find_patient_or_404(session, patient_id)
    new_note = Note(
        patient_id=patient_id,
        note_text=submitted_note.note_text,
        written_at=submitted_note.written_at,
    )
    session.add(new_note)
    await session.commit()
    await session.refresh(new_note)
    return to_note_response(new_note)


@note_router.delete("/notes/{note_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_note(
    patient_id: int = Path(ge=1),
    note_id: int = Path(ge=1),
    session: AsyncSession = Depends(database_session),
) -> None:
    """Remove one note from one patient. Deleting the note does not touch the patient."""
    await find_patient_or_404(session, patient_id)
    note = await session.get(Note, note_id)
    # A note belonging to someone else is treated as missing, so one patient's
    # notes can never be removed from another patient's page.
    if note is None or note.patient_id != patient_id:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Note {note_id} was not found for patient {patient_id}.",
        )
    await session.delete(note)
    await session.commit()
