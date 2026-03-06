import glob
import os

# Your specific replacement rules
REPLACEMENTS = [
    ('<unit type="">', '<unit type="BATCH">'),
    (' stage=""', ' stage="S300"'),
    ('<citation-type code="meeting-report"/>', '<citation-type code="cb"/>'),
    ('<volisspag>', '<sourcetitle>Journal of Clinical Oncology</sourcetitle>\n<sourcetitle-abbrev>ASCO MEETING ABSTRACTS</sourcetitle-abbrev>\n<issn type="print">0732183X</issn>\n<issn type="electronic">15277755</issn>\n<volisspag>'),
    ('</publicationdate>', '</publicationdate>\n<publisher>\n<publishername>American Society of Clinical Oncology</publishername>\n</publisher>\n<additional-srcinfo>\n<conferenceinfo>\n<confevent>\n<confname>ASCO MEETING ABSTRACTS</confname>\n<conflocation country="USA">\n<city>Chicago</city>\n<state>IL</state>\n</conflocation>\n<confdate>\n<startdate>2025-05-30</startdate>\n<enddate>2025-06-03</enddate>\n</confdate>\n</confevent>\n</conferenceinfo>\n</additional-srcinfo>'),
    ('>, <', '>\n<'),
    ('organization>\n<pt>', 'organization>\n<city>'),
    ('</pt>\n<pt>', '</city>\n<state>'),
    ('<bold>', ''),
    ('</bold>', '')

### Refercennces Replacement Rules
    ('><', '>\n<'),
#    ('><idtype="FRAGMENTID">R', 'idtype="FRAGMENTID">ref00'),
#    ('><idtype="FRAGMENTID">ref0010', 'idtype="FRAGMENTID">ref00'),
    ('</ce:initials>', '.</ce:initials>')
    ('><', '>\n<')
    ('><', '>\n<')
    ('><', '>\n<')
    ('><', '>\n<')
    ('><', '>\n<')

]

def process_all_folders(base_path):
    # This pattern tells Python: 
    # 1. Go to base_path
    # 2. Look into any folder starting with 'FINAL-'
    # 3. Find every file ending in '.xml'
    search_pattern = os.path.join(base_path, "FINAL-*", "*.xml")
    
    files_found = glob.glob(search_pattern)
    
    if not files_found:
        print(f"No XML files found matching pattern: {search_pattern}")
        return

    print(f"Found {len(files_found)} files. Starting replacements...")

    for file_path in files_found:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            for old, new in REPLACEMENTS:
                content = content.replace(old, new)

            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✔ Updated: {os.path.basename(file_path)}")
            else:
                print(f"– No changes needed: {os.path.basename(file_path)}")
        
        except Exception as e:
            print(f"✘ Error processing {file_path}: {e}")

# IMPORTANT: Set this to your parent "Output" folder
parent_folder = r'G:\My Drive\VaveTechnologies\CAR_XML\Feb\01_Sravanthi\Output'
process_all_folders(parent_folder)