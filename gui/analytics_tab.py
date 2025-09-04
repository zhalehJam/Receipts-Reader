
# gui/analytics_tab.py
import tkinter as tk
from tkinter import ttk

class AnalyticsTab:
    """Tab for analytics and reporting"""
    
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.frame = ttk.Frame(parent)
        self.create_widgets()
    
    def create_widgets(self):
        """Create tab widgets"""
        # Summary frame
        summary_frame = ttk.LabelFrame(self.frame, text="Expense Summary")
        summary_frame.pack(fill='x', pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=10)
        self.summary_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Controls
        analytics_controls = ttk.Frame(self.frame)
        analytics_controls.pack(fill='x', pady=5)
        
        ttk.Button(analytics_controls, text="Generate Summary", 
                  command=self.generate_summary).pack(side='left', padx=5)
        ttk.Button(analytics_controls, text="Monthly Report", 
                  command=self.monthly_report).pack(side='left', padx=5)
    
    def generate_summary(self):
        """Generate expense summary"""
        try:
            summary_data = self.db_manager.get_expense_summary()
            
            summary = f"=== EXPENSE SUMMARY ===\n\n"
            summary += f"Total Expenses: €{summary_data['total']:.2f}\n\n"
            
            summary += "TOP STORES:\n"
            for store, amount, count in summary_data['by_store'][:10]:
                summary += f"  {store}: €{amount:.2f} ({count} receipts)\n"
            
            summary += "\nEXPENSES BY CATEGORY:\n"
            for category, amount in summary_data['by_category']:
                summary += f"  {category}: €{amount:.2f}\n"
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, summary)
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error generating summary: {str(e)}")
    
    def monthly_report(self):
        """Generate monthly expense report"""
        try:
            monthly_data = self.db_manager.get_monthly_report()
            
            report = "=== MONTHLY REPORT ===\n\n"
            for month, total, receipts in monthly_data:
                report += f"{month}: €{total:.2f} ({receipts} receipts)\n"
            
            self.summary_text.delete(1.0, tk.END)
            self.summary_text.insert(1.0, report)
            
        except Exception as e:
            tk.messagebox.showerror("Error", f"Error generating monthly report: {str(e)}")

