# utils/config.py
class MobileConfig:
    # Camera settings
    CAMERA_RESOLUTION = (640, 480)  # Lower for mobile performance
    STABLE_TIME_THRESHOLD = 3.0
    PROCESSING_INTERVAL = 0.5  # Seconds between frame processing
    
    # OCR settings
    OCR_CONFIDENCE_THRESHOLD = 0.6
    TEXT_MIN_LENGTH = 20
    
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