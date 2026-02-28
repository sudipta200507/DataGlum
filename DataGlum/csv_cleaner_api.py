"""
╔══════════════════════════════════════════════════════════════════╗
║           CSV CLEANER API — Powered by Modal.com                ║
║           Built for: DataPrep Pro (your SaaS tool)              ║
╚══════════════════════════════════════════════════════════════════╝

HOW TO DEPLOY:
  1. pip install modal
  2. modal token new
  3. modal deploy csv_cleaner_api.py

YOUR API ENDPOINT WILL BE:
  https://YOUR-USERNAME--csv-cleaner-api-clean-csv.modal.run
"""

import modal
import io
import json
import pandas as pd
import numpy as np
from datetime import datetime

# ──────────────────────────────────────────────
# 1. MODAL APP SETUP
# ──────────────────────────────────────────────
app = modal.App("csv-cleaner-api")

# Define the container image with all required packages
image = modal.Image.debian_slim(python_version="3.11").pip_install(
    "pandas==2.2.2",
    "numpy==1.26.4",
    "python-multipart==0.0.9",
    "fastapi==0.111.0",
    "uvicorn==0.30.1",
)


# ──────────────────────────────────────────────
# 2. THE CORE CSV CLEANING ENGINE
# ──────────────────────────────────────────────
class CSVCleaningEngine:
    """
    Handles all data quality issues found in raw CSV datasets.
    Each method targets a specific problem ML engineers face.
    """

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()
        self.report = {
            "original_rows": len(df),
            "original_columns": len(df.columns),
            "issues_fixed": [],
            "columns_info": {},
        }

    # ── Step 1: Remove Completely Empty Rows ──
    def remove_empty_rows(self):
        before = len(self.df)
        self.df.dropna(how="all", inplace=True)
        self.df = self.df[~(self.df.astype(str).eq("") | self.df.astype(str).eq(" ")).all(axis=1)]
        removed = before - len(self.df)
        if removed > 0:
            self.report["issues_fixed"].append(
                f"✅ Removed {removed} completely empty row(s)"
            )
        return self

    # ── Step 2: Remove Duplicate Rows ──
    def remove_duplicates(self):
        before = len(self.df)
        self.df.drop_duplicates(inplace=True)
        removed = before - len(self.df)
        if removed > 0:
            self.report["issues_fixed"].append(
                f"✅ Removed {removed} duplicate row(s)"
            )
        return self

    # ── Step 3: Fix Column Names ──
    def clean_column_names(self):
        original = list(self.df.columns)
        # Strip whitespace, lowercase, replace spaces with underscores
        self.df.columns = (
            self.df.columns
            .str.strip()
            .str.lower()
            .str.replace(r"[^\w\s]", "", regex=True)
            .str.replace(r"\s+", "_", regex=True)
            .str.replace(r"_+", "_", regex=True)
        )
        cleaned = list(self.df.columns)
        changes = [(o, c) for o, c in zip(original, cleaned) if o != c]
        if changes:
            self.report["issues_fixed"].append(
                f"✅ Cleaned {len(changes)} column name(s) — standardized to lowercase_underscore format"
            )
        return self

    # ── Step 4: Detect & Fix Data Types ──
    def fix_data_types(self):
        for col in self.df.columns:
            original_dtype = str(self.df[col].dtype)

            # Try converting to numeric first
            converted = pd.to_numeric(self.df[col], errors="coerce")
            numeric_success_rate = converted.notna().sum() / max(len(self.df), 1)

            if numeric_success_rate >= 0.8 and original_dtype == "object":
                self.df[col] = converted
                self.report["issues_fixed"].append(
                    f"✅ Column '{col}': converted text → numeric (int/float)"
                )
                continue

            # Try converting to datetime
            if original_dtype == "object":
                try:
                    converted_dt = pd.to_datetime(self.df[col], infer_datetime_format=True, errors="coerce")
                    dt_success_rate = converted_dt.notna().sum() / max(len(self.df), 1)
                    if dt_success_rate >= 0.8:
                        self.df[col] = converted_dt
                        self.report["issues_fixed"].append(
                            f"✅ Column '{col}': converted text → datetime"
                        )
                        continue
                except Exception:
                    pass

            # Strip whitespace from string columns
            if self.df[col].dtype == object:
                self.df[col] = self.df[col].str.strip() if hasattr(self.df[col], "str") else self.df[col]

        return self

    # ── Step 5: Handle Missing Values (Smart Imputation) ──
    def handle_missing_values(self):
        null_counts_before = self.df.isnull().sum()
        total_nulls_before = null_counts_before.sum()

        for col in self.df.columns:
            null_count = self.df[col].isnull().sum()
            if null_count == 0:
                continue

            total_rows = len(self.df)
            null_pct = null_count / total_rows

            # If more than 60% of column is null → drop the column
            if null_pct > 0.60:
                self.df.drop(columns=[col], inplace=True)
                self.report["issues_fixed"].append(
                    f"✅ Dropped column '{col}' — {null_count}/{total_rows} values ({null_pct:.0%}) were missing"
                )
                continue

            # Numeric columns → fill with median (more robust than mean, ignores outliers)
            if pd.api.types.is_numeric_dtype(self.df[col]):
                median_val = self.df[col].median()
                self.df[col].fillna(median_val, inplace=True)
                self.report["issues_fixed"].append(
                    f"✅ Column '{col}': filled {null_count} missing numeric value(s) with median ({median_val:.4g})"
                )

            # Datetime columns → fill with most frequent date
            elif pd.api.types.is_datetime64_any_dtype(self.df[col]):
                mode_val = self.df[col].mode()
                if len(mode_val) > 0:
                    self.df[col].fillna(mode_val[0], inplace=True)
                    self.report["issues_fixed"].append(
                        f"✅ Column '{col}': filled {null_count} missing date(s) with most frequent date"
                    )

            # Categorical/text columns → fill with mode (most common value)
            else:
                mode_val = self.df[col].mode()
                if len(mode_val) > 0:
                    self.df[col].fillna(mode_val[0], inplace=True)
                    self.report["issues_fixed"].append(
                        f"✅ Column '{col}': filled {null_count} missing text value(s) with most common value ('{mode_val[0]}')"
                    )
                else:
                    self.df[col].fillna("unknown", inplace=True)
                    self.report["issues_fixed"].append(
                        f"✅ Column '{col}': filled {null_count} missing text value(s) with 'unknown'"
                    )

        total_nulls_after = self.df.isnull().sum().sum()
        if total_nulls_before > 0:
            self.report["issues_fixed"].append(
                f"✅ Missing values: {total_nulls_before} → {total_nulls_after} (eliminated {total_nulls_before - total_nulls_after})"
            )

        return self

    # ── Step 6: Remove Whitespace-Only Cells ──
    def clean_whitespace_cells(self):
        for col in self.df.select_dtypes(include=["object"]).columns:
            mask = self.df[col].astype(str).str.strip() == ""
            count = mask.sum()
            if count > 0:
                self.df.loc[mask, col] = np.nan
        return self

    # ── Step 7: Remove Outliers in Numeric Columns (IQR Method) ──
    def handle_outliers(self):
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 3 * IQR   # Using 3x IQR — conservative, preserves most data
            upper = Q3 + 3 * IQR

            outlier_mask = (self.df[col] < lower) | (self.df[col] > upper)
            outlier_count = outlier_mask.sum()

            if outlier_count > 0:
                # Cap outliers instead of dropping rows (safer for ML)
                self.df[col] = self.df[col].clip(lower=lower, upper=upper)
                self.report["issues_fixed"].append(
                    f"✅ Column '{col}': capped {outlier_count} extreme outlier(s) to safe range [{lower:.4g}, {upper:.4g}]"
                )

        return self

    # ── Step 8: Reset Index ──
    def reset_index(self):
        self.df.reset_index(drop=True, inplace=True)
        return self

    # ── Step 9: Build Final Report ──
    def build_report(self):
        self.report["cleaned_rows"] = len(self.df)
        self.report["cleaned_columns"] = len(self.df.columns)
        self.report["rows_removed"] = self.report["original_rows"] - self.report["cleaned_rows"]
        self.report["timestamp"] = datetime.utcnow().isoformat() + "Z"

        if not self.report["issues_fixed"]:
            self.report["issues_fixed"] = ["✅ Your CSV was already clean! No issues found."]

        return self

    # ── Run Full Pipeline ──
    def run(self):
        return (
            self
            .remove_empty_rows()
            .remove_duplicates()
            .clean_column_names()
            .clean_whitespace_cells()
            .fix_data_types()
            .handle_missing_values()
            .handle_outliers()
            .reset_index()
            .build_report()
        )


