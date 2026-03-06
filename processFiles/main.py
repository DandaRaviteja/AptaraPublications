#!/usr/bin/env python3
"""
IEEE Article Processing Pipeline - Complete Automation
Downloads → Converts → Formats → Cleans → Validates
"""
import os
from datetime import datetime   
#from downloadingFiles import run_download
from conversionAndFormat import run_convert
from captionreplacement import run_captions
from sectiontitlecase import run_section_titlecase
from tagsreplacement import run_replacements
from equationreplacer import run_fix_equations

def get_root_path():
    """Prompt user for root folder path once at start"""
    default_path = r"G:\My Drive\Arczenrick\IEEE\2026\January"
    #default_path = r"G:\My Drive\\VaveTechnologies\IEEE\2026\January"
    
    print("\n" + "="*70)
    print("📁 IEEE ARTICLE PROCESSING PIPELINE")
    print("="*70)
    print(f"Default root folder: {default_path}")
    
    while True:
        path = input("\nEnter root folder path (or press Enter for default): ").strip()
        if not path:
            path = default_path
        elif not os.path.exists(path):
            print(f"❌ Folder does not exist: {path}")
            continue
        
        print(f"✅ Using root folder: {path}")
        return path

def main():
    """Main function to run the full IEEE article processing pipeline."""
    # Get root path ONCE from user
    root_path = get_root_path()
    
    print("\n🚀 Starting IEEE Article Processing Pipeline...")
    print(f"📂 Root folder: {root_path}")
    print("=" * 70)

    # Phase 1: Download (passes root_path for download folder creation)
    #print("\n📥 PHASE 1: DOWNLOADING ARTICLES")
    #if not run_download(root_path=root_path):  # Pass root_path
    #    print("❌ Download step failed. Exiting pipeline.")
    #    return False

    Phase 2: Convert and format (modify to accept root_path too)
    print("\n🔄 PHASE 2: CONVERSION & FORMATTING")
    if not run_convert(root_path=root_path):  # Pass root_path
        print("❌ Conversion step failed. Exiting pipeline.")
        return False

    # Phase 3-5: All processing steps use the SAME root_path
    print("\n📝 PHASE3: SECTION TITLE CASE")
    run_section_titlecase(root_path=root_path)

    print("\n✏️  PHASE 4: CAPTION PROCESSING")
    run_captions(root_path=root_path)
    
#    print("\n🔧 PHASE 5: EQUATION FIXER")
#    run_fix_equations(root_path=root_path)

    print("\n🔧 PHASE 6: TAG REPLACEMENTS & CLEANUP")
    run_replacements(root_path=root_path)

    print("\n" + "=" * 70)
    print("✅✅✅ PIPELINE COMPLETED SUCCESSFULLY ✅✅✅")
    print(f"📂 All files processed in: {root_path}")
    print("=" * 70)
    return True

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
