# text_processor.py
import requests
import base64
import json
import re
from utils.logger import app_logger
from utils.config import MobileConfig

class TextProcessor:
    def __init__(self):
        self.mcq_pattern = r'([A-D])[\.\s\)]+\s*(.+?)(?=\s*(?:[A-D][\.\s\)]|$))'
        self.api_key = MobileConfig.OCR_SPACE_API_KEY
        self.api_url = "https://api.ocr.space/parse/image"
        
    def extract_text(self, image_data):
        """Extract text from image using OCR.Space API"""
        try:
            # Convert image to base64
            if hasattr(image_data, 'read'):  # File object
                encoded_image = base64.b64encode(image_data.read()).decode()
            else:  # Assume it's image bytes
                encoded_image = base64.b64encode(image_data).decode()
            
            payload = {
                'apikey': self.api_key,
                'base64Image': f"data:image/jpeg;base64,{encoded_image}",
                'language': 'eng',
                'isOverlayRequired': False,
                'OCREngine': 2  # Engine 2 is more accurate
            }
            
            response = requests.post(self.api_url, data=payload, timeout=30)
            result = response.json()
            
            if result.get('IsErroredOnProcessing'):
                error_msg = result.get('ErrorMessage', 'Unknown OCR error')
                app_logger.error(f"OCR API error: {error_msg}")
                return "", 0.0
            
            # Extract text and confidence
            parsed_results = result.get('ParsedResults', [])
            if parsed_results:
                text = parsed_results[0].get('ParsedText', '')
                confidence = float(parsed_results[0].get('TextOverlay', {}).get('MedianConfidence', 50))
                app_logger.info(f"OCR extracted text with confidence: {confidence}")
                return text, confidence / 100.0  # Convert to 0-1 scale
            
            return "", 0.0
            
        except Exception as e:
            app_logger.error(f"OCR extraction error: {str(e)}")
            return "", 0.0
    
    def parse_mcq(self, text):
        """Parse MCQ question and options from text - IMPROVED VERSION"""
        # First clean the text
        text = self.clean_text(text)
        
        # Split into lines for processing
        lines = text.split('\n')
        question_lines = []
        options = {}
        current_option = None
        option_text = []
        found_first_option = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line starts an option (A), B), etc.)
            option_match = re.match(r'^([A-D])[\.\s\)]\s*(.*)', line, re.IGNORECASE)
            if option_match:
                found_first_option = True
                
                # If we were collecting an option, save it
                if current_option and option_text:
                    options[current_option] = ' '.join(option_text).strip()
                
                # Start new option
                current_option = option_match.group(1).upper()
                option_text = [option_match.group(2).strip()]
                
            elif current_option:
                # Continue collecting current option text
                option_text.append(line)
            elif not found_first_option:
                # This line is part of the question (before any options)
                question_lines.append(line)
        
        # Save the last option if we were collecting one
        if current_option and option_text:
            options[current_option] = ' '.join(option_text).strip()
        
        # Join question lines and clean
        question = ' '.join(question_lines).strip()
        question = self.clean_question(question)
        
        # Debug logs
        app_logger.info(f"Extracted question: '{question}'")
        app_logger.info(f"Question length: {len(question)}")
        app_logger.info(f"Extracted options: {options}")
        app_logger.info(f"Number of options: {len(options)}")
        
        return question, options
    
    def clean_question(self, question):
        """Remove common header patterns from question"""
        # Remove patterns like "1)", "Title", etc.
        patterns = [
            r'^\s*\d+[\.\)]\s*',
            r'^\s*Title\s*',
            r'^\s*Question\s*\d*\s*',
            r'^\s*MCQ\s*\d*\s*',
            r'^\s*[Qq]\s*\d*[\.\)\:\-]\s*'
        ]
        
        for pattern in patterns:
            cleaned = re.sub(pattern, '', question, flags=re.IGNORECASE)
            # Only update if we actually removed something and result is not empty
            if cleaned.strip() and cleaned != question:
                question = cleaned
        
        return question.strip()
    
    def clean_text(self, text):
        """Clean OCR text"""
        # Remove extra whitespace but preserve newlines for line-by-line processing
        text = re.sub(r'[ \t]+', ' ', text)
        # Fix common OCR mistakes
        text = text.replace('|', 'I').replace('0', 'O')
        return text.strip()
    
    def is_valid_question(self, question, options):
        """Check if we have a valid MCQ"""
        # Check if question has meaningful content (not just headers)
        meaningful_question = len(question) > 20 or ('?' in question and len(question) > 10)
        # Check if we have at least 2 options
        valid_options = len(options) >= 2
        
        app_logger.info(f"Question validation - Meaningful: {meaningful_question}, Options: {valid_options}")
        return meaningful_question and valid_options