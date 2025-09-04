
# gui/view_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from data_manager import DataManager

class ViewTab:
    """Tab for viewing stored data"""
    
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.data_manager = DataManager()
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
    
    def create_widgets(self):
        """Create tab widgets"""
        # Controls
        controls_frame = ttk.Frame(self.frame)
        controls_frame.pack(fill='x', pady=5)
        
        ttk.Button(controls_frame, text="Refresh Data", 
                  command=self.refresh_data).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Export Selected", 
                  command=self.export_selected).pack(side='left', padx=5)
        
        # Filter section
        self.create_filter_section()
        
        # Data treeview
        self.create_data_treeview()
    
    def create_filter_section(self):
        """Create filter section"""
        filter_frame = ttk.LabelFrame(self.frame, text="Filters")
        filter_frame.pack(fill='x', pady=5)
        
        ttk.Label(filter_frame, text="Store:").grid(row=0, column=0, padx=5)
        self.filter_store = ttk.Combobox(filter_frame, width=15)
        self.filter_store.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="Date From:").grid(row=0, column=2, padx=5)
        self.filter_date_from = ttk.Entry(filter_frame, width=12)
        self.filter_date_from.grid(row=0, column=3, padx=5)
        
        ttk.Label(filter_frame, text="Date To:").grid(row=0, column=4, padx=5)
        self.filter_date_to = ttk.Entry(filter_frame, width=12)
        self.filter_date_to.grid(row=0, column=5, padx=5)
        
        ttk.Button(filter_frame, text="Apply Filter", 
                  command=self.apply_filter).grid(row=0, column=6, padx=5)
    
    def create_data_treeview(self):
        """Create data treeview"""
        data_frame = ttk.Frame(self.frame)
        data_frame.pack(fill='both', expand=True, pady=5)
        
        columns = ('Receipt ID', 'Store', 'Date', 'Item', 'Price', 'Category')
        self.data_tree = ttk.Treeview(data_frame, columns=columns, show='headings')
        
        for col in columns:
            self.data_tree.heading(col, text=col)
            self.data_tree.column(col, width=120)
        
        data_scrollbar = ttk.Scrollbar(data_frame, orient='vertical', command=self.data_tree.yview)
        self.data_tree.configure(yscrollcommand=data_scrollbar.set)
        
        self.data_tree.pack(side='left', fill='both', expand=True)
        data_scrollbar.pack(side='right', fill='y')
    
    def refresh_data(self):
        """Refresh data display"""
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Load data from database
        rows = self.db_manager.get_all_receipts_with_items()
        
        for row in rows:
            self.data_tree.insert('', 'end', values=row)
        
        # Update store filter
        stores = self.db_manager.get_all_stores()
        self.filter_store['values'] = stores
    
    def apply_filter(self):
        """Apply filters to data view"""
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Get filtered data
        rows = self.db_manager.get_filtered_receipts(
            store_name=self.filter_store.get() or None,
            date_from=self.filter_date_from.get() or None,
            date_to=self.filter_date_to.get() or None
        )
        
        for row in rows:
            self.data_tree.insert('', 'end', values=row)
    
    def export_selected(self):
        """Export filtered data to Excel"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if file_path:
                # Get data from tree view
                data = []
                for child in self.data_tree.get_children():
                    values = self.data_tree.item(child)['values']
                    data.append(values)
                
                self.data_manager.export_receipts_to_excel(data, file_path)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")

