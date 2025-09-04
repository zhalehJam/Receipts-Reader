# database.py
import sqlite3
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self, db_name: str = 'receipts.db'):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        
        # Create receipts table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS receipts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                store_name TEXT,
                date TEXT,
                total_amount REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create items table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                receipt_id INTEGER,
                row_number INTEGER,
                item_name TEXT,
                item_name_dutch TEXT,
                price REAL,
                quantity INTEGER DEFAULT 1,
                category TEXT,
                FOREIGN KEY (receipt_id) REFERENCES receipts (id)
            )
        ''')
        
        self.conn.commit()
    
    def save_receipt(self, store_name: str, date: str, items: List[Dict]) -> int:
        """Save receipt and its items to database"""
        total_amount = sum(item['price'] * item['quantity'] for item in items)
        
        # Insert receipt
        self.cursor.execute('''
            INSERT INTO receipts (store_name, date, total_amount)
            VALUES (?, ?, ?)
        ''', (store_name, date, total_amount))
        
        receipt_id = self.cursor.lastrowid
        
        # Insert items
        for item in items:
            self.cursor.execute('''
                INSERT INTO items (receipt_id, row_number, item_name, item_name_dutch, price, quantity, category)
                VALUES (?,?, ?, ?, ?, ?, ?)
            ''', (receipt_id, item['row_number'],item['english_name'], item['dutch_name'], 
                  item['price'], item['quantity'], item['category']))
        
        self.conn.commit()
        return receipt_id
    
    def get_all_receipts_with_items(self) -> List[Tuple]:
        """Get all receipts with their items"""
        query = '''
            SELECT r.id, r.store_name, r.date, i.row_number, i.item_name, i.price, i.category
            FROM receipts r
            JOIN items i ON r.id = i.receipt_id
            ORDER BY r.date DESC, r.id
        '''
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def get_filtered_receipts(self, store_name: str = None, date_from: str = None, date_to: str = None) -> List[Tuple]:
        """Get filtered receipts"""
        query = '''
            SELECT r.id, r.store_name, r.date, i.row_number, i.item_name, i.price, i.category
            FROM receipts r
            JOIN items i ON r.id = i.receipt_id
            WHERE 1=1
        '''
        params = []
        
        if store_name:
            query += ' AND r.store_name = ?'
            params.append(store_name)
        
        if date_from:
            query += ' AND r.date >= ?'
            params.append(date_from)
        
        if date_to:
            query += ' AND r.date <= ?'
            params.append(date_to)
        
        query += ' ORDER BY r.date DESC, r.id'
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()
    
    def get_all_stores(self) -> List[str]:
        """Get all unique store names"""
        self.cursor.execute('SELECT DISTINCT store_name FROM receipts ORDER BY store_name')
        return [row[0] for row in self.cursor.fetchall()]
    
    def get_expense_summary(self) -> Dict:
        """Get expense summary data"""
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
        
        return {
            'total': total,
            'by_store': store_data,
            'by_category': category_data
        }
    
    def get_monthly_report(self) -> List[Tuple]:
        """Get monthly expense report"""
        self.cursor.execute('''
            SELECT 
                strftime('%Y-%m', date) as month,
                SUM(total_amount) as total,
                COUNT(*) as receipts
            FROM receipts
            GROUP BY strftime('%Y-%m', date)
            ORDER BY month DESC
        ''')
        return self.cursor.fetchall()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

