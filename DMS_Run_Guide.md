# Resume Document Management System — Run Guide

This guide explains how to set up and run the Resume Document Management System in the correct order.

## 1. Open the Project

Open the project folder in VS Code.

Example project structure:

```text
NLP-Assignment/
├── dms/
│   ├── app.py
│   ├── database.py
│   ├── document_processor.py
│   ├── ner_service.py
│   ├── ingest_service.py
│   ├── search_service.py
│   ├── load_sample_resumes.py
│   └── resume_dms.db
├── models/
│   └── benchmark_a/
│       └── best_model/
├── notebooks/
├── results/
└── requirements.txt
```

Make sure the terminal is opened at the project root:

```text
NLP-Assignment>
```

Place model.safetensors inside benchmark_a/best_model
Example : benchmark_a/best_model/model.safetensors

## 2. Check Python

Run:

```powershell
py --version
```

If this works, use `py` for the commands below.

If `py` does not work, try:

```powershell
python --version
```

If neither works, install Python first and restart VS Code.

## 3. Create a Virtual Environment (Recommended)

Run:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

After activation, the terminal should show something similar to:

```text
(.venv) PS C:\...\NLP-Assignment>
```

## 4. Install Python Packages

Run:

```powershell
py -m pip install -r requirements.txt
```

The project requires packages for:
- DeBERTa / Transformers
- PyTorch
- PDF and DOCX processing
- OCR integration
- Similar-entity search
- Streamlit
- Pandas and Matplotlib

## 5. Install Tesseract OCR

`pytesseract` alone is not enough. The Tesseract OCR application must also be installed on Windows.

The common installation location is:

```text
C:\Program Files\Tesseract-OCR\tesseract.exe
```

After installation, open a new terminal and test:

```powershell
tesseract --version
```

If Windows still cannot find Tesseract, make sure `document_processor.py` contains:

```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

OCR is mainly required for scanned PDFs and image resumes.

## 6. Check the NER Model

Make sure this folder exists:

```text
models/benchmark_a/best_model/
```

It should contain at least:

```text
config.json
model.safetensors
tokenizer_config.json
tokenizer.json
```

The DMS uses this trained DeBERTa model for Named Entity Recognition.

Do not move or rename this folder unless `MODEL_PATH` in `ner_service.py` is also changed.

## 7. Initialize the Database

Run:

```powershell
py dms/database.py
```

Expected output:

```text
Database initialized successfully.
Database location: ...\dms\resume_dms.db
```

This creates/checks the SQLite database and its tables.

Main tables:

```text
resumes
entities
```

Running this command again will not delete the existing records.

## 8. Add Resume Data

There are two ways.

### Method A — Use the Streamlit App

This is the recommended method.

The app supports multiple resume uploads and automatically performs:

```text
Resume Upload
→ Text Extraction / OCR
→ DeBERTa NER
→ Store Resume in SQLite
→ Store Extracted Entities in SQLite
```

### Method B — Load Sample Resumes Automatically

If sample data is needed, open:

```text
dms/load_sample_resumes.py
```

Set the number of resumes, for example:

```python
NUMBER_OF_RESUMES = 50
```

Then run:

```powershell
py dms/load_sample_resumes.py
```

The script processes the selected resumes, performs NER, and stores the results in SQLite.

Duplicate files are automatically skipped.

If `resume_dms.db` is already populated with enough resumes, this step can be skipped.

## 9. Run the DMS

From the project root, run:

```powershell
py -m streamlit run dms/app.py
```

Streamlit should display a local address such as:

```text
http://localhost:8501
```

Usually the browser opens automatically. If not, open the displayed Local URL manually.

## 10. Use the System in This Order

### Dashboard

Shows:
- Total resumes
- Total extracted entities
- Entity distribution chart

### Upload Resume

Upload one or multiple files.

Supported formats include:

```text
PDF
DOCX
PNG
JPG
JPEG
BMP
TIFF
WEBP
```

Click:

```text
Process Resumes
```

The system then:

```text
Extracts text
→ Uses OCR when required
→ Runs DeBERTa NER
→ Saves the resume
→ Saves its entities
```

### Search Entity

1. Select an entity type.
2. Enter the entity.
3. Click `Search`.

Example:

```text
Entity Type: LOCATION
Query: Kuala Lumpur
```

If an exact entity exists:

```text
Exact Match
→ Return matching resume(s)
→ Highlight the entity
```

If the exact entity does not exist:

```text
No Exact Match
→ Find similar entities
→ Return resumes containing similar entities
→ Highlight the recommended entity
```

### View Documents

Use this section to:
- View stored resumes
- Check resume IDs
- View extracted entities
- Filter entity records
- Download available original resume files

## 11. View the SQLite Database in VS Code

Install the VS Code extension:

```text
SQLite Viewer
```

Open:

```text
dms/resume_dms.db
```

You should see:

```text
resumes
entities
sqlite_sequence
```

`resumes` stores document information and extracted text.

`entities` stores the entities predicted by the NER model and links each entity to its resume using `resume_id`.

## 12. Correct Run Order Summary

For a new computer:

```text
1. Open project in VS Code
2. Check Python
3. Create/activate virtual environment
4. Install requirements.txt
5. Install Tesseract OCR
6. Check models/benchmark_a/best_model/
7. Run database.py
8. Optional: load sample resumes
9. Run Streamlit app
10. Upload/Search/View documents
```

Commands:

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
py dms/database.py
py -m streamlit run dms/app.py
```

Optional sample data:

```powershell
py dms/load_sample_resumes.py
```

## 13. Common Problems

### `Python was not found`

Try:

```powershell
py --version
```

If `py` works, use `py` instead of `python`.

### `No module named ...`

Run:

```powershell
py -m pip install -r requirements.txt
```

### `tesseract is not installed or it's not in your PATH`

Install Tesseract OCR and check:

```powershell
tesseract --version
```

If necessary, set its path inside `document_processor.py`.

### Model cannot be found

Check:

```text
models/benchmark_a/best_model/
```

and make sure the model/tokenizer files are present.

### Streamlit does not open

Make sure the command is executed in PowerShell, not inside the Python `>>>` interactive console:

```powershell
py -m streamlit run dms/app.py
```

### Database is empty

The database tables are created first, but data only appears after resumes are processed.

Upload resumes through the app or run:

```powershell
py dms/load_sample_resumes.py
```

### Duplicate resume detected

This is expected if the same file has already been stored. The system uses a file hash to avoid inserting duplicate resumes.

## 14. Stop the Application

In the terminal running Streamlit, press:

```text
Ctrl + C
```

This stops the local DMS server.
