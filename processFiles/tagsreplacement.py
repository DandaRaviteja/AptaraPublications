'''
import os
import re
from datetime import datetime

ROOT_PATH = r"G:\My Drive\VaveTechnologies\IEEE\March"
FILE_EXT = ".xml"

REPLACEMENTS = [
    ('*"/>', '"/>'),
    ('="tbl', '="table'),
    ('<disp-formula>', '<disp-formula id="deqn1">'),
    ('*>', '>'),
    ('&#X', '&#x'),
    ('*">', '">'),
    ('<br/>', ''),
    (' </', '</'),
    ('=$</tex-math></inline-formula>', '$</tex-math></inline-formula> ='),
    ('-$</tex-math></inline-formula>', '$</tex-math></inline-formula> -'),
    ('<td></td>', '<td/>'),
    ('<th></th>', '<th/>'),
    ('<td>-</td>', '<td>&#x2013;</td>'),
    ('<td>-', '<td>&#x2212;'),
    ('</xref>(a)', '(a)</xref>'),
    ('</xref>(b)', '(b)</xref>'),
    ('</xref>(c)', '(c)</xref>'),
    ('</xref>(d)', '(d)</xref>'),
    ('</xref><xref ', '</xref> <xref '),
    ('"><label>table ', '">\n<label>Table '),
    ('<kwd-group/>', ''),
    
    (
        r'\end{equation*}</tex-math></disp-formula>',
        r'\\tag{1}\n\\end{equation*}</tex-math></disp-formula>'
    ),
    ('.</article-title>', '</article-title>.'),
    ('<uri content-type="url">', '<uri>'),
    ('.</pub-id>', '</pub-id>.'),
    ('.</uri>', '</uri>.'),
    ('accessed: ', 'accessed: <date-in-citation>'),
    ('Accessed: ', 'Accessed: <date-in-citation>'),
    ('</fpage>&#x<conf-date>2013</conf-date>;<lpage>', '</fpage>&#x2013;<lpage>'),
    ('<article-title> ', '<article-title>'),
    ('</surname>;', ';</surname>'),
    ('<year><year>', '<year>'),
    ('</year></year>', '</year>'),
    ('<source>arXiv preprint arXiv:', '<source>arXiv preprint</source> arXiv:<pub-id pub-id-type="arxiv">'),
    (' arXiv preprint ', ' <source>arXiv preprint</source> '),
    ('</article-title>,</article-title>', '</article-title>,'),
    ('</given-names><string-name><given-names>', '</given-names> <surname>'),
    ('<publisher-name>IEEE</publisher-name>', '<conf-sponsor>IEEE</conf-sponsor>'),
    ('"aff(1)">(1)</xref>', '"aff1"><sup>(1)</sup></xref>'),
    ('"aff(2)">(2)</xref>', '"aff2"><sup>(2)</sup></xref>'),
    (',</p>\n<p>', ', '),
    ('"aff(3)">(3)</xref>', '"aff3"><sup>(3)</sup></xref>'),
    ('"aff1">1</xref>', '"aff1"><sup>1</sup></xref>'),
    ('"aff2">2</xref>', '"aff2"><sup>2</sup></xref>'),
    ('"aff3">3</xref>', '"aff3"><sup>3</sup></xref>'),
    ('"aff4">4</xref>', '"aff4"><sup>4</sup></xref>'),
    ('*</surname>', '</surname>'),
    ('"><label>TABLE', '">\n<label>Table'),
    ('"><label>Table', '">\n<label>Table'),
    ('\#', '#'),
    ('\</p>', '</p>'),
    ('</label><title>', '</label>\n<title>'),
    ('formula></p>\n<p>where', 'formula>\nwhere'),
    ('</fig></p>\n<table-wrap', '</fig>\n<table-wrap'),
    ('\page{***}\n</sec>', ''),
    ('<sup>\dagger</sup>', '<sup>&#x2020;</sup>'),
    ('<sup>\ddagger</sup>', '<sup>&#x2021;</sup>'),
    ('&#x00A7;', '<sup>&#x00A7;</sup>'),
    ('\(1{ }^{\text {st }}\) ', ''),
    ('\(2{ }^{\text {nd }}\) ', ''),
    ('\(3{ }^{\text {rd }}\) ', ''),
    ('\(4{ }^{\text {th }}\) ', ''),
    ('\(5{ }^{\text {th }}\) ', ''),
    ('\(6{ }^{\text {th }}\) ', ''),
    ('\(7{ }^{\text {th }}\) ', ''),
    ('\(8{ }^{\text {th }}\) ', ''),
    ('<conf-loc>IEEE</conf-loc>', '<conf-sponsor>IEEE</conf-sponsor>'),
    ('"latex"', '"LaTeX"'),
    ('<source>in ', 'in <source>'),
    ('<source>Proc. IEEE', '<source specific-use="IEEE">Proc. IEEE'),
    ('<source>IEEE', '<source specific-use="IEEE">IEEE'),
    ('<source>Proceedings of the IEEE', '<source specific-use="IEEE">Proceedings of the IEEE'),
    ('<conf-name>Proceedings of the IEEE', '<source specific-use="IEEE">Proceedings of the IEEE'),
    ('\dagger</xref>', '<sup>&#x2020;</sup></xref>'),
    ('\ddagger</xref>', '<sup>&#x2021;</sup></xref>'),
    ('<inline-formula><tex-math notation="LaTeX">$=$</tex-math></inline-formula>', '='),
    ('<inline-formula><tex-math notation="LaTeX">$$</tex-math></inline-formula>', ''),
    ('<publisher-loc>doi</publisher-loc>: <publisher-name>', 'doi: <pub-id pub-id-type="doi">'),
    ('</p>\n<table-wrap', '\n<table-wrap'),
    ('<publisher-loc>DOI</publisher-loc>: <publisher-name>', 'DOI: <pub-id pub-id-type="doi">'),
    ('publication-type="webpage"', 'publication-type="online"'),
    ('PMID: ', 'PMID: <pub-id pub-id-type="pmid">'),
    ('PMCID: ', 'PMCID: <pub-id pub-id-type="pmcid">'),
    ('<source>Proceedings of the IEEE', '<source specific-use="IEEE">Proceedings of the IEEE'),
    (';<inline-formula>', '; <inline-formula>')



]

def run_replacements(root_path: str = ROOT_PATH) -> bool:
    """Run all configured string replacements on today's XML files under root_path."""
    today_str = datetime.now().strftime("%Y%m%d")
    today_path = os.path.join(root_path, today_str)

    if not os.path.exists(today_path):
        print(f"❌ Today's folder does not exist: {today_path}")
        print(f"   Please create the folder or check the path.")
        return False

    print(f"📁 Processing files in today's folder: {today_path}\n")
    print("=" * 70)

    total_files = 0
    modified_files = 0
    total_replacements = 0

    for subdir, dirs, files in os.walk(today_path):
        for file in files:
            if not file.lower().endswith(FILE_EXT):
                continue

            total_files += 1
            file_path = os.path.join(subdir, file)

            rel_path = os.path.relpath(file_path, today_path)
            print(f"\n📄 Checking: {rel_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            file_changed = False
            file_replacement_count = 0

            for find_str, replace_str in REPLACEMENTS:
                pattern = re.escape(find_str)
                count = len(re.findall(pattern, content))

                if count > 0:
                    content = re.sub(pattern, replace_str, content)
                    file_changed = True
                    file_replacement_count += count
                    print(f"   ✓ Found {count} × '{find_str}' → replaced with '{replace_str}'")

            if file_changed:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                modified_files += 1
                total_replacements += file_replacement_count
                print(f"   ✅ File updated ({file_replacement_count} replacement(s))")
            else:
                print(f"   ⚪ No changes needed")

            print("-" * 70)

    print("\n" + "=" * 70)
    print("📊 PROCESSING COMPLETE - SUMMARY")
    print("=" * 70)
    print(f"📁 Folder: {today_path}")
    print(f"📄 Total XML files found: {total_files}")
    print(f"✅ Files modified: {modified_files}")
    print(f"🔄 Total replacements made: {total_replacements}")
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    run_replacements()
'''
import os
import re
from datetime import datetime

