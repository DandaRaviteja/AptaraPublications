'''
import os
import re
from datetime import datetime


# ================================
# CONFIGURATION
# ================================
ROOT_PATH = r"G:\My Drive\VaveTechnologies\IEEE\February"
FILE_EXT = ".xml"

# ================================
# TITLE CASE UTILITY
# ================================
PREPOSITIONS = {
    "a", "an", "the", "and", "or", "but",
    "on", "in", "to", "for", "with", "at",
    "by", "from", "of", "up", "as", "into",
    "like", "over", "after", "before", "under",
    "between", "without", "within"
}

def title_case(text):
    """Convert to title case while keeping prepositions lowercase (except first/last)."""
    words = re.split(r'(\W+)', text)  # keep spaces/punctuation
    alpha_words = [w for w in words if re.match(r'[A-Za-z0-9]', w)]

    if not alpha_words:
        return text

    first_word = alpha_words[0].lower()
    last_word = alpha_words[-1].lower()

    def fix(w):
        core = re.sub(r'[^A-Za-z0-9]', '', w)
        if not core:
            return w
        low = core.lower()

        if low == first_word or low == last_word:
            new = low.capitalize()
        elif low in PREPOSITIONS:
            new = low
        else:
            new = low.capitalize()

        return re.sub(core, new, w)

    return ''.join(fix(w) for w in words)

# ================================
# REGEX PATTERNS
# ================================
# Match: <sec ...> ... </sec>
sec_block_pattern = re.compile(
    r"(<sec\b[^>]*>)(.*?)(</sec>)",
    re.IGNORECASE | re.DOTALL
)

# Match <title>...</title> inside sec
title_inside_sec_pattern = re.compile(
    r"(<title>)(.*?)(</title>)",
    re.IGNORECASE | re.DOTALL
)

def run_section_titlecase(root_path: str = ROOT_PATH):
    """Process all XML files - title case <title> inside <sec>. Pipeline entry point."""
    today_str = datetime.now().strftime("%Y%m%d")
    today_path = os.path.join(root_path, today_str)

    if not os.path.exists(today_path):
        print(f"❌ Today's folder does not exist: {today_path}")
        return False

    print(f"📁 Processing XML files in: {today_path}")
    print("=" * 70)

    total_files = 0
    modified_files = 0
    total_titles_changed = 0

    for subdir, dirs, files in os.walk(today_path):
        for file in files:
            if not file.lower().endswith(FILE_EXT):
                continue

            total_files += 1
            file_path = os.path.join(subdir, file)

            print(f"\n📄 Checking: {file}")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            titles_changed_in_file = 0

            # ============================================
            # PROCESS EACH <sec> ... </sec> BLOCK
            # ============================================
            sec_blocks = sec_block_pattern.findall(content)

            if sec_blocks:
                for sec_start, sec_inner, sec_end in sec_blocks:

                    # Replace only <title> text inside this block
                    def replace_title(match):
                        before, text, after = match.groups()
                        new_text = title_case(text)
                        return before + new_text + after

                    new_inner, count = title_inside_sec_pattern.subn(replace_title, sec_inner)

                    if count > 0:
                        titles_changed_in_file += count

                        old_block = sec_start + sec_inner + sec_end
                        new_block = sec_start + new_inner + sec_end

                        content = content.replace(old_block, new_block)

            # ============================================
            # SAVE FILE IF MODIFIED
            # ============================================
            if titles_changed_in_file > 0:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                modified_files += 1
                total_titles_changed += titles_changed_in_file

                print(f"   ✓ Updated {titles_changed_in_file} <title> tag(s) inside <sec>")
            else:
                print("   ⚪ No <title> inside <sec> found")

    print("\n" + "=" * 70)
    print("📊 SUMMARY")
    print("=" * 70)
    print(f"📄 Total XML files processed: {total_files}")
    print(f"✏️ Files modified: {modified_files}")
    print(f"🔤 Total section titles updated: {total_titles_changed}")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    run_section_titlecase()
'''
import os
import re
from datetime import datetime

# ================================
# CONFIGURATION
# ================================
ROOT_PATH = r"G:\My Drive\VaveTechnologies\IEEE\February"
FILE_EXT = ".xml"

# ================================
# TITLE CASE UTILITY
# ================================
PREPOSITIONS = {
    "a", "an", "the", "and", "or", "but",
    "on", "in", "to", "for", "with", "at",
    "by", "from", "of", "up", "as", "into",
    "like", "over", "after", "before", "under",
    "between", "without", "within"
}

def title_case(text):
    """Convert to title case while keeping prepositions lowercase (except first/last)."""
    words = re.split(r'(\W+)', text)
    alpha_words = [w for w in words if re.match(r'[A-Za-z0-9]', w)]

    if not alpha_words:
        return text

    first_word = alpha_words[0].lower()
    last_word = alpha_words[-1].lower()

    def fix(w):
        core = re.sub(r'[^A-Za-z0-9]', '', w)
        if not core: return w
        low = core.lower()

        if low == first_word or low == last_word:
            new = low.capitalize()
        elif low in PREPOSITIONS:
            new = low
        else:
            new = low.capitalize()
        return re.sub(core, new, w)

    return ''.join(fix(w) for w in words)

# ================================
# REGEX PATTERNS
# ================================
sec_block_pattern = re.compile(r"(<sec\b[^>]*>)(.*?)(</sec>)", re.IGNORECASE | re.DOTALL)
title_inside_sec_pattern = re.compile(r"(<title>)(.*?)(</title>)", re.IGNORECASE | re.DOTALL)

# ================================
# CORE PROCESSING LOGIC
# ================================
def process_xml_file(file_path):
    """Reads, transforms, and saves the XML if titles are updated."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    titles_changed_in_file = 0
    sec_blocks = sec_block_pattern.findall(content)

    if sec_blocks:
        for sec_start, sec_inner, sec_end in sec_blocks:
            def replace_title(match):
                before, text, after = match.groups()
                return before + title_case(text) + after

            new_inner, count = title_inside_sec_pattern.subn(replace_title, sec_inner)
            if count > 0:
                titles_changed_in_file += count
                old_block = sec_start + sec_inner + sec_end
                new_block = sec_start + new_inner + sec_end
                content = content.replace(old_block, new_block)

    if titles_changed_in_file > 0:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    return titles_changed_in_file

def run_single_date_titlecase():
    """Prompt for a single date folder and process all XMLs within it."""
    print("\n📅 --- XML Section Title Case Tool ---")
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
    print("=" * 60)

    total_files = 0
    modified_files = 0
    total_titles_changed = 0

    for subdir, _, files in os.walk(target_path):
        for file in files:
            if file.lower().endswith(FILE_EXT):
                total_files += 1
                file_path = os.path.join(subdir, file)
                
                changed_count = process_xml_file(file_path)
                
                if changed_count > 0:
                    modified_files += 1
                    total_titles_changed += changed_count
                    print(f"✅ {file}: Updated {changed_count} title(s)")
                else:
                    print(f"⚪ {file}: No section titles needed updating")

    # Final Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"📅 Date Folder: {date_str}")
    print(f"📄 Files Scanned: {total_files}")
    print(f"✏️  Files Modified: {modified_files}")
    print(f"🔤 Total Titles Changed: {total_titles_changed}")
    print("=" * 60)

if __name__ == "__main__":
    run_single_date_titlecase()