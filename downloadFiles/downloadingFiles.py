
"""
XCP to PowerIZEC - Interactive Version with Associate Name
Prompts user for associate name and article IDs
"""

from pywinauto import Application, Desktop
import time
import logging
import sys
import os
from datetime import datetime
import pandas as pd
from typing import Dict, List

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"xcp_powerizec_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"Log file: {log_file}")
    return log_file

log_file = setup_logging()

# ============================================================================
# INTERACTIVE INPUT
# ============================================================================

def load_employee_articles_for_today(
    excel_path: str,
    sheet_name: str = "Employee_work",
    employee_col: str = "Employee_name",
    workid_col: str = "Work_Id",
    date_col: str | None = None
) -> Dict[str, List[str]]:
    """Read Excel and return mapping with DETAILED LOGGING"""
    print(f"\n📊 LOADING EXCEL: {excel_path}")
    print(f"📄 Sheet: {sheet_name}")
    print(f"👥 Employee col: '{employee_col}'")
    print(f"📄 Article col: '{workid_col}'")
    print(f"📅 Date col: {date_col or 'NONE'}")
    
    logging.info(f"Loading Excel: {excel_path} [{sheet_name}]")
    
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    print(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns")
    logging.info(f"Excel loaded: {len(df)} rows, {len(df.columns)} columns")
    
    print("📋 Columns found:", list(df.columns))
    
    # Validate columns
    required = {employee_col, workid_col}
    if date_col:
        required.add(date_col)
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    print(f"✅ All required columns found ✓")
    
    # Drop rows without required data
    subset_cols = [employee_col, workid_col] + ([date_col] if date_col else [])
    before_drop = len(df)
    df = df.dropna(subset=subset_cols)
    print(f"🧹 Dropped {before_drop - len(df)} empty rows → {len(df)} valid rows")
    
    # Normalize text
    df[employee_col] = df[employee_col].astype(str).str.strip()
    df[workid_col] = df[workid_col].astype(str).str.strip()
    
    # Date filter
    if date_col:
        today_str = datetime.now().strftime("%Y-%m-%d")
        print(f"📅 Filtering for today: '{today_str}' in '{date_col}'")
        before_filter = len(df)
        df[date_col] = df[date_col].astype(str)
        df = df[df[date_col].str.contains(today_str, na=False)]
        print(f"🔍 Date filter: {before_filter} → {len(df)} rows")
    
    if df.empty:
        print("❌ No valid data after filtering")
        logging.warning("No valid data after filtering")
        return {}
    
    # Group by employee
    print("\n🔗 GROUPING by employee...")
    mapping: Dict[str, List[str]] = (
        df.groupby(employee_col)[workid_col]
        .apply(list)
        .to_dict()
    )
    
    print(f"📊 Raw groups: {len(mapping)} employees")
    
    # Clean: keep only numeric article IDs
    cleaned: Dict[str, List[str]] = {}
    total_articles = 0
    
    print("\n🧹 CLEANING article IDs (numeric only):")
    for emp, ids in mapping.items():
        raw_count = len(ids)
        valid = [i.strip() for i in ids if str(i).strip().isdigit()]
        cleaned[emp] = valid
        total_articles += len(valid)
        
        print(f"  👤 {emp:12s} | Raw: {raw_count:2d} → Valid: {len(valid):2d} | IDs: {valid[:3]}{'...' if len(valid)>3 else ''}")
        logging.info(f"Employee '{emp}': {raw_count} raw → {len(valid)} valid articles")
    
    print(f"\n🎉 SUMMARY:")
    print(f"   👥 Employees: {len(cleaned)}")
    print(f"   📄 Total articles: {total_articles}")
    print(f"   📁 Excel path: {excel_path}")
    
    logging.info(f"Final: {len(cleaned)} employees, {total_articles} total articles")
    
    return cleaned
# After Excel loading, add this function:
def print_manual_commands(employee_article_map, root_path=None):
    """Print copy-paste ready commands with paths"""
    print("\n" + "="*120)
    print("📋 MANUAL COPY-PASTE COMMANDS (Associate → Articles → Path)")
    print("="*120)
    
    if root_path is None:
        root_path = r'G:\My Drive\Arczenrick\IEEE\2025\December'
    today_folder = datetime.now().strftime("%Y%m%d")
    
    for emp_name, article_ids in employee_article_map.items():
        ids_string = ','.join(article_ids)
        full_path = os.path.join(root_path, today_folder, emp_name)
        
        print(f"👤 {emp_name:<12} --> 📄 {ids_string:<40} --> 📁 {full_path}")
        print(f"python downloadingFiles.py --associate \"{emp_name}\" --articles \"{ids_string}\"")
        print("-" * 120)
    
    print("="*120)

def get_associate_name():
    """Prompt user for associate name"""
    print("\n" + "="*70)
    print("XCP TO POWERIZEC - BATCH DOWNLOAD")
    print("="*70)
    
    while True:
        associate_name = input("\nEnter Associate Name: ").strip()
        
        if not associate_name:
            print("❌ Associate name cannot be empty. Please try again.")
            continue
        
        # Validate - no special characters that break folder names
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in associate_name for char in invalid_chars):
            print(f"❌ Invalid characters found: {' '.join(invalid_chars)}")
            print("   Please use only letters, numbers, spaces, hyphens, or underscores.")
            continue
        
        logging.info(f"Associate name: {associate_name}")
        return associate_name

