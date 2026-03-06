#XCP to PowerIZEC - Interactive Version with Associate Name
#Prompts user for associate name and article IDs

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
    
    logging.info(f"System initialized. Log: {log_file}")
    return log_file

log_file = setup_logging()

# ============================================================================
# INTERACTIVE INPUT
# ============================================================================
def get_target_date():
    while True:
        print("\n" + "="*40)
        user_input = input("📅 Enter Date (YYYYMMDD) [Enter for Today]: ").strip()
        
        if not user_input:
            today = datetime.now().strftime("%Y%m%d")
            logging.info(f"Using default date: {today}")
            return today
        
        try:
            datetime.strptime(user_input, "%Y%m%d")
            logging.info(f"Target date set to: {user_input}")
            return user_input
        except ValueError:
            print(f"❌ Error: '{user_input}' is invalid. Please use YYYYMMDD.")

def load_employee_articles_for_date(excel_path, target_date, sheet_name="Sheet1", employee_col="Assigned TO", workid_col="Article", date_col="Assigned Date") -> Dict[str, List[str]]:
    logging.info(f"Reading data from: {excel_path}")
    
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    search_date = pd.to_datetime(target_date, format='%Y%m%d')

    df[employee_col] = df[employee_col].astype(str).str.strip()
    df[workid_col] = df[workid_col].astype(str).str.strip()
    df['Assigned Date'] = pd.to_datetime(df['Assigned Date'], errors='coerce')

    filtered_df = df[df['Assigned Date'].dt.date == search_date.date()].copy()

    if filtered_df.empty:
        logging.warning(f"No records found for date: {target_date}")
        return {}

    mapping = filtered_df.groupby(employee_col)[workid_col].apply(list).to_dict()
    
    cleaned_mapping = {}
    for emp, ids in mapping.items():
        valid_ids = [i for i in ids if i.isdigit()]
        if valid_ids:
            cleaned_mapping[emp] = valid_ids
            logging.info(f"Data Loaded | Associate: {emp:15} | Articles: {len(valid_ids)}")

    return cleaned_mapping

def print_manual_commands(employee_article_map, target_date, root_path):
    print("\n" + "═"*80)
    print(f"📋 BATCH SUMMARY: {target_date}")
    print("═"*80)
    
    for emp_name, article_ids in employee_article_map.items():
        full_path = os.path.join(root_path, target_date, emp_name)
        print(f"👤 Associate  : {emp_name}")
        print(f"📦 Articles   : {len(article_ids)} IDs found")
        print(f"📂 Destination: {full_path}")
        print("-" * 80)

def start_xcp_and_click():
    logging.info("PHASE 1: Initializing XCP Environment Selection")
    
    CONFIG = {
        'XCP_EXE': r'E:\Haritha\01_IEEE_Tools_Guidelines\IEEE_Tools\download\setup.exe',
        'XCP_WINDOW_TITLE': 'XCP Integrated System - Environment Selection',
        'XCP_BUTTON_TEXT': 'Start XCP Integrated System',
        'BACKEND': 'uia',
    }
    
    try:
        logging.info(f"Launching executable: {CONFIG['XCP_EXE']}")
        app = Application(backend=CONFIG['BACKEND']).start(CONFIG['XCP_EXE'])
        time.sleep(5)
    except Exception as e:
        logging.error(f"Execution failed: {e}")
        return False

    desktop = Desktop(backend=CONFIG['BACKEND'])
    xcp_window = None
    
    for _ in range(10):
        for window in desktop.windows():
            if CONFIG['XCP_WINDOW_TITLE'] in window.window_text():
                xcp_window = window
                logging.info(f"UI Located: {window.window_text()}")
                break
        if xcp_window: break
        time.sleep(1)

    if not xcp_window:
        logging.error("Timeout: XCP Selection window not found.")
        return False

    try:
        xcp_window.set_focus()
        children = xcp_window.children()
        buttons = [c for c in children if c.element_info.control_type == "Button"]
        
        for button in buttons:
            if CONFIG['XCP_BUTTON_TEXT'] in button.window_text():
                button.click()
                logging.info("Environment selected successfully.")
                return True
    except Exception as e:
        logging.error(f"Click interaction failed: {e}")
    
    return False

def process_sequential_downloads(powerizec_window, article_list, download_path):
    total = len(article_list)
    success_count = 0

    logging.info(f"Starting sequential processing for {total} articles.")
    
    for index, single_id in enumerate(article_list, 1):
        logging.info(f"[{index}/{total}] Processing ID: {single_id}")
        
        result = automate_powerizec(powerizec_window, single_id, [single_id], download_path)
        
        if not result:
            logging.error(f"🛑 Critical Failure: ID {single_id} failed or 'OK' not found. Terminating Batch.")
            sys.exit("Script terminated by user requirement: 'OK' button not found.")
            # You can choose to sys.exit() to stop everything, or return False to move to next associate
            return False
        '''        if result:
            success_count += 1
            logging.info(f"Completed ID: {single_id}")
        else:
            logging.warning(f"Failed ID: {single_id}")
            time.sleep(2)
        '''

    return success_count == total

