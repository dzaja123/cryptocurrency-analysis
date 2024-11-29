"""
Cryptocurrency Data Analyzer

This module provides comprehensive analysis and visualization of cryptocurrency data,
including technical indicators, trend analysis, and price predictions.
"""

import os
import yaml
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from datetime import datetime, timedelta
from plotly.subplots import make_subplots
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
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
        """Load and preprocess the cryptocurrency data."""
        try:
            if not os.path.exists(self.csv_file_path):
                logger.warning("CSV file not found at '%s'. Creating an empty file with headers.", self.csv_file_path)
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
                # Create an empty CSV with headers
                empty_df = pd.DataFrame(columns=['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
                empty_df.to_csv(self.csv_file_path, index=False)
                self.data = empty_df
                return

            self.data = pd.read_csv(self.csv_file_path)
            if len(self.data) == 0:
                logger.warning("CSV file is empty. No data to analyze.")
                return

            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data = self.data.sort_values('date')
            logger.info("Successfully loaded data from '%s' with %d records", 
                       self.csv_file_path, len(self.data))
        except pd.errors.EmptyDataError:
            logger.warning("CSV file is empty. Creating with headers.")
            empty_df = pd.DataFrame(columns=['date', 'symbol', 'open', 'high', 'low', 'close', 'volume'])
            empty_df.to_csv(self.csv_file_path, index=False)
            self.data = empty_df
        except Exception as e:
            logger.error("Failed to load data from '%s': %s", self.csv_file_path, str(e))
            raise RuntimeError(f"Failed to load or create data file: {str(e)}")

    def calculate_technical_indicators(self, coin: str) -> pd.DataFrame:
        """Calculate various technical indicators for a specific coin."""
        try:
            logger.info("Calculating technical indicators for %s", coin)
            coin_data = self.data[self.data['coin'] == coin].copy()
            if coin_data.empty:
                logger.warning("No data found for coin %s", coin)
                return pd.DataFrame()
                
            # Moving averages
            coin_data['MA7'] = coin_data['close'].rolling(window=7).mean()
            coin_data['MA20'] = coin_data['close'].rolling(window=20).mean()
            coin_data['MA50'] = coin_data['close'].rolling(window=50).mean()
            
            # RSI
            delta = coin_data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            coin_data['RSI'] = 100 - (100 / (1 + rs))
            
            # MACD
            exp1 = coin_data['close'].ewm(span=12, adjust=False).mean()
            exp2 = coin_data['close'].ewm(span=26, adjust=False).mean()
            coin_data['MACD'] = exp1 - exp2
            coin_data['Signal_Line'] = coin_data['MACD'].ewm(span=9, adjust=False).mean()
            
            # Bollinger Bands
            coin_data['BB_middle'] = coin_data['close'].rolling(window=20).mean()
            coin_data['BB_upper'] = coin_data['BB_middle'] + 2 * coin_data['close'].rolling(window=20).std()
            coin_data['BB_lower'] = coin_data['BB_middle'] - 2 * coin_data['close'].rolling(window=20).std()
            
            logger.info("Successfully calculated technical indicators for %s", coin)
            return coin_data
        except Exception as e:
            logger.error("Failed to calculate technical indicators for %s: %s", coin, str(e))
            raise

    def prepare_prediction_data(self, coin_data: pd.DataFrame, lookback: int = 60) -> tuple:
        """Prepare data for prediction model."""
        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(coin_data[['close']].values)
        
        X, y = [], []
        for i in range(lookback, len(scaled_data)):
            X.append(scaled_data[i-lookback:i, 0])
            y.append(scaled_data[i, 0])
            
        X, y = np.array(X), np.array(y)
        return X, y, scaler

    def predict_future_prices(self, coin: str, days_ahead: int = 730) -> pd.DataFrame:
        """Predict future prices using Random Forest model."""
        try:
            logger.info("Predicting future prices for %s over %d days", coin, days_ahead)
            coin_data = self.data[self.data['coin'] == coin].copy()
            
            # Prepare features for Random Forest
            lookback = 60
            features = ['open', 'high', 'low', 'close', 'volume']
            rf_data = coin_data[features].values
            X, y = [], []
            
            for i in range(lookback, len(rf_data)):
                X.append(rf_data[i-lookback:i].flatten())
                y.append(rf_data[i, 3])  # Close price
                
            X, y = np.array(X), np.array(y)
            
            # Train Random Forest model
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, y)
            
            # Generate future dates
            last_date = coin_data['date'].iloc[-1]
            future_dates = pd.date_range(start=last_date + timedelta(days=1), 
                                       periods=days_ahead, freq='D')
            
            # Make predictions
            predictions = []
            last_sequence = X[-1]
            
            for _ in range(days_ahead):
                pred_price = model.predict(last_sequence.reshape(1, -1))[0]
                predictions.append(pred_price)
                # Update the sequence for next prediction
                last_sequence = np.roll(last_sequence, -5)
                last_sequence[-5:] = [pred_price] * 5
            
            # Create prediction DataFrame
            predictions_df = pd.DataFrame({
                'date': future_dates,
                'prediction': predictions
            })
            
            logger.info("Successfully generated price predictions for %s", coin)
            return predictions_df
        except Exception as e:
            logger.error("Failed to predict prices for %s: %s", coin, str(e))
            raise

    def plot_analysis(self, coin: str):
        """Create comprehensive interactive plots for analysis."""
        try:
            logger.info("Creating analysis plot for %s", coin)
            # Remove /USDT from coin name
            coin_name = coin.split('/')[0]
            
            coin_data = self.calculate_technical_indicators(coin)
            predictions = self.predict_future_prices(coin)
            
            # Create subplots
            fig = make_subplots(rows=4, cols=1, 
                               subplot_titles=('Price and Moving Averages', 'Volume', 'RSI', 'MACD'),
                               vertical_spacing=0.05,
                               row_heights=[0.4, 0.2, 0.2, 0.2])

            # Price and Moving Averages
            fig.add_trace(go.Candlestick(x=coin_data['date'],
                                        open=coin_data['open'],
                                        high=coin_data['high'],
                                        low=coin_data['low'],
                                        close=coin_data['close'],
                                        name='Price'),
                         row=1, col=1)
            
            fig.add_trace(go.Scatter(x=coin_data['date'], y=coin_data['MA7'],
                                    name='MA7', line=dict(color='blue')), row=1, col=1)
            fig.add_trace(go.Scatter(x=coin_data['date'], y=coin_data['MA20'],
                                    name='MA20', line=dict(color='orange')), row=1, col=1)
            fig.add_trace(go.Scatter(x=coin_data['date'], y=coin_data['MA50'],
                                    name='MA50', line=dict(color='green')), row=1, col=1)
            
            # Add predictions
            fig.add_trace(go.Scatter(x=predictions['date'], y=predictions['prediction'],
                                    name='Price Prediction', line=dict(color='red', dash='dash')), row=1, col=1)
            
            # Volume
            fig.add_trace(go.Bar(x=coin_data['date'], y=coin_data['volume'],
                                name='Volume'), row=2, col=1)
            
            # RSI
            fig.add_trace(go.Scatter(x=coin_data['date'], y=coin_data['RSI'],
                                    name='RSI', line=dict(color='purple')), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=3, col=1)
            
            # MACD
            fig.add_trace(go.Scatter(x=coin_data['date'], y=coin_data['MACD'],
                                    name='MACD', line=dict(color='blue')), row=4, col=1)
            fig.add_trace(go.Scatter(x=coin_data['date'], y=coin_data['Signal_Line'],
                                    name='Signal Line', line=dict(color='orange')), row=4, col=1)
            
            # Update layout
            fig.update_layout(
                title=f'{coin_name} Analysis and Predictions',
                xaxis4_title="Date",
                height=1800,
                showlegend=True,
                xaxis_rangeslider_visible=False
            )
            
            # Save the plot in the output directory with proper coin name
            output_path = os.path.join(self.output_dir, f'analysis_{coin_name.lower()}.html')
            fig.write_html(output_path)
            logger.info("Successfully saved analysis plot for %s to '%s'", coin, output_path)
            
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