def get_article_ids():
    """Prompt user for article IDs"""
    while True:
        print("\nEnter Article IDs:")
        print("  (You can enter comma-separated or space-separated IDs)")
        print("  Example: 11238990,11239001,11239012")
        print("  Example: 11238990 11239001 11239012")
        
        article_input = input("\nArticle IDs: ").strip()
        
        if not article_input:
            print("❌ No article IDs provided. Please try again.")
            continue
        
        # Parse IDs (handle both comma and space separation)
        article_ids = []
        
        # First split by comma
        if ',' in article_input:
            article_ids = [id.strip() for id in article_input.split(',') if id.strip()]
        else:
            # Then split by space
            article_ids = [id.strip() for id in article_input.split() if id.strip()]
        
        # Validate IDs (must be numeric)
        valid_ids = []
        invalid_ids = []
        
        for article_id in article_ids:
            if article_id.isdigit():
                valid_ids.append(article_id)
            else:
                invalid_ids.append(article_id)
        
        if invalid_ids:
            print(f"\n⚠️  Skipping invalid IDs: {', '.join(invalid_ids)}")
        
        if not valid_ids:
            print("❌ No valid article IDs found. Please try again.")
            continue
        
        print(f"\n✅ Found {len(valid_ids)} valid article ID(s): {', '.join(valid_ids)}")
        
        # Confirm with user
        confirm = input("\nProceed with these IDs? (yes/no): ").strip().lower()
        
        if confirm in ['yes', 'y']:
            article_ids_string = ','.join(valid_ids)
            logging.info(f"Article IDs: {article_ids_string}")
            return article_ids_string, valid_ids
        else:
            print("Let's try again...")

# ============================================================================
# CONFIGURATION
# ============================================================================

def get_download_path_with_date_and_associate(associate_name, root_path: str = None):
    """Get download path with today's date folder and associate subfolder"""
    if root_path is None:
        root_path = r'G:\My Drive\Arczenrick\IEEE\2025\December'
    
    today_folder = datetime.now().strftime("%Y%m%d")  # 20251228
    
    # Create path: root_path/YYYYMMDD/AssociateName/
    full_path = os.path.join(root_path, today_folder, associate_name)
    
    # Create the folder if it doesn't exist
    try:
        os.makedirs(full_path, exist_ok=True)
        logging.info(f"✓ Created/verified folder structure:")
        logging.info(f"  Date folder: {today_folder}")
        logging.info(f"  Associate: {associate_name}")
        logging.info(f"  Full path: {full_path}")
        print(f"\n📁 Download folder created: {full_path}")
    except Exception as e:
        logging.error(f"✗ Could not create folder: {e}")
        print(f"\n❌ Error creating folder: {e}")
        sys.exit(1)
    
    return full_path

# ============================================================================
# PHASE 1: XCP
# ============================================================================

