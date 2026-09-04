# py dms/load_sample_resumes.py
from pathlib import Path
import kagglehub

from database import initialize_database
from ingest_service import process_resume

DATASET = "snehaanbhawal/resume-dataset"
NUMBER_OF_RESUMES = 100

print("Downloading/finding resume dataset...")

dataset_path = kagglehub.dataset_download(DATASET)
dataset_path = Path(dataset_path)

print("Dataset location:", dataset_path)

pdf_files = list(dataset_path.rglob("*.pdf"))

print("PDF resumes found:", len(pdf_files))

if not pdf_files:
    print("No PDF resumes found.")
    raise SystemExit

initialize_database()

selected_resumes = pdf_files[:NUMBER_OF_RESUMES]

for number, file_path in enumerate(selected_resumes, start=1):
    print()
    print(f"Processing resume {number}/{len(selected_resumes)}")
    print("File:", file_path.name)

    try:
        result = process_resume(file_path)

        if result is None:
            print("Failed to process.")

        elif result["status"] == "duplicate":
            print("Already exists in database.")

        else:
            print("Stored successfully.")
            print("Entities:", len(result["entities"]))

    except Exception as error:
        print("Error:", error)

print()
print("Finished.")