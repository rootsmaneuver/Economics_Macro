#!/usr/bin/env python3
"""
Treasury Yield Curve Application Launcher
Author: Valentin Ivanov
Description: Unified launcher for Treasury yield curve analysis tools
"""

import sys
import os
import json
import subprocess
import importlib.util

def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = [
        'pandas', 'numpy', 'plotly', 'dash', 'fredapi'
    ]
    
    missing_packages = []
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing packages: {', '.join(missing_packages)}")
        print("Install with: pip install " + " ".join(missing_packages))
        return False
    else:
        print("✅ All required packages are installed")
        return True

def load_config():
    """Load configuration from config.json."""
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        fred_key = config.get('fred_api_key', '')
        if fred_key and fred_key != "YOUR_FRED_API_KEY_HERE":
            print("✅ FRED API key configured")
        else:
            print("⚠️  FRED API key not configured. Using sample data.")
        
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def run_web_app(port=8050, debug=False):
    """Launch the interactive web application."""
    try:
        from web_yield_curve_visualizer import WebYieldCurveVisualizer
        
        print("🚀 Starting Treasury Yield Curve Web Application...")
        print("=" * 60)
        
        # Load configuration
        config = load_config()
        if not config:
            return
        
        # Initialize visualizer with FRED API
        visualizer = WebYieldCurveVisualizer(
            fred_api_key=config.get('fred_api_key')
        )
        
        print("📊 Starting web server...")
        print(f"🌐 Starting server on http://localhost:{port}")
        print("📱 Open your browser and navigate to the URL above")
        print("⏹️  Press Ctrl+C to stop the server")
        
        # Run the web application
        visualizer.run_web_app(port=port, debug=debug)
        
    except Exception as e:
        print(f"❌ Error starting web application: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check internet connection")
        print("   2. Verify FRED API key is valid") 
        print("   3. Ensure all required packages are installed")

def run_demo():
    """Run demo mode to generate sample visualizations."""
    try:
        from web_yield_curve_visualizer import WebYieldCurveVisualizer
        
        print("🎬 Running Treasury Yield Curve Demo...")
        print("=" * 50)
        
        # Load configuration
        config = load_config()
        fred_api_key = config.get('fred_api_key') if config else None
        
        # Initialize visualizer
        visualizer = WebYieldCurveVisualizer(fred_api_key=fred_api_key)
        
        print("📊 Loading yield curve data...")
        data = visualizer.load_fred_data(start_date='2020-01-01')
        
        if data is not None and not data.empty:
            print("✅ Data loaded successfully!")
            print(f"📈 Data range: {data.index.min().strftime('%Y-%m-%d')} to {data.index.max().strftime('%Y-%m-%d')}")
            print(f"📊 Data points: {len(data)}")
            
            # Generate demo visualization
            print("🎨 Generating demo visualization...")
            fig = visualizer.create_animated_plot(data)
            
            # Export to HTML
            output_file = 'demo_yield_curve.html'
            fig.write_html(output_file)
            print(f"💾 Demo saved as: {output_file}")
            print("🌐 Open the HTML file in your browser to view the demo")
            
        else:
            print("❌ Failed to load data for demo")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def run_assessment():
    """Run the assessment tool."""
    try:
        from final_assessment import main as assessment_main
        assessment_main()
    except Exception as e:
        print(f"❌ Assessment failed: {e}")

def show_help():
    """Display help information."""
    help_text = """
🏛️  Treasury Yield Curve Application
=====================================

USAGE:
    python app.py [OPTION]

OPTIONS:
    --web           Launch interactive web application
    --demo          Generate demo visualization
    --assess        Run data quality assessment  
    --help, -h      Show this help message

INTERACTIVE MODE:
    python app.py   (no arguments for interactive menu)

EXAMPLES:
    python app.py --web        # Start web server on port 8050
    python app.py --demo       # Generate HTML demo file
    python app.py --assess     # Test FRED API and data quality

For more information, visit: https://github.com/your-repo
"""
    print(help_text)

def interactive_menu():
    """Display interactive menu for user selection."""
    while True:
        print("\n🏛️  Treasury Yield Curve Application")
        print("=" * 50)
        print("1. 🌐 Launch Web Application")
        print("2. 🎬 Generate Demo")
        print("3. 🔍 Run Assessment")
        print("4. ❓ Help")
        print("5. 🚪 Exit")
        
        try:
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                run_web_app()
                break
            elif choice == '2':
                run_demo()
            elif choice == '3':
                run_assessment()
            elif choice == '4':
                show_help()
            elif choice == '5':
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1-5.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main application entry point."""
    print("=" * 60)
    print("🏛️  US Treasury Yield Curve Visualization")
    print("   Real-Time Financial Data Analysis")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        return
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['--web', '-w']:
            run_web_app()
        elif arg in ['--demo', '-d']:
            run_demo()
        elif arg in ['--assess', '-a']:
            run_assessment()
        elif arg in ['--help', '-h']:
            show_help()
        else:
            print(f"❌ Unknown argument: {sys.argv[1]}")
            show_help()
    else:
        # No arguments - show interactive menu
        interactive_menu()

if __name__ == "__main__":
    main()
