'''
import os
import re
from datetime import datetime

# ================================
# CONFIGURATION
# ================================
ROOT_PATH = r"G:\My Drive\VaveTechnologies\IEEE\March"
FILE_EXT = ".xml"

# ================================
# SENTENCE CASE UTILITY
# ================================
def sentence_case(text):
    """Convert text to: First letter uppercase, rest lowercase."""
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:].lower()

# ================================
# REGEX PATTERNS
# ================================
caption_title_pattern = re.compile(
    r"<caption>\s*<title>(.*?)</title>\s*</caption>",
    re.DOTALL
)
caption_p_pattern = re.compile(
    r"<caption>\s*<p>(.*?)</p>\s*</caption>",
    re.DOTALL
)

def run_captions(root_path: str = ROOT_PATH):
    """Process all XML files - sentence case captions. Pipeline entry point."""
    today_str = datetime.now().strftime("%Y%m%d")
    today_path = os.path.join(root_path, today_str)

    if not os.path.exists(today_path):
        print(f"❌ Today's folder does not exist: {today_path}")
        return False

    print(f"📁 Processing XML files in folder: {today_path}\n")
    print("=" * 70)

    # Track stats
    total_files = 0
    modified_files = 0
    total_replacements = 0

    for subdir, dirs, files in os.walk(today_path):
        for file in files:
            if file.lower().endswith(FILE_EXT):
                total_files += 1
                file_path = os.path.join(subdir, file)
                rel_path = os.path.relpath(file_path, today_path)

                print(f"\n📄 Checking: {rel_path}")

                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                original_content = content
                file_changed = False
                file_replacement_count = 0

                # ----- Replace <caption><title>...</title></caption> -----
                matches_title = caption_title_pattern.findall(content)
                if matches_title:
                    def repl_title(match):
                        inner = match.group(1)
                        new_text = sentence_case(inner)
                        return f"<caption><title>{new_text}</title></caption>"

                    content = caption_title_pattern.sub(repl_title, content)
                    file_changed = True
                    file_replacement_count += len(matches_title)
                    print(f"   ✓ Replaced {len(matches_title)} caption title(s)")

                # ----- Replace <caption><p>...</p></caption> -----
                matches_p = caption_p_pattern.findall(content)
                if matches_p:
                    def repl_p(match):
                        inner = match.group(1)
                        new_text = sentence_case(inner)
                        return f"<caption><p>{new_text}</p></caption>"

                    content = caption_p_pattern.sub(repl_p, content)
                    file_changed = True
                    file_replacement_count += len(matches_p)
                    print(f"   ✓ Replaced {len(matches_p)} caption <p> text(s)")

                # ----- Write file back -----
                if file_changed:
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(content)

                    modified_files += 1
                    total_replacements += file_replacement_count
                    print(f"   ✅ File updated ({file_replacement_count} replacement(s))")
                else:
                    print("   ⚪ No captions found")

                print("-" * 70)

    # ================================
    # SUMMARY
    # ================================
    print("\n" + "=" * 70)
    print("📊 PROCESSING COMPLETE - SUMMARY")
    print("=" * 70)
    print(f"📁 Folder: {today_path}")
    print(f"📄 Total XML files found: {total_files}")
    print(f"✅ Files modified: {modified_files}")
    print(f"🔄 Total caption replacements made: {total_replacements}")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    run_captions()
'''
import os
import re
from datetime import datetime

# ================================
# CONFIGURATION
# ================================
ROOT_PATH = r"G:\My Drive\VaveTechnologies\IEEE\March"
FILE_EXT = ".xml"

# ================================
# SENTENCE CASE UTILITY
# ================================
def sentence_case(text):
    """Convert text to: First letter uppercase, rest lowercase."""
    text = text.strip()
    if not text:
        return text
    return text[0].upper() + text[1:].lower()

# ================================
# REGEX PATTERNS
# ================================
caption_title_pattern = re.compile(
    r"<caption>\s*<title>(.*?)</title>\s*</caption>",
    re.DOTALL
)
caption_p_pattern = re.compile(
    r"<caption>\s*<p>(.*?)</p>\s*</caption>",
    re.DOTALL
)

# ================================
# CORE PROCESSING LOGIC
# ================================
def process_caption_file(file_path):
    """Reads and transforms XML captions to sentence case."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    file_replacement_count = 0
    file_changed = False

    # ----- Replace <caption><title>... -----
    matches_title = caption_title_pattern.findall(content)
    if matches_title:
        def repl_title(match):
            inner = match.group(1)
            return f"<caption><title>{sentence_case(inner)}</title></caption>"
        content = caption_title_pattern.sub(repl_title, content)
        file_changed = True
        file_replacement_count += len(matches_title)

    # ----- Replace <caption><p>... -----
    matches_p = caption_p_pattern.findall(content)
    if matches_p:
        def repl_p(match):
            inner = match.group(1)
            return f"<caption><p>{sentence_case(inner)}</p></caption>"
        content = caption_p_pattern.sub(repl_p, content)
        file_changed = True
        file_replacement_count += len(matches_p)

    if file_changed:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    return file_replacement_count

def run_captions_prompt():
    """Prompt for a single date folder and process all XMLs for captions."""
    print("\n📅 --- XML Caption Sentence Case Tool ---")
    date_str = input("Enter Date Folder (YYYYMMDD) [e.g. 20260207]: ").strip()

    # Validate date format
    try:
        datetime.strptime(date_str, "%Y%m%d")
    except ValueError:
        print(f"❌ Error: '{date_str}' is not in YYYYMMDD format.")
        return

    target_path = os.path.join(ROOT_PATH, date_str)

    if not os.path.exists(target_path):
        print(f"❌ Folder not found: {target_path}")
        return

    print(f"\n📁 Processing: {target_path}")
    print("=" * 70)

    total_files = 0
    modified_files = 0
    total_replacements = 0

    for subdir, _, files in os.walk(target_path):
        for file in files:
            if file.lower().endswith(FILE_EXT):
                total_files += 1
                file_path = os.path.join(subdir, file)
                rel_path = os.path.relpath(file_path, target_path)

                print(f"📄 Checking: {rel_path}")
                
                count = process_caption_file(file_path)
                
                if count > 0:
                    modified_files += 1
                    total_replacements += count
                    print(f"   ✅ Updated {count} caption(s)")
                else:
                    print("   ⚪ No captions found")
                
                print("-" * 40)

    # ================================
    # SUMMARY
    # ================================
    print("\n" + "=" * 70)
    print("📊 PROCESSING COMPLETE - SUMMARY")
    print("=" * 70)
    print(f"📅 Date Folder: {date_str}")
    print(f"📄 Total XML files found: {total_files}")
    print(f"✅ Files modified: {modified_files}")
    print(f"🔄 Total caption replacements: {total_replacements}")
    print("=" * 70)

if __name__ == "__main__":
    run_captions_prompt()