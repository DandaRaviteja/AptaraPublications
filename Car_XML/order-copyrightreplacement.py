import os
from lxml import etree

# --- CONFIGURATION ---
INPUT_BASE_PATH = r'E:\Haritha\01_Vave_Technologies\02_CAR_XML\Training\Input'
OUTPUT_BASE_PATH = r'E:\Haritha\01_Vave_Technologies\02_CAR_XML\Training\Output'

# Namespaces used in the BATCH-*.xml files
NS = {
    'ani': 'http://www.elsevier.com/xml/ani/ani',
    'ce': 'http://www.elsevier.com/xml/ani/common'
}

def update_car_xml_files():
    if not os.path.exists(INPUT_BASE_PATH):
        print(f"Error: Input path not found: {INPUT_BASE_PATH}")
        return

    for folder_name in os.listdir(INPUT_BASE_PATH):
        input_folder_path = os.path.join(INPUT_BASE_PATH, folder_name)
        output_folder_path = os.path.join(OUTPUT_BASE_PATH, folder_name)

        if os.path.isdir(input_folder_path):
            order_file = os.path.join(input_folder_path, 'order.xml')
            
            # Find the input BATCH xml to get the copyright
            input_batch_file = None
            for f in os.listdir(input_folder_path):
                if f.startswith("BATCH-") and f.endswith(".xml"):
                    input_batch_file = os.path.join(input_folder_path, f)
                    break
            
            if os.path.exists(order_file) and input_batch_file:
                print(f"Processing: {folder_name}")
                
                # 1. Extract IDs from order.xml
                data = extract_order_values(order_file)
                
                # 2. Extract Copyright from Input BATCH xml and convert © to &#x00A9;
                raw_copyright = extract_copyright_from_input(input_batch_file)
                if raw_copyright:
                    data['copyright'] = raw_copyright.replace('©', '&#x00A9;')
                else:
                    data['copyright'] = None
                
                # 3. Apply all changes to Output BATCH xml
                if os.path.exists(output_folder_path):
                    for file in os.listdir(output_folder_path):
                        if file.startswith("BATCH-") and file.endswith(".xml"):
                            batch_output_path = os.path.join(output_folder_path, file)
                            apply_updates_to_output(batch_output_path, data)

def extract_order_values(xml_path):
    """Parses order.xml for IDs."""
    tree = etree.parse(xml_path)
    return {
        'doi': tree.findtext(".//DOI"),
        'tpa_id': tree.findtext(".//tpa-id"),
        'ipui': tree.findtext(".//ipui"),
        'source_id': tree.findtext(".//source-id")
    }

def extract_copyright_from_input(xml_path):
    """Extracts copyright-statement text from the input BATCH xml."""
    try:
        parser = etree.XMLParser(recover=True)
        tree = etree.parse(xml_path, parser)
        # Looking for copyright-statement in the input file
        copyright_text = tree.findtext(".//copyright-statement")
        return copyright_text
    except:
        return None

def apply_updates_to_output(file_path, data):
    """Updates the Output BATCH xml file."""
    try:
        parser = etree.XMLParser(recover=True, remove_blank_text=False)
        tree = etree.parse(file_path, parser)
        root = tree.getroot()

        # Update ce:doi
        doi_tag = root.find(".//ce:doi", NS)
        if doi_tag is not None:
            doi_tag.text = data['doi']

        # Update IPUI
        ipui_tag = root.xpath(".//ani:itemid[@idtype='IPUI']", namespaces=NS)
        if ipui_tag:
            ipui_tag[0].text = data['ipui']

        # Update TPA-ID
        tpa_tag = root.xpath(".//ani:itemid[@idtype='TPA-ID']", namespaces=NS)
        if tpa_tag:
            tpa_tag[0].text = data['tpa_id']

        # Update source srcid
        source_tag = root.find(".//ani:source", NS)
        if source_tag is not None:
            source_tag.set('srcid', data['source_id'])

        # Update publishercopyright using extracted text (already contains &#x00A9;)
        copyright_tag = root.find(".//ani:publishercopyright", NS)
        if copyright_tag is not None and data['copyright']:
            # We use a custom method to write the entity value directly
            copyright_tag.text = data['copyright']

        # Write back to file. Note: lxml may escape '&' by default. 
        # If you need literal '&#x00A9;' in the final file, we handle that during write.
        xml_output = etree.tostring(tree, encoding='utf-8', xml_declaration=True).decode('utf-8')
        xml_output = xml_output.replace('&amp;#x00A9;', '&#x00A9;')
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(xml_output)
            
        print(f"  [Success] Updated {os.path.basename(file_path)}")

    except Exception as e:
        print(f"  [Error] Failed to update {file_path}: {e}")

if __name__ == "__main__":
    update_car_xml_files()