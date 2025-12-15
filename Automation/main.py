# main.py
import sys
import os

# Ensure current directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import your scripts
import downloadingFiles
import conversionAndFormat
import Addsomemoretagsreplacement
import sectiontitlecase
import captionreplacement

def main():
    print("\n=== Starting Automation Sequence ===\n")
    
    # Step 1: Download
    print(">>> Running downloadingFiles.py ...")
    download_success = downloadingFiles.main()
    if not download_success:
        print("\n❌ downloadingFiles.py failed. Stopping sequence.\n")
        return
    
    print("✅ downloadingFiles.py completed successfully!\n")
    
    # Step 2: Conversion
    print(">>> Running conversionAndFormat.py ...")
    conversion_success = conversionAndFormat.main()
    if not conversion_success:
        print("\n❌ conversionAndFormat.py failed. Stopping sequence.\n")
        return
    
    print("✅ conversionAndFormat.py completed successfully!\n")
    
    # Step 3: Add Tags Replacement
    print(">>> Running Addsomemoretagsreplacement.py ...")
    add_tags_success = Addsomemoretagsreplacement.main()
    if not add_tags_success:
        print("\n❌ Addsomemoretagsreplacement.py failed. Stopping sequence.\n")
        return
    
    print("✅ Addsomemoretagsreplacement.py completed successfully!\n")
    
    # Step 4: Section Title Case
    print(">>> Running sectiontitlecase.py ...")
    section_case_success = sectiontitlecase.main()
    if not section_case_success:
        print("\n❌ sectiontitlecase.py failed. Stopping sequence.\n")
        return
    
    print("✅ sectiontitlecase.py completed successfully!\n")
    
    # Step 5: Caption Replacement
    print(">>> Running captionreplacement.py ...")
    caption_success = captionreplacement.main()
    if not caption_success:
        print("\n❌ captionreplacement.py failed. Stopping sequence.\n")
        return
    
    print("✅ captionreplacement.py completed successfully!\n")
    
    print("\n🎉 All steps completed successfully! 🎉\n")

if __name__ == "__main__":
    main()
