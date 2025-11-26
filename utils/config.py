# utils/config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class MobileConfig:
    # Camera settings
    CAMERA_RESOLUTION = (640, 480)
    PROCESSING_INTERVAL = 0.5

    # OCR.Space API settings
    OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "")
    OCR_CONFIDENCE_THRESHOLD = 0.5
    TEXT_MIN_LENGTH = 20

    # Capture modes
    AUTO_CAPTURE_INTERVAL = 2.0
    MANUAL_MODE = "manual"
    AUTO_MODE = "auto"

    # Search settings
    MAX_SEARCH_RESULTS = 3
    SEARCH_TIMEOUT = 15
    CACHE_DURATION = 300

    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL = "gemini-2.5-flash-lite"
    GEMINI_TIMEOUT = 30
    GEMINI_MAX_RETRIES = 2

    # Answer confidence thresholds
    GEMINI_MIN_CONFIDENCE = 0.7
    SEARCH_FALLBACK_ENABLED = True

    # UI settings
    FONT_SIZE_SMALL = 14
    FONT_SIZE_MEDIUM = 18
    FONT_SIZE_LARGE = 22

    # Performance
    MAX_QUEUE_SIZE = 5
    FRAME_SKIP_COUNT = 3
