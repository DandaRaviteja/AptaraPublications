"""
upload.py - Stage 3: IEEE XML Conversion Upload
Uses exact control names and searches dialogs for OK button
"""

import os
import logging
import time
import sys
from datetime import datetime
from pywinauto import Application, Desktop

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"upload_{timestamp}.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    logging.info(f"Logging initialized. Log file: {log_file}")
    return log_file

log_file = setup_logging()

# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    'EXE_PATH': r'E:\Haritha\01_IEEE_Tools_Guidelines\IEEE_Tools\IEEE_XML_Conversion_App_1006_21Jul2025\IEEE_XML_Conversion_App.exe',
    'TOOL_WINDOW_TITLE': 'IEEE_XML_Conversion_App',
    'BACKEND': 'uia',
}

BASE_PATH = r"G:\My Drive\VaveTechnologies\IEEE\February"

# ============================================================================
# FOLDER DISCOVERY
# ============================================================================

'''
def get_today_folder(base_path):
    today_str = datetime.now().strftime("%Y%m%d")
    today_folder = os.path.join(base_path
                                , today_str)
    if not os.path.exists(today_folder):
        logging.warning(f"Today's folder does not exist: {today_folder}")
        return None
    return today_folder
'''

def get_target_folder(base_path, target_date=None):
    """
    Finds the processing folder.
    :param base_path: The root directory (e.g., December 2025)
    :param target_date: A string like '20251225'. If None, uses today's date.
    """
    # 1. Handle default: If no date provided, use today
    if not target_date:
        target_date = datetime.now().strftime("%Y%m%d")
        logging.info(f"No date provided. Using default (today): {target_date}")
    
    # 2. Construct the full path
    target_folder = os.path.join(base_path, target_date)
    
    # 3. Validation
    if not os.path.exists(target_folder):
        logging.error(f"✗ Folder not found: {target_folder}")
        return None
        
    logging.info(f"✓ Target folder confirmed: {target_folder}")
    return target_folder


def find_leaf_folders(base_folder):
    """Find leaf folders"""
    leaf_folders = []
    
    for dirpath, dirnames, filenames in os.walk(base_folder):
        depth = dirpath.replace(base_folder, '').count(os.sep)
        has_files = len(filenames) > 0
        has_meta = 'Meta' in dirnames
        is_article_level = depth >= 2
        
        if (has_files or has_meta or is_article_level) and dirpath != base_folder:
            if os.path.basename(dirpath) != 'Meta':
                leaf_folders.append(dirpath)
    
    return leaf_folders

def pair_input_with_meta(leaf_folders):
    """Pair input folders with Meta folders"""
    pairs = []
    
    for folder in leaf_folders:
        meta_folder = os.path.join(folder, 'Meta')
        
        if os.path.exists(meta_folder) and os.path.isdir(meta_folder):
            pairs.append({
                'input_folder': folder,
                'meta_folder': meta_folder,
                'folder_name': os.path.basename(folder)
            })
    
    return pairs

# ============================================================================
# PHASE 1: OPEN APPLICATION
# ============================================================================

def open_ieee_tool():
    """Open the IEEE XML Conversion App"""
    logging.info("="*70)
    logging.info("PHASE 1: OPENING IEEE XML CONVERSION TOOL")
    logging.info("="*70)
    
    if not os.path.exists(CONFIG['EXE_PATH']):
        logging.error(f"✗ EXE not found: {CONFIG['EXE_PATH']}")
        return False
    
    logging.info(f"\n[1.1] Starting application...")
    
    try:
        app = Application(backend=CONFIG['BACKEND']).start(CONFIG['EXE_PATH'])
        logging.info("✓ Application started")
        time.sleep(4)
        return app
    except Exception as e:
        logging.error(f"✗ Failed to start application: {e}")
        return False

def find_tool_window():
    """Find the IEEE tool window"""
    logging.info(f"\n[1.2] Finding tool window...")

    desktop = Desktop(backend=CONFIG['BACKEND'])
    
    for window in desktop.windows():
        try:
            title = window.window_text()
            if 'IEEE' in title and 'Conversion' in title:
                logging.info(f"✓ Found window: '{title}'")
                time.sleep(1)
                return window
        except:
            pass
    
    logging.error(f"✗ Tool window not found")
    return False

# ============================================================================
# PHASE 2: CLICK CONVERSION TAB
# ============================================================================

