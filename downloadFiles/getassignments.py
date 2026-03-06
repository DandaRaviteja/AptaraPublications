import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List

EXCEL_PATH = r"G:\My Drive\VaveTech-IEEE-JAN.xlsx"
DEFAULT_ROOT_PATH = r"G:\My Drive\Arczenrick\IEEE\2025\December"

def load_employee_articles_for_today(df) -> Dict[str, List[str]]:
    # Use EXACT column names from your Sheet1
    col_employee = "Assigned TO"
    col_article = "Article"
    col_date = "Assigned Date"

    print(f"\n📊 EXTRACTING ASSIGNMENTS")
    
    # Check if headers exist
    if col_employee not in df.columns:
        print(f"❌ Error: Could not find column '{col_employee}'")
        print(f"Available columns: {list(df.columns[:5])} ... {list(df.columns[-5:])}")
        return {}

    # 1. Format today's date to match your sheet (e.g., '12-Jan' or '2026-01-12')
    # Based on your file, it looks like YYYY-MM-DD format in the data
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # 2. Filter for today's assignments
    # We convert to string to handle potential datetime objects safely
    date_mask = df[col_date].astype(str).str.contains(today_date, na=False)
    today_articles = df[date_mask]
    
    print(f"📅 Filtered Date ({today_date}): {len(today_articles)} rows found")
    
    if today_articles.empty:
        # Fallback: check if the sheet uses 'DD-Mon' format (like '07-Jan')
        alt_date = datetime.now().strftime("%d-%b")
        date_mask = df[col_date].astype(str).str.contains(alt_date, na=False, case=False)
        today_articles = df[date_mask]
        if not today_articles.empty:
            print(f"📅 Found matches using alternate format ({alt_date})")

    # 3. Group by employee
    associates = {}
    for _, row in today_articles.iterrows():
        emp_name = str(row[col_employee]).strip()
        article_id = str(row[col_article]).strip()
        
        if emp_name.lower() != 'nan' and article_id.lower() != 'nan':
            if emp_name not in associates:
                associates[emp_name] = []
            associates[emp_name].append(article_id)
    
    # Clean up and sort
    return {k: sorted(list(set(v))) for k, v in associates.items()}

def main():
    print("🚀 IEEE ASSIGNMENTS EXTRACTOR")
    print("=" * 60)
    
    if not os.path.exists(EXCEL_PATH):
        print(f"❌ Excel missing: {EXCEL_PATH}")
        return

    # LOAD SHEET1 SPECIFICALLY
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name='Sheet1')
        print(f"📊 Loaded: {len(df)} rows from Sheet1")
    except Exception as e:
        print(f"❌ Error loading Sheet1: {e}")
        return
    
    associates = load_employee_articles_for_today(df)
    
    if not associates:
        print("❌ No assignments found for today's date in 'Sheet1'.")
        return

    # Print results (using your existing print_assignments logic)
    print("\n" + "="*100)
    print("📋 TODAY'S ASSIGNMENTS")
    print("="*100)
    for emp, ids in associates.items():
        print(f"👤 {emp:<15} --> 📄 {', '.join(ids)}")

if __name__ == "__main__":
    main()