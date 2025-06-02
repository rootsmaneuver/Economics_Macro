"""
Interactive Treasury Yield Curve Visualizer with Real FRED Data
Author: Valentin Ivanov
Description: Comprehensive web application for Treasury yield curve analysis
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, callback
import datetime as dt
from fredapi import Fred
import json

# Check if FRED API is available
try:
    from fredapi import Fred
    FREDAPI_AVAILABLE = True
except ImportError:
    FREDAPI_AVAILABLE = False
    print("⚠️ FRED API not available. Install with: pip install fredapi")

class WebYieldCurveVisualizer:
    """Interactive web application for Treasury yield curve visualization with real FRED data."""
    
    def __init__(self, fred_api_key=None):
        """Initialize the visualizer with FRED API key."""
        self.fred = None
        self.data = None
        self.using_real_data = False
        
        # Treasury maturities configuration
        self.maturities = {
            '1mo': {'years': 0.083, 'series': 'DGS1MO', 'label': '1 Month'},
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
        
        # Initialize FRED API if available
        if FREDAPI_AVAILABLE and fred_api_key:
            try:
                self.fred = Fred(api_key=fred_api_key)
                print("✅ FRED API initialized successfully")
            except Exception as e:
                print(f"⚠️ FRED API initialization failed: {e}")
        
        # Load data immediately upon initialization
        self.load_fred_data()
                
        # Create Dash app
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
    
    def load_fred_data(self, start_date='1990-01-01', end_date=None):
        """Load real Treasury yield data from FRED API."""
        if not FREDAPI_AVAILABLE:
            print("❌ FRED API not available. Using sample data.")
            return self.load_sample_data(start_date, end_date)
            
        if not self.fred:
            print("❌ FRED API key not provided. Using sample data.")
            return self.load_sample_data(start_date, end_date)
        
        if end_date is None:
            end_date = dt.datetime.now().strftime('%Y-%m-%d')
        
        print("🏛️ Fetching real Treasury yield data from FRED...")
        print("-" * 50)
        
        all_data = {}
        successful_series = 0
        
        for maturity, info in self.maturities.items():
            try:
                print(f"Fetching {info['label']} yields ({info['series']})...")
                series_data = self.fred.get_series(
                    info['series'], 
                    start=start_date, 
                    end=end_date
                )
                
                if not series_data.empty:
                    # Clean and process the data
                    series_data = series_data.dropna()
                    if len(series_data) > 0:
                        all_data[maturity] = series_data
                        successful_series += 1
                        print(f"✅ {info['label']}: {len(series_data)} data points, Current: {series_data.iloc[-1]:.2f}%")
                    else:
                        print(f"⚠️ No valid data for {info['label']}")
                else:
                    print(f"⚠️ No data available for {info['label']}")
                    
            except Exception as e:
                print(f"❌ Error fetching {info['label']}: {str(e)}")
                continue
        
        if all_data and successful_series >= 5:  # At least 5 series for a meaningful curve
            # Combine all series into a single DataFrame
            self.data = pd.DataFrame(all_data)
            
            # Clean the data
            self.data = self.data.dropna(how='all')  # Remove rows with all NaN
            self.data = self.data.fillna(method='ffill')  # Forward fill missing values
            
            self.using_real_data = True
            print(f"\n✅ Successfully loaded REAL FRED data!")
            print(f"📊 Data range: {self.data.index.min().strftime('%Y-%m-%d')} to {self.data.index.max().strftime('%Y-%m-%d')}")
            print(f"📈 Total observations: {len(self.data)}")
            print(f"🎯 Series coverage: {len(all_data)}/{len(self.maturities)}")
            
            return self.data
        else:
            print(f"❌ Insufficient real data ({successful_series} series). Using sample data.")
            return self.load_sample_data(start_date, end_date)
    
    def load_sample_data(self, start_date='1990-01-01', end_date=None):
        """Load realistic sample Treasury yield data as fallback."""
        if end_date is None:
            end_date = dt.datetime.now().strftime('%Y-%m-%d')
        
        print("📊 Generating realistic sample Treasury yield data...")
        
        # Create date range
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Current realistic yield levels (as of May 2025)
        current_yields = {
            '1mo': 4.35, '3mo': 4.37, '6mo': 4.36, '1yr': 4.13,
            '2yr': 3.92, '3yr': 3.95, '5yr': 4.00, '7yr': 4.15,
            '10yr': 4.43, '20yr': 4.70, '30yr': 4.92
        }
        
        all_data = {}
        
        for maturity, info in self.maturities.items():
            # Base rate with realistic yield curve shape
            base_rate = current_yields.get(maturity, 4.0)
            
            # Add realistic historical variation
            # Gradual decline from higher rates in the past
            time_trend = np.linspace(2.0, 0.0, len(date_range))
            
            # Business cycle variation
            business_cycle = 0.8 * np.sin(np.linspace(0, 4*np.pi, len(date_range)))
            
            # Random market noise
            noise = np.random.normal(0, 0.15, len(date_range))
            
            # Combine components
            rates = base_rate + time_trend + business_cycle + noise
            rates = np.maximum(rates, 0.01)  # Floor at 1 basis point
            
            all_data[maturity] = rates
        
        self.data = pd.DataFrame(all_data, index=date_range)
        self.using_real_data = False
        
        print(f"✅ Generated sample data with realistic current yields")
        print(f"📊 Data range: {start_date} to {end_date}")
        print(f"📈 Total observations: {len(self.data)}")
        
        return self.data
    
    def setup_layout(self):
        """Setup the Dash app layout with all components."""
        
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1("🏛️ US Treasury Yield Curve Analyzer", 
                       style={'textAlign': 'center', 'color': '#2c3e50', 'marginBottom': '10px'}),
                html.P("Interactive visualization of Treasury yields with real-time FRED data",
                       style={'textAlign': 'center', 'color': '#7f8c8d', 'fontSize': '18px'}),
                
                # Data source indicator
                html.Div(id='data-source-indicator', 
                        style={'textAlign': 'center', 'marginBottom': '20px'}),
                
            ], style={'backgroundColor': '#ecf0f1', 'padding': '20px', 'marginBottom': '20px'}),
            
            # Control Panel
            html.Div([
                html.H3("📊 Visualization Controls", style={'color': '#2c3e50'}),
                
                # Date Range Selector
                html.Div([
                    html.Label("📅 Select Date Range:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dcc.DatePickerRange(
                        id='date-range-picker',
                        start_date=dt.datetime(2020, 1, 1),
                        end_date=dt.datetime.now(),
                        display_format='YYYY-MM-DD',
                        with_portal=True,
                        style={'marginBottom': '15px'}
                    ),
                ], style={'marginBottom': '20px'}),
                
                # Animation Speed Control (only for animated plots)
                html.Div([
                    html.Label("🚀 Animation Speed:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dcc.Slider(
                        id='animation-speed-slider',
                        min=50,
                        max=1000,
                        step=25,  # Smaller steps for more granular control
                        value=200,
                        marks={
                            50: {'label': 'Fast', 'style': {'color': '#27ae60'}},
                            200: {'label': 'Medium', 'style': {'color': '#f39c12'}},
                            500: {'label': 'Slow', 'style': {'color': '#e74c3c'}},
                            1000: {'label': 'Very Slow', 'style': {'color': '#8e44ad'}}
                        },
                        tooltip={"placement": "bottom", "always_visible": True},
                        updatemode='drag'  # This enables real-time updates while dragging
                    ),
                    html.P("💡 Animation speed updates in real-time! No need to pause/play.", 
                           style={'fontSize': '12px', 'color': '#7f8c8d', 'fontStyle': 'italic', 'marginTop': '10px'})
                ], id='speed-control-div', style={'marginBottom': '20px'}),
                
                # Visualization Type Selector
                html.Div([
                    html.Label("📈 Visualization Type:", style={'fontWeight': 'bold', 'marginBottom': '10px'}),
                    dcc.Dropdown(
                        id='viz-type-dropdown',
                        options=[
                            {'label': '📹 Animated Time Lapse', 'value': 'animated'},
                            {'label': '🏔️ 3D Surface Plot', 'value': '3d_surface'},
                            {'label': '🔥 Heatmap', 'value': 'heatmap'}
                        ],
                        value='animated',
                        style={'marginBottom': '15px'}
                    ),
                ]),
                
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'marginBottom': '20px', 'borderRadius': '8px'}),
            
            # Main Visualization Area
            html.Div([
                dcc.Graph(id='main-chart', style={'height': '700px'})
            ]),
            
            # Current Yield Curve Display
            html.Div([
                html.H3("📊 Current Yield Curve", style={'color': '#2c3e50', 'marginBottom': '15px'}),
                html.Div(id='current-yields-display')
            ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'marginTop': '20px', 'borderRadius': '8px'}),
        ])
    
    def setup_callbacks(self):
        """Setup all Dash callbacks for interactivity."""
        
        @self.app.callback(
            Output('data-source-indicator', 'children'),
            Input('main-chart', 'id')  # Trigger on app load
        )
        def update_data_source_indicator(_):
            """Display whether using real or sample data."""
            if self.using_real_data:
                return html.Div([
                    html.Span("🟢 LIVE FRED DATA", 
                             style={'backgroundColor': '#d4edda', 'color': '#155724', 
                                   'padding': '8px 15px', 'borderRadius': '20px', 
                                   'fontWeight': 'bold', 'border': '1px solid #c3e6cb'})
                ])
            else:
                return html.Div([
                    html.Span("🔴 SAMPLE DATA", 
                             style={'backgroundColor': '#f8d7da', 'color': '#721c24', 
                                   'padding': '8px 15px', 'borderRadius': '20px', 
                                   'fontWeight': 'bold', 'border': '1px solid #f5c6cb'})
                ])
        
        @self.app.callback(
            Output('main-chart', 'figure'),
            [Input('viz-type-dropdown', 'value'),
             Input('date-range-picker', 'start_date'),
             Input('date-range-picker', 'end_date'),
             Input('animation-speed-slider', 'value')]
        )
        def update_main_chart(viz_type, start_date, end_date, animation_speed):
            """Update the main chart based on selected visualization type."""
            
            if self.data is None or self.data.empty:
                return go.Figure().add_annotation(
                    text="No data available", 
                    xref="paper", yref="paper", 
                    x=0.5, y=0.5, showarrow=False
                )
            
            # Filter data by date range
            if start_date and end_date:
                mask = (self.data.index >= start_date) & (self.data.index <= end_date)
                filtered_data = self.data.loc[mask].copy()
            else:
                filtered_data = self.data.copy()
            
            if filtered_data.empty:
                return go.Figure().add_annotation(
                    text="No data in selected date range", 
                    xref="paper", yref="paper", 
                    x=0.5, y=0.5, showarrow=False
                )
            
            # Sort data chronologically
            filtered_data = filtered_data.sort_index()
            
            # Generate visualization based on type
            if viz_type == 'animated':
                return self.create_animated_plot(filtered_data, animation_speed)
            elif viz_type == '3d_surface':
                return self.create_3d_surface_plot(filtered_data)
            elif viz_type == 'heatmap':
                return self.create_heatmap_plot(filtered_data)
            else:
                return self.create_animated_plot(filtered_data, animation_speed)
        
        @self.app.callback(
            Output('speed-control-div', 'style'),
            Input('viz-type-dropdown', 'value')
        )
        def toggle_speed_control(viz_type):
            """Show/hide speed control based on visualization type."""
            if viz_type == 'animated':
                return {'marginBottom': '20px'}
            else:
                return {'marginBottom': '20px', 'display': 'none'}
        
        @self.app.callback(
            Output('current-yields-display', 'children'),
            Input('main-chart', 'figure')
        )
        def update_current_yields(_):
            """Display current yield curve values."""
            if self.data is None or self.data.empty:
                return "No data available"
            
            latest_data = self.data.iloc[-1]
            latest_date = self.data.index[-1].strftime('%Y-%m-%d')
            
            yields_display = [
                html.H4(f"As of {latest_date}", style={'color': '#2c3e50', 'marginBottom': '15px'})
            ]
            
            # Create yield curve display
            yields_list = []
            for maturity, value in latest_data.items():
                if pd.notna(value):
                    maturity_label = self.maturities[maturity]['label']
                    yields_list.append(
                        html.Div([
                            html.Span(f"{maturity_label}: ", style={'fontWeight': 'bold'}),
                            html.Span(f"{value:.2f}%", style={'color': '#e74c3c', 'fontSize': '18px'})
                        ], style={'display': 'inline-block', 'marginRight': '20px', 'marginBottom': '8px'})
                    )
            
            yields_display.extend(yields_list)
            return yields_display
    
    def create_animated_plot(self, data, animation_speed=200):
        """Create animated time lapse yield curve plot with real-time speed control."""
        
        # Prepare maturity years for x-axis
        maturity_years = [self.maturities[col]['years'] for col in data.columns if col in self.maturities]
        maturity_labels = [self.maturities[col]['label'] for col in data.columns if col in self.maturities]
        
        # Sample data for animation (every 7 days to manage performance)
        sample_freq = max(1, len(data) // 150)  # Max 150 frames for better performance
        sampled_data = data.iloc[::sample_freq].copy()
        
        # Create frames for animation
        frames = []
        for i, (date, row) in enumerate(sampled_data.iterrows()):
            yields = [row[col] for col in data.columns if col in self.maturities and pd.notna(row[col])]
            valid_maturities = [self.maturities[col]['years'] for col in data.columns if col in self.maturities and pd.notna(row[col])]
            valid_labels = [self.maturities[col]['label'] for col in data.columns if col in self.maturities and pd.notna(row[col])]
            
            frame = go.Frame(
                data=[
                    go.Scatter(
                        x=valid_maturities,
                        y=yields,
                        mode='lines+markers',
                        name='Yield Curve',
                        line=dict(color='#3498db', width=3),
                        marker=dict(size=8, color='#e74c3c'),
                        hovertemplate='<b>%{text}</b><br>Yield: %{y:.2f}%<extra></extra>',
                        text=valid_labels
                    )
                ],
                name=date.strftime('%Y-%m-%d'),
                layout=go.Layout(
                    title=f"US Treasury Yield Curve - {date.strftime('%B %d, %Y')}",
                    annotations=[
                        dict(
                            x=0.02, y=0.98,
                            xref='paper', yref='paper',
                            text=f"📅 {date.strftime('%B %d, %Y')}",
                            showarrow=False,
                            font=dict(size=16, color='#2c3e50'),
                            bgcolor='rgba(255,255,255,0.9)',
                            bordercolor='#bdc3c7',
                            borderwidth=1,
                            borderpad=8
                        )
                    ]
                )
            )
            frames.append(frame)
        
        # Create initial plot
        if len(sampled_data) > 0:
            initial_yields = [sampled_data.iloc[0][col] for col in data.columns if col in self.maturities and pd.notna(sampled_data.iloc[0][col])]
            initial_maturities = [self.maturities[col]['years'] for col in data.columns if col in self.maturities and pd.notna(sampled_data.iloc[0][col])]
            initial_labels = [self.maturities[col]['label'] for col in data.columns if col in self.maturities and pd.notna(sampled_data.iloc[0][col])]
        else:
            initial_yields, initial_maturities, initial_labels = [], [], []
        
        fig = go.Figure(
            data=[
                go.Scatter(
                    x=initial_maturities,
                    y=initial_yields,
                    mode='lines+markers',
                    name='Yield Curve',
                    line=dict(color='#3498db', width=3),
                    marker=dict(size=8, color='#e74c3c'),
                    hovertemplate='<b>%{text}</b><br>Yield: %{y:.2f}%<extra></extra>',
                    text=initial_labels
                )
            ],
            frames=frames
        )
        
        # Calculate transition duration based on speed
        transition_duration = max(50, animation_speed // 4)  # Smooth transitions
        
        # Update layout with improved animation controls that respond to speed changes
        fig.update_layout(
            title={
                'text': "🎬 US Treasury Yield Curve Time Lapse",
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 24, 'color': '#2c3e50'}
            },
            xaxis_title="Maturity (Years)",
            yaxis_title="Yield (%)",
            xaxis=dict(
                type='log', 
                tickmode='array', 
                tickvals=maturity_years, 
                ticktext=maturity_labels,
                gridcolor='#ecf0f1'
            ),
            yaxis=dict(
                range=[0, max(data.max()) * 1.1] if not data.empty else [0, 10],
                gridcolor='#ecf0f1'
            ),
            showlegend=False,
            template='plotly_white',
            font=dict(size=12),
            plot_bgcolor='white',
            paper_bgcolor='white',
            # Add animation configuration that updates with speed
            updatemenus=[{
                'type': 'buttons',
                'direction': 'left',
                'showactive': False,
                'x': 0.1,
                'y': 0.02,
                'xanchor': 'right',
                'yanchor': 'top',
                'pad': {'t': 87, 'r': 10},
                'buttons': [
                    {
                        'label': '▶️ Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {
                                'duration': animation_speed, 
                                'redraw': True
                            },
                            'fromcurrent': True,
                            'transition': {
                                'duration': transition_duration, 
                                'easing': 'quadratic-in-out'
                            },
                            'mode': 'immediate'
                        }]
                    },
                    {
                        'label': '⏸️ Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ]
            }],
            sliders=[{
                'active': 0,
                'yanchor': 'top',
                'xanchor': 'left',
                'currentvalue': {
                    'font': {'size': 16},
                    'prefix': '📅 Date: ',
                    'visible': True,
                    'xanchor': 'right'
                },
                'transition': {
                    'duration': transition_duration, 
                    'easing': 'cubic-in-out'
                },
                'pad': {'b': 10, 't': 50},
                'len': 0.9,
                'x': 0.1,
                'y': 0,
                'steps': [
                    {                        'args': [
                            [frame.name],
                            {
                                'frame': {
                                    'duration': animation_speed, 
                                    'redraw': True
                                },
                                'mode': 'immediate',
                                'transition': {
                                    'duration': transition_duration
                                }
                            }
                        ],
                    'label': frame.name,
                    'method': 'animate'
                }
                for frame in frames
                ]
            }]
        )
        
        return fig
    
    def create_3d_surface_plot(self, data):
        """Create 3D surface plot of yield curve over time."""
        
        # Prepare data for 3D surface
        maturity_years = [self.maturities[col]['years'] for col in data.columns if col in self.maturities]
        maturity_labels = [self.maturities[col]['label'] for col in data.columns if col in self.maturities]
        
        # Sample data to manage performance
        sample_freq = max(1, len(data) // 200)  # Max 200 time points
        sampled_data = data.iloc[::sample_freq].copy()
        
        # Create meshgrid
        dates_numeric = np.arange(len(sampled_data))
        X, Y = np.meshgrid(maturity_years, dates_numeric)
        
        # Prepare Z values (yields)
        Z = []
        for _, row in sampled_data.iterrows():
            z_row = [row[col] for col in data.columns if col in self.maturities]
            Z.append(z_row)
        Z = np.array(Z)
        
        # Create 3D surface plot
        fig = go.Figure(data=[
            go.Surface(
                x=X,
                y=Y, 
                z=Z,
                colorscale='Viridis',
                colorbar=dict(title="Yield (%)"),
                hovertemplate='<b>Maturity:</b> %{x:.1f} years<br><b>Date Index:</b> %{y}<br><b>Yield:</b> %{z:.2f}%<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title='🏔️ 3D Treasury Yield Surface Over Time',
            scene=dict(
                xaxis_title='Maturity (Years)',
                yaxis_title='Time Period',
                zaxis_title='Yield (%)',
                camera=dict(eye=dict(x=1.2, y=1.2, z=0.8))
            ),
            template='plotly_white',
            font=dict(size=12)
        )
        
        return fig
    
    def create_heatmap_plot(self, data):
        """Create heatmap of yield curve over time."""
        
        # Sample data for better visualization
        sample_freq = max(1, len(data) // 100)  # Max 100 rows
        sampled_data = data.iloc[::sample_freq].copy()
        
        # Prepare data for heatmap
        heatmap_data = sampled_data.T  # Transpose so maturities are on y-axis
        
        # Create custom hover text
        hover_text = []
        for i, maturity in enumerate(heatmap_data.index):
            hover_row = []
            for j, date in enumerate(heatmap_data.columns):
                if pd.notna(heatmap_data.iloc[i, j]):
                    hover_row.append(
                        f"Date: {date.strftime('%Y-%m-%d')}<br>"
                        f"Maturity: {self.maturities[maturity]['label']}<br>"
                        f"Yield: {heatmap_data.iloc[i, j]:.2f}%"
                    )
                else:
                    hover_row.append("No data")
            hover_text.append(hover_row)
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=[date.strftime('%Y-%m-%d') for date in heatmap_data.columns],
            y=[self.maturities[maturity]['label'] for maturity in heatmap_data.index],
            colorscale='RdYlBu_r',
            colorbar=dict(title="Yield (%)"),
            hovertemplate='%{customdata}<extra></extra>',
            customdata=hover_text
        ))
        
        fig.update_layout(
            title='🔥 Treasury Yield Heatmap Over Time',
            xaxis_title='Date',
            yaxis_title='Maturity',
            template='plotly_white',
            font=dict(size=12),
            xaxis=dict(tickangle=45)
        )
        
        return fig
    
    def run_web_app(self, port=8050, debug=False):
        """Run the web application."""
        print(f"🚀 Starting Treasury Yield Curve Web Application...")
        print(f"🌐 Loading at http://localhost:{port}")
        
        self.app.run(host='0.0.0.0', port=port, debug=debug)
    
    def run_server(self, port=8050, debug=False):
        """Alias for run_web_app for compatibility."""
        return self.run_web_app(port, debug)

def main():
    """Main function to run the application."""
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        fred_api_key = config.get('fred_api_key')
    except:
        fred_api_key = "df764c31adfa56ce0e019e7f5b89850a"  # Your API key
    
    # Create and run the application
    app = WebYieldCurveVisualizer(fred_api_key=fred_api_key)
    app.run_web_app(port=8050, debug=True)

if __name__ == "__main__":
    main()