def click_conversion_tab(window):
    """Click the Conversion tab"""
    logging.info("\n" + "="*70)
    logging.info("PHASE 2: CLICK CONVERSION TAB")
    logging.info("="*70)
    
    logging.info(f"\n[2.1] Looking for 'Conversion' tab...")
    
    try:
        all_descendants = list(window.descendants())
        tabs = [c for c in all_descendants if c.element_info.control_type == "TabItem"]
        logging.info(f"Found {len(tabs)} tab item(s)")
        
        conversion_tab = None
        
        for idx, tab in enumerate(tabs, 1):
            try:
                tab_text = tab.window_text()
                logging.info(f"  Tab {idx}: '{tab_text}'")
                
                if 'Conversion' in tab_text:
                    conversion_tab = tab
                    logging.info(f"✓ Found 'Conversion' tab: '{tab_text}'")
                    break
            except Exception as e:
                logging.debug(f"Tab {idx} error: {e}")
        
        if not conversion_tab:
            logging.error(f"✗ Conversion tab not found")
            return False
        
        logging.info("Clicking Conversion tab...")
        
        try:
            conversion_tab.click_input()
            logging.info("✓ Clicked Conversion tab")
            time.sleep(2)
            return True
        except Exception as e:
            logging.error(f"✗ Failed to click Conversion tab: {e}")
            return False
        
    except Exception as e:
        logging.error(f"✗ Error in click_conversion_tab: {e}")
        return False

# ============================================================================
# PHASE 3: INPUT FOLDER PATHS
# ============================================================================

def input_folder_paths(window, input_folder, meta_folder):
    """Enter input and meta folder paths"""
    logging.info("\n" + "="*70)
    logging.info("PHASE 3: INPUT FOLDER PATHS")
    logging.info("="*70)
    
    time.sleep(1)
    
    # Find edit fields
    logging.info(f"\n[3.1] Finding edit fields...")
    all_descendants = list(window.descendants())
    edit_fields = [c for c in all_descendants if c.element_info.control_type == "Edit"]
    
    logging.info(f"Found {len(edit_fields)} Edit field(s)")
    
    if len(edit_fields) < 2:
        logging.error(f"✗ Not enough edit fields found (need 2, found {len(edit_fields)})")
        return False
    
    # Sort by vertical position
    sorted_fields = sorted(edit_fields, key=lambda f: f.rectangle().top)
    input_field = sorted_fields[0]
    meta_field = sorted_fields[1]
    
    logging.info(f"✓ Using fields by position")
    
    # Enter Input Folder Path
    logging.info(f"\n[3.2] Entering Input Folder path...")
    logging.info(f"  Path: {input_folder}")
    
    try:
        input_field.set_focus()
        time.sleep(0.3)
        input_field.type_keys("^a", with_spaces=False)
        time.sleep(0.2)
        input_field.type_keys(input_folder, with_spaces=True)
        logging.info(f"✓ Entered input folder path")
        time.sleep(0.5)
    except Exception as e:
        logging.error(f"✗ Failed to enter input folder: {e}")
        return False
    
    # Enter Meta Folder Path
    logging.info(f"\n[3.3] Entering Meta Folder path...")
    logging.info(f"  Path: {meta_folder}")
    
    try:
        meta_field.set_focus()
        time.sleep(0.3)
        meta_field.type_keys("^a", with_spaces=False)
        time.sleep(0.2)
        meta_field.type_keys(meta_folder, with_spaces=True)
        logging.info(f"✓ Entered meta folder path")
        time.sleep(0.5)
    except Exception as e:
        logging.error(f"✗ Failed to enter meta folder: {e}")
        return False
    
    logging.info("✓ All paths entered successfully")
    return True

# ============================================================================
# PHASE 4: CLICK PROCESS AND WAIT FOR OK
# ============================================================================

