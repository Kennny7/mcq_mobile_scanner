# main.py
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import cv2
import numpy as np

from mobile_camera import MobileCameraController
from text_processor import TextProcessor
from question_solver import QuestionSolver
from utils.logger import app_logger
from utils.config import MobileConfig

class MCQMobileApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 10
        self.spacing = 10
        
        # Initialize components
        self.camera_controller = MobileCameraController()
        self.text_processor = TextProcessor()
        self.question_solver = QuestionSolver()
        
        self.current_question = None
        self.is_processing = False
        self.processing_scheduled = False
        
        app_logger.info("MCQMobileApp UI initializing")
        self.setup_ui()
        self.start_camera()
    
    def setup_ui(self):
        """Setup mobile-optimized UI"""
        # Title
        title = Label(
            text='MCQ Scanner Mobile',
            size_hint_y=0.1,
            font_size=MobileConfig.FONT_SIZE_LARGE,
            bold=True
        )
        self.add_widget(title)
        
        # Camera preview
        self.camera_preview = Image(
            size_hint_y=0.4
        )
        self.add_widget(self.camera_preview)
        
        # Status area
        self.status_label = Label(
            text='Initializing camera... Point at MCQ and hold still',
            size_hint_y=0.15,
            font_size=MobileConfig.FONT_SIZE_SMALL
        )
        self.add_widget(self.status_label)
        
        # Results area
        self.results_label = Label(
            text='Answer will appear here',
            size_hint_y=0.25,
            font_size=MobileConfig.FONT_SIZE_MEDIUM
        )
        self.add_widget(self.results_label)
        
        # Control buttons
        controls_layout = BoxLayout(
            orientation='horizontal',
            size_hint_y=0.1,
            spacing=10
        )
        
        self.start_btn = Button(text='Start Scanning')
        self.start_btn.bind(on_press=self.toggle_scanning)
        controls_layout.add_widget(self.start_btn)
        
        self.stop_btn = Button(text='Stop')
        self.stop_btn.bind(on_press=self.stop_scanning)
        controls_layout.add_widget(self.stop_btn)
        
        self.add_widget(controls_layout)
        
        app_logger.info("UI setup completed")
    
    def start_camera(self):
        """Initialize and start camera"""
        if self.camera_controller.initialize_camera():
            self.add_widget(self.camera_controller.camera)
            # Start processing loop
            Clock.schedule_interval(self.update, MobileConfig.PROCESSING_INTERVAL)
            self.status_label.text = "Camera ready. Point at MCQ and hold still."
            app_logger.info("Camera processing started")
        else:
            self.status_label.text = "Camera not available"
            app_logger.error("Camera could not be started")
    
    def update(self, dt):
        """Main update loop - optimized for mobile"""
        if self.is_processing or self.processing_scheduled:
            return
        
        frame = self.camera_controller.capture_frame()
        if frame and self.camera_controller.check_stability():
            self.processing_scheduled = True
            Clock.schedule_once(lambda dt: self.process_question(), 0.1)
    
    def process_question(self):
        """Process question from current frame"""
        self.is_processing = True
        self.processing_scheduled = False
        
        app_logger.info("Starting question processing")
        self.status_label.text = "Processing question..."
        
        try:
            # Convert texture to numpy array for OCR
            frame_data = self.frame_to_numpy(self.camera_controller.current_frame)
            
            # Extract and parse text
            text, confidence = self.text_processor.extract_text(frame_data)
            app_logger.info(f"OCR extracted text (confidence: {confidence:.2f}): {text[:100]}...")
            
            if confidence >= MobileConfig.OCR_CONFIDENCE_THRESHOLD:
                question, options = self.text_processor.parse_mcq(text)
                
                if self.text_processor.is_valid_question(question, options):
                    app_logger.info(f"Valid question found: {question[:50]}...")
                    self.current_question = (question, options)
                    self.search_answer(question, options)
                else:
                    self.status_label.text = "No valid question detected"
                    app_logger.warning("Invalid question format detected")
            else:
                self.status_label.text = "Low text confidence"
                app_logger.warning(f"Low OCR confidence: {confidence}")
                
        except Exception as e:
            app_logger.error(f"Question processing error: {str(e)}")
            self.status_label.text = f"Error: {str(e)}"
        
        self.is_processing = False
    
    def frame_to_numpy(self, texture):
        """Convert Kivy texture to numpy array"""
        try:
            buffer = texture.pixels
            image_data = np.frombuffer(buffer, dtype=np.uint8)
            image_data = image_data.reshape(texture.height, texture.width, 4)
            return cv2.cvtColor(image_data, cv2.COLOR_RGBA2BGR)
        except Exception as e:
            app_logger.error(f"Frame conversion error: {str(e)}")
            return None
    
    def search_answer(self, question, options):
        """Search for answer online"""
        app_logger.info(f"Searching answer for question: {question[:50]}...")
        self.status_label.text = "Searching for answer..."
        
        def search_thread():
            try:
                answers = self.question_solver.search_question(question, options)
                
                # Update UI in main thread
                Clock.schedule_once(lambda dt: self.display_results(answers, options))
                
            except Exception as e:
                app_logger.error(f"Search error: {str(e)}")
                Clock.schedule_once(lambda dt: self.display_error(str(e)))
        
        # Run search in background
        import threading
        thread = threading.Thread(target=search_thread)
        thread.daemon = True
        thread.start()
    
    def display_results(self, answers, options):
        """Display results in UI"""
        try:
            if "error" in answers:
                result_text = f"Search Error: {answers['error']}"
                app_logger.error(f"Search returned error: {answers['error']}")
            else:
                answer_text = ", ".join(answers) if isinstance(answers, list) else str(answers)
                options_text = "\n".join([f"{k}: {v}" for k, v in options.items()])
                result_text = f"Options:\n{options_text}\n\nAnswer: {answer_text}"
                app_logger.info(f"Answer found: {answer_text}")
            
            self.results_label.text = result_text
            self.status_label.text = "Answer found! Move to next question."
            
        except Exception as e:
            app_logger.error(f"Results display error: {str(e)}")
            self.results_label.text = f"Display error: {str(e)}"
    
    def display_error(self, error_msg):
        """Display error message"""
        self.status_label.text = f"Error: {error_msg}"
        self.results_label.text = "Could not get answer"
        app_logger.error(f"Error displayed to user: {error_msg}")
    
    def toggle_scanning(self, instance):
        """Toggle scanning on/off"""
        self.is_processing = not self.is_processing
        if self.is_processing:
            self.start_btn.text = "Pause Scanning"
            self.status_label.text = "Scanning active..."
            app_logger.info("Scanning activated")
        else:
            self.start_btn.text = "Resume Scanning"
            self.status_label.text = "Scanning paused"
            app_logger.info("Scanning paused")
    
    def stop_scanning(self, instance):
        """Stop scanning completely"""
        self.is_processing = False
        self.camera_controller.stop_camera()
        self.status_label.text = "Scanning stopped"
        app_logger.info("Scanning stopped by user")

class MCQMobileAppClass(App):
    def build(self):
        self.title = "MCQ Scanner Mobile"
        return MCQMobileApp()

if __name__ == '__main__':
    try:
        app_logger.info("=== Starting MCQ Mobile Scanner App ===")
        MCQMobileAppClass().run()
    except Exception as e:
        app_logger.error(f"App crashed: {str(e)}")
        raise