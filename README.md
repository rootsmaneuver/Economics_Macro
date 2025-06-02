# 🏛️ Interactive US Treasury Yield Curve Visualization

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.0%2B-brightgreen.svg)](https://plotly.com)
[![FRED API](https://img.shields.io/badge/FRED-API%20Integrated-orange.svg)](https://fred.stlouisfed.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A comprehensive Python application for visualizing US Treasury yield curves over time with interactive controls, real-time FRED API integration, and web deployment capabilities.

![Yield Curve Demo](https://img.shields.io/badge/Demo-Interactive-brightgreen.svg)

## 🌟 Overview

This application provides professional-grade visualization of US Treasury yield curves, enabling users to analyze interest rate trends, identify yield curve inversions, and understand macroeconomic cycles through interactive charts and 3D visualizations.

## Features

### 🎯 Core Functionality
- **Interactive Time-lapse Animation**: Watch yield curves evolve over 30+ years
- **Multiple Visualization Types**: 
  - Animated 2D yield curves with trails
  - 3D surface plots showing time evolution
  - Heatmaps for pattern analysis
- **Customizable Controls**:
  - Date range selection
  - Animation speed control
  - Maturity selection
  - Trail fade effects

### 🌐 Web-Ready
- **Plotly-based Interactive Plots**: Modern web-compatible visualizations
- **Dash Web Application**: Full-featured web app with controls
- **HTML Export**: Standalone files for easy sharing
- **Mobile-responsive Design**: Works on all devices

### 📊 Data Sources
- **Federal Reserve Economic Data (FRED)**: Real Treasury rates
- **Sample Data Generator**: For testing and demonstration
- **Multiple Maturities**: 1mo to 30yr Treasury securities

## Installation

1. **Clone or download the files** to your preferred directory

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional: Get FRED API Key** (for real data):
   - Register at [FRED API](https://fred.stlouisfed.org/docs/api/api_key.html)
   - Add your key to `config.json`

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/economics-macro-yield-curves.git
   cd economics-macro-yield-curves
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Optional: Configure FRED API** (for real data)
   - Get your free API key from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html)
   - Update `config.json` with your API key

### Usage

**Interactive Menu (Recommended)**
```bash
python app.py
```

**Direct Commands**
```bash
python app.py --web              # Launch web application
python app.py --demo             # Generate demo chart
python app.py --assess           # Run comprehensive assessment
python app.py --web --port 8080  # Custom port
```

## Usage Examples

### Quick Start with App Launcher
```bash
# Interactive menu
python app.py

# Direct web launch
python app.py --web --port 8050

# Generate demo
python app.py --demo
```

### Programmatic Usage
```python
from web_yield_curve_visualizer import WebYieldCurveVisualizer

# Create web app
viz = WebYieldCurveVisualizer()
viz.run_web_app(port=8050)
# Navigate to http://localhost:8050
```

### Basic Animation
```python
from web_yield_curve_visualizer import quick_yield_curve_animation

# Quick animated plot (opens in browser)
fig = quick_yield_curve_animation(start_date='2000-01-01')
fig.show()
```

### Advanced Customization
```python
viz = WebYieldCurveVisualizer()

# Load data for specific period
viz.load_sample_data(start_date='2008-01-01', end_date='2012-12-31')

# Create 3D visualization
fig_3d = viz.create_3d_surface_plot()
fig_3d.show()

# Create heatmap
fig_heatmap = viz.create_heatmap()
fig_heatmap.show()
```

### Web Application with Custom Settings
```python
viz = WebYieldCurveVisualizer()
app = viz.create_dash_app()

# Customize and run
app.run_server(
    debug=False,
    port=8080,
    host='0.0.0.0'  # For deployment
)
```

## 📁 Project Structure

```
economics-macro/
├── app.py                          # 🎯 Main application launcher
├── web_yield_curve_visualizer.py   # 🌐 Web visualization engine
├── yield_curve_visualizer.py       # 🖥️ Desktop visualization engine
├── final_assessment.py             # 📊 Assessment and testing tool
├── config.json                     # ⚙️ Configuration settings
├── requirements.txt                # 📦 Dependencies
├── README.md                       # 📖 Documentation
└── .gitignore                      # 🚫 Git ignore patterns
```

## 🎯 Key Features

### 📈 Visualization Types
- **Interactive Time-lapse Animation**: Watch yield curves evolve over 30+ years
- **3D Surface Plots**: Visualize entire time series evolution
- **Heatmaps**: Identify patterns and correlations
- **Real-time Data**: Direct FRED API integration

### 🌐 Web-Ready
- **Plotly Dash Web App**: Full-featured interactive application
- **HTML Export**: Standalone files for easy sharing
- **Mobile Responsive**: Works on all devices
- **Production Ready**: Deploy to cloud platforms

### 📊 Analysis Features
- **Yield Curve Inversions**: Recession indicator detection
- **Spread Analysis**: Term structure analysis
- **Historical Data**: 30+ years of Treasury data
- **Multiple Maturities**: 1 month to 30 years

## Configuration

Edit `config.json` to customize:

```json
{
  "data_sources": {
    "fred_api_key": "YOUR_API_KEY_HERE"
  },
  "default_settings": {
    "start_date": "1990-01-01",
    "animation_speed": 200,
    "max_trails": 20
  },
  "web_app": {
    "port": 8050,
    "debug": true
  }
}
```

## 🔧 Configuration

Edit `config.json` to customize your setup:

```json
{
  "data_sources": {
    "fred_api_key": "YOUR_API_KEY_HERE",
    "primary": "sample_data"
  },
  "default_settings": {
    "start_date": "1990-01-01",
    "animation_speed": 200,
    "max_trails": 20
  },
  "web_app": {
    "port": 8050,
    "debug": true
  }
}
```

## 🌐 Web Application

The web application provides a full-featured dashboard with:

- **Interactive Controls**: Time slider, play/pause, speed control
- **Multiple Views**: Animation, 3D surface, heatmap
- **Real-time Updates**: Live FRED data integration
- **Export Options**: HTML, PNG, PDF

**Deployment Options:**
- Local development: `python app.py --web`
- Production: Deploy to Heroku, AWS, or Azure
- Static export: Generate standalone HTML files

## 📊 Data Sources

### Federal Reserve Economic Data (FRED)
- **Real-time**: Direct API integration
- **Historical**: 30+ years of data
- **Coverage**: All major Treasury maturities
- **Quality**: High-frequency, cleaned data

### Sample Data
- **Realistic**: Mathematically generated curves
- **Testing**: Perfect for development and demos
- **No API Required**: Works offline

## 🚀 Advanced Usage

### Programmatic Access

```python
from web_yield_curve_visualizer import WebYieldCurveVisualizer

# Create visualizer
viz = WebYieldCurveVisualizer(fred_api_key="your_key")

# Load data
viz.load_fred_data(start_date='2020-01-01')

# Create visualizations
animated_fig = viz.create_animated_plot()
surface_fig = viz.create_3d_surface_plot()
heatmap_fig = viz.create_heatmap()

# Export
viz.export_to_html('my_yield_curves.html')
```

### Web Application Integration

```python
# Create Dash app
app = viz.create_dash_app()

# Customize and deploy
app.run_server(
    debug=False,
    port=8080,
    host='0.0.0.0'  # For cloud deployment
)
```

## 🧪 Testing & Assessment

Run comprehensive tests to verify functionality:

```bash
python app.py --assess
```

**Assessment includes:**
- ✅ FRED API connectivity
- ✅ Data quality validation
- ✅ Visualization engine testing
- ✅ Performance benchmarking
- ✅ User experience evaluation

## 🛠️ Development

### Requirements
- Python 3.8+
- Internet connection (for FRED data)
- Modern web browser

### Dependencies
- `pandas` >= 1.3.0 - Data manipulation
- `plotly` >= 5.0.0 - Interactive visualizations
- `dash` >= 2.0.0 - Web application framework
- `fredapi` >= 0.5.0 - FRED API integration
- `numpy` >= 1.21.0 - Numerical computing

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Submit a pull request

## 📈 Use Cases

### Financial Analysis
- **Recession Prediction**: Monitor yield curve inversions
- **Policy Analysis**: Track Federal Reserve impacts
- **Risk Management**: Understand term structure risk
- **Portfolio Optimization**: Duration and convexity analysis

### Education & Research
- **Macroeconomics Teaching**: Visual learning tool
- **Academic Research**: Historical analysis
- **Student Projects**: Real data access
- **Financial Literacy**: Understanding bond markets

### Professional Applications
- **Investment Banks**: Client presentations
- **Asset Management**: Portfolio analysis
- **Central Banks**: Policy communication
- **Financial Media**: Market commentary

## 🔍 Technical Details

### Performance
- **Data Processing**: Pandas optimized operations
- **Visualization**: GPU-accelerated Plotly rendering
- **Memory Efficient**: Streaming data processing
- **Responsive**: <100ms interaction latency

### Browser Compatibility
- ✅ Chrome/Edge: Full support
- ✅ Firefox: Full support  
- ✅ Safari: Full support
- ✅ Mobile: Responsive design

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💼 Author

**Valentin Ivanov**
- Economics & Finance Professional
- Python Developer
- Data Visualization Specialist

## 🙏 Acknowledgments

- Federal Reserve Bank of St. Louis for FRED API
- Plotly team for excellent visualization library
- Python community for amazing data science tools

## 📞 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Check existing documentation
- Review the assessment output for troubleshooting

---

⭐ **Star this repository if you find it useful!**