def move_meta_to_ftxml(input_folder):
    """
    Move Meta folder from input_folder to Appout/UniqueID/ (alongside FTXML)
    Returns True if successful, False otherwise
    """
    logging.info("\n[4.3] Moving Meta folder to Appout/UniqueID...")
    
    try:
        # Find Meta folder in input folder
        meta_source = os.path.join(input_folder, 'Meta')
        
        if not os.path.exists(meta_source):
            logging.error(f"✗ Meta folder not found in input: {input_folder}")
            return False
        
        logging.info(f"✓ Found Meta folder in input: {meta_source}")
        
        # Find Appout folder
        appout_folder = os.path.join(input_folder, 'Appout')
        
        if not os.path.exists(appout_folder):
            logging.error(f"✗ Appout folder not found: {appout_folder}")
            return False
        
        logging.info(f"✓ Found Appout folder")
        
        # Find the unique ID subfolder (should be only one folder inside Appout)
        subfolders = [f for f in os.listdir(appout_folder) if os.path.isdir(os.path.join(appout_folder, f))]
        
        if not subfolders:
            logging.error(f"✗ No subfolder found in Appout")
            return False
        
        if len(subfolders) > 1:
            logging.warning(f"⚠ Multiple subfolders found in Appout, using first one: {subfolders[0]}")
        
        unique_id_folder = os.path.join(appout_folder, subfolders[0])
        logging.info(f"✓ Found unique ID folder: {subfolders[0]}")
        
        # Move Meta folder to unique ID folder (alongside FTXML)
        meta_destination = os.path.join(unique_id_folder, 'Meta')
        
        import shutil
        shutil.move(meta_source, meta_destination)
        
        logging.info(f"✓ Moved Meta folder to unique ID folder")
        logging.info(f"  From: {meta_source}")
        logging.info(f"  To:   {meta_destination}")
        
        return True
        
    except Exception as e:
        logging.error(f"✗ Error moving Meta folder: {e}")
        logging.error(f"  Exception details: {e}", exc_info=True)
        return False

def wait_for_and_click_ok_popup(timeout=10):
    """Monitor for OK button in dialog and click it"""
    logging.info("\n[4.2] Waiting for OK button popup...")
    
    desktop = Desktop(backend='uia')
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        elapsed = time.time() - start_time
        
        # Check ALL windows on desktop
        all_windows = list(desktop.windows())
        
        for window in all_windows:
            try:
                all_descendants = list(window.descendants())
                buttons = [c for c in all_descendants if c.element_info.control_type == "Button"]
                
                for button in buttons:
                    try:
                        button_text = button.window_text()
                        
                        # Check for OK button by exact name match
                        if hasattr(button.element_info, 'name') and button.element_info.name == 'OK':
                            logging.info(f"✓ OK button found by name! (after {elapsed:.1f}s)")
                            
                            try:
                                button.click()
                                logging.info("✓ Clicked OK button")
                                time.sleep(1)
                                return True
                            except:
                                try:
                                    button.click_input()
                                    logging.info("✓ Clicked OK button (click_input)")
                                    time.sleep(1)
                                    return True
                                except Exception as click_err:
                                    logging.error(f"✗ Failed to click OK: {click_err}")
                        
                        # Fallback: check by text
                        if button_text == 'OK':
                            logging.info(f"✓ OK button found by text! (after {elapsed:.1f}s)")
                            
                            try:
                                button.click()
                                logging.info("✓ Clicked OK button (text match)")
                                time.sleep(1)
                                return True
                            except:
                                try:
                                    button.click_input()
                                    logging.info("✓ Clicked OK button (text match - click_input)")
                                    time.sleep(1)
                                    return True
                                except Exception as click_err:
                                    logging.error(f"✗ Failed to click OK: {click_err}")
                    
                    except:
                        pass
                    
            except:
                pass
        
        time.sleep(0.2)
    
    logging.warning(f"⚠ No OK button found within {timeout}s")
    return False


def click_process_button(window, input_folder):
    """Click the Process button, wait for popup, and move Meta folder"""
    logging.info("\n" + "="*70)
    logging.info("PHASE 4: CLICK PROCESS BUTTON")
    logging.info("="*70)
    
    logging.info(f"\n[4.1] Looking for 'Process' button...")
    
    try:
        all_descendants = list(window.descendants())
        buttons = [c for c in all_descendants if c.element_info.control_type == "Button"]
        
        logging.info(f"Found {len(buttons)} button(s)")
        
        process_button = None
        
        # Find the Process button
        for button in buttons:
            try:
                # Check by exact name
                if hasattr(button.element_info, 'name') and button.element_info.name == 'Process':
                    process_button = button
                    logging.info(f"✓ Found 'Process' button")
                    break
                
                # Fallback: Check by text
                button_text = button.window_text()
                if button_text == 'Process':
                    process_button = button
                    logging.info(f"✓ Found 'Process' button")
                    break
            except:
                pass
        
        if not process_button:
            logging.error(f"✗ Process button not found")
            return False
        
        # Click using click_input
        logging.info("Clicking Process button...")
        process_button.click_input()
        logging.info("✓ Process button clicked")
        
        # Give process time to start
        time.sleep(1)
        
        # Wait for OK popup and click it
        ok_clicked = wait_for_and_click_ok_popup(timeout=10)
        
        if not ok_clicked:
            logging.error("✗ Failed to click OK button")
            return False
        
        # Wait a moment for file operations to complete
        time.sleep(2)
        
        # Move Meta folder to FTXML
        meta_moved = move_meta_to_ftxml(input_folder)
        
        if not meta_moved:
            logging.error("✗ Failed to move Meta folder")
            return False
        
        return True
        
    except Exception as e:
        logging.error(f"✗ Error in click_process_button: {e}")
        return False
    