# ================================
# CONFIGURATION
# ================================
ROOT_PATH = r"G:\My Drive\VaveTechnologies\IEEE\March"
FILE_EXT = ".xml"

# List of (find_string, replace_string)
REPLACEMENTS = [
    ('*"/>', '"/>'),
    ('="tbl', '="table'),
    ('<disp-formula>', '<disp-formula id="deqn1">'),
    ('*>', '>'),
    ('&#X', '&#x'),
    ('*">', '">'),
    ('<br/>', ''),
    (' </', '</'),
    ('=$</tex-math></inline-formula>', '$</tex-math></inline-formula> ='),
    ('-$</tex-math></inline-formula>', '$</tex-math></inline-formula> -'),
    ('<td></td>', '<td/>'),
    ('<th></th>', '<th/>'),
    ('<td>-</td>', '<td>&#x2013;</td>'),
    ('<td>-', '<td>&#x2212;'),
    ('</xref>(a)', '(a)</xref>'),
    ('</xref>(b)', '(b)</xref>'),
    ('</xref>(c)', '(c)</xref>'),
    ('</xref>(d)', '(d)</xref>'),
    ('</xref><xref ', '</xref> <xref '),
    ('"><label>table ', '">\n<label>Table '),
    ('<kwd-group/>', ''),
    (r'\end{equation*}</tex-math></disp-formula>', r'\\tag{1}\n\\end{equation*}</tex-math></disp-formula>'),
    ('.</article-title>', '</article-title>.'),
    ('<uri content-type="url">', '<uri>'),
    ('.</pub-id>', '</pub-id>.'),
    ('.</uri>', '</uri>.'),
    ('accessed: ', 'accessed: <date-in-citation>'),
    ('Accessed: ', 'Accessed: <date-in-citation>'),
    ('</fpage>&#x<conf-date>2013</conf-date>;<lpage>', '</fpage>&#x2013;<lpage>'),
    ('<article-title> ', '<article-title>'),
    ('</surname>;', ';</surname>'),
    ('<year><year>', '<year>'),
    ('</year></year>', '</year>'),
    ('<source>arXiv preprint arXiv:', '<source>arXiv preprint</source> arXiv:<pub-id pub-id-type="arxiv">'),
    (' arXiv preprint ', ' <source>arXiv preprint</source> '),
    ('</article-title>,</article-title>', '</article-title>,'),
    ('</given-names><string-name><given-names>', '</given-names> <surname>'),
    ('<publisher-name>IEEE</publisher-name>', '<conf-sponsor>IEEE</conf-sponsor>'),
    ('"aff(1)">(1)</xref>', '"aff1"><sup>(1)</sup></xref>'),
    ('"aff(2)">(2)</xref>', '"aff2"><sup>(2)</sup></xref>'),
    (',</p>\n<p>', ', '),
    ('"aff(3)">(3)</xref>', '"aff3"><sup>(3)</sup></xref>'),
    ('"aff1">1</xref>', '"aff1"><sup>1</sup></xref>'),
    ('"aff2">2</xref>', '"aff2"><sup>2</sup></xref>'),
    ('"aff3">3</xref>', '"aff3"><sup>3</sup></xref>'),
    ('"aff4">4</xref>', '"aff4"><sup>4</sup></xref>'),
    ('*</surname>', '</surname>'),
    ('"><label>TABLE', '">\n<label>Table'),
    ('"><label>Table', '">\n<label>Table'),
    ('\#', '#'),
    ('\</p>', '</p>'),
    ('</label><title>', '</label>\n<title>'),
    ('formula></p>\n<p>where', 'formula>\nwhere'),
    ('</fig></p>\n<table-wrap', '</fig>\n<table-wrap'),
    ('\page{***}\n</sec>', ''),
    ('<sup>\dagger</sup>', '<sup>&#x2020;</sup>'),
    ('<sup>\ddagger</sup>', '<sup>&#x2021;</sup>'),
    ('&#x00A7;', '<sup>&#x00A7;</sup>'),
    ('\(1{ }^{\text {st }}\) ', ''),
    ('\(2{ }^{\text {nd }}\) ', ''),
    ('\(3{ }^{\text {rd }}\) ', ''),
    ('\(4{ }^{\text {th }}\) ', ''),
    ('\(5{ }^{\text {th }}\) ', ''),
    ('\(6{ }^{\text {th }}\) ', ''),
    ('\(7{ }^{\text {th }}\) ', ''),
    ('\(8{ }^{\text {th }}\) ', ''),
    ('<conf-loc>IEEE</conf-loc>', '<conf-sponsor>IEEE</conf-sponsor>'),
    ('"latex"', '"LaTeX"'),
    ('<source>in ', 'in <source>'),
    ('<source>Proc. IEEE', '<source specific-use="IEEE">Proc. IEEE'),
    ('<source>IEEE', '<source specific-use="IEEE">IEEE'),
    ('<source>Proceedings of the IEEE', '<source specific-use="IEEE">Proceedings of the IEEE'),
    ('\dagger</xref>', '<sup>&#x2020;</sup></xref>'),
    ('\ddagger</xref>', '<sup>&#x2021;</sup></xref>'),
    ('<inline-formula><tex-math notation="LaTeX">$=$</tex-math></inline-formula>', '='),
    ('<inline-formula><tex-math notation="LaTeX">$$</tex-math></inline-formula>', ''),
    ('<publisher-loc>doi</publisher-loc>: <publisher-name>', 'doi: <pub-id pub-id-type="doi">'),
    ('</p>\n<table-wrap', '\n<table-wrap'),
    ('<publisher-loc>DOI</publisher-loc>: <publisher-name>', 'DOI: <pub-id pub-id-type="doi">'),
    ('publication-type="webpage"', 'publication-type="online"'),
    ('PMID: ', 'PMID: <pub-id pub-id-type="pmid">'),
    ('PMCID: ', 'PMCID: <pub-id pub-id-type="pmcid">'),
    (';<inline-formula>', '; <inline-formula>')
]

