"""
SQLite database initialisation.
Creates the diseases, recommendations, and image_logs tables if they don't exist.
"""

import os
import sqlite3
import logging

logger = logging.getLogger(__name__)

# backend/ directory (one level up from this file)
_BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_BACKEND_DIR, "diseases.db")

CREATE_TABLES_SQL = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS diseases (
    disease_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_name TEXT NOT NULL,
    crop_type    TEXT NOT NULL,
    description  TEXT NOT NULL,
    symptoms     TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recommendations (
    recommendation_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_id          INTEGER NOT NULL REFERENCES diseases(disease_id),
    category            TEXT NOT NULL CHECK(category IN ('chemical','biological','cultural','preventive')),
    recommendation_text TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS image_logs (
    image_id             INTEGER PRIMARY KEY AUTOINCREMENT,
    predicted_disease_id INTEGER,
    confidence           REAL,
    timestamp            TEXT
);
"""


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row_factory set to Row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create all tables if they do not already exist."""
    try:
        conn = get_connection()
        conn.executescript(CREATE_TABLES_SQL)
        conn.commit()
        conn.close()
        logger.info("Database initialised at %s", DB_PATH)
    except Exception as exc:
        logger.error("Database init failed: %s", exc)
