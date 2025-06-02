#!/usr/bin/env python3
"""
Real FRED Data Web Application
Launch the yield curve web app with live Treasury data
"""

from web_yield_curve_visualizer import WebYieldCurveVisualizer
import json

def main():
    """Launch web app with real FRED data."""
    print("🚀 Starting Yield Curve Web Application with Real FRED Data")
    print("=" * 65)
    
    # Load API key from config
    fred_api_key = "df764c31adfa56ce0e019e7f5b89850a"
    
    try:
        # Initialize visualizer with FRED API key
        print("📊 Initializing visualizer with FRED API...")
        viz = WebYieldCurveVisualizer(fred_api_key=fred_api_key)
        
        # Load real Treasury data (recent years for faster loading)
        print("📈 Loading real Treasury yield data from FRED...")
        viz.load_fred_data('2020-01-01', '2024-12-31')
        
        if viz.data is not None and not viz.data.empty:
            print(f"✅ Data loaded successfully!")
            print(f"   • {len(viz.data)} observations")
            print(f"   • {len(viz.data.columns)} maturities")
            print(f"   • Date range: {viz.data.index.min().strftime('%Y-%m-%d')} to {viz.data.index.max().strftime('%Y-%m-%d')}")
            
            # Show latest rates
            latest = viz.data.iloc[-1].dropna()
            print(f"\n📊 Latest Treasury Rates ({viz.data.index[-1].strftime('%Y-%m-%d')}):")
            for maturity, rate in latest.items():
                if maturity in viz.maturities:
                    print(f"   • {viz.maturities[maturity]['label']}: {rate:.2f}%")
            
            # Create and save demo visualizations
            print(f"\n🎨 Creating demonstration visualizations...")
            
            # 1. Current yield curve
            current_fig = viz.create_animated_plot()
            current_fig.write_html("real_current_yield_curve.html")
            print("✅ Current yield curve saved to: real_current_yield_curve.html")
            
            # 2. 3D surface plot
            surface_fig = viz.create_3d_surface()
            surface_fig.write_html("real_3d_yield_surface.html")
            print("✅ 3D yield surface saved to: real_3d_yield_surface.html")
            
            # 3. Heatmap
            heatmap_fig = viz.create_heatmap()
            heatmap_fig.write_html("real_yield_heatmap.html")
            print("✅ Yield heatmap saved to: real_yield_heatmap.html")
            
            print(f"\n🌐 Starting web application...")
            print(f"📱 The app will open at: http://localhost:8050")
            print(f"⏹️  Press Ctrl+C to stop the server")
            
            # Create and run Dash app
            app = viz.create_dash_app()
            app.run(debug=True, port=8050, host='127.0.0.1')
            
        else:
            print("❌ No data could be loaded from FRED API")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check internet connection")
        print("   2. Verify FRED API key is valid")
        print("   3. Ensure all required packages are installed")

if __name__ == "__main__":
    main()
