"""
FRED API test with log file output
"""
import sys
import traceback
import datetime

log_file = "fred_test_log.txt"

with open(log_file, "w") as f:
    try:
        f.write("FRED API Test Log - " + str(datetime.datetime.now()) + "\n")
        f.write("=" * 50 + "\n\n")
        
        f.write("Importing fredapi...\n")
        from fredapi import Fred
        f.write("FRED API package imported successfully\n")
        
        f.write("Loading API key...\n")
        api_key = "df764c31adfa56ce0e019e7f5b89850a"
        f.write(f"API key loaded: {api_key[:5]}...\n")
        
        # Initialize Fred client with the API key
        f.write("Initializing FRED client...\n")
        fred = Fred(api_key=api_key)
        f.write("FRED client initialized\n")
        
        # Try to fetch a simple series like GDP
        f.write("Attempting to fetch GDP data...\n")
        gdp = fred.get_series('GDP')
        
        if gdp is not None and not gdp.empty:
            f.write(f"Successfully fetched GDP data with {len(gdp)} observations\n")
            f.write(f"Latest GDP value: {gdp.iloc[-1]}\n")
            
            # Try to fetch Treasury yields
            f.write("\nFetching Treasury yield data...\n")
            t30y = fred.get_series('DGS30')
            if t30y is not None and not t30y.empty:
                f.write(f"Successfully fetched 30-Year Treasury yield with {len(t30y)} observations\n")
                f.write(f"Latest 30-Year Treasury yield: {t30y.iloc[-1]}%\n")
            else:
                f.write("No 30-Year Treasury yield data found\n")
        else:
            f.write("No GDP data found or data is empty\n")
            
    except Exception as e:
        f.write(f"Error: {str(e)}\n")
        f.write(f"Exception type: {type(e)}\n")
        f.write("Traceback:\n")
        traceback.print_exc(file=f)
    finally:
        f.write("\nTest completed\n")

print(f"Test completed. Results written to {log_file}")
