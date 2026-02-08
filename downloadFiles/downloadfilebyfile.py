
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
def get_target_date():
    """
    Prompts the user for a date in YYYYMMDD format.
    Defaults to today's date if input is empty.
    """
    while True:
        print("\n" + "="*30)
        user_input = input("Enter Date (YYYYMMDD) [or press Enter for Today]: ").strip()
        
        # Fallback to Today
        if not user_input:
            today = datetime.now().strftime("%Y%m%d")
            print(f"✅ Using Today's Date: {today}")
            return today
        
        # Validation Logic
        try:
            # Check if it's exactly 8 digits and a valid calendar date
            valid_date = datetime.strptime(user_input, "%Y%m%d")
            print(f"✅ Target Date Set: {user_input}")
            return user_input
        except ValueError:
            print(f"❌ Error: '{user_input}' is not a valid date. Please use YYYYMMDD format.")

def load_employee_articles_for_date(
    excel_path: str,
    target_date: str,  # Passed from our Step 1 input
    sheet_name: str = "Sheet1",
    employee_col: str = "Assigned TO",
    workid_col: str = "Article",
    date_col: str = "Assigned Date"
) -> Dict[str, List[str]]:
    """
    Reads Excel and returns a dictionary of {Employee: [ArticleID, ArticleID]}
    filtered by the specific target_date.
    """
    print(f"\n📊 LOADING EXCEL: {excel_path}")
    
    # 1. Load the file
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    search_date = pd.to_datetime(target_date, format='%Y%m%d')

    # 2. Basic Cleaning
    df[employee_col] = df[employee_col].astype(str).str.strip()
    df[workid_col] = df[workid_col].astype(str).str.strip()
    df[date_col] = df[date_col].astype(str).str.strip()
    df['Assigned Date'] = pd.to_datetime(df['Assigned Date'], errors='coerce')

    # 3. Filter by the CUSTOM date (YYYYMMDD)
    # Note: We check if target_date exists anywhere in the date column string
    print(f"📅 Filtering Excel for Date: '{target_date}'")
    #filtered_df = df[df[date_col].str.contains(target_date, na=False)].copy()
    filtered_df = df[df['Assigned Date'].dt.date == search_date.date()].copy()

    if filtered_df.empty:
        print(f"❌ No records found for date: {target_date}")
        return {}

    # 4. Group by Employee
    mapping = filtered_df.groupby(employee_col)[workid_col].apply(list).to_dict()
    
    # 5. Final Clean (Keep only numeric IDs)
    cleaned_mapping = {}
    for emp, ids in mapping.items():
        valid_ids = [i for i in ids if i.isdigit()]
        if valid_ids:
            cleaned_mapping[emp] = valid_ids
            print(f"✅ {emp:15} | Found {len(valid_ids)} articles")

    return cleaned_mapping

def print_manual_commands(employee_article_map, target_date, root_path):
    """Prints summary of work using the root_path from main"""
    print("\n" + "="*120)
    print(f"📋 WORK SUMMARY FOR: {target_date}")
    print("="*120)
    
    for emp_name, article_ids in employee_article_map.items():
        ids_string = ', '.join(article_ids)
        # Combines the root path from main with custom date and employee name
        full_path = os.path.join(root_path, target_date, emp_name)
        
        print(f"👤 Associate  : {emp_name:<15}")
        print(f"📄 Article IDs : {ids_string}")
        print(f"📁 Save Path   : {full_path}")
        print("-" * 120)
    
    print("="*120)


def start_xcp_and_click():
    """Start XCP and click the Start button"""
    print("\n" + "="*70)
    print("🚀 PHASE 1: STARTING XCP APPLICATION")
    print("="*70)
    
    CONFIG = {
        'XCP_EXE': r'E:\Haritha\01_IEEE_Tools_Guidelines\IEEE_Tools\download\setup.exe',
        'XCP_WINDOW_TITLE': 'XCP Integrated System - Environment Selection',
        'XCP_BUTTON_TEXT': 'Start XCP Integrated System',
        'BACKEND': 'uia',
    }
    
    # 1. Start the EXE
    print("[1/3] Launching setup.exe...")
    try:
        app = Application(backend=CONFIG['BACKEND']).start(CONFIG['XCP_EXE'])
        time.sleep(5)  # Increased slightly to ensure UI loads on slower systems
    except Exception as e:
        print(f"❌ Failed to launch EXE: {e}")
        return False

    # 2. Find the Window
    print("[2/3] Searching for Environment Selection window...")
    desktop = Desktop(backend=CONFIG['BACKEND'])
    xcp_window = None
    
    # Try finding the window for up to 10 seconds
    for _ in range(10):
        for window in desktop.windows():
            if CONFIG['XCP_WINDOW_TITLE'] in window.window_text():
                xcp_window = window
                print(f"✅ Found: {window.window_text()}")
                break
        if xcp_window: break
        time.sleep(1)

    if not xcp_window:
        print("❌ XCP window not found after timeout.")
        return False

    # 3. Click the Start Button
    print("[3/3] Clicking 'Start XCP Integrated System'...")
    try:
        # Bring to front before clicking
        xcp_window.set_focus()
        
        children = xcp_window.children()
        buttons = [c for c in children if c.element_info.control_type == "Button"]
        
        for button in buttons:
            if CONFIG['XCP_BUTTON_TEXT'] in button.window_text():
                button.click()
                print("✅ XCP Environment Selected!")
                return True
    except Exception as e:
        print(f"❌ Error clicking button: {e}")
    
    print("❌ Start button not found in window.")
    return False


