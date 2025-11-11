# text_processor.py
import easyocr
import re

class TextProcessor:
    def __init__(self):
        self.reader = easyocr.Reader(['en'])
        self.mcq_pattern = r'([A-D])[\.\s\)]+\s*(.+?)(?=\s*(?:[A-D][\.\s\)]|$))'
        
    def extract_text(self, frame):
        """Extract text from frame using OCR"""
        results = self.reader.readtext(frame)
        full_text = ' '.join([result[1] for result in results])
        return full_text, results
    
    def parse_mcq(self, text):
        """Parse MCQ question and options from text"""
        # Find question (text before first option)
        question_match = re.search(r'^(.*?)(?=[A-D][\.\s\)])', text)
        question = question_match.group(1).strip() if question_match else text
        
        # Find options
        options = {}
        option_matches = re.findall(self.mcq_pattern, text + ' ')
        
        for match in option_matches:
            option_letter, option_text = match
            options[option_letter.upper()] = option_text.strip()
            
        return question, options
    
    def is_valid_question(self, question, options):
        """Check if we have a valid MCQ"""
        return len(question) > 10 and len(options) >= 2