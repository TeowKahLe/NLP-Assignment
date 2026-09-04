# Resume Named Entity Recognition (NLP Assignment)

## Assignment overview

This assignment develops and evaluates Named Entity Recognition (NER) models for résumé text. The goal is to automatically identify useful candidate information, then use the trained model in a Resume Document Management System (DMS). The DMS can process uploaded résumés, save the extracted information, and support entity-based search.

## Dataset

This project uses two résumé datasets:

- [Entity Recognition in Resumes — DataTurks](https://dataturks.com/projects/abhishek.narayanan/Entity%20Recognition%20in%20Resumes): manually annotated résumé text for NER. Each annotation identifies an entity such as a candidate name, email address, location, skills, job designation, company, degree, college name, graduation year, or years of experience.
- [Resume Dataset — Kaggle](https://www.kaggle.com/datasets/snehaanbhawal/resume-dataset): a collection of more than 2,400 résumés in PDF and text formats, grouped by job category. It can be used as sample documents for document processing and résumé categorisation tasks.

The data is split into:

- `data/train.json` — used to train the NER models.
- `data/val.json` — used to tune and validate model performance during development.
- `data/test.json` — used to evaluate the final model on unseen résumés.

The dataset enables the model to learn how résumé information appears in real text. After training, the model extracts these entities from new résumés so they can be stored in the DMS and searched—for example, to find candidates by skill, location, education, or previous company.

## Data licence and use

The Kaggle Resume Dataset is published under the [CC0: Public Domain](https://creativecommons.org/publicdomain/zero/1.0/) licence. The DataTurks dataset remains subject to the terms and conditions provided by its source. Use the datasets only for permitted academic or project purposes, retain source attribution, and do not upload, share, or expose personally identifiable information from résumés without appropriate permission.
