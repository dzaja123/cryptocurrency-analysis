"""
Main module for cryptocurrency data analysis.

This module orchestrates the fetching and analysis of cryptocurrency data
by utilizing the CryptoDataFetcher and CryptoAnalyzer classes, and provides
a modern GUI interface for user interaction.
"""

from typing import Optional, List, Dict, Any

import os
import pandas as pd

from PIL import Image, ImageTk

from crypto_gui.crypto_gui import CryptoGUI
from crypto_data_fetcher.crypto_data_fetcher import CryptoDataFetcher
from crypto_analyzer.crypto_analyzer import CryptoAnalyzer

from utils import setup_logger

# Set up centralized logging
logger = setup_logger()


class CryptoApp:
    """Main application class for cryptocurrency analysis."""
    
    def __init__(self, config_file: str) -> None:
        """Initialize the application with configuration.
        
        Args:
            config_file: Path to the configuration file
        """
        self.config_file = config_file
        self.data_fetcher = CryptoDataFetcher(config_file)
        self.analyzer = CryptoAnalyzer(config_file)
        self.gui: Optional[CryptoGUI] = None
        self.export_format: str = 'png'
        self.selected_coin: Optional[str] = None
        self.current_image = None

    def set_export_format(self, value: str) -> None:
        """Set the export format from GUI.
        
        Args:
            value: The export format to set (e.g., 'png', 'jpg')
        """
        self.export_format = value
        logger.debug("Export format set to: %s", value)

    def fetch_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
        """Fetch historical cryptocurrency data.
        
        Args:
            start_date: Optional start date for data fetching (YYYY-MM-DD)
            end_date: Optional end date for data fetching (YYYY-MM-DD)
            
        Raises:
            Exception: If no data was fetched or other errors occur
        """
        try:
            logger.info("Starting data fetch...")
            if hasattr(self.gui, 'current_coin'):
                coin = self.gui.current_coin
                if coin != "ALL COINS":
                    self.selected_coin = coin
                    # Create coin configuration for manually added coins
                    symbol = f"{coin}/USDT"
                    coin_config = {
                        'symbol': symbol,
                        'exchange': 'binance'  # Using binance as default exchange
                    }
                    
                    historical_data = self.data_fetcher.fetch_historical_data(
                        coin_config['symbol'],
                        coin_config['exchange'],
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    # Save the fetched data
                    if not historical_data.empty:
                        # Ensure the data directory exists
                        os.makedirs(os.path.dirname(self.analyzer.csv_file_path), exist_ok=True)
                        
                        # If file exists, append new data, otherwise create new file
                        if os.path.exists(self.analyzer.csv_file_path):
                            existing_data = pd.read_csv(self.analyzer.csv_file_path)
                            # Remove existing data for this coin to avoid duplicates
                            existing_data = existing_data[~existing_data['coin'].str.startswith(coin)]
                            # Combine existing data with new data
                            combined_data = pd.concat([existing_data, historical_data], ignore_index=True)
                            combined_data.to_csv(self.analyzer.csv_file_path, index=False)
                        else:
                            historical_data.to_csv(self.analyzer.csv_file_path, index=False)
                        
                        # Reload data in analyzer
                        self.analyzer.load_data()
                else:
                    historical_data = self.data_fetcher.fetch_all_data(start_date=start_date, end_date=end_date)
            else:
                historical_data = self.data_fetcher.fetch_all_data(start_date=start_date, end_date=end_date)

            if historical_data.empty:
                logger.error("No data was fetched")
                raise Exception("No data was fetched")
            logger.info("Data fetch completed successfully")

        except Exception as e:
            logger.error("Error fetching data: %s", str(e))
            raise

    def analyze_data(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
        """Analyze cryptocurrency data.
        
        Args:
            start_date: Optional start date for analysis (YYYY-MM-DD)
            end_date: Optional end date for analysis (YYYY-MM-DD)
            
        Raises:
            Exception: If no data is available or other errors occur
        """
        try:
            output_path = None
            logger.info("Starting data analysis...")
            if hasattr(self.gui, 'current_coin'):
                coin = self.gui.current_coin
                if coin != "ALL COINS":
                    self.selected_coin = coin
                    # Reload data to ensure we have the latest
                    self.analyzer.load_data()
                    
                    # Check if we have data for this coin
                    coin_data = self.analyzer.data[self.analyzer.data['coin'].str.startswith(coin)]
                    if coin_data.empty:
                        raise Exception(f"No data available for {coin}. Please fetch data first.")

                    # Create coin configuration for manually added coins
                    symbol = f"{coin}/USDT"

                    # Calculate technical indicators with date range
                    self.analyzer.calculate_technical_indicators(symbol, start_date=start_date, end_date=end_date)
                    
                    # Predict future prices with date range
                    self.analyzer.predict_future_prices(symbol, start_date=start_date, end_date=end_date)
                    
                    # Generate and save the analysis plots with date range
                    output_path = self.analyzer.plot_analysis(
                        coin,
                        export_format=self.export_format,
                        start_date=start_date,
                        end_date=end_date
                    )
                    
                    logger.info("Analysis completed for %s", coin)
                else:
                    # Analyze all coins with date range
                    self._analyze_all_coins(start_date=start_date, end_date=end_date)
                    logger.info("Analysis completed for all coins")

                if output_path:
                    self.display_result_image(output_path)
                    logger.info("Result image displayed for %s", coin)

            else:
                # Default to analyzing all coins if no coin is selected
                self._analyze_all_coins(start_date=start_date, end_date=end_date)
                logger.info("Analysis completed for all coins")

        except Exception as e:
            logger.error("Error during analysis: %s", str(e))
            raise

    def _analyze_all_coins(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> None:
        """Helper method to analyze all coins.
        
        Args:
            start_date: Optional start date for analysis (YYYY-MM-DD)
            end_date: Optional end date for analysis (YYYY-MM-DD)
            
        Raises:
            Exception: If no data is available or other errors occur
        """
        if self.analyzer.data is None or self.analyzer.data.empty:
            raise Exception("No data available. Please fetch data first.")

        for coin_config in self.data_fetcher.coins:
            try:
                coin = coin_config['symbol']
                coin_data = self.analyzer.data[self.analyzer.data['coin'] == coin]
                if not coin_data.empty:
                    self.analyzer.calculate_technical_indicators(coin, start_date=start_date, end_date=end_date)
                    self.analyzer.predict_future_prices(coin, start_date=start_date, end_date=end_date)
                    self.analyzer.plot_analysis(
                        coin,
                        export_format=self.export_format,
                        start_date=start_date,
                        end_date=end_date
                    )
            except Exception as e:
                logger.error("Error analyzing %s: %s", coin, str(e))
                continue

    def display_result_image(self, image_path: str) -> None:
        """Display the analysis result image in the scrollable canvas.
        
        Args:
            image_path: Path to the image file to display
            
        Raises:
            Exception: If there's an error loading or displaying the image
        """
        try:
            # Load and resize image
            image = Image.open(image_path)

            # Calculate new width while maintaining aspect ratio
            canvas_width = self.gui.result_canvas.winfo_width()
            ratio = canvas_width / image.width
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(image)

            # Update canvas
            self.gui.result_canvas.delete("all")
            self.current_image = photo  # Keep a reference
            self.gui.result_canvas.create_image(0, 0, anchor="nw", image=photo)
            self.gui.result_canvas.config(scrollregion=(0, 0, new_size[0], new_size[1]))

        except Exception as e:
            logger.error("Error displaying result image: %s", str(e))
            raise

    def search_coin(self, symbol: str) -> bool:
        """Search if a coin exists on the exchange.
        
        Args:
            symbol: The cryptocurrency symbol to search for
            
        Returns:
            bool: True if the coin exists, False otherwise
            
        Raises:
            Exception: If there's an error during the search
        """
        try:
            return self.data_fetcher.search_coin(symbol)
        except Exception as e:
            logger.error("Error searching for coin: %s", str(e))
            raise

    def fetch_top_coins(self) -> List[Dict[str, Any]]:
        """Fetch top 15 coins by market cap.
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing coin information
            
        Raises:
            Exception: If there's an error fetching top coins
        """
        try:
            return self.data_fetcher.fetch_top_coins(limit=15)
        except Exception as e:
            logger.error("Error fetching top coins: %s", str(e))
            raise


def main() -> None:
    """Main function to run the cryptocurrency analysis application.
    
    Raises:
        Exception: If there's an error starting or running the application
    """
    try:
        logger.info("Starting Crypto Analysis Application")
        # Initialize the application
        config_file = "config.yaml"
        app = CryptoApp(config_file)

        # Create and run the GUI
        app.gui = CryptoGUI(
            fetch_data_callback=app.fetch_data,
            analyze_data_callback=app.analyze_data,
            set_export_format_callback=app.set_export_format,
            search_coin_callback=app.search_coin,
            fetch_top_coins_callback=app.fetch_top_coins
        )
        # Start the GUI event loop
        app.gui.run()

    except Exception as e:
        logger.error("Application error: %s", str(e))
        logger.exception("Full error traceback:")
        raise


# Run the application
if __name__ == "__main__":
    main()
