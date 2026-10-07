# WHAT — The patient URLs the dashboard calls.
# WHY — The website needs a safe way to read and change patient records.
# HOW — main.py attaches this router. Each route checks the request with Pydantic, then reads or writes the patients table.
# IMPORTANT — Never trust the browser. Every value is checked here again. Age is calculated from date_of_birth so the browser cannot invent it.

from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status as http_status
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import database_session
from models.patient import Patient

patient_router = APIRouter(prefix="/patients", tags=["patients"])

PatientStatus = Literal["active", "inactive", "critical"]

# The browser may only sort by these. Anything else is a 422.
SORTABLE_COLUMNS = {
    "last_name": Patient.last_name,
    "first_name": Patient.first_name,
    "age": Patient.date_of_birth,
    "last_visit": Patient.last_visit,
    "status": Patient.status,
}


# --------------------------------- request shape ---------------------------------


class PatientRequest(BaseModel):
    """What the browser must send to create or update a patient."""

    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    date_of_birth: date
    email: EmailStr
    phone: str = Field(min_length=7, max_length=30)
    address_line: str = Field(min_length=1, max_length=160)
    city: str = Field(min_length=1, max_length=80)
    state: str = Field(min_length=2, max_length=40)
    postal_code: str = Field(min_length=3, max_length=20)
    blood_type: Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
    status: PatientStatus
    allergies: str = Field("", max_length=500)
    conditions: str = Field("", max_length=500)
    last_visit: date

    @field_validator("date_of_birth")
    @classmethod
    def reject_birth_date_in_the_future(cls, date_of_birth: date) -> date:
        if date_of_birth > date.today():
            raise ValueError("Date of birth cannot be in the future.")
        return date_of_birth

    @field_validator("last_visit")
    @classmethod
    def reject_visit_in_the_future(cls, last_visit: date) -> date:
        if last_visit > date.today():
            raise ValueError("Last visit cannot be in the future.")
        return last_visit


# --------------------------------- response shapes ---------------------------------


class PatientResponse(BaseModel):
    """One patient as the dashboard reads it."""

    id: int
    first_name: str
    last_name: str
    date_of_birth: date
    patient_age: int
    email: str
    phone: str
    address_line: str
    city: str
    state: str
    postal_code: str
    blood_type: str
    status: str
    allergies: str
    conditions: str
    last_visit: date


class PatientListResponse(BaseModel):
    """One page of patients plus the numbers the page controls need."""

    patients: list[PatientResponse]
    total_count: int
    page: int
    page_size: int


# --------------------------------- helpers ---------------------------------


def calculate_age_in_years(date_of_birth: date) -> int:
    """Whole years lived, counting whether this year's birthday has happened yet."""
    today = date.today()
    had_birthday_this_year = (today.month, today.day) >= (
        date_of_birth.month,
        date_of_birth.day,
    )
    return today.year - date_of_birth.year - (0 if had_birthday_this_year else 1)


async def find_patient_or_404(session: AsyncSession, patient_id: int) -> Patient:
    """Return the stored patient, or raise 404 when that id does not exist."""
    patient = await session.get(Patient, patient_id)
    if patient is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} was not found.",
        )
    return patient


def to_patient_response(patient: Patient) -> PatientResponse:
    return PatientResponse(
        id=patient.id,
        first_name=patient.first_name,
        last_name=patient.last_name,
        date_of_birth=patient.date_of_birth,
        patient_age=calculate_age_in_years(patient.date_of_birth),
        email=patient.email,
        phone=patient.phone,
        address_line=patient.address_line,
        city=patient.city,
        state=patient.state,
        postal_code=patient.postal_code,
        blood_type=patient.blood_type,
        status=patient.status,
        allergies=patient.allergies,
        conditions=patient.conditions,
        last_visit=patient.last_visit,
    )


# --------------------------------- routes ---------------------------------


@patient_router.get("", response_model=PatientListResponse)
async def list_patients(
    session: AsyncSession = Depends(database_session),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str = Query("", max_length=80),
    status: PatientStatus | None = Query(None),
    sort_by: Literal["last_name", "first_name", "age", "last_visit", "status"] = Query("last_name"),
    sort_dir: Literal["asc", "desc"] = Query("asc"),
) -> PatientListResponse:
    """One page of patients, narrowed by search and status, in the requested order."""
    patient_query = select(Patient)

    search_text = search.strip()
    if search_text:
        name_pattern = f"%{search_text}%"
        patient_query = patient_query.where(
            or_(
                Patient.first_name.ilike(name_pattern),
                Patient.last_name.ilike(name_pattern),
            )
        )

    if status:
        patient_query = patient_query.where(Patient.status == status)

    total_count = await session.scalar(
        select(func.count()).select_from(patient_query.subquery())
    )

    sort_column = SORTABLE_COLUMNS[sort_by]
    # An older patient has an earlier date of birth, so sorting by age flips the date order.
    sort_ascending = sort_dir == "asc"
    if sort_by == "age":
        sort_ascending = not sort_ascending
    patient_query = patient_query.order_by(
        sort_column.asc() if sort_ascending else sort_column.desc(), Patient.id.asc()
    )

    patient_query = patient_query.offset((page - 1) * page_size).limit(page_size)
    patients_on_page = (await session.scalars(patient_query)).all()

    return PatientListResponse(
        patients=[to_patient_response(patient) for patient in patients_on_page],
        total_count=total_count or 0,
        page=page,
        page_size=page_size,
    )


@patient_router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: int = Path(ge=1),
    session: AsyncSession = Depends(database_session),
) -> PatientResponse:
    """One patient by id, or 404 when nobody has that id."""
    patient = await find_patient_or_404(session, patient_id)
    return to_patient_response(patient)


@patient_router.post(
    "", response_model=PatientResponse, status_code=http_status.HTTP_201_CREATED
)
async def create_patient(
    submitted_patient: PatientRequest,
    session: AsyncSession = Depends(database_session),
) -> PatientResponse:
    """Save a new patient after Pydantic has checked every field."""
    new_patient = Patient(**submitted_patient.model_dump())
    session.add(new_patient)
    await session.commit()
    await session.refresh(new_patient)
    return to_patient_response(new_patient)


@patient_router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(
    submitted_patient: PatientRequest,
    patient_id: int = Path(ge=1),
    session: AsyncSession = Depends(database_session),
) -> PatientResponse:
    """Replace every field of an existing patient, or 404 when that id is missing."""
    patient = await find_patient_or_404(session, patient_id)
    for field_name, new_value in submitted_patient.model_dump().items():
        setattr(patient, field_name, new_value)
    await session.commit()
    await session.refresh(patient)
    return to_patient_response(patient)


@patient_router.delete("/{patient_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_patient(
    patient_id: int = Path(ge=1),
    session: AsyncSession = Depends(database_session),
) -> None:
    """Remove one patient for good, or 404 when that id is missing."""
    patient = await find_patient_or_404(session, patient_id)
    await session.delete(patient)
    await session.commit()
