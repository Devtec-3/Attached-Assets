"""
Database query helpers.

- get_disease_by_name: look up a disease and its recommendations
- log_prediction: record a prediction in image_logs
"""

import logging
from datetime import datetime, timezone
from database.setup import get_connection

logger = logging.getLogger(__name__)


def get_disease_by_name(disease_name: str) -> dict | None:
    """
    Look up a disease record by its exact class name (must match labels.json).
    Returns a dict with all disease fields plus a 'recommendations' list, or None.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM diseases WHERE disease_name = ? COLLATE NOCASE LIMIT 1",
            (disease_name,),
        )
        row = cur.fetchone()
        if row is None:
            conn.close()
            return None

        disease = dict(row)

        cur.execute(
            "SELECT category, recommendation_text FROM recommendations WHERE disease_id = ?",
            (disease["disease_id"],),
        )
        disease["recommendations"] = [dict(r) for r in cur.fetchall()]
        conn.close()
        return disease

    except Exception as exc:
        logger.error("Disease lookup failed: %s", exc)
        return None


def log_prediction(disease_name: str, confidence: float) -> None:
    """
    Insert a row into image_logs.
    Looks up the disease_id from the diseases table; stores NULL if not found.
    """
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT disease_id FROM diseases WHERE disease_name = ? COLLATE NOCASE LIMIT 1",
            (disease_name,),
        )
        row = cur.fetchone()
        disease_id = row["disease_id"] if row else None

        cur.execute(
            "INSERT INTO image_logs (predicted_disease_id, confidence, timestamp) VALUES (?, ?, ?)",
            (disease_id, confidence, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        conn.close()

    except Exception as exc:
        logger.error("Prediction logging failed: %s", exc)
