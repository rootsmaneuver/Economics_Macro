"""
Interactive Yield Curve Visualization Application
Author: Valentin Ivanov
Description: Visualizes US Treasury yield curves over time with interactive controls
Data Source: Federal Reserve Economic Data (FRED) API
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider, Button, CheckButtons
import requests
import datetime as dt
from typing import Dict, List, Tuple, Optional
import warnings
import json
try:
    from fredapi import Fred
    FREDAPI_AVAILABLE = True
except ImportError:
    FREDAPI_AVAILABLE = False
    print("Warning: fredapi not available. Using sample data only.")
warnings.filterwarnings('ignore')

class YieldCurveVisualizer:
    """Interactive yield curve visualization with time-lapse animation."""
    
    def __init__(self, fred_api_key=None):
        """Initialize the visualizer with default settings."""
        self.data = None
        self.filtered_data = None
        self.current_frame = 0
        self.animation = None
        self.is_playing = False
        self.fred_api_key = fred_api_key
        
        # Initialize FRED API client if available
        if FREDAPI_AVAILABLE and fred_api_key:
            self.fred = Fred(api_key=fred_api_key)
        else:
            self.fred = None
        
        # Yield curve maturities (in years) and their FRED series IDs
        self.maturities = {
            '1mo': {'years': 1/12, 'series': 'DGS1MO'},
            '3mo': {'years': 0.25, 'series': 'DGS3MO'},
            '6mo': {'years': 0.5, 'series': 'DGS6MO'},
            '1yr': {'years': 1, 'series': 'DGS1'},
            '2yr': {'years': 2, 'series': 'DGS2'},
            '3yr': {'years': 3, 'series': 'DGS3'},
            '5yr': {'years': 5, 'series': 'DGS5'},
            '7yr': {'years': 7, 'series': 'DGS7'},
            '10yr': {'years': 10, 'series': 'DGS10'},
            '20yr': {'years': 20, 'series': 'DGS20'},
            '30yr': {'years': 30, 'series': 'DGS30'}
        }
        
        # Default settings
        self.selected_maturities = list(self.maturities.keys())
        self.start_date = '1990-01-01'
        self.end_date = dt.datetime.now().strftime('%Y-%m-%d')
        self.animation_speed = 50  # milliseconds
        self.fade_trails = True
        self.max_trails = 20
          # Colors for different yield curves
        self.colors = plt.cm.viridis(np.linspace(0, 1, 11))
    
    def load_config(self, config_path='config.json'):
        """Load configuration and update API key if available."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Get FRED API key from config
            fred_api_key = config.get('data_sources', {}).get('fred_api_key')
            if fred_api_key and fred_api_key != "YOUR_FRED_API_KEY_HERE":
                self.fred_api_key = fred_api_key
                if FREDAPI_AVAILABLE:
                    self.fred = Fred(api_key=fred_api_key)
                    print("✓ FRED API key loaded from config")
                else:
                    print("⚠ FRED API not available")
            
            # Update default settings from config
            default_settings = config.get('default_settings', {})
            if 'start_date' in default_settings:
                self.start_date = default_settings['start_date']
            if 'animation_speed' in default_settings:
                self.animation_speed = default_settings['animation_speed']
            if 'max_trails' in default_settings:
                self.max_trails = default_settings['max_trails']
            if 'fade_trails' in default_settings:
                self.fade_trails = default_settings['fade_trails']
                
        except FileNotFoundError:
            print("Config file not found. Using default settings.")
        except Exception as e:
            print(f"Error loading config: {str(e)}. Using default settings.")
    
    def fetch_fred_data(self, series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch data from FRED API using fredapi library.
        Falls back to pandas_datareader if fredapi is not available.
        """
        # Try FRED API first if available
        if self.fred and FREDAPI_AVAILABLE:
            try:
                print(f"Fetching {series_id} from FRED API...")
                data = self.fred.get_series(series_id, start=start_date, end=end_date)
                if not data.empty:
                    return pd.DataFrame({series_id: data})
                else:
                    print(f"No data returned for {series_id}")
            except Exception as e:
                print(f"FRED API error for {series_id}: {e}")
        
        # Fallback to pandas_datareader
        try:
            print(f"Trying pandas_datareader for {series_id}...")
            import pandas_datareader.data as web
            data = web.get_data_fred(series_id, start_date, end_date)
            return data
        except Exception as e:
            print(f"pandas_datareader error for {series_id}: {e}")
            # Final fallback to simulated data
            print(f"Using sample data for {series_id}")
            return self._generate_sample_data(series_id, start_date, end_date)
    
    def _generate_sample_data(self, series_id: str, start_date: str, end_date: str) -> pd.DataFrame:
        """Generate sample yield curve data for demonstration purposes."""
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Base rates that roughly match historical patterns
        base_rates = {
            'DGS1MO': 1.5, 'DGS3MO': 2.0, 'DGS6MO': 2.2,
            'DGS1': 2.5, 'DGS2': 2.8, 'DGS3': 3.0,
            'DGS5': 3.2, 'DGS7': 3.4, 'DGS10': 3.5,
            'DGS20': 3.7, 'DGS30': 3.8
        }
        
        base_rate = base_rates.get(series_id, 3.0)
        
        # Add some realistic variation and trends
        np.random.seed(42)  # For reproducible sample data
        trend = np.linspace(0, -1, len(date_range))  # Slight downward trend
        noise = np.random.normal(0, 0.5, len(date_range))
        cycle = 2 * np.sin(np.linspace(0, 8*np.pi, len(date_range)))  # Business cycles
        
        rates = base_rate + trend + noise + cycle
        rates = np.maximum(rates, 0.1)  # Ensure non-negative rates
        
        return pd.DataFrame({series_id: rates}, index=date_range)
    
    def load_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Load yield curve data for all maturities."""
        if start_date:
            self.start_date = start_date
        if end_date:
            self.end_date = end_date
            
        print("Loading yield curve data...")
        all_data = {}
        
        for maturity, info in self.maturities.items():
            print(f"Fetching {maturity} data...")
            data = self.fetch_fred_data(info['series'], self.start_date, self.end_date)
            all_data[maturity] = data.iloc[:, 0]  # First column
        
        # Combine all series into a single DataFrame
        self.data = pd.DataFrame(all_data)
          # Forward fill missing values and drop rows with all NaN
        self.data = self.data.fillna(method='ffill').dropna(how='all')
        
        # Sample data monthly for better animation performance
        self.data = self.data.resample('ME').last()
        
        print(f"Data loaded: {len(self.data)} time periods from {self.data.index[0]} to {self.data.index[-1]}")
        self.filter_data()
    
    def filter_data(self):
        """Filter data based on selected maturities."""
        self.filtered_data = self.data[self.selected_maturities].copy()
    
    def setup_plot(self):
        """Setup the matplotlib figure and axes with controls."""
        # Create figure with subplots for main plot and controls
        self.fig = plt.figure(figsize=(16, 10))
        
        # Main yield curve plot
        self.ax_main = plt.subplot2grid((4, 4), (0, 0), colspan=3, rowspan=3)
        self.ax_main.set_xlabel('Maturity (Years)', fontsize=12)
        self.ax_main.set_ylabel('Yield (%)', fontsize=12)
        self.ax_main.set_title('US Treasury Yield Curve Animation', fontsize=14, fontweight='bold')
        self.ax_main.grid(True, alpha=0.3)
        
        # Set up x-axis (maturities in years)
        self.maturity_years = [self.maturities[m]['years'] for m in self.selected_maturities]
        self.ax_main.set_xlim(0, max(self.maturity_years) * 1.1)
        
        # Y-axis will be set based on data range
        y_min = self.filtered_data.min().min() - 0.5
        y_max = self.filtered_data.max().max() + 0.5
        self.ax_main.set_ylim(y_min, y_max)
        
        # Initialize empty line for current yield curve
        self.line_current, = self.ax_main.plot([], [], 'o-', linewidth=3, 
                                              markersize=8, color='red', 
                                              label='Current', zorder=10)
        
        # Initialize trail lines
        self.trail_lines = []
        for i in range(self.max_trails):
            alpha = 0.1 + 0.4 * (i / self.max_trails)
            line, = self.ax_main.plot([], [], 'o-', linewidth=1, 
                                     alpha=alpha, color='blue', zorder=1)
            self.trail_lines.append(line)
        
        # Date display
        self.date_text = self.ax_main.text(0.02, 0.98, '', transform=self.ax_main.transAxes,
                                          fontsize=14, fontweight='bold', 
                                          verticalalignment='top',
                                          bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # Setup control panels
        self.setup_controls()
        
        plt.tight_layout()
    
    def setup_controls(self):
        """Setup interactive controls."""
        # Time slider
        ax_time = plt.subplot2grid((4, 4), (3, 0), colspan=3)
        self.slider_time = Slider(ax_time, 'Time', 0, len(self.filtered_data)-1, 
                                 valinit=0, valfmt='%d')
        self.slider_time.on_changed(self.update_time_slider)
        
        # Control buttons
        ax_play = plt.subplot2grid((4, 4), (0, 3))
        self.btn_play = Button(ax_play, 'Play/Pause')
        self.btn_play.on_clicked(self.toggle_animation)
        
        ax_reset = plt.subplot2grid((4, 4), (1, 3))
        self.btn_reset = Button(ax_reset, 'Reset')
        self.btn_reset.on_clicked(self.reset_animation)
        
        # Speed control
        ax_speed = plt.subplot2grid((4, 4), (2, 3))
        self.slider_speed = Slider(ax_speed, 'Speed', 10, 200, 
                                  valinit=self.animation_speed, valfmt='%d ms')
        self.slider_speed.on_changed(self.update_speed)
    
    def update_time_slider(self, val):
        """Update plot when time slider changes."""
        self.current_frame = int(self.slider_time.val)
        self.update_plot(self.current_frame)
        self.fig.canvas.draw()
    
    def update_speed(self, val):
        """Update animation speed."""
        self.animation_speed = int(self.slider_speed.val)
        if self.animation:
            self.animation.event_source.interval = self.animation_speed
    
    def toggle_animation(self, event):
        """Start or stop the animation."""
        if self.is_playing:
            self.animation.pause()
            self.is_playing = False
        else:
            if self.animation is None:
                self.start_animation()
            else:
                self.animation.resume()
            self.is_playing = True
    
    def reset_animation(self, event):
        """Reset animation to the beginning."""
        self.current_frame = 0
        self.slider_time.set_val(0)
        if self.animation:
            self.animation.pause()
            self.is_playing = False
        self.update_plot(0)
        self.fig.canvas.draw()
    
    def update_plot(self, frame):
        """Update the plot for a given frame."""
        if frame >= len(self.filtered_data):
            return
        
        current_date = self.filtered_data.index[frame]
        current_yields = self.filtered_data.iloc[frame].values
        
        # Update current yield curve
        self.line_current.set_data(self.maturity_years, current_yields)
        
        # Update trails if enabled
        if self.fade_trails:
            trail_start = max(0, frame - self.max_trails)
            trail_frames = range(trail_start, frame)
            
            for i, trail_frame in enumerate(trail_frames):
                if i < len(self.trail_lines):
                    trail_yields = self.filtered_data.iloc[trail_frame].values
                    self.trail_lines[i].set_data(self.maturity_years, trail_yields)
            
            # Hide unused trail lines
            for i in range(len(trail_frames), len(self.trail_lines)):
                self.trail_lines[i].set_data([], [])
        
        # Update date display
        self.date_text.set_text(f"Date: {current_date.strftime('%Y-%m-%d')}")
        
        # Update slider
        self.slider_time.set_val(frame)
        
        return [self.line_current] + self.trail_lines + [self.date_text]
    
    def animate(self, frame):
        """Animation function."""
        self.current_frame = frame % len(self.filtered_data)
        return self.update_plot(self.current_frame)
    
    def start_animation(self):
        """Start the animation."""
        self.animation = animation.FuncAnimation(
            self.fig, self.animate, frames=len(self.filtered_data),
            interval=self.animation_speed, blit=False, repeat=True
        )
        self.is_playing = True
    
    def run(self, start_date: Optional[str] = None, end_date: Optional[str] = None):
        """Run the interactive visualization."""
        # Load data
        self.load_data(start_date, end_date)
        
        # Setup plot
        self.setup_plot()
        
        # Initial plot
        self.update_plot(0)
        
        # Show the plot
        plt.show()

# Utility functions for extending the application
def create_yield_curve_analysis():
    """Create additional analysis tools for yield curves."""
    pass

def export_animation(visualizer, filename='yield_curve_animation.gif', fps=10):
    """Export the animation as a GIF file."""
    if visualizer.animation:
        print(f"Exporting animation to {filename}...")
        visualizer.animation.save(filename, writer='pillow', fps=fps)
        print("Export complete!")

# Main execution
if __name__ == "__main__":
    # Create and run the visualizer
    visualizer = YieldCurveVisualizer()
    
    # You can customize the date range here
    start_date = '1990-01-01'  # Adjust as needed
    end_date = None  # Will use current date
    
    visualizer.run(start_date=start_date, end_date=end_date)