# ──────────────────────────────────────────────
# 3. FASTAPI WEB ENDPOINT (what your website calls)
# ──────────────────────────────────────────────
# NOTE: We import FastAPI types at the TOP so Modal can resolve them correctly
from fastapi import UploadFile, File
from fastapi.responses import JSONResponse
import base64

@app.function(image=image, memory=1024, timeout=120)
@modal.fastapi_endpoint(method="POST", label="clean-csv")
async def clean_csv(file: UploadFile = File(...)):
    """
    POST endpoint — receives a CSV file via multipart/form-data,
    cleans it, and returns the cleaned CSV encoded as base64 + a report.
    """
    try:
        # Read raw bytes from the uploaded file
        contents = await file.read()

        # Decode to text — try UTF-8 first, fall back to latin-1
        try:
            csv_text = contents.decode("utf-8")
        except UnicodeDecodeError:
            csv_text = contents.decode("latin-1")

        # Parse into a pandas DataFrame
        df = pd.read_csv(io.StringIO(csv_text))

        if df.empty:
            return JSONResponse(
                status_code=400,
                content={"error": "The uploaded CSV file is empty."}
            )

        if len(df.columns) < 2:
            return JSONResponse(
                status_code=400,
                content={"error": "CSV must have at least 2 columns to process."}
            )

        # ── Run the full cleaning pipeline ──
        engine = CSVCleaningEngine(df)
        engine.run()

        cleaned_df = engine.df
        report = engine.report

        # Encode cleaned CSV as base64 so it travels safely in JSON
        output_buffer = io.StringIO()
        cleaned_df.to_csv(output_buffer, index=False)
        cleaned_csv_b64 = base64.b64encode(
            output_buffer.getvalue().encode("utf-8")
        ).decode("utf-8")

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "cleaned_csv_base64": cleaned_csv_b64,
                "filename": f"cleaned_{file.filename}",
                "report": report,
            }
        )

    except pd.errors.EmptyDataError:
        return JSONResponse(status_code=400, content={"error": "CSV file is empty or unreadable."})
    except pd.errors.ParserError as e:
        return JSONResponse(status_code=400, content={"error": f"Could not parse CSV: {str(e)}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"Server error: {str(e)}"})


# ──────────────────────────────────────────────
# 4. HEALTH CHECK ENDPOINT
# ──────────────────────────────────────────────
@app.function(image=image)
@modal.fastapi_endpoint(method="GET", label="health")
async def health_check():
    """Simple ping to confirm your API is alive."""
    return JSONResponse(content={
        "status": "online",
        "service": "CSV Cleaner API",
        "version": "3.0.0"
    })


# ──────────────────────────────────────────────
# 5. LOCAL TESTING (run: python csv_cleaner_api.py)
# ──────────────────────────────────────────────
if __name__ == "__main__":
    print("🧪 Running local test with a messy DataFrame...\n")

    # Create a messy test DataFrame that simulates real-world bad CSV data
    test_data = {
        "User ID": [1, 2, 2, 3, None, 5, 6, 6, None, 8],
        "  Full Name  ": ["Alice", "Bob", "Bob", "Charlie", "", "Eve", "Frank", "Frank", None, "Hank"],
        "Age": [25, 30, 30, None, 22, 999, 28, 28, 35, None],
        "Email": ["alice@x.com", "bob@x.com", "bob@x.com", None, "charlie@x.com", "eve@x.com", None, None, "henry@x.com", "hank@x.com"],
        "Salary": ["50000", "60000", "60000", "55000", None, "70000", "65000", "65000", "58000", None],
        "Join Date": ["2020-01-01", "2019-05-15", "2019-05-15", None, "2021-03-10", "bad-date", "2022-07-22", "2022-07-22", "2018-11-30", None],
        "Empty Col": [None, None, None, None, None, None, None, None, None, None],
    }

    df_test = pd.DataFrame(test_data)
    print("BEFORE CLEANING:")
    print(df_test.to_string())
    print(f"\nShape: {df_test.shape}")
    print(f"Null values: {df_test.isnull().sum().sum()}")

    engine = CSVCleaningEngine(df_test)
    engine.run()

    print("\n" + "="*60)
    print("AFTER CLEANING:")
    print(engine.df.to_string())
    print(f"\nShape: {engine.df.shape}")

    print("\n" + "="*60)
    print("CLEANING REPORT:")
    for fix in engine.report["issues_fixed"]:
        print(f"  {fix}")
    print(f"\n  Original: {engine.report['original_rows']} rows × {engine.report['original_columns']} cols")
    print(f"  Cleaned:  {engine.report['cleaned_rows']} rows × {engine.report['cleaned_columns']} cols")
    print("\n✅ Local test complete!")