def start_xcp_and_click():
    """Start XCP and click the Start button"""
    logging.info("="*70)
    logging.info("PHASE 1: XCP ENVIRONMENT SELECTION")
    logging.info("="*70)
    print("\n" + "="*70)
    print("STARTING XCP APPLICATION")
    print("="*70)
    
    logging.info("\n[1.1] Starting XCP application...")
    print("\n[1/3] Starting XCP application...")
    
    CONFIG = {
        'XCP_EXE': r'E:\Haritha\01_IEEE_XML\IEEE_Tools\download\setup.exe',
        'XCP_WINDOW_TITLE': 'XCP Integrated System - Environment Selection',
        'XCP_BUTTON_TEXT': 'Start XCP Integrated System',
        'BACKEND': 'uia',
    }
    
    app = Application(backend=CONFIG['BACKEND']).start(CONFIG['XCP_EXE'])
    logging.info("✓ XCP started")
    print("✅ XCP started")
    time.sleep(3)
    
    logging.info("\n[1.2] Finding XCP window...")
    print("\n[2/3] Finding XCP window...")
    
    desktop = Desktop(backend=CONFIG['BACKEND'])
    
    xcp_window = None
    for window in desktop.windows():
        try:
            if CONFIG['XCP_WINDOW_TITLE'] in window.window_text():
                xcp_window = window
                logging.info(f"✓ Found: {window.window_text()}")
                print(f"✅ Found XCP window")
                break
        except:
            pass
    
    if not xcp_window:
        logging.error("✗ XCP window not found")
        print("❌ XCP window not found")
        return False
    
    logging.info("\n[1.3] Clicking 'Start XCP Integrated System' button...")
    print("\n[3/3] Clicking 'Start XCP Integrated System' button...")
    
    children = xcp_window.children()
    buttons = [c for c in children if c.element_info.control_type == "Button"]
    
    for button in buttons:
        button_text = button.window_text()
        if CONFIG['XCP_BUTTON_TEXT'] in button_text:
            logging.info(f"✓ Found button: '{button_text}'")
            button.click()
            logging.info("✓ Button clicked!")
            print("✅ Button clicked!")
            return True
    
    logging.error("✗ Button not found")
    print("❌ Button not found")
    return False

# ============================================================================
# PHASE 2: POWERIZEC
# ============================================================================

def wait_for_powerizec(timeout=10):
    """Wait for PowerIZEC window"""
    logging.info("\n" + "="*70)
    logging.info("PHASE 2: POWERIZEC DOWNLOADER")
    logging.info("="*70)
    print("\n" + "="*70)
    print("WAITING FOR POWERIZEC")
    print("="*70)
    
    logging.info(f"\n[2.1] Waiting for PowerIZEC window...")
    print("\nWaiting for PowerIZEC window to appear...")
    
    desktop = Desktop(backend='uia')
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        elapsed = time.time() - start_time
        
        for window in desktop.windows():
            try:
                title = window.window_text()
                
                if 'PowerIZEC' in title:
                    logging.info(f"✓ PowerIZEC window found! (after {elapsed:.1f}s)")
                    print(f"✅ PowerIZEC window found! (after {elapsed:.1f}s)")
                    time.sleep(1)
                    return window
            except:
                pass
        
        time.sleep(0.5)
    
    logging.error(f"✗ PowerIZEC window not found within {timeout}s")
    print(f"❌ PowerIZEC window not found within {timeout}s")
    return None

