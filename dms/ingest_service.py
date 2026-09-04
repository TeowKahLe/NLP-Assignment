# py dms/ingest_service.py
from pathlib import Path
import hashlib

from document_processor import extract_text
from ner_service import extract_entities

from database import (
    initialize_database,
    insert_resume,
    insert_entities,
    find_resume_by_hash
)


# CREATE FILE HASH

def calculate_file_hash(file_path):
    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            data = file.read(8192)

            if not data:
                break

            sha256.update(data)

    return sha256.hexdigest()


# PROCESS RESUME

def process_resume(file_path):
    file_path = Path(file_path)

    print("Processing:", file_path.name)

    # 1. Calculate unique file hash
    file_hash = calculate_file_hash(
        file_path
    )

    # 2. Check duplicate
    existing = find_resume_by_hash(
        file_hash
    )

    if existing:
        print(
            "Duplicate resume detected."
        )

        print(
            "Existing Resume ID:",
            existing[0]
        )

        print(
            "Existing File:",
            existing[1]
        )

        return {
            "status": "duplicate",
            "resume_id": existing[0],
            "file_name": existing[1]
        }

    # 3. Extract text
    text, extraction_method = extract_text(
        file_path
    )

    if not text.strip():
        print(
            "No text could be extracted."
        )

        return None

    print(
        "Text extraction:",
        extraction_method
    )

    # 4. Perform NER
    entities = extract_entities(
        text
    )

    print(
        "Entities found:",
        len(entities)
    )

    # 5. Insert resume into database
    resume_id = insert_resume(
        file_name=file_path.name,
        file_path=str(file_path),
        file_type=file_path.suffix.lower(),
        extracted_text=text,
        file_hash=file_hash
    )

    # 6. Insert entities
    insert_entities(
        resume_id,
        entities
    )

    print(
        "Resume stored successfully."
    )

    print(
        "Resume ID:",
        resume_id
    )

    return {
        "status": "success",
        "resume_id": resume_id,
        "file_name": file_path.name,
        "text": text,
        "entities": entities,
        "extraction_method": extraction_method
    }


if __name__ == "__main__":
    initialize_database()

    print(
        "Resume ingestion service ready."
    )
