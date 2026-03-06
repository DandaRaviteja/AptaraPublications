import os
import re

def update_xml_files(root_directory):
    # Regex patterns to extract values from order.xml
    patterns_order = {
        'source_id': r'<source-id>(.*?)</source-id>',
        'tpa_id': r'<tpa-id>(.*?)</tpa-id>',
        'ipui': r'<ipui>(.*?)</ipui>',
        'doi': r'<DOI>(.*?)</DOI>'
    }

    # Iterate through each folder (e.g., FINAL-20269009115932)
    for folder_name in os.listdir(root_directory):
        folder_path = os.path.join(root_directory, folder_name)
        
        if os.path.isdir(folder_path):
            order_xml_path = os.path.join(folder_path, 'order.xml')
            
            # 1. Extract values from order.xml
            if os.path.exists(order_xml_path):
                with open(order_xml_path, 'r', encoding='utf-8') as f:
                    order_content = f.read()
                
                data = {}
                for key, pattern in patterns_order.items():
                    match = re.search(pattern, order_content)
                    data[key] = match.group(1) if match else ""

                # 2. Find and update the article XML file (e.g., BATCH-*.xml)
                for file_name in os.listdir(folder_path):
                    if file_name.startswith("BATCH-") and file_name.endswith(".xml"):
                        file_path = os.path.join(folder_path, file_name)
                        
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()

                        # Update <ce:doi>
                        content = re.sub(r'<ce:doi>.*?</ce:doi>', f'<ce:doi>{data["doi"]}</ce:doi>', content)
                        
                        # Update <itemid idtype="IPUI">
                        content = re.sub(r'<itemid idtype="IPUI">.*?</itemid>', f'<itemid idtype="IPUI">{data["ipui"]}</itemid>', content)
                        
                        # Update <itemid idtype="TPA-ID">
                        content = re.sub(r'<itemid idtype="TPA-ID">.*?</itemid>', f'<itemid idtype="TPA-ID">{data["tpa_id"]}</itemid>', content)
                        
                        # Update <source srcid="">
                        content = re.sub(r'<source srcid=".*?">', f'<source srcid="{data["source_id"]}">', content)

                        # Write the updated content back to the file
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"Updated: {file_path}")

# Set your root path here
path = r'E:\Haritha\01_Vave_Technologies\02_CAR_XML\Training\Output'
update_xml_files(path)