# ============================================================================
# STATISTICS
# ============================================================================

class ProcessStats:
    def __init__(self):
        self.total = 0
        self.successful = 0
        self.failed = 0
        self.failed_items = []
    
    def success(self):
        self.successful += 1
    
    def fail(self, item_name):
        self.failed += 1
        self.failed_items.append(item_name)
    
    def summary(self):
        return {
            'total': self.total,
            'successful': self.successful,
            'failed': self.failed,
            'success_rate': f"{(self.successful/self.total*100):.1f}%" if self.total > 0 else "0%"
        }

stats = ProcessStats()

# ============================================================================
# MAIN PROCESSING
# ============================================================================

def process_batch(window, batch_pairs):
    """Process a batch of input/meta pairs"""
    
    for idx, pair in enumerate(batch_pairs, 1):
        logging.info("\n" + "█"*70)
        logging.info(f"PROCESSING ITEM {idx}/{len(batch_pairs)}")
        logging.info("█"*70)
        
        folder_name = pair['folder_name']
        input_folder = pair['input_folder']
        meta_folder = pair['meta_folder']
        
        logging.info(f"\nItem: {folder_name}")
        logging.info(f"Input: {input_folder}")
        logging.info(f"Meta:  {meta_folder}")
        
        try:
            # Input paths
            if not input_folder_paths(window, input_folder, meta_folder):
                logging.error(f"✗ Failed to input paths for {folder_name}")
                stats.fail(folder_name)
                continue
            
            # Click Process, wait for OK, and move Meta folder
            if not click_process_button(window, input_folder):
                logging.error(f"✗ Failed to process {folder_name}")
                stats.fail(folder_name)
                continue
            
            logging.info(f"✓ {folder_name} processed successfully")
            stats.success()
            
            # Wait before next item
            if idx < len(batch_pairs):
                logging.info(f"\nWaiting 2 seconds before next item...")
                time.sleep(2)
        
        except Exception as e:
            logging.error(f"✗ Error processing {folder_name}: {e}")
            stats.fail(folder_name)

def main(root_path: str = BASE_PATH):
    """Main workflow"""
    logging.info("\n" + "█"*70)
    logging.info("STAGE 3: IEEE XML CONVERSION UPLOAD")
    logging.info("█"*70 + "\n")
    
    # Get today's batch pairs
    print(f"\nDefault folder date: {datetime.now().strftime('%Y%m%d')}")
    user_input = input("Enter date (YYYYMMDD) or press ENTER for today: ").strip()

    today_folder = get_target_folder(root_path, user_input)
  #  if not today_folder:
  #      logging.error("Cannot find today's folder")
  #      return False
    
    leaf_folders = find_leaf_folders(today_folder)
    pairs = pair_input_with_meta(leaf_folders)
    
    if not pairs:
        logging.error("No pairs found to process")
        return False
    
    logging.info(f"Found {len(pairs)} item(s) to process\n")
    
    stats.total = len(pairs)
    
    # Open application
    app = open_ieee_tool()
    if not app:
        return False
    
    # Find window
    window = find_tool_window()
    if not window:
        return False
    
    # Click Conversion tab
    if not click_conversion_tab(window):
        return False
    
    # Process all pairs
    process_batch(window, pairs)
    
    # Summary
    summary = stats.summary()
    
    logging.info("\n" + "="*70)
    logging.info("PROCESSING COMPLETE - SUMMARY")
    logging.info("="*70)
    logging.info(f"Total Items: {summary['total']}")
    logging.info(f"Successful: {summary['successful']}")
    logging.info(f"Failed: {summary['failed']}")
    logging.info(f"Success Rate: {summary['success_rate']}")
    
    if stats.failed_items:
        logging.info(f"\nFailed Items:")
        for item in stats.failed_items:
            logging.info(f"  - {item}")
    
    logging.info(f"\nLog file: {log_file}")
    logging.info("="*70)
    
    return summary['failed'] == 0

def run_convert(root_path: str = r"G:\My Drive\Arczenrick\IEEE\2025\December"):
    # conversion and formatting logic
    print("Converting and formatting...")
    return main(root_path=root_path)

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logging.info("\n⚠ Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"\n✗ Critical error: {e}", exc_info=True)
        sys.exit(1)