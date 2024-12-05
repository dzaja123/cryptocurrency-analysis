"""
Cryptocurrency Data Fetcher

This module handles fetching historical cryptocurrency data from various exchanges
using the CCXT library.
"""

from datetime import datetime

import time
import yaml
import ccxt

import pandas as pd

from utils import setup_logger

# Set up logger for this module
logger = setup_logger()


class CryptoDataFetcher:
    """Class for fetching and processing crypto data."""
    def __init__(self, config_file: str = None, save_to_csv: bool = True):
        self.save_to_csv = save_to_csv
        self.config_file = config_file
        self.csv_file_path = self.load_config()
        self.coins = self.fetch_top_coins()

    def load_config(self) -> tuple:
        """Load coin configurations and CSV file path from a YAML file."""
        try:
            with open(self.config_file, 'r', encoding="utf-8") as file:
                config = yaml.safe_load(file)
            logger.info("Configuration successfully loaded from YAML.")
            return (
                config['csv_file_path']
            )
        except Exception as e:
            logger.error("Error loading configuration: %s", e)
            raise

    def fetch_historical_data(self, symbol: str, exchange: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Fetch historical data from the specified exchange."""
        exchange_class = getattr(ccxt, exchange)()
        
        # Parse dates
        if start_date:
            start_timestamp = datetime.strptime(start_date, "%Y-%m-%d").timestamp() * 1000
        else:
            # Default to 1 year ago if no start date provided
            start_timestamp = (datetime.now().timestamp() - 365 * 24 * 60 * 60) * 1000
            
        if end_date:
            end_timestamp = datetime.strptime(end_date, "%Y-%m-%d").timestamp() * 1000
        else:
            end_timestamp = datetime.now().timestamp() * 1000
            
        since = int(start_timestamp)
        data = []
        logger.info("Fetching data for %s on %s from %s to %s...", 
                   symbol, exchange, 
                   datetime.fromtimestamp(start_timestamp/1000).strftime('%Y-%m-%d'),
                   datetime.fromtimestamp(end_timestamp/1000).strftime('%Y-%m-%d'))

        while since < end_timestamp:
            try:
                ohlcv = exchange_class.fetch_ohlcv(symbol, timeframe="1d", since=since, limit=1000)
                if not ohlcv:
                    logger.warning("No data found for %s on %s.", symbol, exchange)
                    break
                data.extend(ohlcv)
                since = ohlcv[-1][0] + 86400000
                time.sleep(exchange_class.rateLimit / 1000)
            except ccxt.NetworkError as e:
                logger.error(
                    "Network error while fetching data for %s on %s: %s",
                    symbol,
                    exchange,
                    e
                )
                break
            except ccxt.ExchangeError as e:
                logger.error("Exchange error for %s on %s: %s", symbol, exchange, e)
                break

        if data:
            df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            # Convert timestamp to datetime in ISO format
            df['date'] = pd.to_datetime(df['date'], unit='ms').dt.strftime('%Y-%m-%d %H:%M:%S')
            # Add coin column using base currency from symbol (e.g., 'BTC/USDT' -> 'BTC')
            df['coin'] = symbol.split('/')[0]
            df['exchange'] = exchange
            
            # Filter data to the specified date range
            if start_date or end_date:
                df['date'] = pd.to_datetime(df['date'])
                if start_date:
                    df = df[df['date'] >= start_date]
                if end_date:
                    df = df[df['date'] <= end_date]
                df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
                
            return df
        return pd.DataFrame()

    def fetch_all_data(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Fetch historical data for all configured coins."""
        all_data = []
        for coin in self.coins:
            df = self.fetch_historical_data(coin['symbol'], coin['exchange'], start_date, end_date)
            if not df.empty:
                all_data.append(df)

        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            if self.save_to_csv:
                combined_data.to_csv(self.csv_file_path, index=False)
                logger.info("Data saved to %s", self.csv_file_path)
            return combined_data
        return pd.DataFrame()

    def fetch_top_coins(self, limit: int = 15) -> list:
        """Fetch top cryptocurrencies by market cap."""
        try:
            exchange = ccxt.binance()
            markets = exchange.fetch_markets()
            usdt_markets = [market for market in markets if market['quote'] == 'USDT']
            
            # Get tickers with market cap info
            tickers = exchange.fetch_tickers([market['symbol'] for market in usdt_markets[:50]])
            
            # Calculate market cap (price * circulating supply) and sort
            market_caps = []
            for symbol, ticker in tickers.items():
                if ticker['last'] and ticker['baseVolume']:
                    # Using volume as a proxy for circulating supply since it's not directly available
                    market_cap = ticker['last'] * ticker['baseVolume']
                    market_caps.append((symbol, market_cap))
            
            # Sort by market cap
            sorted_markets = sorted(
                market_caps,
                key=lambda x: x[1] or 0,
                reverse=True
            )
            
            return [{'symbol': symbol, 'exchange': 'binance'} for symbol, _ in sorted_markets[:limit]]
        except Exception as e:
            logger.error(f"Error fetching top coins: {e}")
            return []

    def search_coin(self, coin_symbol: str) -> bool:
        """Search if a coin exists on the exchange."""
        try:
            exchange = ccxt.binance()
            markets = exchange.fetch_markets()
            symbol = f"{coin_symbol.upper()}/USDT"
            return any(market['symbol'] == symbol for market in markets)
        except Exception as e:
            logger.error(f"Error searching for coin {coin_symbol}: {e}")
            return False
