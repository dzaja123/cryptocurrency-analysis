"""
Cryptocurrency Data Analyzer

This module provides comprehensive analysis and visualization of cryptocurrency data,
including technical indicators, trend analysis, and price predictions.
"""

from datetime import timedelta

import os
import yaml
import pandas as pd
import numpy as np

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor

from utils import setup_logger

# Set up logger for this module
logger = setup_logger()


class CryptoAnalyzer:
    """Cryptocurrency Data Analyzer class."""
    def __init__(self, config_file: str):
        """Initialize the CryptoAnalyzer with the path to the config file."""
        self.config_file = config_file
        self.data = None
        self.config = self.load_config()
        self.csv_file_path = self.config['csv_file_path']
        self.output_dir = self.config['output_dir']

        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        self.load_data()

    def load_config(self):
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)

            # Convert relative paths to absolute paths
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            config['csv_file_path'] = os.path.join(base_dir, config['csv_file_path'])
            config['output_dir'] = os.path.join(base_dir, config['output_dir'])

            logger.info("Configuration loaded successfully from '%s'", self.config_file)
            return config
        except Exception as e:
            logger.error("Failed to load configuration from '%s': %s", self.config_file, str(e))
            raise

    def load_data(self):
        """Load data from the CSV file."""
        try:
            if not os.path.exists(self.csv_file_path):
                logger.warning(
                    "CSV file not found at '%s'. Creating an empty file with headers.",
                    self.csv_file_path
                )
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
                # Create an empty CSV with headers
                empty_df = pd.DataFrame(
                    columns=['date', 'coin', 'open', 'high', 'low', 'close', 'volume']
                )
                empty_df.to_csv(self.csv_file_path, index=False)
                self.data = empty_df
                return

            self.data = pd.read_csv(self.csv_file_path)
            if len(self.data) == 0:
                logger.warning("CSV file is empty. No data to analyze.")
                return

            # Handle datetime parsing with a more flexible format
            self.data['date'] = pd.to_datetime(self.data['date'], format='mixed')
            self.data = self.data.sort_values('date')
            logger.info(
                "Successfully loaded data from '%s' with %d records",
                self.csv_file_path,
                len(self.data)
            )
        except Exception as e:
            logger.error("Failed to load data from '%s': %s", self.csv_file_path, str(e))
            raise

    def calculate_technical_indicators(self, coin: str) -> pd.DataFrame:
        """Calculate various technical indicators for a specific coin."""
        try:
            logger.info("Calculating technical indicators for %s", coin)
            # Extract base coin from symbol if needed (e.g., "BTC/USDT" -> "BTC")
            base_coin = coin.split('/')[0] if '/' in coin else coin
            
            # Filter data for the specific coin
            coin_data = self.data[self.data['coin'] == base_coin].copy()
            
            if coin_data.empty:
                logger.warning("No data found for coin %s", coin)
                return pd.DataFrame()
                
            # Sort by date
            coin_data = coin_data.sort_values('date')
            
            # Calculate technical indicators
            coin_data['SMA_20'] = coin_data['close'].rolling(window=20).mean()
            coin_data['SMA_50'] = coin_data['close'].rolling(window=50).mean()
            coin_data['SMA_200'] = coin_data['close'].rolling(window=200).mean()
            
            # Calculate RSI
            delta = coin_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            coin_data['RSI'] = 100 - (100 / (1 + rs))
            
            # Calculate MACD
            exp1 = coin_data['close'].ewm(span=12, adjust=False).mean()
            exp2 = coin_data['close'].ewm(span=26, adjust=False).mean()
            coin_data['MACD'] = exp1 - exp2
            coin_data['Signal_Line'] = coin_data['MACD'].ewm(span=9, adjust=False).mean()
            
            # Calculate Bollinger Bands
            coin_data['BB_middle'] = coin_data['close'].rolling(window=20).mean()
            bb_std = coin_data['close'].rolling(window=20).std()
            coin_data['BB_upper'] = coin_data['BB_middle'] + (bb_std * 2)
            coin_data['BB_lower'] = coin_data['BB_middle'] - (bb_std * 2)
            
            logger.info("Technical indicators calculated successfully for %s", coin)
            return coin_data
            
        except Exception as e:
            logger.error("Error calculating technical indicators for %s: %s", coin, str(e))
            raise

    def prepare_prediction_data(self, data: pd.DataFrame, lookback: int = 60) -> tuple:
        """Prepare data for prediction model.
        
        Args:
            data (pd.DataFrame): Input data with features
            lookback (int): Number of previous time steps to use for prediction
            
        Returns:
            tuple: (X, y) where X is the input features and y is the target values
        """
        try:
            # Convert DataFrame to numpy array
            values = data.values
            
            # Create sequences of lookback days
            X, y = [], []
            for i in range(lookback, len(values)):
                X.append(values[i-lookback:i])
                y.append(values[i, 3])  # Close price is at index 3
                
            # Convert to numpy arrays
            X = np.array(X)
            y = np.array(y)
            
            # Reshape X to 2D array for RandomForest (samples, features)
            n_samples = X.shape[0]
            n_features = X.shape[1] * X.shape[2]
            X = X.reshape((n_samples, n_features))
            
            return X, y
            
        except Exception as e:
            logger.error("Error preparing prediction data: %s", str(e))
            raise

    def predict_future_prices(self, coin: str, days_ahead: int = 730) -> pd.DataFrame:
        """Predict future prices using Random Forest model."""
        try:
            logger.info("Predicting future prices for %s over %d days", coin, days_ahead)
            # Extract base coin from symbol if needed
            base_coin = coin.split('/')[0] if '/' in coin else coin
            
            # Get data for the specific coin
            coin_data = self.data[self.data['coin'] == base_coin].copy()
            
            if coin_data.empty:
                logger.warning("No data found for coin %s", coin)
                return pd.DataFrame()
            
            # Sort by date
            coin_data = coin_data.sort_values('date')
            
            # Prepare features - use same features for training and prediction
            features = ['open', 'high', 'low', 'close', 'volume', 'SMA_20', 'SMA_50']
            
            # Calculate technical indicators for features
            coin_data['SMA_20'] = coin_data['close'].rolling(window=20).mean()
            coin_data['SMA_50'] = coin_data['close'].rolling(window=50).mean()
            
            # Drop rows with NaN values
            coin_data = coin_data.dropna()
            
            if len(coin_data) < 60:  # Minimum required data points
                logger.warning("Insufficient data points for prediction")
                return pd.DataFrame()
            
            # Prepare data for prediction
            feature_data = coin_data[features].copy()
            X, y = self.prepare_prediction_data(feature_data, lookback=60)
            
            if len(X) == 0:
                logger.warning("No valid data after preparation")
                return pd.DataFrame()
            
            # Train model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Prepare last known data point for prediction
            last_data = feature_data.iloc[-60:].values
            last_sequence = last_data.reshape(1, -1)
            
            # Make predictions
            future_dates = pd.date_range(
                start=coin_data['date'].iloc[-1],
                periods=days_ahead + 1,
                freq='D'
            )[1:]
            
            predictions = []
            current_sequence = last_sequence
            
            # Initial prediction
            pred = model.predict(current_sequence)[0]
            predictions.append(pred)
            
            # Update sequence for subsequent predictions
            for _ in range(1, days_ahead):
                # Update the sequence by shifting and adding new prediction
                new_row = np.zeros(len(features))  # Create new row with features
                new_row[3] = pred  # Set close price (index 3)
                new_row[5] = np.mean(predictions[-20:]) if len(predictions) >= 20 else pred  # SMA_20
                new_row[6] = np.mean(predictions[-50:]) if len(predictions) >= 50 else pred  # SMA_50
                
                # Shift sequence and add new row
                current_sequence = current_sequence.reshape(-1, len(features))
                current_sequence = np.vstack([current_sequence[1:], new_row])
                current_sequence = current_sequence.reshape(1, -1)
                
                # Make next prediction
                pred = model.predict(current_sequence)[0]
                predictions.append(pred)
            
            # Create prediction DataFrame
            pred_df = pd.DataFrame({
                'date': future_dates,
                'predicted_price': predictions
            })
            
            logger.info("Price predictions completed for %s", coin)
            return pred_df
            
        except Exception as e:
            logger.error("Failed to predict prices for %s: %s", coin, str(e))
            raise

    def plot_analysis(self, coin: str, export_format='png') -> str:
        """Create comprehensive interactive plots for analysis."""
        try:
            # Extract base coin from symbol if needed
            base_coin = coin.split('/')[0] if '/' in coin else coin
            
            # Get the data for this coin
            coin_data = self.data[self.data['coin'] == base_coin].copy()
            
            if coin_data.empty:
                logger.warning("No data found for plotting analysis of %s", coin)
                return ""
            
            coin_data = self.calculate_technical_indicators(coin)
            predictions = self.predict_future_prices(coin)

            # Create subplots
            fig = make_subplots(
                rows=4,
                cols=1,
                subplot_titles=('Price and Moving Averages', 'Volume', 'RSI', 'MACD'),
                vertical_spacing=0.05,
                row_heights=[0.4, 0.2, 0.2, 0.2]
            )

            # Price and Moving Averages
            fig.add_trace(
                go.Candlestick(
                    x=coin_data['date'],
                    open=coin_data['open'],
                    high=coin_data['high'],
                    low=coin_data['low'],
                    close=coin_data['close'],
                    name='Price'
                ),
                row=1,
                col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=coin_data['date'],
                    y=coin_data['SMA_20'],
                    name='SMA_20',
                    line=dict(color='blue')
                ),
                row=1,
                col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=coin_data['date'],
                    y=coin_data['SMA_50'],
                    name='SMA_50',
                    line=dict(color='orange')
                ),
                row=1,
                col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=coin_data['date'],
                    y=coin_data['SMA_200'],
                    name='SMA_200',
                    line=dict(color='green')
                ),
                row=1,
                col=1
            )

            # Add predictions
            fig.add_trace(
                go.Scatter(
                    x=predictions['date'],
                    y=predictions['predicted_price'],
                    name='Price Prediction',
                    line=dict(color='red', dash='dash')
                ),
                row=1,
                col=1
            )

            # Volume
            fig.add_trace(
                go.Bar(
                    x=coin_data['date'],
                    y=coin_data['volume'],
                    name='Volume'
                ),
                row=2,
                col=1
            )

            # RSI
            fig.add_trace(
                go.Scatter(
                    x=coin_data['date'],
                    y=coin_data['RSI'],
                    name='RSI',
                    line=dict(color='purple')
                ),
                row=3,
                col=1
            )

            fig.add_hline(
                y=70,
                line_dash="dash",
                line_color="red",
                row=3,
                col=1
            )

            fig.add_hline(
                y=30,
                line_dash="dash",
                line_color="green",
                row=3,
                col=1
            )

            # MACD
            fig.add_trace(
                go.Scatter(
                    x=coin_data['date'],
                    y=coin_data['MACD'],
                    name='MACD',
                    line=dict(color='blue')
                ),
                row=4,
                col=1
            )

            fig.add_trace(
                go.Scatter(
                    x=coin_data['date'],
                    y=coin_data['Signal_Line'],
                    name='Signal Line',
                    line=dict(color='orange')
                ),
                row=4,
                col=1
            )

            # Update layout
            fig.update_layout(
                title=f'{base_coin} Analysis and Predictions',
                xaxis4_title="Date",
                height=1800,
                showlegend=True,
                xaxis_rangeslider_visible=False,
                plot_bgcolor='white',
                paper_bgcolor='white'
            )

            # Save PNG by default
            output_path_png = os.path.join(self.output_dir, f'analysis_{base_coin.lower()}.png')
            fig.write_image(output_path_png, engine='kaleido', scale=2)
            logger.info(
                "Successfully saved PNG analysis plot for %s to '%s'",
                coin,
                output_path_png
            )

            # Save HTML if requested
            if export_format == 'both':
                output_path_html = os.path.join(
                    self.output_dir,
                    f'analysis_{base_coin.lower()}.html'
                )
                fig.write_html(output_path_html)
                logger.info(
                    "Successfully saved HTML analysis plot for %s to '%s'",
                    coin,
                    output_path_html
                )

            return output_path_png

        except Exception as e:
            logger.error("Failed to create analysis plot for %s: %s", coin, str(e))
            raise

    def generate_summary_statistics(self, coin: str) -> dict:
        """Generate summary statistics for a specific coin."""
        coin_data = self.data[self.data['coin'] == coin].copy()

        # Calculate moving averages for market trend
        ma20 = coin_data['close'].rolling(window=20).mean()
        ma50 = coin_data['close'].rolling(window=50).mean()

        return {
            'current_price': coin_data['close'].iloc[-1],
            'all_time_high': coin_data['high'].max(),
            'all_time_low': coin_data['low'].min(),
            'daily_returns': coin_data['close'].pct_change().mean() * 100,
            'volatility': coin_data['close'].pct_change().std() * 100,
            'volume_24h': coin_data['volume'].iloc[-1],
            'market_trend': 'Bullish' if ma20.iloc[-1] > ma50.iloc[-1] else 'Bearish'
        }
