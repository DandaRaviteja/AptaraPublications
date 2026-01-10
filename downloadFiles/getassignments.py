#!/usr/bin/env python3
"""
IEEE ASSIGNMENTS EXTRACTOR - Print assignments from Excel for manual use
Associate Name --> Article IDs --> Download Path
"""
import os
import sys
import pandas as pd
from datetime import datetime
from typing import Dict, List

EXCEL_PATH = r"G:\My Drive\VaveTech-IEEE-JAN.gsheet"
DEFAULT_ROOT_PATH = r"G:\My Drive\Arczenrick\IEEE\2025\December"

def load_employee_articles_for_today(
    df, 
    employee_col: str = "Assigned TO",    # Column T
    workid_col: str = "Article",          # Column R
    date_col: str = "Imported Date"       # Column S
) -> Dict[str, List[str]]:
    """Extract assignments from Excel DataFrame"""
    print(f"\n📊 EXTRACTING ASSIGNMENTS")
    print(f"👥 Employee: '{employee_col}'")
    print(f"📄 Articles: '{workid_col}'") 
    print(f"📅 Date: '{date_col}'")
    
    # Filter today's articles
    today_date = datetime.now().strftime("%Y-%m-%d")
    date_col_data = df.iloc[:, 18].astype(str)  # Column S (index 18)
    date_mask = date_col_data.str.contains(today_date, na=False)
    today_articles = df[date_mask]
    
    print(f"📅 Today ({today_date}): {len(today_articles)} matching rows")
    
    if today_articles.empty:
        print("❌ No assignments found for today!")
        return {}
    
    # Group by employee
    associates = {}
    for _, row in today_articles.iterrows():
        emp_name = str(row.iloc[19]).strip()  # Column T (index 19)
        article_id = str(row.iloc[17]).strip()  # Column R (index 17)
        
        if article_id.isdigit() and emp_name and emp_name != 'nan':
            if emp_name not in associates:
                associates[emp_name] = []
            associates[emp_name].append(article_id)
    
    # Remove duplicates, sort
    for emp in associates:
        associates[emp] = sorted(list(set(associates[emp])))
    
    return associates

def print_assignments(associates: Dict[str, List[str]]):
    """Print clean assignments for manual copy-paste"""
    print("\n" + "="*100)
    print("📋 TODAY'S ASSIGNMENTS (Associate --> Articles --> Path)")
    print("="*100)
    
    today_folder = datetime.now().strftime("%Y%m%d")
    total_articles = 0
    
    for emp_name, article_ids in associates.items():
        ids_string = ','.join(article_ids)
        full_path = os.path.join(DEFAULT_ROOT_PATH, today_folder, emp_name)
        
        print(f"👤 {emp_name:<12} --> 📄 {ids_string:<50} --> 📁 {full_path}")
        print()
        total_articles += len(article_ids)
    
    print(f"\n🎯 SUMMARY: {len(associates)} associates, {total_articles} articles")
    print("="*100)

def main():
    """Extract and display assignments"""
    print("🚀 IEEE ASSIGNMENTS EXTRACTOR")
    print("=" * 60)
    
    if not os.path.exists(EXCEL_PATH):
        print(f"❌ Excel missing: {EXCEL_PATH}")
        sys.exit(1)
    
    # Load Excel
    df = pd.read_excel(EXCEL_PATH, header=0)
    print(f"📊 Loaded: {len(df)} rows")
    
    # Extract assignments
    associates = load_employee_articles_for_today(df)
    
    if not associates:
        print("❌ No assignments found for today!")
        sys.exit(1)
    
    # Print clean format
    print_assignments(associates)

if __name__ == "__main__":
    main()
