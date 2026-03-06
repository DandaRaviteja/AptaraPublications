import os
import glob

def rename_xml_to_axml(base_path):
    # This searches for all .xml files inside any folder starting with 'FINAL-'
    search_pattern = os.path.join(base_path, "FINAL-*", "*.xml")
    
    # Get a list of all matching files
    files_to_rename = glob.glob(search_pattern)
    
    if not files_to_rename:
        print(f"No .xml files found in folders starting with 'FINAL-' at:\n{base_path}")
        return

    print(f"Found {len(files_to_rename)} files to rename. Starting process...")

    count = 0
    for old_path in files_to_rename:
        try:
            # Get the file path without the extension
            base_name, _ = os.path.splitext(old_path)
            
            # Create the new path with .axml extension
            new_path = base_name + ".axml"
            
            # Perform the rename
            os.rename(old_path, new_path)
            
            print(f"✔ Renamed: {os.path.basename(old_path)} -> {os.path.basename(new_path)}")
            count += 1
            
        except Exception as e:
            print(f"✘ Error renaming {os.path.basename(old_path)}: {e}")

    print(f"\nFinished! Total files renamed: {count}")

# --- CONFIGURATION ---
# Replace this with your actual Output folder path
target_directory = r'E:\CarXmlOutput\Test'

# Run the function
rename_xml_to_axml(target_directory)