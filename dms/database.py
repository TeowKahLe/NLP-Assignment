# py dms/database.py
import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent / "resume_dms.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # RESUME TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resumes (
            resume_id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            file_path TEXT,
            file_type TEXT,
            extracted_text TEXT NOT NULL,
            file_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add file_hash to older database if it does not exist
    cursor.execute("PRAGMA table_info(resumes)")
    columns = [
        row[1]
        for row in cursor.fetchall()
    ]

    if "file_hash" not in columns:
        cursor.execute("""
            ALTER TABLE resumes
            ADD COLUMN file_hash TEXT
        """)

    # ENTITY TABLE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS entities (
            entity_id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_id INTEGER NOT NULL,
            entity_type TEXT NOT NULL,
            entity_text TEXT NOT NULL,
            normalized_text TEXT NOT NULL,

            FOREIGN KEY (resume_id)
                REFERENCES resumes(resume_id)
                ON DELETE CASCADE
        )
    """)

    # INDEXES
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_entity_text
        ON entities(normalized_text)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_entity_type
        ON entities(entity_type)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_resume_entity
        ON entities(resume_id)
    """)

    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_resume_hash
        ON resumes(file_hash)
        WHERE file_hash IS NOT NULL
    """)

    connection.commit()
    connection.close()

    print("Database initialized successfully.")
    print("Database location:", DB_PATH)


# CHECK DUPLICATE

def find_resume_by_hash(file_hash):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            resume_id,
            file_name
        FROM resumes
        WHERE file_hash = ?
    """, (file_hash,))

    row = cursor.fetchone()

    connection.close()

    return row


# INSERT RESUME

def insert_resume(
    file_name,
    file_path,
    file_type,
    extracted_text,
    file_hash
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO resumes (
            file_name,
            file_path,
            file_type,
            extracted_text,
            file_hash
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        file_name,
        file_path,
        file_type,
        extracted_text,
        file_hash
    ))

    resume_id = cursor.lastrowid

    connection.commit()
    connection.close()

    return resume_id


# INSERT ENTITIES

def insert_entities(resume_id, entities):
    connection = get_connection()
    cursor = connection.cursor()

    for entity in entities:
        entity_type = entity["label"]
        entity_text = entity["text"].strip()

        if not entity_text:
            continue

        normalized_text = (
            entity_text
            .lower()
            .strip()
        )

        cursor.execute("""
            INSERT INTO entities (
                resume_id,
                entity_type,
                entity_text,
                normalized_text
            )
            VALUES (?, ?, ?, ?)
        """, (
            resume_id,
            entity_type,
            entity_text,
            normalized_text
        ))

    connection.commit()
    connection.close()


# GET ALL RESUMES

def get_all_resumes():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            resume_id,
            file_name,
            file_path,
            file_type,
            created_at
        FROM resumes
        ORDER BY resume_id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


# GET ALL ENTITIES

def get_all_entities():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            e.entity_id,
            e.entity_type,
            e.entity_text,
            r.file_name
        FROM entities e
        JOIN resumes r
            ON e.resume_id = r.resume_id
        ORDER BY
            e.entity_type,
            e.entity_text
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


# EXACT ENTITY SEARCH

def search_exact_entity(
    query,
    entity_type=None
):
    connection = get_connection()
    cursor = connection.cursor()

    normalized_query = (
        query
        .lower()
        .strip()
    )

    if entity_type:
        cursor.execute("""
            SELECT DISTINCT
                r.resume_id,
                r.file_name,
                r.file_path,
                r.extracted_text,
                e.entity_type,
                e.entity_text
            FROM resumes r
            JOIN entities e
                ON r.resume_id = e.resume_id
            WHERE e.normalized_text = ?
              AND e.entity_type = ?
        """, (
            normalized_query,
            entity_type
        ))

    else:
        cursor.execute("""
            SELECT DISTINCT
                r.resume_id,
                r.file_name,
                r.file_path,
                r.extracted_text,
                e.entity_type,
                e.entity_text
            FROM resumes r
            JOIN entities e
                ON r.resume_id = e.resume_id
            WHERE e.normalized_text = ?
        """, (
            normalized_query,
        ))

    rows = cursor.fetchall()

    connection.close()

    return rows


if __name__ == "__main__":
    initialize_database()


def get_resume_count():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM resumes")
    count = cursor.fetchone()[0]
    connection.close()
    return count

def get_entity_count():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM entities")
    count = cursor.fetchone()[0]
    connection.close()
    return count