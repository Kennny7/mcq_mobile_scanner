# utils/logger.py
import logging
import os
from datetime import datetime
import inspect

class MobileLogger:
    def __init__(self, app_name="MCQScanner"):
        self.app_name = app_name
        self.setup_logging()
    
    def setup_logging(self):
        # Create logs directory
        if not os.path.exists('logs'):
            os.makedirs('logs')
        
        # Log file with timestamp
        log_filename = f"logs/{self.app_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
            handlers=[
                logging.FileHandler(log_filename),
                logging.StreamHandler()  # Also print to console
            ]
        )
        
        self.logger = logging.getLogger(self.app_name)
        self.logger.info("=== MCQ Mobile Scanner Started ===")
    
    def get_caller_info(self):
        """Get file and function name of caller"""
        stack = inspect.stack()
        # Skip current frame, get caller's frame
        caller_frame = stack[2]
        filename = os.path.basename(caller_frame.filename)
        function = caller_frame.function
        line_no = caller_frame.lineno
        return f"{filename}:{function}():{line_no}"
    
    def info(self, message):
        caller = self.get_caller_info()
        self.logger.info(f"[{caller}] {message}")
    
    def error(self, message):
        caller = self.get_caller_info()
        self.logger.error(f"[{caller}] {message}")
    
    def warning(self, message):
        caller = self.get_caller_info()
        self.logger.warning(f"[{caller}] {message}")
    
    def debug(self, message):
        caller = self.get_caller_info()
        self.logger.debug(f"[{caller}] {message}")

# Global logger instance
app_logger = MobileLogger()