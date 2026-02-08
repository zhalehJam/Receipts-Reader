# translator.py
from googletrans import Translator
from typing import List, Dict

class TranslationService:
    """Handles translation operations"""
    
    def __init__(self):
        self.translator = Translator()
    
    def translate_items(self, items: List[Dict]) -> List[Dict]:
        """Translate Dutch item names to English"""
        try:
            for item in items:
                if item['dutch_name'] and not item['english_name']:
                    translated = self.translator.translate(item['dutch_name'], src='nl', dest='en')
                    item['english_name'] = translated.text
        except Exception as e:
            print(f"Translation error: {e}")
            # If translation fails, copy dutch name
            for item in items:
                if not item['english_name']:
                    item['english_name'] = item['dutch_name']
        
        return items
    
    async def translate_text(self, text: str, src_lang: str = 'nl', dest_lang: str = 'en') -> str:
        """Translate single text"""
        try:
            result = await self.translator.translate(text, src=src_lang, dest=dest_lang)
            return result.text
        except Exception as e:
            print(f"Translation error: {e}")
            return text