def process_sequential_downloads(powerizec_window, article_list, download_path):
    """
    NEW WRAPPER: Loops through the article list and calls the 
    automation function for each individual ID.
    """
    total = len(article_list)
    success_count = 0

    print(f"\n🔄 STARTING SEQUENTIAL PROCESS: {total} Articles")
    
    for index, single_id in enumerate(article_list, 1):
        print(f"\n🚀 [{index}/{total}] Current Article: {single_id}")
        
        # We pass only the single ID to the automation function
        # We set a shorter timeout (e.g., 120s) because it's only one file
        result = automate_powerizec(
            powerizec_window, 
            single_id,       # Pass single ID as string
            [single_id],     # Pass as a list of one
            download_path
        )
        
        if result:
            success_count += 1
            print(f"✅ Success: {single_id} completed.")
        else:
            print(f"⚠️  Warning: {single_id} failed or timed out.")
            # Optional: Add a brief pause before the next attempt
            time.sleep(2)

    return success_count == total

def automate_powerizec(window_handle, article_ids_string, article_list, download_path):
    """Automate PowerIZEC with comma-separated article IDs"""
    
    # FIX: Ensure we are working with the Wrapper object to use .descendants()
    # If 'window_handle' is a Specification, this resolves it; if it's already a Wrapper, it stays one.
    try:
        window = window_handle.wrapper_object()
    except:
        window = window_handle

    logging.info(f"\n[2.2] Processing {len(article_list)} article(s)...")
    logging.info(f"Article IDs: {article_ids_string}")
    print(f"\nProcessing {len(article_list)} article(s)...")
    
    try:
        # Get all elements once to speed up searching
        all_descendants = list(window.descendants())
        
        # --- Step 1: Select IEEE Meta ---
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
        
        # --- Step 2: Find Article Names field ---
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
        
        # --- Step 3: Enter Article IDs (Multi-Method) ---
        logging.info(f"\n[Step 3] Entering Article IDs...")
        print(f"\n[Step 3/5] Entering {len(article_list)} Article ID(s)...")
        
        input_success = False
        # Method 1: standard type_keys
        try:
            article_field.set_focus()
            time.sleep(0.5)
            article_field.type_keys("^a{BACKSPACE}", with_spaces=False)
            time.sleep(0.3)
            article_field.type_keys(article_ids_string, with_spaces=False)
            input_success = True
        except Exception as e1:
            # Method 2: set_text
            try:
                article_field.set_text(article_ids_string)
                input_success = True
            except Exception as e2:
                logging.error(f"✗ Input failed: {e2}")

        if not input_success:
            return False
        
        print(f"✅ Entered {len(article_list)} article ID(s)")

        # --- Step 4: Set Download Path ---
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
                path_field.type_keys("^a{BACKSPACE}", with_spaces=False)
                time.sleep(0.2)
                path_field.type_keys(download_path, with_spaces=True)
                print(f"✅ Path set")
            except Exception as e:
                print(f"⚠️ Warning: Failed to set path: {e}")
        
        # --- Step 5: Click Download button ---
        logging.info("\n[Step 5] Submitting download request...")
        print("\n[Step 5/5] Submitting download request...")
        
        buttons = [c for c in all_descendants if c.element_info.control_type == "Button"]
        submitted = False
        for button in buttons:
            try:
                button_text = button.window_text()
                if button_text in ['Download', 'Submit', 'Process', 'OK', 'Start']:
                    button.click_input() # Use click_input for physical click
                    logging.info(f"✓ Clicked '{button_text}' button")
                    print(f"✅ Clicked '{button_text}' button")
                    submitted = True
                    break
            except:
                pass
        
        if not submitted:
            print("⚠️ No submit button found - trying Enter key")
            window.type_keys("{ENTER}")
        
        # Wait for completion using your provided wait function
        return wait_for_completion(len(article_list), timeout=120)
        
    except Exception as e:
        logging.error(f"✗ Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return False

def wait_for_completion(article_count, timeout=120):
    """Wait for download completion dialog/prompt - AUTO-CLICK OK"""
    logging.info("\n" + "="*70)
    logging.info("WAITING FOR DOWNLOAD COMPLETION POPUP")
    logging.info("="*70)
    print("\n" + "="*70)
    print("⏳ WAITING FOR DOWNLOAD COMPLETION POPUP")
    print("="*70)
    
    print(f"⏳ Waiting for 'Download Complete' dialog...")
    print(f" 📦 Expecting {article_count} articles")
    print(f" ⏱️ Max wait: {timeout//60} minutes")
    
    desktop = Desktop(backend='uia')
    start_time = time.time()
    check_interval = 3  # Reduced for faster detection
    last_update = 0
    
    # EXPANDED success keywords
    success_keywords = [
        'download complete', 'download completed', 'downloads complete',
        'completed successfully', 'completed', 'all downloads complete', 
        'all complete', 'processing complete', 'process complete',
        'success', 'successful', 'finished', 'done', 'complete'
    ]

    while (time.time() - start_time) < timeout:
        elapsed = int(time.time() - start_time)
        
        # Status update every 60s
        if elapsed - last_update >= 60:
            remaining = int(timeout - elapsed)
            print(f"⏳ [{elapsed//60}m{elapsed%60:02d}s] Still waiting... {remaining//60}m{remaining%60:02d}s left")
            last_update = elapsed
        
        # Check all visible windows
        for window in desktop.windows():
            try:
                window_text = window.window_text().lower()
                
                # Check title OR internal text elements
                is_match = any(keyword in window_text for keyword in success_keywords)
                
                if not is_match:
                    # Quick scan of internal text labels if title doesn't match
                    texts = [c.window_text().lower() for c in window.descendants(control_type="Text")]
                    is_match = any(any(k in t for k in success_keywords) for t in texts)

                if is_match:
                    print(f"\n🎉 SUCCESS DETECTED!")
                    logging.info(f"✓ Popup found: {window.window_text()}")
                    
                    # Find and click the confirmation button
                    buttons = window.descendants(control_type="Button")
                    for button in buttons:
                        btn_text = button.window_text().upper()
                        if any(x in btn_text for x in ['OK', 'CLOSE', 'DONE', 'YES', 'FINISH']):
                            print(f"🔘 AUTO-CLICKING: '{button.window_text()}'")
                            button.click_input() # Use physical click for reliability
                            time.sleep(1)
                            return True
                    
                    # If we found success text but no button, return True anyway
                    return True
            except:
                continue
        
        time.sleep(check_interval)
    
    print(f"\n⚠️ TIMEOUT: No popup after {int(time.time() - start_time)//60} minutes")
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


def wait_for_powerizec(timeout=60):
    """Wait for PowerIZEC window"""
    logging.info("\n" + "="*70)
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

if __name__ == "__main__":
    # 1. SETUP BASE PATHS
    root_path = r'G:\My Drive\VaveTechnologies\IEEE\February'
    excel_path = r"C:\Users\raviteja\OneDrive\PublicationWork\Aptara\IEEE\downloadFile.xlsx"

    # 2. GET TARGET DATE (Defaults to 20260206)
    target_date = get_target_date()
    
    # 3. LOAD DATA FROM EXCEL
    # Returns { 'Sravanthi': ['11379677', '11379571', ...], 'NextUser': [...] }
    employee_work = load_employee_articles_for_date(excel_path, target_date)
    
    if not employee_work:
        print(f"🛑 No work found for {target_date}. Exiting.")
        exit()

    # 4. SHOW SUMMARY & CONFIRM
    print_manual_commands(employee_work, target_date, root_path)
    input("\n📝 Summary looks correct? Press ENTER to start Automation (or Ctrl+C to cancel)...")

    # 5. MAIN AUTOMATION LOOP (Employee by Employee)
    for associate_name, article_list in employee_work.items():
        print(f"\n{'='*70}")
        print(f"👤 STARTING WORK FOR: {associate_name}")
        print(f"{'='*70}")

        # Define the specific folder for this associate
        # Example: .../20260206/Sravanthi/
        download_path = os.path.join(root_path, target_date, associate_name)
        os.makedirs(download_path, exist_ok=True)

        # Step A: Launch XCP Environment
        if start_xcp_and_click():
            powerizec_window = wait_for_powerizec(timeout=60)
            
            if powerizec_window:
                # Run one-by-one
                process_sequential_downloads(powerizec_window, article_list, download_path)
                
                print(f"✅ Finished {associate_name}. Closing application...")
                
                # --- NEW: CLOSE THE WINDOW TO PREVENT CRASH ON NEXT LOOP ---
                try:
                    powerizec_window.close()
                    # Wait for it to actually disappear
                    time.sleep(3)
                except:
                    # If it's already closed or stuck, try to kill the process
                    os.system("taskkill /f /im setup.exe") 
            else:
                print(f"❌ Could not find PowerIZEC window for {associate_name}.")

        print(f"\n🏁 Finished processing for {associate_name}. Moving to next associate...")
        time.sleep(2)

    print("\n🎉 ALL ASSOCIATES PROCESSED SUCCESSFULLY!")