"""
Export US Treasury Yield Data from FRED API to Excel
Author: Valentin Ivanov
Description: Exports comprehensive Treasury yield data to Excel with multiple sheets
"""

import pandas as pd
import numpy as np
from fredapi import Fred
import datetime as dt
import json
import os

def load_config():
    """Load API key from config file."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        return config.get('fred_api_key')
    except:
        return "df764c31adfa56ce0e019e7f5b89850a"  # Your API key

def export_treasury_data_to_excel(start_date='1990-01-01', filename='Treasury_Yield_Data.xlsx'):
    """Export Treasury yield data to Excel with multiple sheets."""
    
    print("🏛️ US Treasury Yield Data Export")
    print("=" * 50)
    
    # Initialize FRED API
    fred_api_key = load_config()
    fred = Fred(api_key=fred_api_key)
    
    # Define all Treasury maturities
    maturities = {
        '1_Month': {'series': 'DGS1MO', 'label': '1 Month Treasury'},
        '3_Month': {'series': 'DGS3MO', 'label': '3 Month Treasury'},
        '6_Month': {'series': 'DGS6MO', 'label': '6 Month Treasury'},
        '1_Year': {'series': 'DGS1', 'label': '1 Year Treasury'},
        '2_Year': {'series': 'DGS2', 'label': '2 Year Treasury'},
        '3_Year': {'series': 'DGS3', 'label': '3 Year Treasury'},
        '5_Year': {'series': 'DGS5', 'label': '5 Year Treasury'},
        '7_Year': {'series': 'DGS7', 'label': '7 Year Treasury'},
        '10_Year': {'series': 'DGS10', 'label': '10 Year Treasury'},
        '20_Year': {'series': 'DGS20', 'label': '20 Year Treasury'},
        '30_Year': {'series': 'DGS30', 'label': '30 Year Treasury'}
    }
    
    end_date = dt.datetime.now().strftime('%Y-%m-%d')
    all_data = {}
    summary_stats = {}
    
    print(f"📊 Fetching data from {start_date} to {end_date}")
    print("-" * 50)
    
    # Fetch data for each maturity
    for maturity, info in maturities.items():
        try:
            print(f"Fetching {info['label']} ({info['series']})...")
            series_data = fred.get_series(
                info['series'], 
                start=start_date, 
                end=end_date
            )
            
            if not series_data.empty:
                # Clean the data
                series_data = series_data.dropna()
                all_data[maturity] = series_data
                
                # Calculate summary statistics
                summary_stats[maturity] = {
                    'Series_ID': info['series'],
                    'Description': info['label'],
                    'Start_Date': series_data.index.min().strftime('%Y-%m-%d'),
                    'End_Date': series_data.index.max().strftime('%Y-%m-%d'),
                    'Data_Points': len(series_data),
                    'Current_Rate': series_data.iloc[-1] if len(series_data) > 0 else None,
                    'Average_Rate': series_data.mean(),
                    'Min_Rate': series_data.min(),
                    'Max_Rate': series_data.max(),
                    'Std_Dev': series_data.std()
                }
                
                print(f"✅ {info['label']}: {len(series_data)} data points, Current: {series_data.iloc[-1]:.2f}%")
            else:
                print(f"⚠️  No data available for {info['label']}")
                
        except Exception as e:
            print(f"❌ Error fetching {info['label']}: {str(e)}")
            continue
    
    if not all_data:
        print("❌ No data was successfully retrieved!")
        return
    
    print(f"\n📈 Creating Excel file: {filename}")
    print("-" * 50)
    
    # Create Excel file with multiple sheets
    with pd.ExcelWriter(filename, engine='openpyxl') as writer:
        
        # Sheet 1: All data combined
        combined_data = pd.DataFrame(all_data)
        combined_data.to_excel(writer, sheet_name='All_Treasury_Yields', index=True)
        print("✅ Sheet 1: All Treasury Yields (combined data)")
        
        # Sheet 2: Summary statistics
        summary_df = pd.DataFrame(summary_stats).T
        summary_df.to_excel(writer, sheet_name='Summary_Statistics', index=True)
        print("✅ Sheet 2: Summary Statistics")
        
        # Sheet 3: Monthly data (resampled)
        monthly_data = combined_data.resample('ME').last()
        monthly_data.to_excel(writer, sheet_name='Monthly_Data', index=True)
        print("✅ Sheet 3: Monthly Data")
        
        # Sheet 4: Recent data (last 2 years)
        recent_date = dt.datetime.now() - dt.timedelta(days=730)
        recent_data = combined_data[combined_data.index >= recent_date]
        recent_data.to_excel(writer, sheet_name='Recent_2_Years', index=True)
        print("✅ Sheet 4: Recent 2 Years")
        
        # Sheet 5: Individual sheets for each maturity
        for maturity, data in all_data.items():
            if len(data) > 0:
                sheet_name = maturity.replace('_', '')[:31]  # Excel sheet name limit
                data.to_excel(writer, sheet_name=sheet_name, index=True)
                print(f"✅ Sheet: {maturity}")
        
        # Sheet 6: Yield curve snapshots (current and historical)
        snapshot_dates = [
            dt.datetime.now().strftime('%Y-%m-%d'),
            '2020-01-01',
            '2010-01-01',
            '2000-01-01'
        ]
        
        yield_curves = {}
        for date_str in snapshot_dates:
            try:
                date_obj = pd.to_datetime(date_str)
                curve_data = {}
                for maturity, data in all_data.items():
                    if len(data) > 0:
                        # Find closest date
                        closest_date = data.index[data.index <= date_obj]
                        if len(closest_date) > 0:
                            curve_data[maturity] = data.loc[closest_date[-1]]
                
                if curve_data:
                    yield_curves[date_str] = curve_data
                    
            except Exception as e:
                print(f"⚠️  Could not create snapshot for {date_str}: {e}")
        
        if yield_curves:
            curves_df = pd.DataFrame(yield_curves)
            curves_df.to_excel(writer, sheet_name='Yield_Curve_Snapshots', index=True)
            print("✅ Sheet: Yield Curve Snapshots")
    
    print(f"\n🎉 Excel export completed successfully!")
    print(f"📁 File saved as: {filename}")
    print(f"📊 File size: {os.path.getsize(filename) / 1024 / 1024:.1f} MB")
    
    # Print summary
    print(f"\n📈 DATA SUMMARY")
    print("-" * 30)
    print(f"Date Range: {start_date} to {end_date}")
    print(f"Maturities: {len(all_data)} series")
    print(f"Total Data Points: {sum(len(data) for data in all_data.values())}")
    
    # Current yield curve
    print(f"\n📊 CURRENT YIELD CURVE")
    print("-" * 30)
    for maturity, data in all_data.items():
        if len(data) > 0:
            current_rate = data.iloc[-1]
            print(f"{maturity.replace('_', ' ')}: {current_rate:.2f}%")
    
    return filename

if __name__ == "__main__":
    # Export options
    print("🏛️ Treasury Yield Data Export Options")
    print("1. Full historical data (1990-present)")
    print("2. Recent data (2020-present)")
    print("3. Custom date range")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    if choice == "2":
        start_date = "2020-01-01"
        filename = "Treasury_Yields_Recent.xlsx"
    elif choice == "3":
        start_date = input("Enter start date (YYYY-MM-DD): ").strip()
        filename = f"Treasury_Yields_{start_date.replace('-', '_')}.xlsx"
    else:
        start_date = "1990-01-01"
        filename = "Treasury_Yields_Full_History.xlsx"
    
    try:
        export_treasury_data_to_excel(start_date=start_date, filename=filename)
    except Exception as e:
        print(f"❌ Export failed: {e}")