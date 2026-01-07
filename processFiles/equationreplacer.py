import os
import re
from datetime import datetime

def count_equations(block: str) -> int:
    """Count number of equations inside equation environment (split by \\)"""
    return block.count('\\\\') + 1

def process_latex_to_disp_formulas(tex: str) -> list[str]:
    """Convert LaTeX equation environments to proper IEEE JATS <disp-formula> blocks"""
    eq_pattern = re.compile(
        r'\\begin\{equation\}(.*?)\\end\{equation\}',
        re.S
    )

    eq_counter = 1
    disp_formulas: list[str] = []

    for block in eq_pattern.findall(tex):
        block = re.sub(r'\\label\{[^}]+\}', '', block).strip()
        eq_count = count_equations(block)

        if eq_count == 1:
            disp_id = f"deqn{eq_counter}"
        else:
            disp_id = f"deqn{eq_counter}-deqn{eq_counter + eq_count - 1}"

        if eq_count == 1:
            math = f"""\\begin{{equation*}}
{block}
\\tag{{{eq_counter}}}
\\end{{equation*}}"""
        else:
            lines = block.split('\\\\')
            tagged_lines = []
            for i, line in enumerate(lines):
                tag_num = eq_counter + i
                line = line.rstrip().rstrip(',').rstrip('.')
                tagged_lines.append(f"{line} \\tag{{{tag_num}}}")
            inner = " \\\\\n".join(tagged_lines)
            math = f"""\\begin{{equation*}}
\\begin{{gathered}}
{inner}
\\end{{gathered}}
\\end{{equation*}}"""

        disp_formulas.append(
            f"""<disp-formula id="{disp_id}"><tex-math notation="LaTeX">
{math}
</tex-math></disp-formula>"""
        )
        eq_counter += eq_count

    return disp_formulas

def replace_disp_formulas_in_xml(xml_text: str, new_disp_list: list[str]) -> str:
    """Replace existing <disp-formula> blocks position by position"""
    pattern = re.compile(r'<disp-formula[^>]*>.*?</disp-formula>', re.DOTALL)
    matches = list(pattern.finditer(xml_text))
    
    if not matches:
        print("  ⚠️  No <disp-formula> found in XML.")
        return xml_text

    print(f"  ➤ Found {len(matches)} existing equations")
    print(f"  ➤ Generated {len(new_disp_list)} new equations")

    result = xml_text
    for i in range(len(matches) - 1, -1, -1):
        if i < len(new_disp_list):
            m = matches[i]
            new_block = new_disp_list[i]
            result = result[:m.start()] + new_block + result[m.end():]
            print(f"  ✓ Replaced equation #{i+1}")
        else:
            print(f"  ⚠️  Warning: More XML equations than LaTeX")

    return result

def find_tex_and_xml_in_article_folder(article_folder: str) -> tuple[str, str]:
    """Find .tex file and corresponding FTXML file in AppOut structure"""
    
    # 1. Find .tex file in source folder (any level deep)
    tex_path = None
    for root, dirs, files in os.walk(article_folder):
        for file in files:
            if file.lower().endswith('.tex'):
                tex_path = os.path.join(root, file)
                print(f"  📄 Found LaTeX: {os.path.relpath(tex_path, article_folder)}")
                break
        if tex_path:
            break
    
    if not tex_path:
        return None, None
    
    # 2. Find corresponding XML in AppOut/UniqueID/FTXML/
    appout_path = os.path.join(article_folder, 'AppOut')
    if not os.path.exists(appout_path):
        print(f"  ⚠️  No AppOut folder found")
        return None, None
    
    # Find FTXML folder (deepest level)
    ftxml_path = None
    for root, dirs, files in os.walk(appout_path):
        if 'FTXML' in dirs or any(f.lower().endswith('.xml') for f in files):
            # Go deepest first
            ftxml_candidates = []
            for r, d, f in os.walk(appout_path):
                if any(fi.lower().endswith('.xml') for fi in f):
                    ftxml_candidates.append(r)
            if ftxml_candidates:
                ftxml_path = max(ftxml_candidates, key=len)  # Deepest path
                break
    
    if not ftxml_path or not os.path.exists(ftxml_path):
        print(f"  ⚠️  No FTXML/XML folder found")
        return None, None
    
    # Find first .xml file
    xml_files = [f for f in os.listdir(ftxml_path) if f.lower().endswith('.xml')]
    if not xml_files:
        print(f"  ⚠️  No XML files in {os.path.relpath(ftxml_path, article_folder)}")
        return None, None
    
    xml_path = os.path.join(ftxml_path, xml_files[0])
    print(f"  📄 Found XML:   {os.path.relpath(xml_path, article_folder)}")
    
    return tex_path, xml_path

