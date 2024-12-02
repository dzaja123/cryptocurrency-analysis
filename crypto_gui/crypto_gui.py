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
from datetime import datetime
from tkcalendar import DateEntry

from utils.logger_setup import LoggerManager

# Get logger instance
logger = LoggerManager.get_logger()


class CryptoGUI:
    """Class for cryptocurrency analysis GUI interface."""
    def __init__(
        self,
        fetch_data_callback: callable,
        analyze_data_callback: callable,
        set_export_format_callback: callable,
        search_coin_callback: callable,
        fetch_top_coins_callback: callable,
        set_date_range_callback: callable
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

        # Configure grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)  # Main area

        # Store callbacks
        self.fetch_data = fetch_data_callback
        self.analyze_data = analyze_data_callback
        self.set_export_format = set_export_format_callback
        self.search_coin = search_coin_callback
        self.fetch_top_coins = fetch_top_coins_callback
        self.set_date_range = set_date_range_callback

        # Initialize class attributes
        self.coins = self._load_coins()
        self.sidebar_frame = None
        self.main_frame = None
        self.result_canvas = None
        self.scrollable_frame = None
        self.scrollbar = None
        self.image_label = None
        self.status_label = None
        self.current_coin = None
        self.search_entry = None
        self.search_loading = False
        self.loading_label = None
        self.start_date = None
        self.end_date = None

        # Create GUI elements
        self._create_gui_elements()

    def _create_gui_elements(self):
        """Create all GUI elements using grid layout."""
        # Create main sections
        self._create_sidebar()
        self._create_main_area()

    def _create_sidebar(self):
        """Create sidebar with controls using grid layout."""
        # Create sidebar frame
        self.sidebar_frame = ctk.CTkFrame(self.root, width=250)
        self.sidebar_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Title label
        title_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Crypto Analysis",
            font=("Helvetica", 20, "bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # Date Range Selection
        date_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Date Range",
            font=("Helvetica", 14, "bold")
        )
        date_label.grid(row=1, column=0, padx=20, pady=(10, 5))

        # Start date
        start_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Start Date:",
            font=("Helvetica", 12)
        )
        start_label.grid(row=2, column=0, padx=20, pady=(5, 0), sticky="w")

        self.start_date = DateEntry(
            self.sidebar_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            maxdate=datetime.now()
        )
        self.start_date.grid(row=3, column=0, padx=20, pady=(0, 5), sticky="ew")

        # End date
        end_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="End Date:",
            font=("Helvetica", 12)
        )
        end_label.grid(row=4, column=0, padx=20, pady=(5, 0), sticky="w")

        self.end_date = DateEntry(
            self.sidebar_frame,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd',
            maxdate=datetime.now()
        )
        self.end_date.grid(row=5, column=0, padx=20, pady=(0, 5), sticky="ew")

        # Apply date range button
        apply_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Apply Date Range",
            command=self._apply_date_range
        )
        apply_button.grid(row=6, column=0, padx=20, pady=(0, 15), sticky="ew")

        # Coin selection label
        coin_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Coin Selection",
            font=("Helvetica", 14, "bold")
        )
        coin_label.grid(row=7, column=0, padx=20, pady=(10, 5))

        # Search frame
        search_frame = ctk.CTkFrame(self.sidebar_frame)
        search_frame.grid(row=8, column=0, padx=20, pady=5, sticky="ew")

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Search coin..."
        )
        self.search_entry.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        search_button = ctk.CTkButton(
            search_frame,
            text="🔍",
            width=40,
            command=self._handle_search
        )
        search_button.grid(row=0, column=1, padx=5, pady=5)
        search_frame.grid_columnconfigure(0, weight=1)

        # Coin dropdown
        self.coin_menu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=self.coins,
            command=self._select_coin,
            width=200
        )
        self.coin_menu.grid(row=9, column=0, padx=20, pady=10, sticky="ew")
        self.coin_menu.set("Select Coin")

        # Control buttons
        fetch_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Fetch Data",
            command=self._handle_fetch
        )
        fetch_button.grid(row=10, column=0, padx=20, pady=5, sticky="ew")

        analyze_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Analyze",
            command=self._handle_analyze
        )
        analyze_button.grid(row=11, column=0, padx=20, pady=5, sticky="ew")

        # Export format selector
        format_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Export Format:",
            font=("Helvetica", 12)
        )
        format_label.grid(row=12, column=0, padx=20, pady=(10, 0), sticky="w")

        format_var = ctk.StringVar(value="png")
        format_combobox = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["png", "jpg", "pdf"],
            command=self.set_export_format,
            variable=format_var,
            width=200
        )
        format_combobox.grid(row=13, column=0, padx=20, pady=(0, 20), sticky="ew")

    def _create_main_area(self):
        """Create main display area using grid layout."""
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Status frame at the top
        status_frame = ctk.CTkFrame(self.main_frame)
        status_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        
        # Status label with custom styling
        self.status_label = ctk.CTkLabel(
            status_frame,
            text="Ready",
            font=("Helvetica", 12),
            wraplength=800,
            height=50,
            corner_radius=6
        )
        self.status_label.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        status_frame.grid_columnconfigure(0, weight=1)

        # Create canvas with scrollbar
        self.result_canvas = ctk.CTkCanvas(
            self.main_frame,
            highlightthickness=0
        )
        self.result_canvas.grid(row=1, column=0, sticky="nsew")

        # Scrollbar
        self.scrollbar = ctk.CTkScrollbar(
            self.main_frame,
            orientation="vertical",
            command=self.result_canvas.yview
        )
        self.scrollbar.grid(row=1, column=1, sticky="ns")

        # Configure canvas
        self.result_canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create frame for content
        self.scrollable_frame = ctk.CTkFrame(self.result_canvas)
        self.result_canvas.create_window(
            (0, 0),
            window=self.scrollable_frame,
            anchor="nw",
            width=self.result_canvas.winfo_width()
        )

        # Image label for displaying analysis results
        self.image_label = ctk.CTkLabel(self.scrollable_frame, text="")
        self.image_label.grid(row=0, column=0, padx=20, pady=20)

        # Configure scrollable frame
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.result_canvas.configure(
                scrollregion=self.result_canvas.bbox("all")
            )
        )

    def _load_coins(self) -> list:
        """Load top 15 coins by market cap."""
        try:
            coins = self.fetch_top_coins()  # Get top 15 coins
            coin_symbols = ["ALL COINS"]  # Add "ALL COINS" option at the beginning
            coin_symbols.extend([coin['symbol'].split('/')[0] for coin in coins])
            logger.info("Successfully loaded %d coins", len(coin_symbols)-1)
            return coin_symbols
        except Exception as e:
            logger.error("Failed to load coins: %s", str(e))
            return ["ALL COINS"]  # Return at least "ALL COINS" option

    def _apply_date_range(self):
        """Apply the selected date range."""
        start_date = self.start_date.get_date().strftime("%Y-%m-%d")
        end_date = self.end_date.get_date().strftime("%Y-%m-%d")
        self.set_date_range(start_date, end_date)
        logger.info(f"Date range set: {start_date} to {end_date}")

    def _handle_search(self):
        """Handle search button click."""
        search_text = self.search_entry.get().strip().upper()
        if not search_text:
            self.status_label.configure(text="Please enter a coin symbol")
            return

        self.search_loading = True
        self.loading_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Searching...",
            text_color="gray"
        )
        self.loading_label.grid(row=14, column=0, padx=20, pady=10)
        self.search_entry.configure(state="disabled")
        
        def search_thread():
            try:
                exists = self.search_coin(search_text)
                self.root.after(0, lambda: self._handle_search_result(search_text, exists))
            except Exception as e:
                self.root.after(0, lambda: self.status_label.configure(
                    text=f"Error searching coin: {str(e)}"
                ))
            finally:
                self.root.after(0, self._finish_search)

        threading.Thread(target=search_thread, daemon=True).start()

    def _handle_search_result(self, coin: str, exists: bool):
        """Handle the result of coin search."""
        if exists:
            current_values = list(self.coin_menu.cget("values"))
            if coin not in current_values:
                current_values.append(coin)
                self.coin_menu.configure(values=current_values)
                self.status_label.configure(text=f"Added {coin} to the list")
            else:
                self.status_label.configure(text=f"{coin} is already in the list")
        else:
            self.status_label.configure(text=f"Coin {coin} not found")

    def _finish_search(self):
        """Clean up after search completes."""
        self.search_loading = False
        self.loading_label.destroy()
        self.search_entry.configure(state="normal")
        self.search_entry.delete(0, "end")  # Clear search entry

    def _select_coin(self, coin):
        """Handle coin selection."""
        self.current_coin = coin
        self.status_label.configure(text=f"Selected coin: {coin}")

    def _handle_fetch(self):
        """Handle fetch data button click."""
        logger.info("Initiating data fetch operation for %s", self.current_coin)
        self.status_label.configure(text=f"Fetching data for {self.current_coin}...")
        self.fetch_data()  # Call without parameters

    def _handle_analyze(self):
        """Handle analyze data button click."""
        logger.info("Initiating data analysis operation for %s", self.current_coin)
        self.status_label.configure(text=f"Analyzing {self.current_coin}...")
        self.analyze_data()  # Call without parameters

    def run(self):
        """Start the GUI application."""
        logger.info("Starting GUI application")
        self.root.mainloop()