# ================================
# CORE LOGIC
# ================================
def process_replacements_in_file(file_path):
    """Applies all replacements in REPLACEMENTS list to a single file."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    file_changed = False
    file_replacement_count = 0

    for find_str, replace_str in REPLACEMENTS:
        # Use re.escape to handle special characters in find_str safely
        pattern = re.escape(find_str)
        matches = re.findall(pattern, content)
        count = len(matches)

        if count > 0:
            content = re.sub(pattern, replace_str, content)
            file_changed = True
            file_replacement_count += count
    
    if file_changed:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
            
    return file_replacement_count

def run_replacements_prompt():
    """Prompt for a single date folder and run global replacements."""
    print("\n📝 --- XML Global Replacements Tool ---")
    date_str = input("Enter Date Folder (YYYYMMDD) [e.g. 20260207]: ").strip()

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
    total_reps_made = 0

    for subdir, _, files in os.walk(target_path):
        for file in files:
            if file.lower().endswith(FILE_EXT):
                total_files += 1
                file_path = os.path.join(subdir, file)
                rel_path = os.path.relpath(file_path, target_path)

                print(f"📄 Checking: {rel_path}")
                count = process_replacements_in_file(file_path)

                if count > 0:
                    modified_files += 1
                    total_reps_made += count
                    print(f"   ✅ Done: {count} replacement(s) applied")
                else:
                    print(f"   ⚪ No replacements needed")
                print("-" * 40)

    # Final Summary
    print("\n" + "=" * 70)
    print("📊 REPLACEMENT SUMMARY")
    print("=" * 70)
    print(f"📅 Date Folder: {date_str}")
    print(f"📄 Total XML files scanned: {total_files}")
    print(f"✅ Files modified:         {modified_files}")
    print(f"🔄 Total replacements:      {total_reps_made}")
    print("=" * 70)

if __name__ == "__main__":
    run_replacements_prompt()