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
    def __init__(self, config_file: str, save_to_csv: bool = True):
        self.config_file = config_file
        self.save_to_csv = save_to_csv
        self.coins, self.csv_file_path, self.start_date, self.end_date = self.load_config()
        self.start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        if self.end_date.lower() == "now":
            self.end_date = datetime.now()
        else:
            self.end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        logger.info(
            "Configuration loaded. Start date: %s, End date: %s",
            self.start_date,
            self.end_date
        )

    def load_config(self) -> tuple:
        """Load coin configurations, CSV file path, and date range from a YAML file."""
        try:
            with open(self.config_file, 'r', encoding="utf-8") as file:
                config = yaml.safe_load(file)
            logger.info("Configuration successfully loaded from YAML.")
            return (
                config['coins'],
                config['csv_file_path'],
                config['start_date'],
                config['end_date']
            )
        except Exception as e:
            logger.error("Error loading configuration: %s", e)
            raise

    def fetch_historical_data(self, symbol: str, exchange: str) -> pd.DataFrame:
        """Fetch historical data from the specified exchange."""
        exchange_class = getattr(ccxt, exchange)()
        since = int(self.start_date.timestamp() * 1000)
        data = []
        logger.info("Fetching data for %s on %s...", symbol, exchange)

        while since < self.end_date.timestamp() * 1000:
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
            return df
        return pd.DataFrame()

    def fetch_all_data(self) -> pd.DataFrame:
        """Fetch historical data for all configured coins."""
        all_data = []
        for coin in self.coins:
            df = self.fetch_historical_data(coin['symbol'], coin['exchange'])
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
            
            # Get tickers with volume info
            tickers = exchange.fetch_tickers([market['symbol'] for market in usdt_markets[:50]])
            
            # Sort by volume and get top ones
            sorted_markets = sorted(
                [(symbol, ticker['quoteVolume']) for symbol, ticker in tickers.items()],
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
