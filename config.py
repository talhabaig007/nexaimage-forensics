import os

class Config:
    SECRET_KEY = os.urandom(24)
    MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'tiff', 'tif'}
    
    # Supported languages for OCR
    OCR_LANGUAGES = {
        'eng': 'English',
        'urd': 'Urdu'
    }