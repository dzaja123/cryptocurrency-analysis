# Cryptocurrency Analysis Dashboard

A comprehensive Python application for cryptocurrency data analysis, featuring real-time data fetching, technical analysis, price predictions, and interactive visualizations. Built with modern libraries and a user-friendly GUI interface.

## Key Features

- **Real-time Data Fetching**
  - Integration with Binance exchange via CCXT
  - Historical price data retrieval (OHLCV)
  - Support for any cryptocurrency trading pair
  - Top coins by market cap discovery
  - Flexible date range selection with calendar widgets
  - Automated data updates

- **Advanced Technical Analysis**
  - Multiple Moving Averages (20, 50, 200 days)
  - Relative Strength Index (RSI)
  - Moving Average Convergence Divergence (MACD)
  - Bollinger Bands
  - Volume Analysis
  - Market Trend Detection
  - Price prediction using Random Forest (2-year forecast)
  - Date range filtered analysis

- **Interactive Visualization**
  - Dynamic candlestick charts
  - Technical indicator overlays
  - Volume analysis
  - Price prediction visualization
  - Export to PNG and HTML formats
  - Zoomable and pannable charts
  - Customizable time ranges
  - Date-filtered visualizations

- **Modern GUI Interface**
  - Dark theme using CustomTkinter
  - Real-time status updates
  - Coin search functionality
  - Top coins selection
  - Calendar widgets for date selection
  - Threaded operations for responsiveness
  - Progress indicators
  - Error handling and user feedback
  - Organized sidebar layout

## Project Structure

```
cryptocurrency-analysis/
├── crypto_analyzer/          # Technical analysis and visualization
├── crypto_data_fetcher/      # Data fetching and processing
├── crypto_gui/               # GUI interface and controls
├── utils/                    # Utility functions and logging
├── data/                     # Data storage
├── logs/                     # Application logs
├── analysis_results/         # Analysis output
└── config.yaml              # Configuration file
```

## Requirements

- Python 3.10+
- Dependencies:
  ```
  pandas>=1.5.0
  numpy>=1.23.0
  plotly>=5.13.0
  scikit-learn>=1.2.0
  ccxt>=4.0.0
  pyyaml>=6.0.0
  customtkinter>=5.1.2
  pillow>=9.0.0
  kaleido==0.1.*
  tkcalendar>=1.6.1
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dzaja123/cryptocurrency-analysis.git
   cd cryptocurrency-analysis
   ```

2. Set up a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure `config.yaml`:
   ```yaml
   csv_file_path: "data/combined_crypto_data.csv"
   output_dir: "analysis_results"
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Using the Interface:
   - Enter a cryptocurrency symbol in the search bar or select from top coins
   - Select a date range using the calendar widgets:
     * Start Date: Choose the beginning of your analysis period
     * End Date: Choose the end of your analysis period
     * Default: Last 365 days if no dates are selected
   - Choose your preferred export format (PNG/HTML)
   - Click "Fetch Data" to retrieve historical data
   - Click "Analyze Data" to generate analysis and visualizations

3. Data Persistence:
   - Historical data is saved in the `data` directory
   - Analysis results are stored in `analysis_results`
   - Application logs are maintained in `logs`
   - All data persists between sessions for offline analysis

## Features in Detail

### Data Fetching
- Historical OHLCV data retrieval
- Automatic pagination for large datasets
- Rate limiting compliance
- Error handling for network issues
- Data validation and cleaning
- CSV storage for offline analysis

### Technical Analysis
- **Moving Averages**: Short, medium, and long-term trends
- **RSI**: Overbought/oversold conditions
- **MACD**: Trend direction and momentum
- **Volume Analysis**: Trading activity patterns
- **Price Predictions**: Machine learning-based forecasting
- **Market Trends**: Automatic trend detection

### Visualization
- **Interactive Charts**: Zoomable candlestick patterns
- **Multiple Timeframes**: Daily to yearly analysis
- **Technical Overlays**: Indicators on price charts
- **Volume Bars**: Trading volume visualization
- **Prediction Lines**: Future price forecasts
- **Export Options**: PNG for sharing, HTML for interaction

### GUI Features
- **Modern Design**: Clean, intuitive interface
- **Real-time Updates**: Live status messages
- **Error Handling**: User-friendly error messages
- **Threading**: Non-blocking operations
- **Progress Tracking**: Visual feedback
- **File Management**: Automatic file handling

## Architecture

- **Modular Design**: Separate packages for core functionalities
- **Event-Driven**: Threaded operations for UI responsiveness
- **Configurable**: External YAML configuration
- **Extensible**: Easy to add new indicators or data sources
- **Maintainable**: Comprehensive logging and error handling

## Logging

- Centralized logging system
- Log file: `logs/crypto_analysis.log`
- Includes timestamps and module information
- Both file and console output
- Detailed error tracking

## Error Handling

- Comprehensive exception management
- Network error recovery
- Data validation checks
- User-friendly error messages
- Detailed error logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
