import pytesseract
from PIL import Image
import os

class OCRProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = Image.open(image_path)
    
    def extract_text(self, languages=None):
        """Extract text using OCR"""
        if languages is None:
            languages = ['eng', 'urd']
        
        results = {}
        lang_string = '+'.join(languages)
        
        try:
            # Configure tesseract
            custom_config = r'--oem 3 --psm 6'
            
            # Extract text
            text = pytesseract.image_to_string(
                self.image, 
                lang=lang_string,
                config=custom_config
            )
            
            results = {
                'available': True,
                'text': text.strip(),
                'word_count': len(text.split()),
                'character_count': len(text),
                'languages_used': languages
            }
        except Exception as e:
            results = {
                'available': False,
                'text': '',
                'word_count': 0,
                'character_count': 0,
                'error': str(e)
            }
        
        return results