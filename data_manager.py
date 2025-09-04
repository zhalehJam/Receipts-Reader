
# data_manager.py
import pandas as pd
from typing import List, Dict, Tuple

class DataManager:
    """Handles data operations and exports"""
    
    @staticmethod
    def export_to_excel(data: List[Dict], file_path: str, additional_info: Dict = None):
        """Export data to Excel file"""
        try:
            df = pd.DataFrame(data)
            
            if additional_info:
                for key, value in additional_info.items():
                    df[key] = value
            
            df.to_excel(file_path, index=False)
            return True
        except Exception as e:
            raise Exception(f"Error exporting to Excel: {str(e)}")
    
    @staticmethod
    def export_receipts_to_excel(receipts_data: List[Tuple], file_path: str):
        """Export receipts data to Excel"""
        try:
            df = pd.DataFrame(receipts_data, 
                            columns=['Receipt ID', 'Store', 'Date', 'Item', 'Price', 'Category'])
            df.to_excel(file_path, index=False)
            return True
        except Exception as e:
            raise Exception(f"Error exporting receipts to Excel: {str(e)}")
    
    @staticmethod
    def validate_item_data(item: Dict) -> bool:
        """Validate item data"""
        required_fields = ['dutch_name', 'english_name', 'price', 'quantity', 'category']
        
        for field in required_fields:
            if field not in item:
                return False
        
        try:
            float(item['price'])
            int(item['quantity'])
        except ValueError:
            return False
        
        return True
