# utils/config.py
class MobileConfig:
    # Camera settings
    CAMERA_RESOLUTION = (640, 480)  # Lower for mobile performance
    PROCESSING_INTERVAL = 0.5  # Seconds between frame processing
    
    # OCR.Space API settings
    OCR_SPACE_API_KEY = "K83498410088957"  # Free API key - get from https://ocr.space/ocrapi
    OCR_CONFIDENCE_THRESHOLD = 0.5
    TEXT_MIN_LENGTH = 20
    
    # Capture modes
    AUTO_CAPTURE_INTERVAL = 2.0  # Seconds between auto-captures
    MANUAL_MODE = "manual"
    AUTO_MODE = "auto"
    
    # Search settings
    MAX_SEARCH_RESULTS = 3
    SEARCH_TIMEOUT = 15
    CACHE_DURATION = 300  # Cache results for 5 minutes
    
    # UI settings
    FONT_SIZE_SMALL = 14
    FONT_SIZE_MEDIUM = 18
    FONT_SIZE_LARGE = 22
    
    # Performance
    MAX_QUEUE_SIZE = 5
    FRAME_SKIP_COUNT = 3  # Process every 3rd frame