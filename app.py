#!/usr/bin/env python3
"""
US Treasury Yield Curve Visualization Application
Main entry point for the yield curve visualization system

Features:
- Real-time Treasury data from FRED API
- Interactive web-based visualization
- Historical yield curve analysis
- Professional-grade charts and exports

Author: Valentin Ivanov
"""

import sys
import json
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = ['pandas', 'numpy', 'plotly', 'dash', 'fredapi']
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
        
        print("📊 Loading real Treasury yield data from FRED...")
        visualizer.load_data_with_config('config.json')
        
        print(f"🌐 Starting server on http://localhost:{port}")
        print("📱 Open your browser and navigate to the URL above")
        print("⏹️  Press Ctrl+C to stop the server")
        print("=" * 60)
        
        # Start the web application
        visualizer.run_web_app(debug=debug, port=port)
        
    except Exception as e:
        print(f"❌ Error starting web application: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check internet connection")
        print("   2. Verify FRED API key is valid")
        print("   3. Ensure all required packages are installed")

def run_assessment():
    """Run comprehensive assessment of the application."""
    try:
        from final_assessment import main as assessment
        assessment()
    except ImportError:
        print("❌ Assessment module not found")
    except Exception as e:
        print(f"❌ Error running assessment: {e}")

def create_demo():
    """Create a quick demonstration chart."""
    try:
        from web_yield_curve_visualizer import WebYieldCurveVisualizer
        
        print("🎨 Creating demonstration yield curve...")
        
        config = load_config()
        if not config:
            return
        
        visualizer = WebYieldCurveVisualizer(
            fred_api_key=config.get('fred_api_key')
        )
        
        # Load data and create demo
        visualizer.load_sample_data()
        demo_file = 'demo_yield_curve.html'
        visualizer.export_to_html(demo_file)
        print(f"✅ Demo chart created: {demo_file}")
        
    except Exception as e:
        print(f"❌ Error creating demo: {e}")

def main():
    """Main entry point with command line interface."""
    parser = argparse.ArgumentParser(
        description="US Treasury Yield Curve Visualization Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python app.py                    # Interactive mode
  python app.py --web             # Launch web application
  python app.py --demo            # Create demo chart
  python app.py --assess          # Run assessment
  python app.py --web --port 9000 # Custom port
        """
    )
    
    parser.add_argument('--web', action='store_true', 
                       help='Launch web application')
    parser.add_argument('--demo', action='store_true',
                       help='Create demonstration chart')
    parser.add_argument('--assess', action='store_true',
                       help='Run comprehensive assessment')
    parser.add_argument('--port', type=int, default=8050,
                       help='Port for web application (default: 8050)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Display header
    print("=" * 60)
    print("🏛️  US Treasury Yield Curve Visualization")
    print("   Real-Time Financial Data Analysis")
    print("=" * 60)
    
    # Check dependencies first
    if not check_dependencies():
        return 1
    
    # Handle command line arguments
    if args.web:
        run_web_app(port=args.port, debug=args.debug)
    elif args.demo:
        create_demo()
    elif args.assess:
        run_assessment()
    else:
        # Interactive mode
        print("\nChoose your preferred option:")
        print("1. 🌐 Launch Web Application (Recommended)")
        print("2. 🎨 Create Demo Chart")
        print("3. 📊 Run Assessment")
        print("4. ❌ Exit")
        
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                run_web_app(port=args.port, debug=args.debug)
            elif choice == '2':
                create_demo()
            elif choice == '3':
                run_assessment()
            elif choice == '4':
                print("👋 Goodbye!")
            else:
                print("❌ Invalid choice. Please select 1-4.")
                return 1
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            return 0
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
