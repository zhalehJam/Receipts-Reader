

# gui/process_tab.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from datetime import datetime
from typing import List, Dict
from image_processor import ImageProcessor
from translator import TranslationService
from data_manager import DataManager

class ProcessTab:
    """Tab for processing receipts"""
    
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.image_processor = ImageProcessor()
        self.translator = TranslationService()
        self.data_manager = DataManager()
        
        self.frame = ttk.Frame(parent)
        self.current_image_path = None
        self.extracted_items = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create tab widgets"""
        # Left frame for image and controls
        left_frame = ttk.Frame(self.frame)
        left_frame.pack(side='left', fill='both', expand=True, padx=5)
        
        # Controls
        controls_frame = ttk.Frame(left_frame)
        controls_frame.pack(fill='x', pady=5)
        
        ttk.Button(controls_frame, text="Load Image", 
                  command=self.load_image).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Process Receipt", 
                  command=self.process_receipt).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Save to Database", 
                  command=self.save_to_database).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Export to Excel", 
                  command=self.export_to_excel).pack(side='left', padx=5)
        
        # Image display
        self.image_label = ttk.Label(left_frame, text="No image loaded")
        self.image_label.pack(pady=10)
        
        # Right frame for extracted data
        right_frame = ttk.Frame(self.frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Store info
        self.create_info_section(right_frame)
        
        # Items treeview
        self.create_items_section(right_frame)
        
        # Edit controls
        self.create_edit_controls(right_frame)
    
    def create_info_section(self, parent):
        """Create receipt information section"""
        info_frame = ttk.LabelFrame(parent, text="Receipt Information")
        info_frame.pack(fill='x', pady=5)
        
        ttk.Label(info_frame, text="Store Name:").grid(row=0, column=0, sticky='w', padx=5)
        self.store_entry = ttk.Entry(info_frame, width=30)
        self.store_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Date:").grid(row=1, column=0, sticky='w', padx=5)
        self.date_entry = ttk.Entry(info_frame, width=30)
        self.date_entry.grid(row=1, column=1, padx=5, pady=2)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
    
    def create_items_section(self, parent):
        """Create items treeview section"""
        items_frame = ttk.LabelFrame(parent, text="Extracted Items")
        items_frame.pack(fill='both', expand=True, pady=5)
        
        columns = ('Dutch Name', 'English Name', 'Price', 'Quantity', 'Category')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.items_tree.heading(col, text=col)
            self.items_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(items_frame, orient='vertical', command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def create_edit_controls(self, parent):
        """Create edit controls section"""
        edit_frame = ttk.Frame(parent)
        edit_frame.pack(fill='x', pady=5)
        
        ttk.Button(edit_frame, text="Edit Selected", 
                  command=self.edit_selected_item).pack(side='left', padx=5)
        ttk.Button(edit_frame, text="Delete Selected", 
                  command=self.delete_selected_item).pack(side='left', padx=5)
        ttk.Button(edit_frame, text="Add Item", 
                  command=self.add_manual_item).pack(side='left', padx=5)
    
    def load_image(self):
        """Load receipt image"""
        file_path = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        
        if file_path:
            self.current_image_path = file_path
            self.display_image(file_path)
    
    def display_image(self, image_path):
        """Display loaded image"""
        image = Image.open(image_path)
        image.thumbnail((400, 600))
        photo = ImageTk.PhotoImage(image)
        
        self.image_label.configure(image=photo, text="")
        self.image_label.image = photo
    
    def process_receipt(self):
        """Process the loaded receipt"""
        if not self.current_image_path:
            messagebox.showerror("Error", "Please load an image first!")
            return
        
        try:
            # Extract text from image
            text = self.image_processor.extract_text_from_image(self.current_image_path)
            
            # Extract items and prices
            self.extracted_items = self.image_processor.extract_items_from_text(text)
            
            # Translate items
            self.extracted_items = self.translator.translate_items(self.extracted_items)
            
            # Update display
            self.update_items_display()
            
            messagebox.showinfo("Success", f"Processed receipt! Found {len(self.extracted_items)} items.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing receipt: {str(e)}")
    
    def update_items_display(self):
        """Update items treeview"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Add new items
        for item in self.extracted_items:
            self.items_tree.insert('', 'end', values=(
                item['row_number'],
                item['dutch_name'],
                item['english_name'],
                f"€{item['price']:.2f}",
                item['quantity'],
                item['category']
            ))
    
    def edit_selected_item(self):
        """Edit selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit!")
            return
        
        item_index = self.items_tree.index(selection[0])
        item = self.extracted_items[item_index]
        
        self.create_item_edit_dialog(item, item_index)
    
    def create_item_edit_dialog(self, item: Dict, index: int = None):
        """Create item edit dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("Edit Item" if index is not None else "Add Item")
        dialog.geometry("400x300")
        
        # Form fields
        fields = self.create_form_fields(dialog, item)
        
        # Buttons
        self.create_dialog_buttons(dialog, fields, item, index)
    
    def create_form_fields(self, dialog, item):
        """Create form fields for item dialog"""
        fields = {}
        
        ttk.Label(dialog, text="Row Number:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        fields['row_number'] = ttk.Entry(dialog, width=40)
        fields['row_number'].grid(row=0, column=1, padx=5, pady=5)
        fields['row_number'].insert(0, item['row_number'])
        
        ttk.Label(dialog, text="Dutch Name:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        fields['dutch'] = ttk.Entry(dialog, width=40)
        fields['dutch'].grid(row=0, column=1, padx=5, pady=5)
        fields['dutch'].insert(0, item['dutch_name'])
        
        ttk.Label(dialog, text="English Name:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        fields['english'] = ttk.Entry(dialog, width=40)
        fields['english'].grid(row=1, column=1, padx=5, pady=5)
        fields['english'].insert(0, item['english_name'])
        
        ttk.Label(dialog, text="Price (€):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        fields['price'] = ttk.Entry(dialog, width=40)
        fields['price'].grid(row=2, column=1, padx=5, pady=5)
        fields['price'].insert(0, str(item['price']))
        
        ttk.Label(dialog, text="Quantity:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        fields['quantity'] = ttk.Entry(dialog, width=40)
        fields['quantity'].grid(row=3, column=1, padx=5, pady=5)
        fields['quantity'].insert(0, str(item['quantity']))
        
        ttk.Label(dialog, text="Category:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        fields['category'] = ttk.Combobox(dialog, width=37, values=[
            'Groceries', 'Electronics', 'Clothing', 'Health & Beauty', 
            'Home & Garden', 'Sports', 'Books', 'Restaurants', 'Other'
        ])
        fields['category'].grid(row=4, column=1, padx=5, pady=5)
        fields['category'].set(item['category'])
        
        return fields
    
    def create_dialog_buttons(self, dialog, fields, item, index):
        """Create dialog buttons"""
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_item():
            try:
                updated_item = {
                    'row_number': int(fields['row_number'].get()),
                    'dutch_name': fields['dutch'].get(),
                    'english_name': fields['english'].get(),
                    'price': float(fields['price'].get()),
                    'quantity': int(fields['quantity'].get()),
                    'category': fields['category'].get()
                }
                
                if not self.data_manager.validate_item_data(updated_item):
                    messagebox.showerror("Error", "Please fill all fields with valid data!")
                    return
                
                if index is not None:
                    self.extracted_items[index] = updated_item
                else:
                    self.extracted_items.append(updated_item)
                
                self.update_items_display()
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter valid numeric values for price and quantity!")
        
        ttk.Button(button_frame, text="Save", command=save_item).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side='left', padx=5)
    
    def add_manual_item(self):
        """Add item manually"""
        empty_item = {
            'row_number': 0,
            'dutch_name': '',
            'english_name': '',
            'price': 0.0,
            'quantity': 1,
            'category': 'Uncategorized'
        }
        self.create_item_edit_dialog(empty_item)
    
    def delete_selected_item(self):
        """Delete selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            item_index = self.items_tree.index(selection[0])
            del self.extracted_items[item_index]
            self.update_items_display()
    
    def save_to_database(self):
        """Save receipt to database"""
        if not self.extracted_items:
            messagebox.showwarning("Warning", "No items to save!")
            return
        
        try:
            store_name = self.store_entry.get() or "Unknown Store"
            receipt_date = self.date_entry.get()
            
            receipt_id = self.db_manager.save_receipt(store_name, receipt_date, self.extracted_items)
            
            messagebox.showinfo("Success", f"Receipt saved to database! (ID: {receipt_id})")
            
            # Clear current data
            self.clear_form()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saving to database: {str(e)}")
    
    def export_to_excel(self):
        """Export current receipt to Excel"""
        if not self.extracted_items:
            messagebox.showwarning("Warning", "No items to export!")
            return
        
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")]
            )
            
            if file_path:
                additional_info = {
                    'store': self.store_entry.get() or "Unknown Store",
                    'date': self.date_entry.get()
                }
                
                self.data_manager.export_to_excel(self.extracted_items, file_path, additional_info)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting to Excel: {str(e)}")
    
    def clear_form(self):
        """Clear form data"""
        self.extracted_items = []
        self.update_items_display()
        self.store_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

