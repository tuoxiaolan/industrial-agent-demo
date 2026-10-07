import sqlite3
from pathlib import Path


DB_PATH = Path("agent.db")


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT UNIQUE,
                model TEXT NOT NULL,
                issue TEXT NOT NULL,
                evidence TEXT,
                status TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_ticket(model, issue, evidence):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO tickets (
                ticket_id,
                model,
                issue,
                evidence,
                status
            )
            VALUES (NULL, ?, ?, ?, ?)
            """,
            (
                model,
                issue,
                evidence,
                "created",
            ),
        )

        row_id = cursor.lastrowid
        ticket_id = f"MT-{row_id:04d}"

        connection.execute(
            "UPDATE tickets SET ticket_id = ? WHERE id = ?",
            (ticket_id, row_id),
        )

        row = connection.execute(
            "SELECT * FROM tickets WHERE id = ?",
            (row_id,),
        ).fetchone()

    return dict(row)


def list_tickets():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM tickets ORDER BY id DESC"
        ).fetchall()

    return [dict(row) for row in rows]


init_db()