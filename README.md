# DataGlum

An automated CSV data-quality and preprocessing tool designed to prepare messy datasets for machine-learning workflows.

## Overview

DataGlum focuses on one of the most repetitive parts of ML engineering: turning inconsistent tabular data into a cleaner dataset that can be inspected and used for downstream modelling.

## Cleaning Pipeline

`text
CSV Upload
    ↓
Schema Inspection
    ↓
Missing-value Handling
    ↓
Duplicate Detection
    ↓
Type Normalization
    ↓
Outlier Processing
    ↓
Column-name Normalization
    ↓
Clean Dataset
`

## Automated Checks

- Empty rows
- Duplicate rows
- Missing values
- Mostly-empty columns
- Numeric values stored as text
- Date-like values
- Extreme outliers
- Inconsistent column names
- Leading/trailing whitespace
- Error-like cell values

## Tech Stack

| Layer | Technology |
|---|---|
| Data Processing | Python, Pandas, NumPy |
| API | FastAPI |
| Cloud Compute | Modal |
| Frontend | HTML, CSS, JavaScript |
| Hosting | Vercel |
| Authentication | Supabase |

## Architecture

`text
Frontend
   ↓
FastAPI
   ↓
Data Cleaning Engine
   ↓
Pandas DataFrame
   ↓
Processed CSV
`

## Engineering Focus

The project is useful for exploring:

- Data-quality automation
- Pandas-based preprocessing
- API design
- File upload workflows
- Cloud execution
- ML data preparation

## Project Structure

`text
dataglum/
├── dataglum.html
├── csv_cleaner_api.py
└── README.md
`

## Status

**Active project / experimentation.**

The cleaning rules and deployment architecture may evolve as additional dataset types are supported.

## Author

**Sudipta Roy**  
B.Tech CSE (AI & ML)

Focus: **AI/ML • Data Engineering • LLM Engineering • Python**
