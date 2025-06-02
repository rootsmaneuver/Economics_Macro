"""
Enhanced Yield Curve Visualizer with Web Export Capabilities
Author: Valentin Ivanov
Description: Advanced yield curve visualization with Plotly for web deployment
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, callback
import datetime as dt
from typing import Dict, List, Tuple, Optional
import json
try:
    from fredapi import Fred
    FREDAPI_AVAILABLE = True
except ImportError:
    FREDAPI_AVAILABLE = False
    print("Warning: fredapi not available. Using sample data only.")

class WebYieldCurveVisualizer:
    """Web-ready yield curve visualizer using Plotly and Dash."""
    
    def __init__(self, fred_api_key=None):
        """Initialize the web visualizer."""
        self.data = None
        self.app = None
        self.fred_api_key = fred_api_key
        
        # Initialize FRED API client if available
        if FREDAPI_AVAILABLE and fred_api_key:
            self.fred = Fred(api_key=fred_api_key)
        else:
            self.fred = None
        
        # Yield curve maturities
        self.maturities = {
            '1mo': {'years': 1/12, 'series': 'DGS1MO', 'label': '1 Month'},
            '3mo': {'years': 0.25, 'series': 'DGS3MO', 'label': '3 Month'},
            '6mo': {'years': 0.5, 'series': 'DGS6MO', 'label': '6 Month'},
            '1yr': {'years': 1, 'series': 'DGS1', 'label': '1 Year'},
            '2yr': {'years': 2, 'series': 'DGS2', 'label': '2 Year'},
            '3yr': {'years': 3, 'series': 'DGS3', 'label': '3 Year'},
            '5yr': {'years': 5, 'series': 'DGS5', 'label': '5 Year'},
            '7yr': {'years': 7, 'series': 'DGS7', 'label': '7 Year'},
            '10yr': {'years': 10, 'series': 'DGS10', 'label': '10 Year'},
            '20yr': {'years': 20, 'series': 'DGS20', 'label': '20 Year'},
            '30yr': {'years': 30, 'series': 'DGS30', 'label': '30 Year'}
        }
          # Color palette
        self.color_scale = px.colors.sequential.Viridis
        
    def load_sample_data(self, start_date='1990-01-01', end_date=None):
        """Load sample yield curve data."""
        if end_date is None:
            end_date = dt.datetime.now().strftime('%Y-%m-%d')
            
        date_range = pd.date_range(start=start_date, end=end_date, freq='ME')
        
        # Generate realistic yield curve data
        np.random.seed(42)
        all_data = {}
        
        for maturity, info in self.maturities.items():
            base_rate = 0.5 + info['years'] * 0.3  # Upward sloping base
              # Add macroeconomic cycles and trends
            time_trend = np.linspace(5, 1, len(date_range))  # Declining trend
            business_cycle = 2 * np.sin(np.linspace(0, 6*np.pi, len(date_range)))
            noise = np.random.normal(0, 0.3, len(date_range))
            
            rates = base_rate + time_trend + business_cycle + noise
            rates = np.maximum(rates, 0.01)  # Floor at 1bp
            
            all_data[maturity] = rates
        
        self.data = pd.DataFrame(all_data, index=date_range)
        return self.data
    
    def load_fred_data(self, start_date='1990-01-01', end_date=None):
        """Load real yield curve data from FRED API."""
        if not FREDAPI_AVAILABLE:
            print("FRED API not available. Using sample data instead.")
            return self.load_sample_data(start_date, end_date)
            
        if not self.fred:
            print("FRED API key not provided. Using sample data instead.")
            return self.load_sample_data(start_date, end_date)
        
        if end_date is None:
            end_date = dt.datetime.now().strftime('%Y-%m-%d')
        
        print("Fetching real yield curve data from FRED...")
        all_data = {}
        
        for maturity, info in self.maturities.items():
            try:
                print(f"Fetching {info['label']} yields ({info['series']})...")
                series_data = self.fred.get_series(
                    info['series'], 
                    start=start_date, 
                    end=end_date
                )
                if not series_data.empty:
                    # Resample to monthly frequency and forward fill missing values
                    monthly_data = series_data.resample('ME').last().ffill()
                    all_data[maturity] = monthly_data
                    print(f"✓ {info['label']}: {len(monthly_data)} data points")
                else:
                    print(f"⚠ No data available for {info['label']}")
                    
            except Exception as e:
                print(f"⚠ Error fetching {info['label']}: {str(e)}")
                continue
        
        if all_data:
            # Combine all series into a single DataFrame
            self.data = pd.DataFrame(all_data)
            
            # Drop rows where all values are NaN
            self.data = self.data.dropna(how='all')
            
            # Forward fill any remaining NaN values
            self.data = self.data.ffill()
            
            print(f"✓ Successfully loaded yield curve data: {len(self.data)} observations")
            print(f"Date range: {self.data.index.min().strftime('%Y-%m-%d')} to {self.data.index.max().strftime('%Y-%m-%d')}")
            return self.data
        else:
            print("⚠ No FRED data could be loaded. Using sample data instead.")
            return self.load_sample_data(start_date, end_date)
    
    def load_data_with_config(self, config_path='config.json'):
        """Load data using configuration file settings."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Get settings from config
            fred_api_key = config.get('data_sources', {}).get('fred_api_key')
            primary_source = config.get('data_sources', {}).get('primary', 'sample_data')
            start_date = config.get('default_settings', {}).get('start_date', '1990-01-01')
            
            # Update API key if provided in config
            if fred_api_key and fred_api_key != "YOUR_FRED_API_KEY_HERE":
                self.fred_api_key = fred_api_key
                if FREDAPI_AVAILABLE:
                    self.fred = Fred(api_key=fred_api_key)
            
            # Load data based on primary source setting
            if primary_source == "FRED" and self.fred:
                return self.load_fred_data(start_date)
            else:
                return self.load_sample_data(start_date)
                
        except FileNotFoundError:
            print("Config file not found. Using sample data with default settings.")
            return self.load_sample_data()
        except Exception as e:
            print(f"Error loading config: {str(e)}. Using sample data.")
            return self.load_sample_data()
    
    def create_animated_plot(self):
        """Create an animated yield curve plot."""
        if self.data is None:
            self.load_sample_data()
        
        # Prepare data for animation
        frames = []
        maturity_years = [self.maturities[m]['years'] for m in self.data.columns]
        
        for i, (date, row) in enumerate(self.data.iterrows()):
            frame_data = go.Scatter(
                x=maturity_years,
                y=row.values,
                mode='lines+markers',
                name=f'Yield Curve {date.strftime("%Y-%m")}',
                line=dict(width=3, color='red'),
                marker=dict(size=8)
            )
            
            frames.append(go.Frame(
                data=[frame_data],
                name=str(i),
                layout=go.Layout(
                    title=f"US Treasury Yield Curve - {date.strftime('%B %Y')}",
                    annotations=[
                        dict(
                            x=0.02, y=0.98,
                            xref='paper', yref='paper',
                            text=f"Date: {date.strftime('%Y-%m-%d')}",
                            showarrow=False,
                            bgcolor='white',
                            bordercolor='black',
                            borderwidth=1
                        )
                    ]
                )
            ))
        
        # Initial frame
        initial_data = go.Scatter(
            x=maturity_years,
            y=self.data.iloc[0].values,
            mode='lines+markers',
            name='Yield Curve',
            line=dict(width=3, color='red'),
            marker=dict(size=8)
        )
        
        # Create figure
        fig = go.Figure(
            data=[initial_data],
            frames=frames,
            layout=go.Layout(
                title="Interactive US Treasury Yield Curve (1990-2025)",
                xaxis=dict(
                    title="Maturity (Years)",
                    range=[0, max(maturity_years) * 1.1],
                    showgrid=True
                ),
                yaxis=dict(
                    title="Yield (%)",
                    range=[self.data.min().min() - 0.5, self.data.max().max() + 0.5],
                    showgrid=True
                ),
                updatemenus=[{
                    "buttons": [
                        {
                            "args": [None, {"frame": {"duration": 100, "redraw": True},
                                          "fromcurrent": True, "transition": {"duration": 50}}],
                            "label": "Play",
                            "method": "animate"
                        },
                        {
                            "args": [[None], {"frame": {"duration": 0, "redraw": True},
                                             "mode": "immediate", "transition": {"duration": 0}}],
                            "label": "Pause",
                            "method": "animate"
                        }
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "showactive": False,
                    "type": "buttons",
                    "x": 0.1,
                    "xanchor": "right",
                    "y": 0,
                    "yanchor": "top"
                }],
                sliders=[{
                    "active": 0,
                    "yanchor": "top",
                    "xanchor": "left",
                    "currentvalue": {
                        "font": {"size": 20},
                        "prefix": "Date: ",
                        "visible": True,
                        "xanchor": "right"
                    },
                    "transition": {"duration": 300, "easing": "cubic-in-out"},
                    "pad": {"b": 10, "t": 50},
                    "len": 0.9,
                    "x": 0.1,
                    "y": 0,
                    "steps": [
                        {
                            "args": [[str(i)], {
                                "frame": {"duration": 300, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 300}
                            }],
                            "label": self.data.index[i].strftime('%Y-%m'),
                            "method": "animate"
                        }
                        for i in range(len(self.data))
                    ]
                }],
                height=600,
                template="plotly_white"
            )
        )
        
        return fig
    
    def create_3d_surface_plot(self):
        """Create a 3D surface plot of yield curves over time."""
        if self.data is None:
            self.load_sample_data()
        
        # Prepare data for 3D surface
        maturity_years = [self.maturities[m]['years'] for m in self.data.columns]
        dates_numeric = [(d - self.data.index[0]).days for d in self.data.index]
        
        X, Y = np.meshgrid(maturity_years, dates_numeric)
        Z = self.data.values
        
        fig = go.Figure(data=[go.Surface(
            x=X,
            y=Y,
            z=Z,
            colorscale='Viridis',
            colorbar=dict(title="Yield (%)"),
            hovertemplate='Maturity: %{x:.1f} years<br>Days: %{y}<br>Yield: %{z:.2f}%<extra></extra>'
        )])
        
        fig.update_layout(
            title="3D Yield Curve Evolution",
            scene=dict(
                xaxis_title="Maturity (Years)",
                yaxis_title="Days from Start",
                zaxis_title="Yield (%)",
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))
            ),
            height=700,
            template="plotly_white"
        )
        
        return fig
    
    def create_heatmap(self):
        """Create a heatmap of yield curves over time."""
        if self.data is None:
            self.load_sample_data()
        
        fig = go.Figure(data=go.Heatmap(
            z=self.data.T.values,
            x=[d.strftime('%Y-%m') for d in self.data.index],
            y=[self.maturities[m]['label'] for m in self.data.columns],
            colorscale='RdYlBu_r',
            colorbar=dict(title="Yield (%)"),
            hovertemplate='Date: %{x}<br>Maturity: %{y}<br>Yield: %{z:.2f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title="Yield Curve Heatmap",
            xaxis_title="Date",
            yaxis_title="Maturity",
            height=500,
            template="plotly_white"
        )
        
        return fig
    
    def create_dash_app(self):
        """Create a Dash web application."""
        self.app = dash.Dash(__name__)
        
        # Load data
        self.load_sample_data()
        
        # Define layout
        self.app.layout = html.Div([
            html.H1("Interactive Yield Curve Visualization", 
                   style={'textAlign': 'center', 'marginBottom': 30}),
            
            # Controls
            html.Div([
                html.Div([
                    html.Label("Select Visualization Type:"),
                    dcc.Dropdown(
                        id='viz-type',
                        options=[
                            {'label': 'Animated Yield Curves', 'value': 'animated'},
                            {'label': '3D Surface Plot', 'value': '3d'},
                            {'label': 'Heatmap', 'value': 'heatmap'}
                        ],
                        value='animated'
                    )
                ], style={'width': '30%', 'display': 'inline-block'}),
                
                html.Div([
                    html.Label("Date Range:"),
                    dcc.DatePickerRange(
                        id='date-range',
                        start_date=self.data.index[0],
                        end_date=self.data.index[-1],
                        display_format='YYYY-MM-DD'
                    )
                ], style={'width': '40%', 'display': 'inline-block', 'marginLeft': '5%'}),
                
                html.Div([
                    html.Label("Animation Speed:"),
                    dcc.Slider(
                        id='speed-slider',
                        min=50,
                        max=500,
                        step=50,
                        value=200,
                        marks={i: f'{i}ms' for i in range(50, 501, 100)}
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'marginLeft': '5%'})
            ], style={'marginBottom': 30}),
            
            # Main plot
            dcc.Graph(id='main-plot', style={'height': '70vh'}),
            
            # Statistics panel
            html.Div(id='stats-panel', style={'marginTop': 20})        ])
        
        # Callbacks
        @self.app.callback(
            Output('main-plot', 'figure'),
            [Input('viz-type', 'value'),
             Input('date-range', 'start_date'),
             Input('date-range', 'end_date')]
        )
        def update_plot(viz_type, start_date, end_date):
            # Filter data based on date range
            filtered_data = self.data[start_date:end_date]
            
            if viz_type == 'animated':
                return self.create_animated_plot()
            elif viz_type == '3d':
                return self.create_3d_surface_plot()
            elif viz_type == 'heatmap':
                return self.create_heatmap()
        
        return self.app
    
    def run_web_app(self, debug=True, port=8050):
        """Run the web application."""
        if self.app is None:
            self.create_dash_app()
        
        print(f"Starting web application on http://localhost:{port}")
        self.app.run(debug=debug, port=port)
    
    def run_server(self, debug=True, port=8050):
        """Alias for run_web_app for backward compatibility."""
        return self.run_web_app(debug=debug, port=port)
    
    def export_to_html(self, filename='yield_curve_viz.html'):
        """Export the visualization to an HTML file."""
        fig = self.create_animated_plot()
        fig.write_html(filename)
        print(f"Visualization exported to {filename}")

# Standalone plotting functions for quick use
def quick_yield_curve_animation(start_date='1990-01-01', end_date=None):
    """Quick function to create and display yield curve animation."""
    viz = WebYieldCurveVisualizer()
    viz.load_sample_data(start_date, end_date)
    fig = viz.create_animated_plot()
    fig.show()
    return fig

def export_yield_curve_html(filename='yield_curve.html', start_date='1990-01-01'):
    """Export yield curve visualization to HTML."""
    viz = WebYieldCurveVisualizer()
    viz.load_sample_data(start_date)
    viz.export_to_html(filename)

if __name__ == "__main__":
    # Create and run the web application
    viz = WebYieldCurveVisualizer()
    viz.run_web_app(debug=True, port=8050)
