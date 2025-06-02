#!/usr/bin/env python3
"""
Enhanced Yield Curve Application Launcher with Real FRED Data
Author: Valentin Ivanov
Description: Launch the yield curve visualization app with real Treasury data from FRED
"""

import sys
import os
import json
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['pandas', 'numpy', 'matplotlib', 'plotly', 'dash', 'fredapi']
    missing = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing required packages: {', '.join(missing)}")
        print("Install them using: pip install " + " ".join(missing))
        return False
    
    print("✅ All required packages are installed")
    return True

def load_config():
    """Load configuration from config.json."""
    config_path = Path('config.json')
    if not config_path.exists():
        print("❌ config.json not found!")
        return None
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
          # Check if FRED API key is configured
        fred_key = config.get('fred_api_key', '')
        if fred_key and fred_key != "YOUR_FRED_API_KEY_HERE":
            print("✅ FRED API key found in config")
        else:
            print("⚠️  FRED API key not configured. Using sample data.")
        
        return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return None

def launch_web_app():
    """Launch the web-based Dash application."""
    try:
        from web_yield_curve_visualizer import WebYieldCurveVisualizer
        
        print("🚀 Starting web application...")
        
        # Load config to get API key
        config = load_config()
        fred_api_key = None
        if config:
            fred_api_key = config.get('data_sources', {}).get('fred_api_key')
        
        # Initialize visualizer
        viz = WebYieldCurveVisualizer(fred_api_key=fred_api_key)
        
        # Load data using config settings
        print("📊 Loading yield curve data...")
        viz.load_data_with_config()
        
        # Create and run the web app
        print("🌐 Creating web application...")
        app = viz.create_dash_app()
        
        # Get port from config or use default
        port = 8050
        if config and 'web_app' in config:
            port = config['web_app'].get('port', 8050)
        
        print(f"🎯 Starting server on http://localhost:{port}")
        print("📱 Open your browser and navigate to the URL above")
        print("⏹️  Press Ctrl+C to stop the server")
        
        app.run(debug=True, port=port, host='127.0.0.1')
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed.")
    except Exception as e:
        print(f"❌ Error starting web app: {e}")

def launch_desktop_app():
    """Launch the desktop matplotlib application."""
    try:
        from yield_curve_visualizer import YieldCurveVisualizer
        
        print("🖥️  Starting desktop application...")
        
        # Load config to get API key
        config = load_config()
        fred_api_key = None
        if config:
            fred_api_key = config.get('data_sources', {}).get('fred_api_key')
        
        # Initialize visualizer
        viz = YieldCurveVisualizer(fred_api_key=fred_api_key)
        
        # Load config settings
        viz.load_config()
        
        # Load data
        print("📊 Loading yield curve data...")
        viz.load_data()
        
        # Start interactive visualization
        print("🎨 Starting interactive visualization...")
        viz.create_interactive_plot()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required packages are installed.")
    except Exception as e:
        print(f"❌ Error starting desktop app: {e}")

def main():
    """Main launcher function."""
    print("=" * 60)
    print("🏛️  US Treasury Yield Curve Visualization")
    print("   Interactive Analysis with Real FRED Data")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Show menu
    print("\nChoose your preferred interface:")
    print("1. 🌐 Web Application (Recommended)")
    print("2. 🖥️  Desktop Application") 
    print("3. 🧪 Quick Demo")
    print("4. ❌ Exit")
    
    try:
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            launch_web_app()
        elif choice == '2':
            launch_desktop_app()
        elif choice == '3':
            print("🧪 Running quick demo...")
            os.system('python quick_demo.py')
        elif choice == '4':
            print("👋 Goodbye!")
            sys.exit(0)
        else:
            print("❌ Invalid choice. Please enter 1, 2, 3, or 4.")
            main()
            
    except KeyboardInterrupt:
        print("\n👋 Application interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