def automate_powerizec(window, article_ids_string, article_list, download_path):
    """Automate PowerIZEC with comma-separated article IDs"""
    
    logging.info(f"\n[2.2] Processing {len(article_list)} article(s)...")
    logging.info(f"Article IDs: {article_ids_string}")
    print(f"\nProcessing {len(article_list)} article(s)...")
    
    try:
        all_descendants = list(window.descendants())
        
        # Select IEEE Meta
        logging.info("\n[Step 1] Selecting 'IEEE Meta' radio button...")
        print("\n[Step 1/5] Selecting 'IEEE Meta'...")
        
        radios = [c for c in all_descendants if c.element_info.control_type == "RadioButton"]
        
        for radio in radios:
            try:
                if radio.window_text() == 'IEEE Meta':
                    radio.click_input()
                    logging.info("✓ IEEE Meta selected!")
                    print("✅ IEEE Meta selected!")
                    time.sleep(1)
                    break
            except:
                pass
        
        # Find Article Names field
        logging.info(f"\n[Step 2] Finding 'Article Names' field...")
        print("\n[Step 2/5] Finding 'Article Names' field...")
        
        article_field = None
        edit_fields = [c for c in all_descendants if c.element_info.control_type == "Edit"]
        
        for edit in edit_fields:
            try:
                if hasattr(edit.element_info, 'name') and edit.element_info.name == 'Article Names':
                    article_field = edit
                    logging.info(f"✓ Found 'Article Names' field")
                    print("✅ Found 'Article Names' field")
                    break
            except:
                pass
        
        if not article_field and edit_fields:
            article_field = edit_fields[0]
            print("✅ Using first edit field")
        
        if not article_field:
            logging.error("✗ Article Names field not found!")
            print("❌ Article Names field not found!")
            return False
        
        # Enter comma-separated Article IDs
        logging.info(f"\n[Step 3] Entering Article IDs...")
        print(f"\n[Step 3/5] Entering {len(article_list)} Article ID(s)...")
        
        input_success = False
        
        # Method 1: Try standard type_keys
        try:
            article_field.set_focus()
            time.sleep(0.5)
            article_field.type_keys("^a", with_spaces=False)
            time.sleep(0.3)
            article_field.type_keys(article_ids_string, with_spaces=False)
            
            logging.info(f"✓ Entered {len(article_list)} article ID(s) (method 1)")
            print(f"✅ Entered {len(article_list)} article ID(s)")
            input_success = True
            time.sleep(0.5)
            
        except Exception as e1:
            logging.debug(f"Method 1 (type_keys) failed: {e1}")
            
            # Method 2: Try set_text
            try:
                article_field.set_text('')
                time.sleep(0.2)
                article_field.set_text(article_ids_string)
                
                logging.info(f"✓ Entered {len(article_list)} article ID(s) (method 2)")
                print(f"✅ Entered {len(article_list)} article ID(s)")
                input_success = True
                time.sleep(0.5)
                
            except Exception as e2:
                logging.debug(f"Method 2 (set_text) failed: {e2}")
                
                # Method 3: Try wrapper_object
                try:
                    wrapper = article_field.wrapper_object()
                    wrapper.set_focus()
                    time.sleep(0.3)
                    wrapper.type_keys("^a", with_spaces=False)
                    time.sleep(0.2)
                    wrapper.type_keys(article_ids_string, with_spaces=False)
                    
                    logging.info(f"✓ Entered {len(article_list)} article ID(s) (method 3)")
                    print(f"✅ Entered {len(article_list)} article ID(s)")
                    input_success = True
                    time.sleep(0.5)
                    
                except Exception as e3:
                    logging.error(f"✗ All input methods failed")
                    logging.error(f"  Method 1: {e1}")
                    logging.error(f"  Method 2: {e2}")
                    logging.error(f"  Method 3: {e3}")
                    print(f"❌ Failed to enter article IDs - all methods failed")
        
        if not input_success:
            return False
        
        # Set Download Path
        logging.info(f"\n[Step 4] Setting Download Path...")
        print("\n[Step 4/5] Setting Download Path...")
        
        path_field = None
        for edit in edit_fields:
            try:
                if hasattr(edit.element_info, 'name') and edit.element_info.name == 'Download Path':
                    path_field = edit
                    break
            except:
                pass
        
        if not path_field and len(edit_fields) > 1:
            path_field = edit_fields[1]
        
        if path_field:
            try:
                path_field.set_focus()
                time.sleep(0.3)
                path_field.type_keys("^a", with_spaces=False)
                time.sleep(0.2)
                path_field.type_keys(download_path, with_spaces=True)
                logging.info(f"✓ Path set: {download_path}")
                print(f"✅ Path set")
                time.sleep(0.5)
            except Exception as e:
                logging.warning(f"⚠ Failed to set path: {e}")
                print(f"⚠️  Warning: Failed to set path: {e}")
        
        # Click Download button
        logging.info("\n[Step 5] Submitting download request...")
        print("\n[Step 5/5] Submitting download request...")
        
        buttons = [c for c in all_descendants if c.element_info.control_type == "Button"]
        
        submitted = False
        for button in buttons:
            try:
                button_text = button.window_text()
                if button_text in ['Download', 'Submit', 'Process', 'OK', 'Start']:
                    button.click()
                    logging.info(f"✓ Clicked '{button_text}' button")
                    print(f"✅ Clicked '{button_text}' button")
                    submitted = True
                    time.sleep(2)
                    break
            except:
                pass
        
        if not submitted:
            logging.info("⚠ No explicit submit button found - submission may be automatic")
            print("⚠️  No submit button found - assuming automatic submission")
            time.sleep(2)
        
        logging.info(f"✓ Download request submitted for {len(article_list)} article(s)")
        print(f"✅ Download request submitted for {len(article_list)} article(s)")
        print(f"⏳ Tool will now process all articles automatically...")
        
        # Wait for completion
        return wait_for_completion(len(article_list), timeout=120)
        
    except Exception as e:
        logging.error(f"✗ Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return False

def wait_for_completion(article_count, timeout=120):  # 15 minutes
    """Wait for download completion dialog/prompt - AUTO-CLICK OK"""
    logging.info("\n" + "="*70)
    logging.info("WAITING FOR DOWNLOAD COMPLETION POPUP")
    logging.info("="*70)
    print("\n" + "="*70)
    print("⏳ WAITING FOR DOWNLOAD COMPLETION POPUP")
    print("="*70)
    
    logging.info(f"Monitoring for popup (timeout: {timeout}s = {timeout//60}min)")
    print(f"⏳ Waiting for 'Download Complete' dialog...")
    print(f"  📦 Expecting {article_count} articles")
    print(f"  ⏱️  Max wait: {timeout//60} minutes")
    print(f"  🔍 Checking every 30 seconds")
    print()
    
    desktop = Desktop(backend='uia')
    start_time = time.time()
    check_interval = 5  # 30 seconds
    
    last_update = 0
    
    while (time.time() - start_time) < timeout:
        elapsed = int(time.time() - start_time)
        
        # Status update every 60s
        if elapsed - last_update >= 60:
            remaining = int(timeout - elapsed)
            print(f"⏳ [{elapsed//60}m{elapsed%60:02d}s] Still waiting... {remaining//60}m{remaining%60:02d}s left")
            last_update = elapsed
        
        # Check ALL windows for success text
        for window in desktop.windows():
            try:
                # Check window title first
                title_lower = window.window_text().lower()
                if any(keyword in title_lower for keyword in ['complete', 'success', 'done', 'finish']):
                    print(f"✅ POPUP FOUND IN TITLE: {window.window_text()}")
                    # Try to click OK in this window
                    try:
                        buttons = [c for c in window.descendants() if c.element_info.control_type == "Button"]
                        for btn in buttons:
                            btn_text = btn.window_text().upper()
                            if 'OK' in btn_text or 'CLOSE' in btn_text or 'DONE' in btn_text:
                                print(f"🔘 AUTO-CLICK: {btn.window_text()}")
                                btn.click()
                                time.sleep(2)
                                return True
                    except:
                        pass
                
                # Check all text elements
                try:
                    all_descendants = list(window.descendants())
                    texts = [c for c in all_descendants if c.element_info.control_type == "Text"]
                    
                    for text in texts:
                        try:
                            text_content = text.window_text().lower().strip()
                            
                            # EXPANDED success keywords
                            success_keywords = [
                                'download complete', 'download completed', 'downloads complete',
                                'completed successfully', 'completed', 
                                'all downloads complete', 'all complete',
                                'processing complete', 'process complete',
                                'success', 'successful', 'finished', 'done', 'complete'
                            ]
                            
                            if any(keyword in text_content for keyword in success_keywords):
                                elapsed_time = int(time.time() - start_time)
                                print(f"\n🎉 SUCCESS DETECTED after {elapsed_time//60}m{elapsed_time%60:02d}s!")
                                print(f"📄 Message: '{text.window_text()}'")
                                
                                # AUTO-CLICK ANY OK/CLOSE/DONE button in this window
                                buttons = [c for c in all_descendants if c.element_info.control_type == "Button"]
                                clicked = False
                                
                                for button in buttons:
                                    try:
                                        btn_text = button.window_text().upper().strip()
                                        if any(x in btn_text for x in ['OK', 'CLOSE', 'DONE', 'YES', 'FINISH']):
                                            print(f"🔘 AUTO-CLICKING: '{button.window_text()}'")
                                            button.click()
                                            time.sleep(2)
                                            clicked = True
                                            logging.info(f"✓ AUTO-CLICKED '{button.window_text()}'")
                                            print("✅ Button clicked - proceeding!")
                                            break
                                    except:
                                        continue
                                
                                if clicked or 'complete' in text_content:
                                    return True
                                
                        except:
                            continue
                except:
                    continue
                    
            except:
                continue
        
        time.sleep(check_interval)
    
    # Timeout
    elapsed_time = int(time.time() - start_time)
    print(f"\n⚠️  TIMEOUT: No popup after {elapsed_time//60}m{elapsed_time%60:02d}s")
    print("   Downloads may still be processing...")
    return False

# ============================================================================
# MAIN
# ============================================================================
def main(root_path: str = None, associate_name: str = None, article_ids_string: str = None, article_list: list = None):
    """Main automation workflow - supports both interactive and batch modes"""
    
    # BATCH MODE: Use Excel mapping if provided
    excel_path = r"C:\Users\raviteja\OneDrive\Documents\IEEE_December.xlsx"
    sheet_name = "Dec-2025"  
    if associate_name is None or article_ids_string is None:
        print("\n🔍 LOADING WORK FROM EXCEL...")
        employee_article_map = load_employee_articles_for_today(
            excel_path=excel_path,
            sheet_name=sheet_name,
            employee_col="Assigned TO",      # Column T
            workid_col="Article",            # Column R  
            date_col="Imported Date"         # Column S (optional)
        )
        print_manual_commands(employee_article_map)
        if not employee_article_map:
            print("❌ No work found in Excel")
            return False
            
        print(f"\n📋 Found {len(employee_article_map)} employees:")
        for emp, ids in employee_article_map.items():
            print(f"   👤 {emp}: {len(ids)} articles")
        
        # Process ALL employees from Excel
        total_success = 0
        for idx, (associate_name, article_list) in enumerate(employee_article_map.items(), 1):
            article_ids_string = ','.join(article_list)
            
            print(f"\n{'█'*70}")
            print(f"[{idx}/{len(employee_article_map)}] {associate_name}")
            print(f"{'█'*70}")
            
            # SINGLE download with 15min wait
            success = process_single_download(
                root_path=root_path,
                associate_name=associate_name,
                article_ids_string=article_ids_string,
                article_list=article_list
            )
            
            if success:
                total_success += 1
            else:
                print(f"⚠️  {associate_name}: Failed/Timed out")
            
            # Wait before next employee
            if idx < len(employee_article_map):
                print("\n⏳ Waiting 10s before next employee...")
                time.sleep(10)
        
        print(f"\n🎉 BATCH COMPLETE: {total_success}/{len(employee_article_map)}")
        return total_success == len(employee_article_map)
    
    # INTERACTIVE MODE: Single associate
    else:
        return process_single_download(
            root_path=root_path,
            associate_name=associate_name,
            article_ids_string=article_ids_string,
            article_list=article_list
        )


def process_single_download(root_path, associate_name, article_ids_string, article_list):
    """Process single associate download (XCP → PowerIZEC → wait 15min)"""
    
    # Create download path
    download_path = get_download_path_with_date_and_associate(associate_name, root_path)
    
    # Phase 1: Start XCP (if not already running)
    success = start_xcp_and_click()
    if not success:
        return False
    
    # Wait for PowerIZEC
    powerizec_window = wait_for_powerizec(timeout=15)
    if not powerizec_window:
        return False
    
    # Submit download + wait 15min for completion popup
    completion_success = automate_powerizec(
        powerizec_window, 
        article_ids_string, 
        article_list, 
        download_path
    )
    
    # Summary
    print("\n" + "="*70)
    print(f"👤 {associate_name}: {'✅ SUCCESS' if completion_success else '⚠️ TIMEOUT'}")
    print(f"📁 {download_path}")
    print("="*70)
    
    return completion_success


def run_download(root_path=None, associate_name=None, article_ids_string=None):
    """Batch-friendly entry point"""
    return main(root_path, associate_name, article_ids_string)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
