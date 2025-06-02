"""
Update the Treasury Yield Curve Visualizer with fixes

This script copies the fixed visualizer over the original file
and creates a backup of the original file.
"""

import shutil
from pathlib import Path
import os

# Paths
original_file = Path('web_yield_curve_visualizer.py')
fixed_file = Path('web_yield_curve_visualizer_fixed.py')
backup_file = Path('web_yield_curve_visualizer.py.bak')

# Create a backup of the original file
if original_file.exists():
    shutil.copy2(original_file, backup_file)
    print(f"Created backup of original file: {backup_file}")

# Copy the fixed file over the original
if fixed_file.exists():
    shutil.copy2(fixed_file, original_file)
    print(f"Replaced {original_file} with fixed version")

print("Update complete. You can now run the application with 'python app.py'")

# Create a summary of changes
with open('UPDATE_SUMMARY.md', 'w') as f:
    f.write("""# Treasury Yield Curve Visualizer Updates

## Fixed Issues:
1. **Current Yield Values**: Updated sample data to use current market yield values (around 4.5% for 30yr Treasuries, not 10%)
2. **Animation Speed Slider**: Fixed to update in real-time while dragging
3. **Pause Button**: Fixed functionality to properly pause the animation
4. **Date Picker**: Improved with direct text input fields for easier date selection 
5. **Animation Jumping**: Fixed chronological ordering to prevent animation from jumping between dates
6. **Visual Indicators**: Added color-coded indicators showing whether real or sample data is being used
7. **Code Formatting**: Fixed indentation errors for proper execution

## Technical Improvements:
1. Improved error handling for FRED API connectivity
2. Added date validation for user input
3. Added proper sorting of time series data
4. Added comprehensive verification and diagnostics

The application will now correctly show either real FRED API data when available, 
or accurate sample data when the API is unavailable.
""")
    
print("Created UPDATE_SUMMARY.md with details of the changes")
