import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import pytesseract
from PIL import Image, ImageTk
import re
import sqlite3
import pandas as pd
from datetime import datetime
from googletrans import Translator
import os
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
class ReceiptProcessor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Receipt Processing App")
        self.root.geometry("1200x800")
        
        # Initialize database
        self.init_database()
        
        # Initialize translator
        self.translator = Translator()
        
        # Variables
        self.current_image_path = None
        self.extracted_items = []
        
        self.create_widgets()
        
    def init_database(self):
        """Initialize SQLite database"""
        self.conn = sqlite3.connect('receipts.db')
        self.cursor = self.conn.cursor()
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT,
                date TEXT,
                total_amount REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER,
                item_name TEXT,
                item_name_dutch TEXT,
                price REAL,
                quantity INTEGER DEFAULT 1,
                category TEXT,
                FOREIGN KEY (receipt_id) REFERENCES receipts (id)
            )
        ''')
        
        self.conn.commit()
    
    def create_widgets(self):
        """Create the main GUI"""
        # Create notebook for tabs
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Process Receipt
        self.process_frame = ttk.Frame(notebook)
        notebook.add(self.process_frame, text="Process Receipt")
        self.create_process_tab()
        
        # Tab 2: View Data
        self.view_frame = ttk.Frame(notebook)
        notebook.add(self.view_frame, text="View Data")
        self.create_view_tab()
        
        # Tab 3: Analytics
        self.analytics_frame = ttk.Frame(notebook)
        notebook.add(self.analytics_frame, text="Analytics")
        self.create_analytics_tab()
    
    def create_process_tab(self):
        """Create the receipt processing tab"""
        # Left frame for image and controls
        left_frame = ttk.Frame(self.process_frame)
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
        right_frame = ttk.Frame(self.process_frame)
        right_frame.pack(side='right', fill='both', expand=True, padx=5)
        
        # Store info
        info_frame = ttk.LabelFrame(right_frame, text="Receipt Information")
        info_frame.pack(fill='x', pady=5)
        
        ttk.Label(info_frame, text="Store Name:").grid(row=0, column=0, sticky='w', padx=5)
        self.store_entry = ttk.Entry(info_frame, width=30)
        self.store_entry.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(info_frame, text="Date:").grid(row=1, column=0, sticky='w', padx=5)
        self.date_entry = ttk.Entry(info_frame, width=30)
        self.date_entry.grid(row=1, column=1, padx=5, pady=2)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Items treeview
        items_frame = ttk.LabelFrame(right_frame, text="Extracted Items")
        items_frame.pack(fill='both', expand=True, pady=5)
        
        # Treeview for items
        columns = ('Dutch Name', 'English Name', 'Price', 'Quantity', 'Category')
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.items_tree.heading(col, text=col)
            self.items_tree.column(col, width=120)
        
        scrollbar = ttk.Scrollbar(items_frame, orient='vertical', command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Edit controls
        edit_frame = ttk.Frame(right_frame)
        edit_frame.pack(fill='x', pady=5)
        
        ttk.Button(edit_frame, text="Edit Selected", 
                  command=self.edit_selected_item).pack(side='left', padx=5)
        ttk.Button(edit_frame, text="Delete Selected", 
                  command=self.delete_selected_item).pack(side='left', padx=5)
        ttk.Button(edit_frame, text="Add Item", 
                  command=self.add_manual_item).pack(side='left', padx=5)
    
    def create_view_tab(self):
        """Create the data viewing tab"""
        # Controls
        controls_frame = ttk.Frame(self.view_frame)
        controls_frame.pack(fill='x', pady=5)
        
        ttk.Button(controls_frame, text="Refresh Data", 
                  command=self.refresh_data).pack(side='left', padx=5)
        ttk.Button(controls_frame, text="Export Selected", 
                  command=self.export_selected).pack(side='left', padx=5)
        
        # Filter frame
        filter_frame = ttk.LabelFrame(self.view_frame, text="Filters")
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
        
        # Data treeview
        data_frame = ttk.Frame(self.view_frame)
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
    
    def create_analytics_tab(self):
        """Create the analytics tab"""
        # Summary frame
        summary_frame = ttk.LabelFrame(self.analytics_frame, text="Expense Summary")
        summary_frame.pack(fill='x', pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=10)
        self.summary_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Controls
        analytics_controls = ttk.Frame(self.analytics_frame)
        analytics_controls.pack(fill='x', pady=5)
        
        ttk.Button(analytics_controls, text="Generate Summary", 
                  command=self.generate_summary).pack(side='left', padx=5)
        ttk.Button(analytics_controls, text="Monthly Report", 
                  command=self.monthly_report).pack(side='left', padx=5)
    
    def load_image(self):
        """Load image file"""
        file_path = filedialog.askopenfilename(
            title="Select Receipt Image",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff")]
        )
        
        if file_path:
            self.current_image_path = file_path
            
            # Display image
            image = Image.open(file_path)
            image.thumbnail((400, 600))
            photo = ImageTk.PhotoImage(image)
            
            self.image_label.configure(image=photo, text="")
            self.image_label.image = photo
    
    def preprocess_image(self, image_path):
        """Preprocess image for better OCR"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply threshold
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    def test_preprocess_image(self, image_path):
        """Test and save the output of preprocess_image"""
        processed_img = self.preprocess_image(image_path)
        cv2.imwrite("processed_receipt.png", processed_img)
        print("Processed image saved as processed_receipt.png")
    
    def process_receipt(self):
        """Process the loaded receipt image"""
        if not self.current_image_path:
            messagebox.showerror("Error", "Please load an image first!")
            return
        
        try:
            # Preprocess image
            # self.test_preprocess_image(self.current_image_path)
            processed_img = self.preprocess_image(self.current_image_path)
            
            # Perform OCR
            text = pytesseract.image_to_string(processed_img, lang='nld+eng')
            
            # Extract items and prices
            self.extracted_items = self.extract_items_from_text(text)
            
            # Translate items
            self.translate_items()
            
            # Update display
            self.update_items_display()
            
            messagebox.showinfo("Success", f"Processed receipt! Found {len(self.extracted_items)} items.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing receipt: {str(e)}")
    
    def extract_items_from_text(self, text):
        """Extract items and prices from OCR text"""
        lines = text.split('\n')
        items = []
        
        # Pattern to match price (numbers with . or , as decimal separator)
        price_pattern = r'(\d+[.,]\d{2})'
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for lines with prices
            price_matches = re.findall(price_pattern, line)
            if price_matches:
                # Get the price (last match usually)
                price_str = price_matches[-1].replace(',', '.')
                try:
                    price = float(price_str)
                    
                    # Extract item name (text before the price)
                    item_text = re.sub(price_pattern, '', line).strip()
                    
                    # Clean up item name
                    item_text = re.sub(r'\s+', ' ', item_text)
                    item_text = item_text.strip('.,- ')
                    
                    if len(item_text) > 2:  # Avoid very short meaningless text
                        items.append({
                            'dutch_name': item_text,
                            'english_name': '',
                            'price': price,
                            'quantity': 1,
                            'category': 'Uncategorized'
                        })
                        
                except ValueError:
                    continue
        
        return items
    
    def translate_items(self):
        """Translate Dutch item names to English"""
        try:
            for item in self.extracted_items:
                if item['dutch_name']:
                    translated = self.translator.translate(item['dutch_name'], src='nl', dest='en')
                    item['english_name'] = translated.text
        except Exception as e:
            print(f"Translation error: {e}")
            # If translation fails, copy dutch name
            for item in self.extracted_items:
                if not item['english_name']:
                    item['english_name'] = item['dutch_name']
    
    def update_items_display(self):
        """Update the items treeview"""
        # Clear existing items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Add new items
        for item in self.extracted_items:
            self.items_tree.insert('', 'end', values=(
                item['dutch_name'],
                item['english_name'],
                f"€{item['price']:.2f}",
                item['quantity'],
                item['category']
            ))
    
    def edit_selected_item(self):
        """Edit the selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to edit!")
            return
        
        item_index = self.items_tree.index(selection[0])
        item = self.extracted_items[item_index]
        
        # Create edit dialog
        self.create_item_edit_dialog(item, item_index)
    
    def create_item_edit_dialog(self, item, index=None):
        """Create dialog for editing/adding items"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Item" if index is not None else "Add Item")
        dialog.geometry("400x300")
        
        # Form fields
        ttk.Label(dialog, text="Dutch Name:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        dutch_entry = ttk.Entry(dialog, width=40)
        dutch_entry.grid(row=0, column=1, padx=5, pady=5)
        dutch_entry.insert(0, item['dutch_name'])
        
        ttk.Label(dialog, text="English Name:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        english_entry = ttk.Entry(dialog, width=40)
        english_entry.grid(row=1, column=1, padx=5, pady=5)
        english_entry.insert(0, item['english_name'])
        
        ttk.Label(dialog, text="Price (€):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        price_entry = ttk.Entry(dialog, width=40)
        price_entry.grid(row=2, column=1, padx=5, pady=5)
        price_entry.insert(0, str(item['price']))
        
        ttk.Label(dialog, text="Quantity:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        quantity_entry = ttk.Entry(dialog, width=40)
        quantity_entry.grid(row=3, column=1, padx=5, pady=5)
        quantity_entry.insert(0, str(item['quantity']))
        
        ttk.Label(dialog, text="Category:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        category_combo = ttk.Combobox(dialog, width=37, values=[
            'Groceries', 'Electronics', 'Clothing', 'Health & Beauty', 
            'Home & Garden', 'Sports', 'Books', 'Restaurants', 'Other'
        ])
        category_combo.grid(row=4, column=1, padx=5, pady=5)
        category_combo.set(item['category'])
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        def save_item():
            try:
                updated_item = {
                    'dutch_name': dutch_entry.get(),
                    'english_name': english_entry.get(),
                    'price': float(price_entry.get()),
                    'quantity': int(quantity_entry.get()),
                    'category': category_combo.get()
                }
                
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
            'dutch_name': '',
            'english_name': '',
            'price': 0.0,
            'quantity': 1,
            'category': 'Uncategorized'
        }
        self.create_item_edit_dialog(empty_item)
    
    def delete_selected_item(self):
        """Delete the selected item"""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to delete!")
            return
        
        if messagebox.askyesno("Confirm", "Are you sure you want to delete this item?"):
            item_index = self.items_tree.index(selection[0])
            del self.extracted_items[item_index]
            self.update_items_display()
    
    def save_to_database(self):
        """Save current receipt to database"""
        if not self.extracted_items:
            messagebox.showwarning("Warning", "No items to save!")
            return
        
        try:
            store_name = self.store_entry.get() or "Unknown Store"
            receipt_date = self.date_entry.get()
            total_amount = sum(item['price'] * item['quantity'] for item in self.extracted_items)
            
            # Insert receipt
            self.cursor.execute('''
                INSERT INTO receipts (store_name, date, total_amount)
                VALUES (?, ?, ?)
            ''', (store_name, receipt_date, total_amount))
            
            receipt_id = self.cursor.lastrowid
            
            # Insert items
            for item in self.extracted_items:
                self.cursor.execute('''
                    INSERT INTO items (receipt_id, item_name, item_name_dutch, price, quantity, category)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (receipt_id, item['english_name'], item['dutch_name'], 
                      item['price'], item['quantity'], item['category']))
            
            self.conn.commit()
            messagebox.showinfo("Success", "Receipt saved to database!")
            
            # Clear current data
            self.extracted_items = []
            self.update_items_display()
            self.store_entry.delete(0, tk.END)
            
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
                df = pd.DataFrame(self.extracted_items)
                df['store'] = self.store_entry.get() or "Unknown Store"
                df['date'] = self.date_entry.get()
                df = df[['store', 'date', 'dutch_name', 'english_name', 'price', 'quantity', 'category']]
                
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting to Excel: {str(e)}")
    
    def refresh_data(self):
        """Refresh data in view tab"""
        # Clear existing data
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        # Load data from database
        query = '''
            SELECT r.id, r.store_name, r.date, i.item_name, i.price, i.category
            FROM receipts r
            JOIN items i ON r.id = i.receipt_id
            ORDER BY r.date DESC, r.id
        '''
        
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        
        for row in rows:
            self.data_tree.insert('', 'end', values=row)
        
        # Update store filter
        self.cursor.execute('SELECT DISTINCT store_name FROM receipts ORDER BY store_name')
        stores = [row[0] for row in self.cursor.fetchall()]
        self.filter_store['values'] = stores
    
    def apply_filter(self):
        """Apply filters to data view"""
        # Build query with filters
        query = '''
            SELECT r.id, r.store_name, r.date, i.item_name, i.price, i.category
            FROM receipts r
            JOIN items i ON r.id = i.receipt_id
            WHERE 1=1
        '''
        params = []
        
        if self.filter_store.get():
            query += ' AND r.store_name = ?'
            params.append(self.filter_store.get())
        
        if self.filter_date_from.get():
            query += ' AND r.date >= ?'
            params.append(self.filter_date_from.get())
        
        if self.filter_date_to.get():
            query += ' AND r.date <= ?'
            params.append(self.filter_date_to.get())
        
        query += ' ORDER BY r.date DESC, r.id'
        
        # Clear and populate tree
        for item in self.data_tree.get_children():
            self.data_tree.delete(item)
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
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
                
                df = pd.DataFrame(data, columns=['Receipt ID', 'Store', 'Date', 'Item', 'Price', 'Category'])
                df.to_excel(file_path, index=False)
                messagebox.showinfo("Success", f"Data exported to {file_path}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {str(e)}")
    
    def generate_summary(self):
        """Generate expense summary"""
        try:
            # Total expenses
            self.cursor.execute('SELECT SUM(total_amount) FROM receipts')
            total = self.cursor.fetchone()[0] or 0
            
            # Expenses by store
            self.cursor.execute('''
                SELECT store_name, SUM(total_amount), COUNT(*)
                FROM receipts
                GROUP BY store_name
                ORDER BY SUM(total_amount) DESC
            ''')
            store_data = self.cursor.fetchall()
            
            # Expenses by category
            self.cursor.execute('''
                SELECT i.category, SUM(i.price * i.quantity)
                FROM items i
                GROUP BY i.category
                ORDER BY SUM(i.price * i.quantity) DESC
            ''')
            category_data = self.cursor.fetchall()
            
            # Create summary text
            summary = f"=== EXPENSE SUMMARY ===\n\n"
            summary += f"Total Expenses: €{total:.2f}\n\n"
            
            summary += "TOP STORES:\n"
            for store, amount, count in store_data[:10]:
                summary += f"  {store}: €{amount:.2f} ({count} receipts)\n"
            
            summary += "\nEXPENSES BY CATEGORY:\n"
            for category, amount in category_data:
                summary += f"  {category}: €{amount:.2f}\n"
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating summary: {str(e)}")
    
    def monthly_report(self):
        """Generate monthly expense report"""
        try:
            self.cursor.execute('''
                SELECT 
                    strftime('%Y-%m', date) as month,
                    SUM(total_amount) as total,
                    COUNT(*) as receipts
                FROM receipts
                GROUP BY strftime('%Y-%m', date)
                ORDER BY month DESC
            ''')
            monthly_data = self.cursor.fetchall()
            
            report = "=== MONTHLY REPORT ===\n\n"
            for month, total, receipts in monthly_data:
                report += f"{month}: €{total:.2f} ({receipts} receipts)\n"
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, report)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating monthly report: {str(e)}")
    
    def run(self):
        """Start the application"""
        self.refresh_data()
        self.root.mainloop()
        
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    app = ReceiptProcessor()
    app.run()