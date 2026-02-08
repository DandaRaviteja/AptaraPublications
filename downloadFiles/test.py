"""
XCP to PowerIZEC - Stable Automation Version
Fixes: UIAWrapper attribute error and integrates robust input methods.
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
    return log_file

# ============================================================================
# DATA HANDLING
# ============================================================================

def get_target_date():
    while True:
        print("\n" + "="*30)
        user_input = input("Enter Date (YYYYMMDD) [or press Enter for Today]: ").strip()
        if not user_input:
            return datetime.now().strftime("%Y%m%d")
        try:
            datetime.strptime(user_input, "%Y%m%d")
            return user_input
        except ValueError:
            print(f"❌ Error: '{user_input}' is not a valid date.")

def load_employee_articles_for_date(excel_path, target_date):
    print(f"\n📊 LOADING EXCEL: {excel_path}")
    try:
        df = pd.read_excel(excel_path)
        search_date = pd.to_datetime(target_date, format='%Y%m%d').date()
        
        df['Assigned Date'] = pd.to_datetime(df['Assigned Date'], errors='coerce')
        filtered_df = df[df['Assigned Date'].dt.date == search_date].copy()

        if filtered_df.empty:
            return {}

        mapping = filtered_df.groupby('Assigned TO')['Article'].apply(list).to_dict()
        cleaned_mapping = {emp: [str(i) for i in ids if str(i).isdigit()] 
                           for emp, ids in mapping.items() if ids}
        return cleaned_mapping
    except Exception as e:
        print(f"❌ Excel Error: {e}")
        return {}

# ============================================================================
# AUTOMATION ENGINE
# ============================================================================

def start_xcp_and_click():
    print("\n🚀 PHASE 1: STARTING XCP")
    config = {
        'exe': r'E:\Haritha\01_IEEE_Tools_Guidelines\IEEE_Tools\download\setup.exe',
        'title': 'XCP Integrated System - Environment Selection',
        'btn': 'Start XCP Integrated System'
    }
    try:
        Application(backend='uia').start(config['exe'])
        time.sleep(2)
        desktop = Desktop(backend='uia')
        window = desktop.window(title_re=f".*{config['title']}.*")
        window.wait('visible', timeout=20)
        window.set_focus()
        window.child_window(title=config['btn'], control_type="Button").click()
        return True
    except Exception as e:
        print(f"❌ XCP Launch Failed: {e}")
        return False

def wait_for_powerizec(timeout=60):
    print("⏳ Waiting for PowerIZEC main window...")
    start_time = time.time()
    while (time.time() - start_time) < timeout:
        try:
            # We connect to the app to return a Specification (prevents UIAWrapper error)
            app = Application(backend="uia").connect(title_re=".*PowerIZEC.*", timeout=2)
            window = app.window(title_re=".*PowerIZEC.*")
            if window.exists():
                print("✅ PowerIZEC window found!")
                return window
        except:
            time.sleep(2)
    return None

def automate_powerizec(window, article_id, download_path):
    """Automates a single article download using robust input methods"""
    try:
        window.set_focus()
        # Step 1: Select IEEE Meta
        window.child_window(title="IEEE Meta", control_type="RadioButton").click_input()
        
        # Step 2: Enter Article ID (Using your multi-method logic)
        article_field = window.child_window(name="Article Names", control_type="Edit")
        article_field.click_input()
        article_field.type_keys("^a{BACKSPACE}", with_spaces=False)
        time.sleep(0.3)
        article_field.type_keys(str(article_id), with_spaces=False)
        
        # Step 3: Set Download Path
        try:
            path_field = window.child_window(name="Download Path", control_type="Edit")
        except:
            path_field = window.child_window(control_type="Edit", found_index=1)
            
        path_field.click_input()
        path_field.type_keys("^a{BACKSPACE}", with_spaces=False)
        time.sleep(0.3)
        path_field.type_keys(download_path, with_spaces=True)
        
        # Step 4: Click Download
        btn_names = ['Download', 'Submit', 'Process', 'OK', 'Start']
        for name in btn_names:
            btn = window.child_window(title=name, control_type="Button")
            if btn.exists(timeout=0):
                btn.click_input()
                return wait_for_completion(1)
        
        # Fallback if no button found
        window.type_keys("{ENTER}")
        return wait_for_completion(1)
    except Exception as e:
        print(f"❌ Error on {article_id}: {e}")
        return False

def wait_for_completion(count, timeout=120):
    desktop = Desktop(backend='uia')
    start_time = time.time()
    keywords = ['complete', 'success', 'done', 'finish']
    
    while (time.time() - start_time) < timeout:
        for win in desktop.windows():
            title = win.window_text().lower()
            if any(k in title for k in keywords):
                # Try clicking OK/Close
                for btn in win.descendants(control_type="Button"):
                    if any(x in btn.window_text().upper() for x in ['OK', 'CLOSE', 'DONE']):
                        btn.click()
                        return True
        time.sleep(2)
    return False

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    root_path = r'G:\My Drive\Arczenrick\IEEE\2025\December'
    excel_path = r"C:\Users\raviteja\OneDrive\PublicationWork\Aptara\IEEE\downloadFile.xlsx"
    
    target_date = get_target_date()
    employee_work = load_employee_articles_for_date(excel_path, target_date)
    
    if not employee_work:
        print("🛑 No work found. Exiting.")
        sys.exit()

    for associate, articles in employee_work.items():
        print(f"\n👤 Associate: {associate} ({len(articles)} articles)")
        save_path = os.path.join(root_path, target_date, associate)
        os.makedirs(save_path, exist_ok=True)

        if start_xcp_and_click():
            p_win = wait_for_powerizec()
            if p_win:
                for idx, art_id in enumerate(articles, 1):
                    print(f"🚀 [{idx}/{len(articles)}] Downloading {art_id}...")
                    automate_powerizec(p_win, art_id, save_path)
                
                # Cleanup for next user
                try:
                    p_win.close()
                except:
                    os.system("taskkill /f /im setup.exe")
                time.sleep(3)

    print("\n🎉 ALL TASKS FINISHED!")