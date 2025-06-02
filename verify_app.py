"""
Verify Treasury Yield Curve Application
This script verifies that the application is working correctly and using the latest sample data.
"""

import pandas as pd
import json
import sys
from pathlib import Path

# Add diagnostic information to a log file
log_file = Path('app_verification.log')
with open(log_file, 'w') as f:
    f.write("Treasury Yield Curve Verification Log\n")
    f.write("=" * 50 + "\n\n")
    
    # Check that the fixed files exist
    f.write("Checking for fixed files:\n")
    fixed_app = Path('app_fixed.py')
    fixed_visualizer = Path('web_yield_curve_visualizer_fixed.py')
    
    if fixed_app.exists():
        f.write("✅ app_fixed.py exists\n")
    else:
        f.write("❌ app_fixed.py not found\n")
        
    if fixed_visualizer.exists():
        f.write("✅ web_yield_curve_visualizer_fixed.py exists\n")
    else:
        f.write("❌ web_yield_curve_visualizer_fixed.py not found\n")
    
    # Check the config file
    f.write("\nChecking config.json:\n")
    try:
        with open('config.json', 'r') as cfg:
            config = json.load(cfg)
            f.write(f"✅ config.json loaded successfully\n")
            
            # Check for API key
            api_key = config.get('fred_api_key', '')
            if api_key and api_key != "YOUR_FRED_API_KEY_HERE":
                f.write(f"✅ FRED API key found: {api_key[:5]}...\n")
            else:
                f.write("⚠️ No valid FRED API key found in config\n")
                
    except Exception as e:
        f.write(f"❌ Error loading config.json: {str(e)}\n")
    
    # Import and test the visualizer
    f.write("\nTesting the fixed visualizer:\n")
    try:
        sys.path.append('.')
        from web_yield_curve_visualizer_fixed import WebYieldCurveVisualizer
        
        # Create the visualizer
        f.write("Creating visualizer instance...\n")
        visualizer = WebYieldCurveVisualizer()
        
        # Load sample data
        f.write("Loading sample data...\n")
        data = visualizer.load_sample_data()
        
        # Check the loaded data
        if data is not None and not data.empty:
            f.write(f"✅ Successfully loaded sample data with {len(data)} observations\n")
            
            # Check the most recent data points
            f.write("\nMost recent sample data (last row):\n")
            last_row = data.iloc[-1]
            for maturity, value in last_row.items():
                f.write(f"{maturity}: {value:.2f}%\n")
                
            # Verify that 30-year Treasury is around 4.5% (not 10%)
            thirty_year = last_row.get('30yr', None)
            if thirty_year is not None:
                if 4.0 <= thirty_year <= 5.0:
                    f.write(f"\n✅ 30-year Treasury yield is {thirty_year:.2f}%, which is in the expected range (4.0%-5.0%)\n")
                else:
                    f.write(f"\n⚠️ 30-year Treasury yield is {thirty_year:.2f}%, which is outside the expected range\n")
            
        else:
            f.write("❌ Failed to load sample data\n")
            
    except Exception as e:
        f.write(f"❌ Error testing visualizer: {str(e)}\n")
    
    f.write("\nVerification complete\n")

print(f"Verification complete. Check {log_file} for results.")
