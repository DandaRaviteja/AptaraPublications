import logging
import os
import sys
from datetime import datetime

# ============================================================================
# 1. LOGGING SETUP
# ============================================================================
def setup_logging():
    """Sets up a log file so we can see what the bot is doing."""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create a unique filename based on current time
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"bot_run_{timestamp}.log")
    
    # Configure logging to show in both Terminal and File
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logging.info("--- Logger Initialized ---")
    return log_file

# ============================================================================
# 2. PATH VALIDATION (The "Health Check")
# ============================================================================
def check_environment(excel_path, xcp_path):
    """Checks if the files you need actually exist before starting."""
    logging.info("Checking environment...")
    
    if not os.path.exists(excel_path):
        logging.error(f"Excel file NOT FOUND at: {excel_path}")
        return False
    
    if not os.path.exists(xcp_path):
        logging.error(f"XCP setup.exe NOT FOUND at: {xcp_path}")
        return False
        
    logging.info("✓ Environment looks good.")
    return True

# ============================================================================
# 3. MAIN ENGINE
# ============================================================================
def main():
    # Start the log
    setup_logging()
    
    # --- CONFIGURATION (Check these paths carefully!) ---
    # Use 'r' before the string to handle backslashes correctly
    excel_file = r"G:\My Drive\VaveTech-IEEE-JAN.xlsx"
    xcp_executable = r"C:\Path\To\Your\XCP\setup.exe" # UPDATE THIS TO ACTUAL PATH
    
    logging.info("Starting the bot...")

    # Run the health check
    if not check_environment(excel_file, xcp_executable):
        logging.critical("Bot stopped: Missing required files.")
        return

    # If it gets here, we are ready for the next step
    logging.info("Bot is ready for Phase 2: Excel Loading.")

if __name__ == "__main__":
    main()