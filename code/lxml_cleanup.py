import os
import re
from lxml import etree as ET

# --- Configuration (Set your paths) ---
INPUT_DIR = r'C:\Users\raviteja\OneDrive\Desktop\IEEE_Articles\xml-input'
INPUT_FILE_NAME = '11273200_ft_input.xml'

INPUT_FILE_PATH = os.path.join(INPUT_DIR, INPUT_FILE_NAME)
CLEAN_FILE_PATH = os.path.join(INPUT_DIR, INPUT_FILE_NAME.replace('.xml', '_CLEANED_TAGS_ONLY.xml'))

ENCODING = 'utf-8'

def clean_xml_structural_fix_only(input_path, output_path):
    """
    Surgically fixes structural errors (tags) using LXML recovery 
    while guaranteeing preservation of the original file's header.
    NOTE: This script allows LXML to normalize character entities in the content.
    """
    print(f"Starting minimal structural tag fix on: {input_path}")
    
    with open(input_path, 'r', encoding=ENCODING) as f:
        full_content = f.read()

    # --- 1. Isolate Header/Body (RAW STRING PRESERVATION) ---
    # This protects the XML Declaration and DOCTYPE from being parsed or modified.
    root_match = re.search(r'(<\w+[^>]*>)', full_content)
    if not root_match:
        print("❌ Error: Could not find the XML root tag.")
        return
        
    root_start_index = root_match.start()
    header = full_content[:root_start_index]
    xml_body = full_content[root_start_index:]
    
    # --- 2. Structural Fix on the Body Only (Tags are corrected here) ---
    # The recover=True setting automatically fixes the missing tags (e.g., </p>).
    parser = ET.XMLParser(recover=True, encoding=ENCODING)
    
    try:
        root = ET.fromstring(xml_body.encode(ENCODING), parser)
        
        # Serialize the fixed root element back to string.
        # LXML's default behavior will normalize entities here (e.g., &#x00A9; -> ©).
        fixed_body_bytes = ET.tostring(
            root,
            pretty_print=True,
            xml_declaration=False, # CRITICAL: Do not output a new declaration
            encoding=ENCODING
        )
        
        fixed_body_string = fixed_body_bytes.decode(ENCODING)
        
        # --- 3. Reassembly and Write ---

        # Combine the untouched header string with the tag-fixed body string.
        final_content = header + fixed_body_string

        with open(output_path, 'w', encoding=ENCODING) as f:
            f.write(final_content)

        print(f"✅ Structural tag fix successful. Header preserved.")
        print(f"File saved to: {output_path}")

    except Exception as e:
        print(f"❌ Failed to process the file: {e}")

if __name__ == "__main__":
    clean_xml_structural_fix_only(INPUT_FILE_PATH, CLEAN_FILE_PATH)