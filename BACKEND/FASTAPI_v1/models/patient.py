# WHAT — The patients table and the first set of sample rows.
# WHY — The dashboard needs stored patients, and a new database should not start empty.
# HOW — main.py creates this table on startup, then calls seed_patients_if_empty.
# IMPORTANT — These 20 people are fictional. The seed runs only when the table has zero rows, so a restart does not insert them again.

from datetime import date

from sqlalchemy import Date, Integer, String, Text, func, select
from sqlalchemy.orm import Mapped, mapped_column

from config.database import DatabaseBase, SessionLocal


class Patient(DatabaseBase):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(80))
    last_name: Mapped[str] = mapped_column(String(80))
    date_of_birth: Mapped[date] = mapped_column(Date)
    email: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(30))
    address_line: Mapped[str] = mapped_column(String(160))
    city: Mapped[str] = mapped_column(String(80))
    state: Mapped[str] = mapped_column(String(40))
    postal_code: Mapped[str] = mapped_column(String(20))
    blood_type: Mapped[str] = mapped_column(String(3))
    status: Mapped[str] = mapped_column(String(20))
    allergies: Mapped[str] = mapped_column(Text, default="")
    conditions: Mapped[str] = mapped_column(Text, default="")
    last_visit: Mapped[date] = mapped_column(Date)


def sample_patients() -> list[Patient]:
    """Twenty fictional patients. Age is calculated later from date_of_birth."""
    rows = [
        ("Amelia", "Nguyen", date(1988, 3, 14), "amelia.nguyen@example.com", "415-555-0101", "18 Grove St", "San Francisco", "CA", "94102", "O+", "active", "Penicillin", "Hypertension", date(2026, 9, 2)),
        ("Jonah", "Brooks", date(1975, 11, 2), "jonah.brooks@example.com", "415-555-0102", "90 Market St", "San Francisco", "CA", "94105", "A-", "critical", "None known", "Type 2 diabetes, heart failure", date(2026, 9, 28)),
        ("Priya", "Shah", date(1996, 7, 21), "priya.shah@example.com", "510-555-0103", "44 College Ave", "Berkeley", "CA", "94704", "B+", "active", "Peanuts", "Asthma", date(2026, 8, 19)),
        ("Mateo", "Rivera", date(1962, 1, 9), "mateo.rivera@example.com", "650-555-0104", "12 Oak Lane", "Palo Alto", "CA", "94301", "AB+", "inactive", "Sulfa drugs", "Osteoarthritis", date(2025, 12, 11)),
        ("Hannah", "Cole", date(2001, 5, 30), "hannah.cole@example.com", "408-555-0105", "77 Elm St", "San Jose", "CA", "95112", "O-", "active", "Latex", "None recorded", date(2026, 9, 14)),
        ("Owen", "Patel", date(1983, 9, 4), "owen.patel@example.com", "925-555-0106", "5 Willow Ct", "Walnut Creek", "CA", "94596", "A+", "active", "Shellfish", "High cholesterol", date(2026, 7, 22)),
        ("Sofia", "Alvarez", date(1991, 12, 18), "sofia.alvarez@example.com", "707-555-0107", "230 Pine St", "Santa Rosa", "CA", "95401", "B-", "critical", "Ibuprofen", "Pregnancy, anemia", date(2026, 10, 1)),
        ("Leo", "Kim", date(1954, 4, 27), "leo.kim@example.com", "916-555-0108", "88 Capitol Ave", "Sacramento", "CA", "95814", "O+", "active", "None known", "COPD", date(2026, 6, 3)),
        ("Nora", "Bennett", date(1979, 8, 8), "nora.bennett@example.com", "831-555-0109", "16 Lighthouse Rd", "Monterey", "CA", "93940", "A+", "inactive", "Codeine", "Migraine", date(2026, 1, 17)),
        ("Eli", "Washington", date(1999, 2, 11), "eli.washington@example.com", "209-555-0110", "401 Main St", "Stockton", "CA", "95202", "AB-", "active", "Dust mites", "Seasonal allergies", date(2026, 9, 9)),
        ("Grace", "Okafor", date(1986, 6, 25), "grace.okafor@example.com", "559-555-0111", "63 Cedar Ave", "Fresno", "CA", "93721", "O+", "active", "None known", "Hypothyroidism", date(2026, 8, 5)),
        ("Caleb", "Murphy", date(1970, 10, 3), "caleb.murphy@example.com", "661-555-0112", "9 Desert Bloom", "Bakersfield", "CA", "93301", "B+", "critical", "Aspirin", "Chronic kidney disease", date(2026, 9, 30)),
        ("Isla", "Fernandez", date(2004, 3, 2), "isla.fernandez@example.com", "760-555-0113", "150 Palm Dr", "Palm Springs", "CA", "92262", "A-", "active", "Bee stings", "None recorded", date(2026, 5, 20)),
        ("Henry", "Clark", date(1948, 7, 16), "henry.clark@example.com", "949-555-0114", "22 Harbor View", "Newport Beach", "CA", "92663", "O+", "inactive", "Penicillin", "Atrial fibrillation", date(2025, 11, 2)),
        ("Ava", "Rossi", date(1993, 1, 28), "ava.rossi@example.com", "714-555-0115", "300 Birch St", "Anaheim", "CA", "92805", "AB+", "active", "None known", "Anxiety", date(2026, 9, 18)),
        ("Miles", "Johnson", date(1980, 5, 6), "miles.johnson@example.com", "213-555-0116", "810 Spring St", "Los Angeles", "CA", "90012", "B-", "active", "Eggs", "Type 2 diabetes", date(2026, 8, 27)),
        ("Chloe", "Martin", date(1968, 9, 19), "chloe.martin@example.com", "818-555-0117", "55 Magnolia Blvd", "Burbank", "CA", "91502", "A+", "critical", "Iodine", "Breast cancer follow-up", date(2026, 10, 3)),
        ("Theo", "Nakamura", date(1997, 11, 23), "theo.nakamura@example.com", "310-555-0118", "14 Ocean Ave", "Santa Monica", "CA", "90401", "O-", "active", "None known", "None recorded", date(2026, 4, 12)),
        ("Ruby", "Edwards", date(1959, 2, 7), "ruby.edwards@example.com", "619-555-0119", "70 Island Ave", "San Diego", "CA", "92101", "B+", "inactive", "Latex, sulfa drugs", "Osteoporosis", date(2026, 2, 8)),
        ("Felix", "Berg", date(1984, 12, 1), "felix.berg@example.com", "858-555-0120", "6 Canyon Rd", "La Jolla", "CA", "92037", "A+", "active", "Pollen", "Hypertension", date(2026, 9, 25)),
    ]
    return [
        Patient(
            first_name=first_name,
            last_name=last_name,
            date_of_birth=date_of_birth,
            email=email,
            phone=phone,
            address_line=address_line,
            city=city,
            state=state,
            postal_code=postal_code,
            blood_type=blood_type,
            status=status,
            allergies=allergies,
            conditions=conditions,
            last_visit=last_visit,
        )
        for (
            first_name,
            last_name,
            date_of_birth,
            email,
            phone,
            address_line,
            city,
            state,
            postal_code,
            blood_type,
            status,
            allergies,
            conditions,
            last_visit,
        ) in rows
    ]


async def seed_patients_if_empty() -> int:
    """Insert the sample patients when the table has no rows. Returns how many were added."""
    async with SessionLocal() as session:
        patient_count = await session.scalar(select(func.count()).select_from(Patient))
        if patient_count:
            return 0
        patients = sample_patients()
        session.add_all(patients)
        await session.commit()
        return len(patients)
