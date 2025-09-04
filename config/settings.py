# Application settings
APP_NAME = "Receipt Processing App"
APP_VERSION = "1.0.0"

# Database settings
DATABASE_NAME = "receipts.db"

# OCR settings
OCR_LANGUAGES = "nld+eng"
TESSERACT_CONFIG = "--psm 6"

# Translation settings
DEFAULT_SOURCE_LANG = "nl"
DEFAULT_TARGET_LANG = "en"

# Categories
DEFAULT_CATEGORIES = [
    'Groceries', 'Electronics', 'Clothing', 'Health & Beauty',
    'Home & Garden', 'Sports', 'Books', 'Restaurants', 'Other'
]

# Image settings
MAX_IMAGE_SIZE = (800, 1200)
SUPPORTED_FORMATS = ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tiff"]