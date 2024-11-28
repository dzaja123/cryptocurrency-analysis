"""
Cryptocurrency Analysis GUI

This module provides a modern graphical user interface for the cryptocurrency
analysis application using CustomTkinter.
"""

import threading
import os
import yaml
import customtkinter as ctk
import tkinterweb

from utils import setup_logger

# Set up logger for this module
logger = setup_logger()


class CryptoGUI:
    """Class for cryptocurrency analysis GUI interface."""
    def __init__(self, fetch_data_callback: callable, analyze_data_callback: callable):
        """Initialize the GUI with callback functions for data operations."""
        logger.info("Initializing Cryptocurrency Analysis GUI")
        
        # Set theme and color scheme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize main window
        self.root = ctk.CTk()
        self.root.title("Cryptocurrency Analysis Dashboard")
        self.root.geometry("1200x800")
        
        # Store callbacks
        self.fetch_data = fetch_data_callback
        self.analyze_data = analyze_data_callback
        
        # Load configuration
        self.config_file = 'config.yaml'
        
        # Initialize GUI components
        self._create_sidebar()
        self._create_main_area()
        
        logger.info("GUI initialization completed")
        
    def _load_coins(self) -> list:
        """Load available coins from configuration."""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                coins = [coin['symbol'].split('/')[0] for coin in config.get('coins', [])]
                coins.insert(0, "ALL COINS")  # Add "ALL COINS" option at the beginning
                logger.info("Successfully loaded %d coins from configuration", len(coins)-1)
                return coins
        except Exception as e:
            logger.error("Failed to load coins from configuration: %s", str(e))
            return ["ALL COINS"]  # Return at least "ALL COINS" option

    def _create_sidebar(self):
        """Create the sidebar with controls."""
        try:
            logger.debug("Creating sidebar controls")
            # Sidebar frame
            self.sidebar = ctk.CTkFrame(self.root, width=200)
            self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
            
            # Title
            title = ctk.CTkLabel(self.sidebar, 
                               text="Controls", 
                               font=ctk.CTkFont(size=20, weight="bold"))
            title.pack(pady=10)
            
            # Coin selection
            coins = self._load_coins()
            self.selected_coin = ctk.StringVar(value=coins[0])
            
            coin_label = ctk.CTkLabel(self.sidebar, 
                                    text="Select Coin:",
                                    anchor="center")
            coin_label.pack(pady=5)
            
            self.coin_dropdown = ctk.CTkOptionMenu(
                self.sidebar,
                values=coins,
                variable=self.selected_coin,
                command=self._handle_coin_selection,
                anchor="center",
                width=150,  
                dynamic_resizing=False  
            )
            self.coin_dropdown.pack(pady=5, padx=10)  
            
            # Buttons
            self.fetch_button = ctk.CTkButton(
                self.sidebar,
                text="Fetch Data",
                command=self._handle_fetch_data
            )
            self.fetch_button.pack(pady=10)
            
            self.analyze_button = ctk.CTkButton(
                self.sidebar,
                text="Analyze Data",
                command=self._handle_analyze_data
            )
            self.analyze_button.pack(pady=10)
            
            # Status label
            self.status_label = ctk.CTkLabel(self.sidebar, 
                                           text="Ready",
                                           wraplength=180)
            self.status_label.pack(pady=10)
            
            logger.debug("Sidebar controls created successfully")
        except Exception as e:
            logger.error("Failed to create sidebar: %s", str(e))
            raise

    def _create_main_area(self):
        """Create the main display area."""
        try:
            logger.debug("Creating main display area")
            
            # Clear existing main area if it exists
            if hasattr(self, 'main_area'):
                self.main_area.destroy()
            
            self.main_area = ctk.CTkFrame(self.root)
            self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)
            
            # Create HTML viewer
            self.html_viewer = tkinterweb.HtmlFrame(self.main_area)
            self.html_viewer.pack(fill="both", expand=True)
            
            # Load initial message with better formatting
            self.html_viewer.load_html("""
                <div style='text-align: center; padding: 40px; font-family: Arial, sans-serif;'>
                    <h1 style='color: #2986cc; margin-bottom: 30px;'>Cryptocurrency Analysis Dashboard</h1>
                    
                    <div style='max-width: 600px; margin: 0 auto; text-align: left; line-height: 1.6;'>
                        <h2 style='color: #666; margin-bottom: 20px;'>Quick Start Guide:</h2>
                        
                        <ol style='color: #444; font-size: 16px;'>
                            <li style='margin-bottom: 15px;'>
                                <strong>Select a Coin</strong>
                                <p>Choose a specific cryptocurrency or "ALL COINS" from the dropdown menu.</p>
                            </li>
                            
                            <li style='margin-bottom: 15px;'>
                                <strong>Fetch Data</strong>
                                <p>Click "Fetch Data" to retrieve historical price data for the selected coin(s).</p>
                            </li>
                            
                            <li style='margin-bottom: 15px;'>
                                <strong>Analyze Data</strong>
                                <p>Click "Analyze Data" to generate technical analysis and predictions.</p>
                            </li>
                            
                            <li style='margin-bottom: 15px;'>
                                <strong>View Results</strong>
                                <p>Analysis results will be displayed here with interactive charts and indicators.</p>
                            </li>
                        </ol>
                        
                        <p style='color: #666; margin-top: 30px; font-style: italic;'>
                            Note: Fetching and analyzing data may take a few moments depending on the selected timeframe and number of coins.
                        </p>
                    </div>
                </div>
            """)
            logger.debug("Main display area created successfully")
        except Exception as e:
            logger.error("Failed to create main display area: %s", str(e))
            raise

    def _handle_fetch_data(self):
        """Handle fetch data button click."""
        selected_coin = self.selected_coin.get()
        logger.info("Initiating data fetch operation for %s", selected_coin)
        self.status_label.configure(text=f"Fetching data for {selected_coin}...")
        self.fetch_button.configure(state="disabled")
        
        try:
            threading.Thread(target=lambda: self._fetch_data_thread(selected_coin), 
                           daemon=True).start()
        except Exception as e:
            error_msg = f"Failed to start data fetch: {str(e)}"
            logger.error(error_msg)
            self.status_label.configure(text=error_msg)
            self.fetch_button.configure(state="normal")

    def _fetch_data_thread(self, selected_coin: str):
        """Run data fetching in a separate thread."""
        try:
            # Store selected coin in a class variable for the callback to use
            self.current_coin = selected_coin
            self.fetch_data()  # Call without parameters
            
            logger.info("Data fetch completed successfully for %s", selected_coin)
            self.status_label.configure(text=f"Data fetch completed for {selected_coin}")
        except Exception as e:
            error_msg = f"Error during data fetch: {str(e)}"
            logger.error(error_msg)
            self.root.after(0, lambda: self.status_label.configure(text=error_msg))
        finally:
            self.root.after(0, lambda: self.fetch_button.configure(state="normal"))
            
    def _handle_analyze_data(self):
        """Handle analyze data button click."""
        selected_coin = self.selected_coin.get()
        logger.info("Initiating data analysis operation for %s", selected_coin)
        self.status_label.configure(text=f"Analyzing {selected_coin}...")
        self.analyze_button.configure(state="disabled")
        
        try:
            threading.Thread(target=lambda: self._analyze_data_thread(selected_coin), 
                           daemon=True).start()
        except Exception as e:
            error_msg = f"Failed to start analysis: {str(e)}"
            logger.error(error_msg)
            self.status_label.configure(text=error_msg)
            self.analyze_button.configure(state="normal")

    def _analyze_data_thread(self, selected_coin: str):
        """Run data analysis in a separate thread."""
        try:
            # Store selected coin in a class variable for the callback to use
            self.current_coin = selected_coin
            self.analyze_data()  # Call without parameters
            
            logger.info("Analysis completed successfully for %s", selected_coin)
            self.status_label.configure(text=f"Analysis completed for {selected_coin}")
            self._update_analysis_files()
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            logger.error(error_msg)
            self.root.after(0, lambda: self.status_label.configure(text=error_msg))
        finally:
            self.root.after(0, lambda: self.analyze_button.configure(state="normal"))

    def _update_analysis_files(self):
        """Update the coin dropdown with available analysis files."""
        try:
            logger.debug("Updating analysis files list")
            with open(self.config_file, 'r', encoding='utf-8') as file:
                config = yaml.safe_load(file)
                output_dir = config.get('output_dir', 'analysis_results')
                
                if os.path.exists(output_dir):
                    all_files = os.listdir(output_dir)
                    all_coins = ["ALL COINS"]  # Always include "ALL COINS" option
                    analyzed_coins = [f.replace('analysis_', '').replace('.html', '').upper() 
                                    for f in all_files if f.startswith('analysis_')]
                    all_coins.extend(analyzed_coins)
                    
                    if analyzed_coins:
                        self.coin_dropdown.configure(values=all_coins)
                        logger.info("Found %d analysis files", len(analyzed_coins))
                    else:
                        logger.warning("No analysis files found in %s", output_dir)
                        self.coin_dropdown.configure(values=["ALL COINS"])
                else:
                    logger.warning("Output directory %s does not exist", output_dir)
        except Exception as e:
            logger.error("Failed to update analysis files: %s", str(e))
            self.status_label.configure(text=f"Error updating files: {str(e)}")

    def _handle_coin_selection(self, coin: str):
        """Handle coin selection from dropdown."""
        try:
            logger.debug("Selected coin: %s", coin)
            if coin == "ALL COINS":
                # Show welcome screen with instructions
                self._create_main_area()  # This will now properly clear existing content
                return
                
            # Clear existing main area if it exists
            if hasattr(self, 'main_area'):
                self.main_area.destroy()
                
            self.main_area = ctk.CTkFrame(self.root)
            self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)
            
            # Create new HTML viewer
            self.html_viewer = tkinterweb.HtmlFrame(self.main_area)
            self.html_viewer.pack(fill="both", expand=True)
            
            if coin != "No coins available" and coin != "No analysis files":
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    output_dir = config.get('output_dir', 'analysis_results')
                    analysis_file = os.path.join(output_dir, f'analysis_{coin.lower()}.html')
                    
                    if os.path.exists(analysis_file):
                        with open(analysis_file, 'r', encoding='utf-8') as html_file:
                            self.html_viewer.load_html(html_file.read())
                            logger.info("Successfully loaded analysis for %s", coin)
                    else:
                        logger.warning("Analysis file not found for %s", coin)
                        self.html_viewer.load_html(f"""
                            <div style='text-align: center; padding: 40px; font-family: Arial, sans-serif;'>
                                <h2 style='color: #666;'>No Analysis Available for {coin}</h2>
                                <p style='color: #444; margin-top: 20px;'>
                                    To generate analysis for {coin}:
                                </p>
                                <ol style='text-align: left; max-width: 400px; margin: 20px auto;'>
                                    <li style='margin: 10px 0;'>Click "Fetch Data" to retrieve the latest data</li>
                                    <li style='margin: 10px 0;'>Click "Analyze Data" to generate the analysis</li>
                                </ol>
                            </div>
                        """)
        except Exception as e:
            error_msg = f"Error viewing analysis: {str(e)}"
            logger.error(error_msg)
            self.status_label.configure(text=error_msg)

    def run(self):
        """Start the GUI application."""
        logger.info("Starting GUI application")
        self.root.mainloop()
