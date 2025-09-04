

# gui/main_window.py
import tkinter as tk
from tkinter import ttk
from gui.process_tab import ProcessTab
from gui.view_tab import ViewTab
from gui.analytics_tab import AnalyticsTab
from database import DatabaseManager

class MainWindow:
    """Main application window"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Receipt Processing App")
        self.root.geometry("1200x800")
        
        # Initialize database
        self.db_manager = DatabaseManager()
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create main window widgets"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create tabs
        self.process_tab = ProcessTab(self.notebook, self.db_manager)
        self.view_tab = ViewTab(self.notebook, self.db_manager)
        self.analytics_tab = AnalyticsTab(self.notebook, self.db_manager)
        
        # Add tabs to notebook
        self.notebook.add(self.process_tab.frame, text="Process Receipt")
        self.notebook.add(self.view_tab.frame, text="View Data")
        self.notebook.add(self.analytics_tab.frame, text="Analytics")
    
    def run(self):
        """Start the application"""
        self.view_tab.refresh_data()
        self.root.mainloop()
    
    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()

