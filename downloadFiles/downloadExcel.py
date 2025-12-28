#!/usr/bin/env python3
"""
IEEE BATCH DOWNLOADER - Auto-process ALL associates from Excel
No manual input - downloads everything for today!
"""
import os
import sys
import pandas as pd
import logging
from datetime import datetime
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

EXCEL_PATH = r"C:\Users\raviteja\OneDrive\Documents\IEEE_December.xlsx"
DEFAULT_ROOT_PATH = r"G:\My Drive\Arczenrick\IEEE\2025\December"

def get_articles_by_associate(df, today_date: str) -> dict:
    """Group articles by associate name from Excel"""
    # Column indices: S=18(Imported Date), T=19(Assigned TO), R=17(Article)
    date_col = df.iloc[:, 18].astype(str)
    emp_col = df.iloc[:, 19].astype(str)
    article_col = df.iloc[:, 17].astype(str)
    
    # Filter today's articles
    date_mask = date_col.str.contains(today_date, na=False)
    today_articles = df[date_mask]
    
    # Group by employee
    associates = {}
    for _, row in today_articles.iterrows():
        emp_name = row.iloc[19].strip()  # Column T
        article_id = str(row.iloc[17]).strip()  # Column R
        
        if article_id.isdigit() and emp_name:
            if emp_name not in associates:
                associates[emp_name] = []
            associates[emp_name].append(article_id)
    
    # Remove duplicates, sort
    for emp in associates:
        associates[emp] = sorted(list(set(associates[emp])))
    
    return associates

def download_for_associate(associate_name: str, article_ids: list, root_path: str):
    """Call downloadingFiles.py for one associate"""
    print(f"\n🚀 DOWNLOADING {len(article_ids)} articles for {associate_name}")
    print(f"   IDs: {', '.join(article_ids)}")
    
    # Call downloadingFiles.py programmatically
    try:
        from downloadingFiles import run_download
        success = run_download(root_path=root_path, associate_name=associate_name, article_ids_string=','.join(article_ids))
        if success:
            print(f"✅ {associate_name}: SUCCESS")
            return True
        else:
            print(f"❌ {associate_name}: FAILED")
            return False
    except ImportError:
        # Fallback: subprocess call
        cmd = [
            sys.executable, "downloadingFiles.py",
            "--root_path", root_path,
            "--associate", associate_name,
            "--articles", ','.join(article_ids)
        ]
        result = subprocess.run(cmd, cwd=os.getcwd(), capture_output=True, text=True)
        print(f"   Exit code: {result.returncode}")
        return result.returncode == 0

def main():
    """BATCH process ALL associates from Excel"""
    print("🚀 IEEE BATCH DOWNLOADER - ALL ASSOCIATES")
    print("=" * 60)
    
    # Load Excel
    if not os.path.exists(EXCEL_PATH):
        print(f"❌ Excel missing: {EXCEL_PATH}")
        sys.exit(1)
    
    df = pd.read_excel(EXCEL_PATH, header=0)
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    print(f"📊 Loaded Excel: {len(df)} total rows")
    print(f"📅 Filtering for today: {today_date}")
    
    # Group articles by associate
    associates = get_articles_by_associate(df, today_date)
    
    if not associates:
        print("❌ No articles found for today!")
        sys.exit(1)
    
    print(f"\n📋 TODAY'S WORKLOAD:")
    print("=" * 40)
    total_articles = 0
    for emp, ids in associates.items():
        count = len(ids)
        total_articles += count
        print(f"👤 {emp}: {count} articles")
        print(f"   {', '.join(ids[:3])}{'...' if count > 3 else ''}")
    
    print(f"\n📈 TOTAL: {total_articles} articles across {len(associates)} associates")
    
    # Confirm batch download
    confirm = input(f"\n🚀 Download ALL {total_articles} articles? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        print("Cancelled.")
        sys.exit(0)
    
    # Get root path
    root_path = input(f"\n📁 Root path [{DEFAULT_ROOT_PATH}]: ").strip()
    if not root_path:
        root_path = DEFAULT_ROOT_PATH
    
    if not os.path.exists(root_path):
        print(f"❌ Root path doesn't exist: {root_path}")
        sys.exit(1)
    
    print(f"\n🎬 STARTING BATCH DOWNLOAD")
    print("=" * 60)
    
    # Process each associate
    success_count = 0
    for associate_name, article_ids in associates.items():
        print(f"\n{'='*60}")
        print(f"[{success_count+1}/{len(associates)}] {associate_name}")
        print(f"{'='*60}")
        
        if download_for_associate(associate_name, article_ids, root_path):
            success_count += 1
        
        print("-" * 60)
    
    print(f"\n🎉 BATCH COMPLETE!")
    print(f"✅ Success: {success_count}/{len(associates)} associates")
    print(f"📊 Total articles: {total_articles}")
    print(f"📁 Saved to: {root_path}")

if __name__ == "__main__":
    main()
