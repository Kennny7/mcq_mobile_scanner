# question_solver.py
from googlesearch import search
import requests
from bs4 import BeautifulSoup
import re
from utils.logger import app_logger
from utils.config import MobileConfig

class QuestionSolver:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36'
        })
    
    def search_question(self, question, options):
        """Search question online and find answers"""
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