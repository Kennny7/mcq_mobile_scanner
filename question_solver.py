# question_solver.py
import google.generativeai as genai
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import re
import time
from utils.logger import app_logger
from utils.config import MobileConfig

class QuestionSolver:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36'
        })
        
        # Initialize Gemini AI
        try:
            genai.configure(api_key=MobileConfig.GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel(MobileConfig.GEMINI_MODEL)
            self.gemini_available = True
            app_logger.info("Gemini AI initialized successfully")
        except Exception as e:
            self.gemini_available = False
            app_logger.warning(f"Gemini AI initialization failed: {str(e)}")
    
    def search_question(self, question, options):
        """Search question using Gemini AI with fallback to Google search"""
        # Try Gemini AI first
        if self.gemini_available:
            gemini_answer = self.ask_gemini(question, options)
            if gemini_answer and gemini_answer[0] != "Not found":
                app_logger.info(f"Gemini provided answer: {gemini_answer}")
                return gemini_answer
        
        # Fallback to Google search
        app_logger.info("Falling back to Google search")
        return self.search_with_google(question, options)
    
    def ask_gemini(self, question, options):
        """Ask Gemini AI to solve the MCQ question"""
        try:
            # Create the prompt
            prompt = self.create_gemini_prompt(question, options)
            
            # Generate response
            response = self.gemini_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Low temperature for consistent answers
                    max_output_tokens=500,
                )
            )
            
            # Parse the response
            return self.parse_gemini_response(response.text, options)
            
        except Exception as e:
            app_logger.error(f"Gemini API error: {str(e)}")
            return None
    
    def create_gemini_prompt(self, question, options):
        """Create optimized prompt for Gemini"""
        options_text = "\n".join([f"{key}) {value}" for key, value in options.items()])
        
        prompt = f"""
        IMPORTANT: You are an expert at solving Multiple Choice Questions (MCQs). 
        Analyze the following question and options carefully, then provide your answer.

        QUESTION:
        {question}

        OPTIONS:
        {options_text}

        INSTRUCTIONS:
        1. First, provide ONLY the correct option letter(s) (e.g., "A" or "C" or "A,C" for multiple answers)
        2. After that, you may provide a brief explanation
        3. If you're uncertain, provide your best guess
        4. If the question cannot be answered, respond with "Not found"

        YOUR RESPONSE FORMAT:
        Start with: "Answer: [option letters]"
        Then optionally: "Explanation: [brief explanation]"

        Now, provide your answer:
        """
        
        return prompt
    
    def parse_gemini_response(self, response, options):
        """Parse Gemini response to extract answers"""
        try:
            # Clean the response
            response = response.strip()
            app_logger.info(f"Gemini raw response: {response}")
            
            # Look for answer patterns
            answer_patterns = [
                r'Answer:\s*([A-E,]+)',
                r'^([A-E,]+)$',
                r'Correct.*?([A-E,]+)',
                r'Option.*?([A-E,]+)',
            ]
            
            for pattern in answer_patterns:
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    answer_letters = match.group(1).strip().upper()
                    # Split multiple answers if any
                    answers = [letter.strip() for letter in answer_letters.split(',')]
                    
                    # Validate that all answers are in the options
                    valid_answers = [ans for ans in answers if ans in options]
                    if valid_answers:
                        return valid_answers
            
            # If no clear answer found, check if response contains option letters
            for option in options.keys():
                if re.search(rf'\b{option}\b', response, re.IGNORECASE):
                    return [option]
            
            return ["Not found"]
            
        except Exception as e:
            app_logger.error(f"Error parsing Gemini response: {str(e)}")
            return ["Not found"]
    
    def search_with_google(self, question, options):
        """Fallback: Search question using Google"""
        search_query = f'"{question}"'
        
        try:
            # Get search results
            search_results = list(search(
                search_query, 
                num_results=MobileConfig.MAX_SEARCH_RESULTS,
                timeout=MobileConfig.SEARCH_TIMEOUT
            ))
            
            # Analyze each result
            answers = self.analyze_results(search_results, question, options)
            return answers
            
        except Exception as e:
            app_logger.error(f"Search error: {str(e)}")
            return {"error": str(e)}
    
    def analyze_results(self, urls, question, options):
        """Analyze search results to find correct answers"""
        answer_counts = {option: 0 for option in options.keys()}
        total_matches = 0
        
        for url in urls:
            try:
                page_content = self.extract_page_content(url)
                page_answers = self.find_answers_in_content(page_content, question, options)
                
                for answer in page_answers:
                    if answer in answer_counts:
                        answer_counts[answer] += 1
                        total_matches += 1
                        
            except Exception as e:
                app_logger.warning(f"Failed to analyze {url}: {str(e)}")
                continue
        
        # Return answers with confidence
        if total_matches > 0:
            confident_answers = [
                option for option, count in answer_counts.items() 
                if count > 0 and count / total_matches >= 0.3
            ]
            return confident_answers if confident_answers else ["Not found"]
        
        return ["Not found"]
    
    def extract_page_content(self, url):
        """Extract main content from webpage"""
        response = self.session.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        return soup.get_text()
    
    def find_answers_in_content(self, content, question, options):
        """Find answers in text content"""
        found_answers = []
        content_lower = content.lower()
        question_keywords = ' '.join(question.lower().split()[:10])  # First 10 words
        
        # Look for answer patterns
        for option, option_text in options.items():
            option_lower = option_text.lower()
            
            # Check if option appears near question keywords
            if (question_keywords in content_lower and 
                option_lower in content_lower):
                found_answers.append(option)
            
            # Look for "Answer: A" patterns
            answer_patterns = [
                f'answer[:\s]+{option}',
                f'correct[:\s]+{option}',
                f'{option}[\.\s]+.*?correct',
            ]
            
            for pattern in answer_patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    found_answers.append(option)
        
        return found_answers