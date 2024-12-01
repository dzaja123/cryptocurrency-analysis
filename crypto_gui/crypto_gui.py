"""
Cryptocurrency Analysis GUI

This module provides a modern graphical user interface for the cryptocurrency
analysis application using CustomTkinter.
"""

import os
import threading
import yaml

import customtkinter as ctk

from PIL import Image, ImageTk
from utils import setup_logger

# Set up logger for this module
logger = setup_logger()


class CryptoGUI:
    """Class for cryptocurrency analysis GUI interface."""
    def __init__(
        self,
        fetch_data_callback: callable,
        analyze_data_callback: callable,
        set_export_format_callback: callable
        ):
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
        self.set_export_format = set_export_format_callback

        # Load configuration
        self.config_file = 'config.yaml'

        # Initialize class attributes
        self.sidebar = None
        self.main_area = None
        self.result_canvas = None
        self.current_image = None
        self.selected_coin = None
        self.coin_dropdown = None
        self.export_format = None
        self.export_format_checkbox = None
        self.fetch_button = None
        self.analyze_button = None
        self.status_label = None
        self.current_coin = None

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
            title = ctk.CTkLabel(
                self.sidebar,
                text="Controls",
                font=ctk.CTkFont(size=20, weight="bold")
            )
            title.pack(pady=10)

            # Coin selection
            coins = self._load_coins()
            self.selected_coin = ctk.StringVar(value=coins[0])

            coin_label = ctk.CTkLabel(
                self.sidebar,
                text="Select Coin:",
                anchor="center"
            )
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

            # Export format selection
            format_label = ctk.CTkLabel(
                self.sidebar,
                text="Export Format:",
                anchor="center"
            )
            format_label.pack(pady=5)

            self.export_format = ctk.BooleanVar(value=False)
            self.export_format_checkbox = ctk.CTkCheckBox(
                self.sidebar,
                text="Also save as HTML",
                variable=self.export_format,
                command=self._handle_export_format
            )
            self.export_format_checkbox.pack(pady=5)

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
            self.status_label = ctk.CTkLabel(
                self.sidebar,
                text="Ready",
                wraplength=180
            )
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
            if hasattr(self, 'main_area') and self.main_area is not None:
                self.main_area.destroy()

            self.main_area = ctk.CTkFrame(self.root)
            self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)

            # Create canvas with scrollbar
            canvas_frame = ctk.CTkFrame(self.main_area)
            canvas_frame.pack(fill="both", expand=True)

            # Create scrollbar
            scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="vertical")
            scrollbar.pack(side="right", fill="y")

            # Create canvas using CustomTkinter Canvas
            self.result_canvas = ctk.CTkCanvas(
                canvas_frame,
                yscrollcommand=scrollbar.set,
                highlightthickness=0,  # Remove border
                bg="white"
            )
            self.result_canvas.pack(side="left", fill="both", expand=True)

            # Configure scrollbar
            scrollbar.configure(command=self.result_canvas.yview)

            # Configure canvas scrolling
            self.result_canvas.bind(
                '<Configure>', 
                lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))
            )

            # Add welcome message
            welcome_text = """
                Welcome to Cryptocurrency Analysis Dashboard
                
                Quick Start Guide:
                1. Select a Coin from the dropdown menu
                2. Click "Fetch Data" to retrieve historical data
                3. Click "Analyze Data" to generate analysis
                4. View the results in this area
                
                Note: Analysis results will be saved as PNG by default.
                Check "Also save as HTML" to save in both formats.
            """
            self.result_canvas.create_text(
                self.result_canvas.winfo_reqwidth(),
                100,
                text=welcome_text,
                fill="black",
                font=("Arial", 14),
                justify="center"
            )

            logger.debug("Main display area created successfully")
        except Exception as e:
            logger.error("Failed to create main display area: %s", str(e))
            raise

    def _handle_export_format(self):
        """Handle export format checkbox change."""
        try:
            export_format = self.export_format.get()
            export_format = "both" if export_format else "png"
            self.set_export_format(export_format)
            logger.debug("Export format changed to: %s", export_format)
        except Exception as e:
            logger.error("Failed to handle export format change: %s", str(e))

    def _handle_fetch_data(self):
        """Handle fetch data button click."""
        selected_coin = self.selected_coin.get()
        logger.info("Initiating data fetch operation for %s", selected_coin)
        self.status_label.configure(text=f"Fetching data for {selected_coin}...")
        self.fetch_button.configure(state="disabled")

        try:
            threading.Thread(
                target=lambda: self._fetch_data_thread(selected_coin),
                daemon=True
            ).start()
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
            threading.Thread(
                target=lambda: self._analyze_data_thread(selected_coin),
                daemon=True
            ).start()
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
                    analyzed_coins = [
                        f.replace('analysis_', '').replace('.png', '').upper()
                        for f in all_files if f.startswith('analysis_')
                    ]
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
            if hasattr(self, 'main_area') and self.main_area is not None:
                self.main_area.destroy()

            self.main_area = ctk.CTkFrame(self.root)
            self.main_area.pack(side="right", fill="both", expand=True, padx=10, pady=10)

            # Create canvas with scrollbar
            canvas_frame = ctk.CTkFrame(self.main_area)
            canvas_frame.pack(fill="both", expand=True)

            # Create scrollbar
            scrollbar = ctk.CTkScrollbar(canvas_frame, orientation="vertical")
            scrollbar.pack(side="right", fill="y")

            # Create canvas
            self.result_canvas = ctk.CTkCanvas(
                canvas_frame,
                yscrollcommand=scrollbar.set,
                highlightthickness=0  # Remove border
            )
            self.result_canvas.pack(side="left", fill="both", expand=True)

            # Configure scrollbar
            scrollbar.configure(command=self.result_canvas.yview)

            # Configure canvas scrolling
            self.result_canvas.bind(
                '<Configure>',
                lambda e: self.result_canvas.configure(scrollregion=self.result_canvas.bbox("all"))
            )

            if coin != "No coins available" and coin != "No analysis files":
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    output_dir = config.get('output_dir', 'analysis_results')
                    analysis_file = os.path.join(output_dir, f'analysis_{coin.lower()}.png')

                    if os.path.exists(analysis_file):
                        try:
                            logger.info("Attempting to load image from: %s", analysis_file)
                            # Load and display the image
                            image = Image.open(analysis_file)
                            logger.info(
                                "Image loaded successfully. Original size: %dx%d",
                                image.width,
                                image.height
                            )

                            # Ensure canvas is updated and get its actual width
                            self.result_canvas.update_idletasks()
                            canvas_width = self.result_canvas.winfo_width()

                            # If canvas width is still not valid, use a minimum default width
                            if canvas_width <= 1:
                                canvas_width = 800  # Default reasonable width

                            logger.info("Canvas width: %d", canvas_width)
                            ratio = canvas_width / image.width
                            new_size = (int(image.width * ratio), int(image.height * ratio))
                            logger.info("Resizing image to: %dx%d", new_size[0], new_size[1])
                            image = image.resize(new_size, Image.Resampling.LANCZOS)

                            # Convert to PhotoImage
                            photo = ImageTk.PhotoImage(image)
                            logger.info("PhotoImage created successfully")

                            # Clear previous image
                            self.result_canvas.delete("all")

                            # Store reference to prevent garbage collection
                            self.current_image = photo

                            # Display image
                            self.result_canvas.create_image(0, 0, anchor="nw", image=photo)
                            self.result_canvas.config(scrollregion=(0, 0, new_size[0], new_size[1]))

                            logger.info(
                                "Image displayed on canvas with scrollregion: %s",
                                self.result_canvas.cget("scrollregion")
                            )
                        except Exception as e:
                            logger.error("Error loading image: %s", str(e))
                            self._show_error_message(f"Error loading analysis image: {str(e)}")
                    else:
                        logger.warning("Analysis file not found for %s", coin)
                        self._show_error_message(f"""
                            No Analysis Available for {coin}
                            
                            To generate analysis:
                            1. Click "Fetch Data" to retrieve the latest data
                            2. Click "Analyze Data" to generate the analysis
                        """)
        except Exception as e:
            error_msg = f"Error viewing analysis: {str(e)}"
            logger.error(error_msg)
            self.status_label.configure(text=error_msg)

    def _show_error_message(self, message: str):
        """Display an error message in the canvas."""
        self.result_canvas.create_text(
            self.result_canvas.winfo_reqwidth(),
            100,
            text=message,
            fill="black",
            font=("Arial", 14),
            justify="center"
        )

    def run(self):
        """Start the GUI application."""
        logger.info("Starting GUI application")
        self.root.mainloop()
