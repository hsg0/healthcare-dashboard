# WHAT — Marks the models folder as a Python package.
# WHY — This folder will hold the patient and note database tables.
# HOW — SQLAlchemy models in this folder are what get saved to PostgreSQL. Importing them here registers the patients and notes tables.
# IMPORTANT — These tables are the stored record. Do not keep patient data only in the browser.

from models.note import Note
from models.patient import Patient

__all__ = ["Note", "Patient"]
