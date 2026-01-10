#!/usr/bin/env python3
"""
IEEE ASSIGNMENTS EXTRACTOR - Google Sheets Automation
Reads Google Sheet via URL and applies existing logic
Associate Name --> Article IDs --> Download Path
"""

import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List
from io import StringIO
import requests

# ===================== CONFIG =====================

SPREADSHEET_ID = "1aQCPqlY-sFOZoez-HKRjOSapKl5o1oJ7JS3tP-cpw-8"
SHEET_GID = "0"  # first sheet

DEFAULT_ROOT_PATH = r"G:\My Drive\Arczenrick\IEEE\2025\December"

# =================================================


def load_google_sheet() -> pd.DataFrame:
    """Download Google Sheet as CSV and load into DataFrame"""

    csv_url = (
        f"https://docs.google.com/spreadsheets/d/"
        f"{SPREADSHEET_ID}/export?format=csv&gid={SHEET_GID}"
    )

    print("🌐 Fetching Google Sheet data...")
    response = requests.get(csv_url)

    if response.status_code != 200:
        print("❌ Failed to download Google Sheet")
        print("➡ Ensure the sheet allows CSV export")
        sys.exit(1)

    df = pd.read_csv(StringIO(response.text))
    return df


def load_employee_articles_for_today(
    df,
    employee_col: str = "Assigned TO",    # Column T
    workid_col: str = "Article",          # Column R
    date_col: str = "Imported Date"       # Column S
) -> Dict[str, List[str]]:
    """Extract assignments from DataFrame"""

    print(f"\n📊 EXTRACTING ASSIGNMENTS")
    print(f"👥 Employee: '{employee_col}'")
    print(f"📄 Articles: '{workid_col}'")
    print(f"📅 Date: '{date_col}'")

    today_date = datetime.now().strftime("%Y-%m-%d")

    # Column S (index 18)
    date_col_data = df.iloc[:, 18].astype(str)
    date_mask = date_col_data.str.contains(today_date, na=False)
    today_articles = df[date_mask]

    print(f"📅 Today ({today_date}): {len(today_articles)} matching rows")

    if today_articles.empty:
        print("❌ No assignments found for today!")
        return {}

    associates = {}

    for _, row in today_articles.iterrows():
        emp_name = str(row.iloc[19]).strip()    # Column T
        article_id = str(row.iloc[17]).strip()  # Column R

        if article_id.isdigit() and emp_name and emp_name.lower() != "nan":
            associates.setdefault(emp_name, []).append(article_id)

    # Remove duplicates + sort
    for emp in associates:
        associates[emp] = sorted(set(associates[emp]))

    return associates


def print_assignments(associates: Dict[str, List[str]]):
    """Print clean assignments"""

    print("\n" + "=" * 100)
    print("📋 TODAY'S ASSIGNMENTS (Associate --> Articles --> Path)")
    print("=" * 100)

    today_folder = datetime.now().strftime("%Y%m%d")
    total_articles = 0

    for emp_name, article_ids in associates.items():
        ids_string = ",".join(article_ids)
        full_path = os.path.join(DEFAULT_ROOT_PATH, today_folder, emp_name)

        print(f"👤 {emp_name:<12} --> 📄 {ids_string:<50} --> 📁 {full_path}\n")
        total_articles += len(article_ids)

    print(f"\n🎯 SUMMARY: {len(associates)} associates, {total_articles} articles")
    print("=" * 100)


def main():
    print("🚀 IEEE ASSIGNMENTS EXTRACTOR (GOOGLE SHEETS)")
    print("=" * 60)

    df = load_google_sheet()
    print(f"📊 Loaded: {len(df)} rows")

    associates = load_employee_articles_for_today(df)

    if not associates:
        sys.exit(1)

    print_assignments(associates)


if __name__ == "__main__":
    main()
