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
from pathlib import Path


# ============================================================================
# load employee article mapping
# ============================================================================

def load_employee_article_mapping(excel_path: str,sheet_name:str) -> dict[str, list[str]]:
    """
    Reads Excel and returns:
    {
        'Employee Name': ['article1', 'article2', ...]
    }
    """
    df = pd.read_excel(excel_path,sheet_name=sheet_name)

    # ---- Validation (important in real systems) ----
    required_columns = {"Employee_name", "Work_Id"}
    missing = required_columns - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns in Excel: {missing}")

    # ---- Cleanup ----
    df = df.dropna(subset=["Employee_name", "Work_Id"])
    df["Employee_name"] = df["Employee_name"].astype(str).str.strip()
    df["Work_Id"] = df["Work_Id"].astype(str).str.strip()

    # ---- Group ----
    employee_articles = (
        df.groupby("Employee_name")["Work_Id"]
        .apply(list)
        .to_dict()
    )

    return employee_articles

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

def get_download_path_with_date_and_associate(associate_name):
    """Get download path with today's date folder and associate subfolder"""
    #base_path = r'G:\My Drive\Arczenrick\IEEE\2025\December'
    base_path = r'C:\Aptara\Downloads'
    today_folder = datetime.now().strftime("%Y%m%d")  # 20251123
    
    # Create path: base/YYYYMMDD/AssociateName/
    full_path = os.path.join(base_path, today_folder, associate_name)
    
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
        'XCP_EXE': r'C:\Aptara\Tools\IEEE_Tools\download\setup.exe',
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
        return wait_for_completion(len(article_list), timeout=60)
        
    except Exception as e:
        logging.error(f"✗ Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return False

def wait_for_completion(article_count, timeout=60):
    """Wait for download completion dialog/prompt"""
    logging.info("\n" + "="*70)
    logging.info("WAITING FOR DOWNLOAD COMPLETION")
    logging.info("="*70)
    print("\n" + "="*70)
    print("⏳ WAITING FOR DOWNLOAD COMPLETION")
    print("="*70)
    
    logging.info(f"\nMonitoring for completion (timeout: {timeout}s / {timeout//60} minutes)")
    print(f"\n⏳ Monitoring for completion...")
    print(f"   Expecting {article_count} article(s) to download")
    print(f"   Maximum wait time: {timeout//60} minutes")
    print(f"   Checking every 5 seconds...\n")
    
    desktop = Desktop(backend='uia')
    start_time = time.time()
    check_interval = 5
    
    last_update = 0
    
    while (time.time() - start_time) < timeout:
        elapsed = int(time.time() - start_time)
    
        # Print status every 15 seconds
        if elapsed - last_update >= 15:
            remaining = timeout - elapsed
            print(f"   Still waiting... ({elapsed}s elapsed, {remaining}s remaining)")
            last_update = elapsed
        
        # Check all windows for success indicators
        for window in desktop.windows():
            try:
                title = window.window_text()
                
                try:
                    all_descendants = list(window.descendants())
                    texts = [c for c in all_descendants if c.element_info.control_type == "Text"]
                    
                    for text in texts:
                        try:
                            text_content = text.window_text().lower()
                            
                            success_keywords = [
                                'download complete',
                                'download completed',
                                'completed successfully',
                                'all downloads complete',
                                'processing complete',
                                'success',
                                'finished',
                                'done'
                            ]
                            
                            if any(keyword in text_content for keyword in success_keywords):
                                elapsed_time = int(time.time() - start_time)
                                logging.info(f"\n✓ Success indicator found after {elapsed_time}s!")
                                logging.info(f"  Message: '{text.window_text()}'")
                                print(f"\n✅ SUCCESS! Download completed after {elapsed_time}s ({elapsed_time//60}m {elapsed_time%60}s)")
                                print(f"   Message: '{text.window_text()}'")
                                
                                # Click OK/Close
                                buttons = [c for c in all_descendants if c.element_info.control_type == "Button"]
                                for button in buttons:
                                    try:
                                        btn_text = button.window_text()
                                        if btn_text in ['OK', 'Close', 'Done']:
                                            button.click()
                                            logging.info(f"✓ Clicked '{btn_text}' button")
                                            print(f"✅ Closed completion dialog")
                                            time.sleep(1)
                                            break
                                    except:
                                        pass
                                
                                return True
                                
                        except:
                            pass
                except:
                    pass
                    
            except:
                pass
        
        time.sleep(check_interval)
    
    # Timeout
    elapsed_time = int(time.time() - start_time)
    logging.warning(f"\n⚠ Timeout reached after {elapsed_time}s ({elapsed_time//60} minutes)")
    logging.warning(f"  No completion dialog detected")
    
    print(f"\n⚠️  Timeout reached after {elapsed_time//60} minutes")
    print(f"   No completion dialog detected")
    print(f"   Downloads may still be in progress")
    
    return False

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main automation workflow"""
    
    # Get interactive input    
    # logging.info("\n" + "█"*70)
    # logging.info("XCP TO POWERIZEC - BATCH DOWNLOAD")
    # logging.info("█"*70)
    # logging.info(f"\nDate: {today}")
    # logging.info(f"Associate: {associate_name}")
    # logging.info(f"Number of Articles: {len(article_list)}")
    # logging.info(f"Article IDs: {article_ids_string}")
    # logging.info(f"Download Path: {download_path}\n")
    excel_path=r"C:\Aptara\Aptara_Employee_workflow.xlsx"
    sheet_name='Employee_work'

    # Phase 1: Start XCP
    success = start_xcp_and_click()
    if not success:
        logging.error("✗ Phase 1 failed")
        print("\n❌ Phase 1 failed")
        return False
    employee_article_map = load_employee_article_mapping(excel_path,sheet_name)
    for associate_name, article_list in employee_article_map.items():
        article_ids_string = ",".join(article_list)

        download_path = get_download_path_with_date_and_associate(associate_name)
    
        try:
            
            # Wait for PowerIZEC
            powerizec_window = wait_for_powerizec(timeout=10)
            
            if not powerizec_window:
                logging.error("✗ PowerIZEC window not found")
                print("\n❌ PowerIZEC window not found")
                return False
            
            # Phase 2: Submit and wait
            completion_success = automate_powerizec(powerizec_window, article_ids_string, article_list, download_path)
            
            if not completion_success:
                logging.warning("⚠ Downloads may still be in progress")
                print("\n⚠️  Downloads may still be in progress")
            
            # Final summary
            print("\n" + "="*70)
            if completion_success:
                print("✅✅✅ ALL DOWNLOADS COMPLETED SUCCESSFULLY ✅✅✅")
            else:
                print("⚠️⚠️⚠️  DOWNLOAD STATUS UNCERTAIN ⚠️⚠️⚠️")
            print("="*70)
            print(f"\n📥 Requested {len(article_list)} article(s)")
            print(f"📋 Article IDs: {article_ids_string}")
            print(f"👤 Associate: {associate_name}")
            print(f"📁 Download Path: {download_path}")
            
            if completion_success:
                print(f"\n✅ All downloads completed successfully!")
            else:
                print(f"\n⚠️  Timeout reached - please verify downloads manually")
            
            print(f"📝 Log file: {log_file}")
            print("="*70 + "\n")
            
            logging.info("\n" + "="*70)
            if completion_success:
                logging.info("✓✓✓ ALL DOWNLOADS COMPLETED SUCCESSFULLY ✓✓✓")
            else:
                logging.info("⚠⚠⚠ DOWNLOAD STATUS UNCERTAIN ⚠⚠⚠")
            logging.info("="*70)
            logging.info(f"\n📥 Requested {len(article_list)} article(s)")
            logging.info(f"📋 Article IDs: {article_ids_string}")
            logging.info(f"👤 Associate: {associate_name}")
            logging.info(f"📁 Download Path: {download_path}")
            
            if completion_success:
                logging.info(f"\n✅ All downloads completed successfully!")
            else:
                logging.info(f"\n⚠️  Timeout reached")
            
            logging.info(f"📝 Log file: {log_file}")
            logging.info("="*70)
            
        except KeyboardInterrupt:
            logging.info("\n⚠ Interrupted by user")
            print("\n⚠️  Interrupted by user")
            return False
        except Exception as e:
            logging.error(f"\n✗ Critical error: {e}", exc_info=True)
            print(f"\n❌ Critical error: {e}")
            return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
