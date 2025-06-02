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
        self.using_real_data = False

        # Initialize FRED API client if available
        if FREDAPI_AVAILABLE and fred_api_key:
            self.fred = Fred(api_key=fred_api_key)
        else:
            self.fred = None

        # Yield curve maturities
        self.maturities = {
            '1mo': {'years': 1 / 12, 'series': 'DGS1MO', 'label': '1 Month'},
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

        # Current yield curve approximations (accurate as of June 2025)
        current_yields = {
            '1mo': 5.3,
            '3mo': 5.2,
            '6mo': 5.1,
            '1yr': 4.9,
            '2yr': 4.7,
            '3yr': 4.5,
            '5yr': 4.4,
            '7yr': 4.3,
            '10yr': 4.3,
            '20yr': 4.6,
            '30yr': 4.5
        }

        for maturity, info in self.maturities.items():
            # Base rate with more realistic yield curve shape
            base_rate = current_yields.get(maturity, 4.0)

            # Add historical time variation
            # Less extreme time trend (1.5% to 3.5% range)
            # Smaller business cycle variation (±1%)
            time_trend = np.linspace(1.5, 0.0, len(date_range))
            business_cycle = 1.0 * np.sin(np.linspace(0, 6 * np.pi, len(date_range)))
            # Smaller random noise
            noise = np.random.normal(0, 0.2, len(date_range))
            rates = base_rate + time_trend + business_cycle + noise
            rates = np.maximum(rates, 0.01)  # Floor at 1bp
            all_data[maturity] = rates

        print("📈 Generated sample yield curve data with current approximations")
        # Mark that we're using sample data, not real data
        self.using_real_data = False
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

            # Set flag to indicate we're using real data
            self.using_real_data = True

            print(f"✓ Successfully loaded REAL yield curve data: {len(self.data)} observations")
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
            fred_api_key = config.get('fred_api_key') or config.get('data_sources', {}).get('fred_api_key')
            primary_source = config.get('data_sources', {}).get('primary', 'sample_data')
            start_date = config.get('default_settings', {}).get('start_date', '1990-01-01')

            # Update API key if provided in config
            if fred_api_key and fred_api_key != "YOUR_FRED_API_KEY_HERE":
                self.fred_api_key = fred_api_key
                if FREDAPI_AVAILABLE:
                    self.fred = Fred(api_key=fred_api_key)
                    print(f"✅ FRED API initialized with key: {fred_api_key[:5]}...")
                else:
                    print("⚠️ FREDAPI package not available. Will use sample data.")
            else:
                print("⚠️ No valid FRED API key found in config. Will use sample data.")

            # Load data based on primary source setting
            if primary_source == "FRED" and self.fred:
                print("📊 Using FRED as primary data source")
                return self.load_fred_data(start_date)
            else:
                print("📊 Using sample data as primary source")
                return self.load_sample_data(start_date)

        except FileNotFoundError:
            print("Config file not found. Using sample data with default settings.")
            return self.load_sample_data()
        except Exception as e:
            print(f"Error loading config: {str(e)}. Using sample data.")
            return self.load_sample_data()

    def create_animated_plot(self, animation_speed=200):
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
                    ])
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

        # Data source indicator
        data_source = "REAL FRED API DATA" if self.using_real_data else "SAMPLE DATA (Not real market data)"

        # Create figure
        fig = go.Figure(
            data=[initial_data],
            frames=frames,
            layout=go.Layout(
                title=f"Interactive US Treasury Yield Curve (1990-2025) - Using {data_source}",
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
                            "args": [None, {"frame": {"duration": animation_speed, "redraw": True},
                                          "fromcurrent": True, "transition": {"duration": animation_speed // 4}}],
                            "label": "Play",
                            "method": "animate"
                        },
                        {
                            "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                             "mode": "immediate", "transition": {"duration": 0}}],
                            "label": "Pause",
                            "method": "animate"
                        }
                    ],
                    "direction": "left",
                    "pad": {"r": 10, "t": 87},
                    "showactive": True,
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
                    "transition": {"duration": 0, "easing": "cubic-in-out"},
                    "pad": {"b": 10, "t": 50},
                    "len": 0.9,
                    "x": 0.1,
                    "y": 0,
                    "steps": [
                        {
                            "args": [[str(i)], {
                                "frame": {"duration": 0, "redraw": True},
                                "mode": "immediate",
                                "transition": {"duration": 0}
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
        
        # Define layout
        data_source = "REAL FRED API DATA" if self.using_real_data else "SAMPLE DATA (Not real market data)"
        source_color = "green" if self.using_real_data else "red"
        
        self.app.layout = html.Div([
            html.H1("Interactive Yield Curve Visualization", 
                   style={'textAlign': 'center', 'marginBottom': 20}),
                   
            # Data source indicator
            html.H3(f"Using {data_source}", 
                   style={'textAlign': 'center', 'marginBottom': 20, 'color': source_color}),
            
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
                    html.Div([
                        # Direct date input for start date
                        html.Div([
                            html.Label("Start:"),
                            dcc.Input(
                                id='start-date-input',
                                type='text',
                                placeholder='YYYY-MM-DD',
                                value=self.data.index[0].strftime('%Y-%m-%d'),
                                style={'width': '100%', 'marginBottom': '5px'}
                            ),
                        ], style={'width': '45%', 'display': 'inline-block'}),
                        
                        # Direct date input for end date
                        html.Div([
                            html.Label("End:"),
                            dcc.Input(
                                id='end-date-input',
                                type='text',
                                placeholder='YYYY-MM-DD',
                                value=self.data.index[-1].strftime('%Y-%m-%d'),
                                style={'width': '100%', 'marginBottom': '5px'}
                            ),
                        ], style={'width': '45%', 'display': 'inline-block', 'marginLeft': '10%'}),
                        
                        # Hidden date range picker (still needed for callbacks)
                        dcc.DatePickerRange(
                            id='date-range',
                            start_date=self.data.index[0],
                            end_date=self.data.index[-1],
                            display_format='YYYY-MM-DD',
                            with_portal=True,
                            first_day_of_week=1,
                            calendar_orientation='horizontal',
                            clearable=True,
                            month_format='MMMM YYYY',
                            show_outside_days=True,
                            persistence=True,
                            style={'display': 'none'}  # Hide the actual date picker
                        )
                    ])
                ], style={'width': '40%', 'display': 'inline-block', 'marginLeft': '5%'}),
                
                html.Div([
                    html.Label("Animation Speed:"),
                    dcc.Slider(
                        id='speed-slider',
                        min=50,
                        max=500,
                        step=50,
                        value=200,
                        marks={i: f'{i}ms' for i in range(50, 501, 100)},
                        updatemode='drag'  # Update while dragging
                    )
                ], style={'width': '20%', 'display': 'inline-block', 'marginLeft': '5%'})
            ], style={'marginBottom': 30}),
            
            # Data source indicator
            html.Div([
                html.H4(
                    id='data-source-indicator',
                    children=f"Using {'REAL FRED API DATA' if self.using_real_data else 'SAMPLE DATA (Not real market data)'}",
                    style={'textAlign': 'center', 'marginBottom': 10, 'color': 'red' if not self.using_real_data else 'green'}
                )
            ]),
            
            # Main plot
            dcc.Graph(id='main-plot', style={'height': '70vh'}),
            
            # Statistics panel
            html.Div(id='stats-panel', style={'marginTop': 20})
        ])
        
        # Callbacks
        @self.app.callback(
            Output('main-plot', 'figure'),
            [Input('viz-type', 'value'),
             Input('date-range', 'start_date'),
             Input('date-range', 'end_date'),
             Input('speed-slider', 'value')]
        )
        def update_plot(viz_type, start_date, end_date, animation_speed):
            # Filter data based on date range
            try:
                filtered_data = self.data[start_date:end_date]
                # Ensure the data is sorted by date to prevent jumps
                filtered_data = filtered_data.sort_index()
                if not filtered_data.empty:
                    self.data = filtered_data
            except Exception as e:
                print(f"Error filtering data: {e}")
            
            if viz_type == 'animated':
                return self.create_animated_plot(animation_speed=animation_speed)
            elif viz_type == '3d':
                return self.create_3d_surface_plot()
            elif viz_type == 'heatmap':
                return self.create_heatmap()
        
        # Date input callbacks
        @self.app.callback(
            Output('date-range', 'start_date'),
            [Input('start-date-input', 'value')]
        )
        def update_start_date(date_value):
            try:
                # Validate the date format
                pd.to_datetime(date_value)
                return date_value
            except:
                # If invalid, return the current start date
                return self.data.index[0].strftime('%Y-%m-%d')
                
        @self.app.callback(
            Output('date-range', 'end_date'),
            [Input('end-date-input', 'value')]
        )
        def update_end_date(date_value):
            try:
                # Validate the date format
                pd.to_datetime(date_value)
                return date_value
            except:
                # If invalid, return the current end date
                return self.data.index[-1].strftime('%Y-%m-%d')
        
        # Synchronize DatePickerRange with text inputs
        @self.app.callback(
            [Output('start-date-input', 'value'),
             Output('end-date-input', 'value')],
            [Input('date-range', 'start_date'),
             Input('date-range', 'end_date')]
        )
        def sync_date_inputs(start_date, end_date):
            return start_date, end_date
            
        # Update data source indicator
        @self.app.callback(
            [Output('data-source-indicator', 'children'),
             Output('data-source-indicator', 'style')],
            [Input('main-plot', 'figure')]
        )
        def update_data_source_indicator(figure):
            source = "USING REAL FRED API DATA" if self.using_real_data else "USING SAMPLE DATA (Not real market data)"
            style = {'textAlign': 'center', 'marginBottom': 10, 'color': 'green' if self.using_real_data else 'red'}
            return source, style
        
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