def process_article_folder(article_folder: str) -> bool:
    """Process single article: tex → fix equations in FTXML"""
    print(f"\n🔧 Processing: {os.path.basename(article_folder)}")
    
    tex_path, xml_path = find_tex_and_xml_in_article_folder(article_folder)
    
    if not tex_path or not xml_path:
        print(f"  ⏭️  Skipping - missing tex/xml")
        return False
    
    try:
        # 1) Read LaTeX source
        with open(tex_path, encoding="utf-8") as f:
            tex = f.read()
        
        # 2) Generate fixed disp-formula blocks
        disp_list = process_latex_to_disp_formulas(tex)
        
        # 3) Read FTXML
        with open(xml_path, encoding="utf-8") as f:
            xml_text = f.read()
        
        # 4) Replace equations
        fixed_xml = replace_disp_formulas_in_xml(xml_text, disp_list)
        
        # 5) Backup + save
        backup_xml = xml_path + ".backup"
        if os.path.exists(backup_xml):
            os.remove(backup_xml)
        os.rename(xml_path, backup_xml)
        
        with open(xml_path, "w", encoding="utf-8") as f:
            f.write(fixed_xml)
        
        print(f"  ✅ SUCCESS: Fixed {len(disp_list)} equations")
        print(f"  💾 Backup: {os.path.basename(backup_xml)}")
        return True
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        # Restore backup
        backup_xml = xml_path + ".backup"
        if os.path.exists(backup_xml):
            os.rename(backup_xml, xml_path)
        return False

def run_fix_equations(root_path: str = r"G:\My Drive\Arczenrick\IEEE\2025\December") -> bool:
    """Pipeline Step 6: Fix equations ONLY in valid article folders (tex + AppOut/FTXML)"""
    today_str = datetime.now().strftime("%Y%m%d")
    today_path = os.path.join(root_path, today_str)
    
    if not os.path.exists(today_path):
        print(f"❌ Today's folder ({today_path}) does not exist")
        return False
    
    print(f"\n🔧 PHASE 6: EQUATION FIXER")
    print(f"📁 Processing: {today_path}")
    print("=" * 70)
    
    # Find ONLY deepest article folders with BOTH tex AND AppOut/FTXML
    valid_article_folders = []
    for root, dirs, files in os.walk(today_path):
        # Skip root/employee folders
        if root == today_path or os.path.basename(os.path.dirname(root)) == today_path:
            continue
            
        basename = os.path.basename(root)
        if basename in ['Meta', 'AppOut', 'FTXML']:
            continue
            
        # Check if this folder has BOTH tex AND AppOut
        has_tex = any(f.lower().endswith('.tex') for f in files)
        has_appout = os.path.exists(os.path.join(root, 'AppOut'))
        
        if has_tex and has_appout:
            valid_article_folders.append(root)
    
    print(f"📂 Found {len(valid_article_folders)} VALID article folders (tex + AppOut)")
    
    if not valid_article_folders:
        print("⚠️  No valid articles found (need both .tex and AppOut)")
        return False
    
    success_count = 0
    for article_folder in sorted(valid_article_folders):
        print(f"\n{'='*50}")
        print(f"ARTICLE: {os.path.basename(article_folder)}")
        print(f"PATH:    {os.path.relpath(article_folder, today_path)}")
        print(f"{'='*50}")
        
        if process_article_folder(article_folder):
            success_count += 1
    
    print("\n" + "=" * 70)
    print("📊 EQUATION FIX SUMMARY")
    print("=" * 70)
    print(f"📁 Base folder: {today_path}")
    print(f"📂 Valid articles: {len(valid_article_folders)}")
    print(f"✅ Successfully fixed: {success_count}")
    print(f"❌ Failed/Skipped: {len(valid_article_folders) - success_count}")
    print("=" * 70)
    
    return success_count > 0

if __name__ == "__main__":
    run_fix_equations()
