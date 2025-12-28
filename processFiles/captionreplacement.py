import os
import re
from datetime import datetime

# ================================
# CONFIGURATION
# ================================
ROOT_PATH = r"G:\My Drive\Arczenrick\IEEE\2025\December"
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
