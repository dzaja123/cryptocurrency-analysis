# Cryptocurrency Analysis Dashboard

A comprehensive Python application for cryptocurrency data analysis, featuring real-time data fetching, technical analysis, and interactive visualizations.

## Features

- **Real-time Data Fetching**
  - Integration with multiple cryptocurrency exchanges via CCXT
  - Historical price data retrieval (OHLCV)
  - Configurable date ranges and trading pairs
  - Automated data updates

- **Technical Analysis**
  - Moving Averages (7, 20, 50 days)
  - Relative Strength Index (RSI)
  - Moving Average Convergence Divergence (MACD)
  - Bollinger Bands
  - Price prediction using Random Forest Regressor

- **Interactive Visualization**
  - Dynamic candlestick charts
  - Technical indicator overlays
  - Interactive HTML plots using Plotly
  - Embedded web viewer in GUI

- **Modern GUI Interface**
  - Dark theme using CustomTkinter
  - Real-time status updates
  - Coin selection dropdown
  - Threaded operations for responsiveness

## Project Structure

```
cryptocurrency-analysis/
├── crypto_analyzer/          # Technical analysis module
├── crypto_data_fetcher/      # Data fetching module
├── crypto_gui/               # GUI interface module
├── utils/                    # Utility functions
├── data/                     # Data storage
├── logs/                     # Application logs
├── analysis_results/         # Analysis output
└── config.yaml               # Configuration file
```

## Requirements

- Python 3.10+
- Dependencies:
  ```
  pandas>=1.5.0
  numpy>=1.23.0
  ccxt>=4.0.0
  plotly>=5.13.0
  scikit-learn>=1.2.0
  customtkinter>=5.1.2
  pyyaml>=6.0.0
  tkinterweb>=3.16.0
  ```

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd cryptocurrency-analysis
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure `config.yaml`:
   ```yaml
   coins:
     - symbol: "SOL/USDT"
       exchange: "binance"
   csv_file_path: "data/combined_crypto_data.csv"
   output_dir: "analysis_results"
   start_date: "2017-01-01"
   end_date: "now"
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Using the GUI:
   - Click "Fetch Data" to retrieve historical cryptocurrency data
   - Select a coin from the dropdown menu
   - Click "Analyze Data" to generate technical analysis
   - View interactive charts and analysis results in the embedded viewer

## Architecture

- **Modular Design**: Separate packages for data fetching, analysis, and GUI
- **Event-Driven**: Threaded operations for non-blocking UI
- **Configurable**: External YAML configuration for easy customization
- **Extensible**: Easy to add new technical indicators or data sources

## Logging

- Centralized logging system
- Log file: `logs/crypto_analysis.log`
- Includes timestamps, module names, and log levels
- Both file and console output

## Error Handling

- Comprehensive error handling for network issues
- Data validation and integrity checks
- User-friendly error messages in GUI
- Detailed error logging for debugging

## Future Enhancements

- Additional technical indicators
- Support for more cryptocurrency exchanges
- Advanced prediction models
- Portfolio tracking features
- Real-time price alerts

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
