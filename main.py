"""
Main module for cryptocurrency data analysis.

This module orchestrates the fetching and analysis of cryptocurrency data
by utilizing the CryptoDataFetcher and CryptoAnalyzer classes, and provides
a modern GUI interface for user interaction.
"""

import os
import pandas as pd

from PIL import Image, ImageTk
import customtkinter as ctk

from crypto_data_fetcher.crypto_data_fetcher import CryptoDataFetcher
from crypto_analyzer.crypto_analyzer import CryptoAnalyzer
from crypto_gui.crypto_gui import CryptoGUI

from utils.logger_setup import LoggerManager
from utils.config_manager import ConfigManager

# Set up centralized logging and configuration
logger = LoggerManager.setup_logger()


class CryptoApp:
    """CryptoApp class for cryptocurrency analysis application."""
    def __init__(self, config_file):
        """Initialize the cryptocurrency analysis application."""
        # Configuration management
        self.config_manager = ConfigManager(config_file)
        self.config = self.config_manager.get_config()

        # Data fetcher instance
        self.data_fetcher = CryptoDataFetcher(self.config_manager)

        # Data analyzer instance
        self.analyzer = CryptoAnalyzer(self.config_manager)

        # Track currently selected coin
        self.selected_coin = None

        # Store reference to GUI
        self.gui = None

        # Store reference to displayed image
        self.current_image = None

        # Default export format
        self.export_format = "png"
        
        # Date range
        self.start_date = None
        self.end_date = None

    def set_export_format(self, value):
        """Set the export format from GUI."""
        self.export_format = value
        logger.debug("Export format set to: %s", value)

    def set_date_range(self, start_date: str, end_date: str):
        """Set the date range for data fetching."""
        self.start_date = start_date
        self.end_date = end_date
        logger.info(f"Date range updated: {start_date} to {end_date}")

    def fetch_data(self):
        """Fetch historical cryptocurrency data."""
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
                        start_date=self.start_date,
                        end_date=self.end_date
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
                    historical_data = self.data_fetcher.fetch_all_data(
                        start_date=self.start_date,
                        end_date=self.end_date
                    )
            else:
                historical_data = self.data_fetcher.fetch_all_data(
                    start_date=self.start_date,
                    end_date=self.end_date
                )

            if historical_data.empty:
                logger.error("No data was fetched")
                raise Exception("No data was fetched")
            logger.info("Data fetch completed successfully")

        except Exception as e:
            logger.error("Error fetching data: %s", str(e))
            raise

    def analyze_data(self):
        """Analyze cryptocurrency data."""
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

                    # Calculate technical indicators
                    self.analyzer.calculate_technical_indicators(symbol)
                    
                    # Predict future prices
                    self.analyzer.predict_future_prices(symbol)
                    
                    # Generate and save the analysis plots
                    output_path = self.analyzer.plot_analysis(coin, export_format=self.export_format)
                    
                    logger.info("Analysis completed for %s", coin)
                else:
                    # Analyze all coins
                    self._analyze_all_coins()
                    logger.info("Analysis completed for all coins")

                if output_path:
                    self.display_result_image(output_path)
                    logger.info("Result image displayed for %s", coin)

            else:
                # Default to analyzing all coins if no coin is selected
                self._analyze_all_coins()
                logger.info("Analysis completed for all coins")

        except Exception as e:
            logger.error("Error during analysis: %s", str(e))
            raise

    def display_result_image(self, image_path):
        """Display the analysis result image in the GUI."""
        try:
            # Load and resize image
            image = Image.open(image_path)

            # Calculate new width while maintaining aspect ratio
            canvas_width = self.gui.result_canvas.winfo_width()
            if canvas_width <= 1:  # If canvas not yet properly initialized
                canvas_width = 800  # Default width
            ratio = canvas_width / image.width
            new_size = (int(image.width * ratio), int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

            # Convert to CTkImage
            ctk_image = ctk.CTkImage(
                light_image=image,
                dark_image=image,
                size=new_size
            )

            # Update image label
            self.current_image = ctk_image  # Keep a reference
            self.gui.image_label.configure(image=ctk_image)
            
            # Update status
            self.gui.status_label.configure(text=f"Analysis complete! Results displayed for {os.path.basename(image_path)}")
        except Exception as e:
            logger.error("Error displaying result image: %s", str(e))
            self.gui.status_label.configure(text=f"Error displaying result: {str(e)}")

    def _analyze_all_coins(self):
        """Helper method to analyze all coins."""
        if self.analyzer.data is None or self.analyzer.data.empty:
            raise Exception("No data available. Please fetch data first.")

        for coin_config in self.data_fetcher.coins:
            try:
                coin = coin_config['symbol']
                coin_data = self.analyzer.data[self.analyzer.data['coin'] == coin]
                if not coin_data.empty:
                    self.analyzer.calculate_technical_indicators(coin)
                    self.analyzer.predict_future_prices(coin)
                    self.analyzer.plot_analysis(coin, export_format=self.export_format)
            except Exception as e:
                logger.error("Error analyzing %s: %s", coin, str(e))
                continue

    def search_coin(self, symbol: str) -> bool:
        """Search if a coin exists on the exchange."""
        try:
            return self.data_fetcher.search_coin(symbol)
        except Exception as e:
            logger.error("Error searching for coin: %s", str(e))
            raise

    def fetch_top_coins(self) -> list:
        """Fetch top 15 coins by market cap."""
        try:
            return self.data_fetcher.fetch_top_coins(limit=15)
        except Exception as e:
            logger.error("Error fetching top coins: %s", str(e))
            raise

    def initialize_gui(self):
        """Initialize and configure the GUI."""
        self.gui = CryptoGUI(
            fetch_data_callback=self.fetch_data,
            analyze_data_callback=self.analyze_data,
            set_export_format_callback=self.set_export_format,
            search_coin_callback=self.search_coin,
            fetch_top_coins_callback=self.fetch_top_coins,
            set_date_range_callback=self.set_date_range
        )


def main():
    """Main function to run the cryptocurrency analysis application."""
    try:
        logger.info("Starting Crypto Analysis Application")
        # Initialize the application
        config_file = "config.yaml"
        app = CryptoApp(config_file)

        # Create and run the GUI
        app.initialize_gui()
        # Start the GUI event loop
        app.gui.run()

    except Exception as e:
        logger.error("Application error: %s", str(e))
        logger.exception("Full error traceback:")
        raise


# Run the application
if __name__ == "__main__":
    main()
