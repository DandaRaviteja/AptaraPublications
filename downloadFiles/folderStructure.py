import os
import calendar
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================
# The script will use this if you don't enter a custom path
DEFAULT_ROOT = r'G:\My Drive\Arczenrick\IEEE\2026\January'

def create_monthly_structure(associate_list, root_path=None):
    if not root_path:
        root_path = DEFAULT_ROOT

    # 1. Get current Year and Month
    now = datetime.now()
    year = now.year
    month = now.month
    
    # 2. Get number of days in the current month
    _, num_days = calendar.monthrange(year, month)

    print(f"\n📅 Creating structure for: {calendar.month_name[month]} {year}")
    print(f"📂 Root: {root_path}")
    print("-" * 60)

    # 3. Loop through every day of the month
    for day in range(1, num_days + 1):
        date_str = f"{year}{month:02d}{day:02d}"
        date_folder_path = os.path.join(root_path, date_str)
        
        created_count = 0
        exists_count = 0

        # 4. Process each Associate folder
        for associate in associate_list:
            associate = associate.strip()
            if not associate: continue
            
            full_path = os.path.join(date_folder_path, associate)
            
            try:
                if not os.path.exists(full_path):
                    os.makedirs(full_path)
                    created_count += 1
                else:
                    exists_count += 1
            except Exception as e:
                print(f"❌ Error creating {full_path}: {e}")
        
        # Feedback for the day
        status_msg = f"✅ {date_str}: "
        if created_count > 0:
            status_msg += f"Created {created_count} folders. "
        if exists_count > 0:
            status_msg += f"({exists_count} already existed)."
            
        print(status_msg)

# ============================================================================
# EXECUTION
# ============================================================================

if __name__ == "__main__":
    # Define your associates here
    associates_to_create = ["Haritha", "Sravanthi", "Swapna", "Jyothi", "Jithendra", "Navya", "Gowshiran"]

    # Optional: Root Path override
    print(f"Target Month Root: {DEFAULT_ROOT}")
    user_path = input("Press Enter to use default or paste a new Root Path: ").strip()
    final_root = user_path if user_path else DEFAULT_ROOT
    
    create_monthly_structure(associates_to_create, final_root)
    
    print("\n✨ Monthly folder creation complete!")