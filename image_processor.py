# image_processor.py
from nt import replace
import cv2
import pytesseract
import re
from PIL import Image
from typing import List, Dict
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
class ImageProcessor:
    """Handles image processing and OCR operations"""
    
    def __init__(self):
        # Configure tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def preprocess_image(self, image_path: str):
        """Preprocess image for better OCR results"""
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply threshold for better text recognition
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return thresh
    
    def extract_text_from_image(self, image_path: str) -> str:
       
        try:
            processed_img = self.preprocess_image(image_path)

            # Main config: assume block of text, preserve spacing
            config = "--oem 3 --psm 6 -c preserve_interword_spaces=1"
            text = pytesseract.image_to_string(
                processed_img, lang="nld+eng", config=config
            ).strip()

            # --- Post-processing cleanup ---
            # Fix common OCR mistakes
            text = text.replace("’", "'").replace("‘", "'").replace("°", "0").replace("~","-")
            # Fix 3/19 -> 3.19
            text = re.sub(r"(\d)[/](\d)", r"\1.\2", text)
            # Fix 1138 -> 11.38
            text = re.sub(r"(\d)\s+(\d{2})", r"\1.\2", text)

            return text

        except Exception as e:
            raise Exception(f"Error extracting text from image: {str(e)}")
    
    def extract_items_from_text(self, text: str) -> List[Dict]:
        """Extract items and prices from OCR text"""
        lines = text.split('\n')
        items = []
        flag=False
        temp_name=""
        # Pattern to match price (numbers with . or , as decimal separator)
        price_pattern = r'(-?\d+[.,]\d{2})'
        row_number=0
        
        for line in lines:
            line = line.strip()
            
            if not line:
                flag=True
                continue
            
            if not flag:
                temp_name=""
            temp_name+=line+" "
            # Look for lines with prices
            price_matches = re.findall(price_pattern, line)
            
            if price_matches:
                # Get the price (last match usually)
                price_str = price_matches[-1].replace(',', '.')
                try:
                    price = float(price_str)
                    
                    # Extract item name (text before the price)
                    item_text = re.sub(price_pattern, '', temp_name).strip()
                    row_number+=1
                    # Clean up item name
                    item_text = re.sub(r'\s+', ' ', item_text)
                    item_text = item_text.strip('.,- ')
                    
                    if len(item_text) > 1:  # Avoid very short meaningless text
                        items.append({
                            'row_number': row_number,
                            'dutch_name': item_text,
                            'english_name': '',
                            'price': price,
                            'quantity': 1,
                            'category': 'Uncategorized'
                        })
                        temp_name=""
                        flag=False
                except ValueError:
                    continue
        
        return items