def automate_powerizec(window_handle, article_ids_string, article_list, download_path):
    try:
        window = window_handle.wrapper_object()
    except:
        window = window_handle

    try:
        all_descendants = list(window.descendants())
        
        # Step 1: Radio Button
        radios = [c for c in all_descendants if c.element_info.control_type == "RadioButton"]
        for radio in radios:
            if radio.window_text() == 'IEEE Meta':
                radio.click_input()
                time.sleep(1)
                break
        
        # Step 2: Article Name Field
        article_field = None
        edit_fields = [c for c in all_descendants if c.element_info.control_type == "Edit"]
        for edit in edit_fields:
            if hasattr(edit.element_info, 'name') and edit.element_info.name == 'Article Names':
                article_field = edit
                break
        
        if not article_field and edit_fields:
            article_field = edit_fields[0]
        
        if not article_field:
            logging.error("Field mapping failed: 'Article Names' not found.")
            return False
        
        # Step 3: Enter IDs
        article_field.set_focus()
        article_field.type_keys("^a{BACKSPACE}", with_spaces=False)
        article_field.type_keys(article_ids_string, with_spaces=False)
        
        # Step 4: Path
        path_field = None
        for edit in edit_fields:
            if hasattr(edit.element_info, 'name') and edit.element_info.name == 'Download Path':
                path_field = edit
                break
        
        if path_field:
            path_field.set_focus()
            path_field.type_keys("^a{BACKSPACE}", with_spaces=False)
            path_field.type_keys(download_path, with_spaces=True)
        
        # Step 5: Download
        buttons = [c for c in all_descendants if c.element_info.control_type == "Button"]
        submitted = False
        for button in buttons:
            if button.window_text() in ['Download', 'Submit', 'Process', 'OK', 'Start']:
                button.click_input()
                submitted = True
                break
        
        if not submitted:
            window.type_keys("{ENTER}")
        
        return wait_for_completion(len(article_list), timeout=120)
        
    except Exception as e:
        logging.error(f"Automation Error: {e}")
        return False

def wait_for_completion(article_count, timeout=120):  # 15 minutes
    """Wait for download completion dialog/prompt - AUTO-CLICK OK"""
    #logging.info("\n" + "="*70)
    #logging.info("WAITING FOR DOWNLOAD COMPLETION POPUP")
    #logging.info("="*70)
    #print("\n" + "="*70)
    #print("⏳ WAITING FOR DOWNLOAD COMPLETION POPUP")
    #print("="*70)
    
    '''
    logging.info(f"Monitoring for popup (timeout: {timeout}s = {timeout//60}min)")
    print(f"⏳ Waiting for 'Download Complete' dialog...")
    print(f"  📦 Expecting {article_count} articles")
    print(f"  ⏱️  Max wait: {timeout//60} minutes")
    print(f"  🔍 Checking every 30 seconds")
    print()
    '''
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
                            if clicked:
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
    logging.info("Searching for PowerIZEC application window...")
    desktop = Desktop(backend='uia')
    start_time = time.time()
    
    while (time.time() - start_time) < timeout:
        for window in desktop.windows():
            try:
                if 'PowerIZEC' in window.window_text():
                    logging.info(f"PowerIZEC window found after {int(time.time()-start_time)}s")
                    return window
            except:
                pass
        time.sleep(1)
    
    logging.error(f"Timeout: PowerIZEC not found within {timeout}s")
    return None

if __name__ == "__main__":
    root_path = r'G:\My Drive\VaveTechnologies\IEEE\February'
    excel_path = r"C:\Users\raviteja\OneDrive\PublicationWork\Aptara\IEEE\downloadFile.xlsx"

    target_date = get_target_date()
    employee_work = load_employee_articles_for_date(excel_path, target_date)
    
    if not employee_work:
        logging.error(f"Execution stopped: No data for {target_date}")
        exit()

    print_manual_commands(employee_work, target_date, root_path)
    input("\nConfirm details above. Press ENTER to begin automation...")

    for associate_name, article_list in employee_work.items():
        logging.info(f"BEGINNING BATCH: {associate_name}")

        download_path = os.path.join(root_path, target_date, associate_name)
        os.makedirs(download_path, exist_ok=True)

        if start_xcp_and_click():
            powerizec_window = wait_for_powerizec(timeout=60)
            
            if powerizec_window:
                success = process_sequential_downloads(powerizec_window, article_list, download_path)
                logging.info(f"Cleaning up session for {associate_name}...")
                if not success:
                    logging.error(f"Batch for {associate_name} completed with errors. Check logs for details.")      
                try:
                    powerizec_window.close()
                    time.sleep(3)
                except:
                    os.system("taskkill /f /im setup.exe") 
            else:
                logging.error(f"Could not initiate PowerIZEC for {associate_name}")

        logging.info(f"Finished associate: {associate_name}")
        time.sleep(2)

    logging.info("ALL BATCHES COMPLETED SUCCESSFULLY.")