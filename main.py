# main.py
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFloatingActionButton
from kivymd.uix.card import MDCard
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.snackbar import Snackbar
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import threading
import io
import os
import datetime

from mobile_camera import MobileCameraController
from text_processor import TextProcessor
from question_solver import QuestionSolver
from utils.logger import app_logger
from utils.config import MobileConfig

class MCQMobileApp(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = "10dp"
        self.spacing = "10dp"
        
        # Initialize components
        self.camera_controller = MobileCameraController()
        self.text_processor = TextProcessor()
        self.question_solver = QuestionSolver()
        
        self.current_question = None
        self.is_processing = False
        self.capture_mode = MobileConfig.MANUAL_MODE
        
        # Create logs directory if it doesn't exist
        self.logs_dir = "logs"
        os.makedirs(self.logs_dir, exist_ok=True)
        
        app_logger.info("MCQMobileApp UI initializing")
        self.setup_ui()
        self.start_camera()
    
    def setup_ui(self):
        """Setup KivyMD mobile-optimized UI"""
        # App title
        title = MDLabel(
            text='[b]MCQ Scanner Mobile[/b]',
            halign='center',
            size_hint_y=0.08,
            theme_text_color="Primary",
            markup=True
        )
        self.add_widget(title)
        
        # Camera preview card
        camera_card = MDCard(
            orientation='vertical',
            size_hint_y=0.4,
            padding="10dp",
            spacing="10dp"
        )
        
        camera_label = MDLabel(
            text='Camera Preview',
            halign='center',
            size_hint_y=0.2
        )
        camera_card.add_widget(camera_label)
        
        self.camera_preview = MDBoxLayout(
            size_hint_y=0.8
        )
        camera_card.add_widget(self.camera_preview)
        
        self.add_widget(camera_card)
        
        # Status card
        status_card = MDCard(
            orientation='vertical',
            size_hint_y=0.15,
            padding="10dp"
        )
        
        self.status_label = MDLabel(
            text='Initializing camera... Point at MCQ question',
            halign='center'
        )
        status_card.add_widget(self.status_label)
        
        self.progress_bar = MDProgressBar(
            size_hint_y=0.3
        )
        self.progress_bar.opacity = 0  # Hidden initially
        status_card.add_widget(self.progress_bar)
        
        self.add_widget(status_card)
        
        # Results card
        results_card = MDCard(
            orientation='vertical',
            size_hint_y=0.25,
            padding="15dp"
        )
        
        results_label = MDLabel(
            text='[b]Results[/b]',
            halign='center',
            theme_text_color="Primary",
            markup=True
        )
        results_card.add_widget(results_label)
        
        self.results_text = MDLabel(
            text='Answer will appear here after scanning',
            halign='center',
            theme_text_color="Secondary"
        )
        results_card.add_widget(self.results_text)
        
        self.add_widget(results_card)
        
        # Control buttons
        controls_layout = MDBoxLayout(
            orientation='horizontal',
            size_hint_y=0.12,
            spacing="10dp"
        )
        
        self.mode_btn = MDRaisedButton(
            text='Auto Mode',
            size_hint_x=0.4
        )
        self.mode_btn.bind(on_press=self.toggle_mode)
        controls_layout.add_widget(self.mode_btn)
        
        self.capture_btn = MDFloatingActionButton(
            icon="camera",
            size_hint_x=0.3
        )
        self.capture_btn.bind(on_press=self.capture_manual)
        controls_layout.add_widget(self.capture_btn)
        
        self.clear_btn = MDRaisedButton(
            text='Clear',
            size_hint_x=0.3
        )
        self.clear_btn.bind(on_press=self.clear_results)
        controls_layout.add_widget(self.clear_btn)
        
        self.add_widget(controls_layout)
        
        app_logger.info("KivyMD UI setup completed")
    
    def show_snackbar(self, message):
        """Helper method to show snackbar with proper API for KivyMD 1.2.0"""
        try:
            # For KivyMD 1.2.0, use the old Snackbar API but suppress deprecation
            snackbar = Snackbar()
            snackbar.text = message
            snackbar.duration = 3
            snackbar.open()
        except Exception as e:
            app_logger.error(f"Failed to show snackbar: {str(e)}")
            # Fallback: just log the message
            app_logger.info(f"Snackbar message: {message}")
    
    def log_extracted_text(self, text, confidence, success=True):
        """Log extracted text to a file for debugging"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_file = os.path.join(self.logs_dir, "extracted_text.log")
            
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*60}\n")
                f.write(f"Timestamp: {timestamp}\n")
                f.write(f"Confidence: {confidence}\n")
                f.write(f"Status: {'SUCCESS' if success else 'FAILED'}\n")
                f.write(f"Extracted Text:\n{text}\n")
                f.write(f"{'='*60}\n\n")
            
            app_logger.info(f"Extracted text logged to {log_file}")
        except Exception as e:
            app_logger.error(f"Failed to log extracted text: {str(e)}")
    
    def start_camera(self):
        """Initialize and start camera"""
        if self.camera_controller.initialize_camera():
            self.camera_preview.add_widget(self.camera_controller.camera)
            self.status_label.text = "Camera ready. Tap capture or use auto mode."
            app_logger.info("Camera started successfully")
            
            # Set up auto-capture callback
            self.camera_controller.set_capture_callback(self.process_captured_image)
        else:
            self.status_label.text = "Camera not available"
            self.show_snackbar("Camera initialization failed!")
            app_logger.error("Camera could not be started")
    
    def toggle_mode(self, instance):
        """Toggle between manual and auto capture modes"""
        if self.capture_mode == MobileConfig.MANUAL_MODE:
            self.capture_mode = MobileConfig.AUTO_MODE
            self.mode_btn.text = "Manual Mode"
            self.camera_controller.start_auto_capture()
            self.status_label.text = "Auto mode: Scanning every 2 seconds"
            self.show_snackbar("Auto capture mode activated")
            app_logger.info("Switched to auto capture mode")
        else:
            self.capture_mode = MobileConfig.MANUAL_MODE
            self.mode_btn.text = "Auto Mode"
            self.camera_controller.stop_auto_capture()
            self.status_label.text = "Manual mode: Tap camera to capture"
            self.show_snackbar("Manual capture mode activated")
            app_logger.info("Switched to manual capture mode")
    
    def capture_manual(self, instance):
        """Manual capture button handler"""
        if self.is_processing:
            self.show_snackbar("Already processing, please wait...")
            return
        
        self.status_label.text = "Capturing image..."
        app_logger.info("Manual capture triggered")
        
        # Capture image
        image_data = self.camera_controller.capture_image()
        if image_data:
            self.process_captured_image(image_data)
        else:
            self.status_label.text = "Capture failed"
            self.show_snackbar("Capture failed!")
    
    def process_captured_image(self, image_data):
        """Process captured image through OCR and search"""
        if self.is_processing:
            return
            
        self.is_processing = True
        self.progress_bar.opacity = 1
        self.progress_bar.start()
        
        app_logger.info("Starting image processing pipeline")
        self.status_label.text = "Processing image..."
        
        def processing_thread():
            try:
                # Step 1: OCR text extraction
                self.status_label.text = "Extracting text..."
                text, confidence = self.text_processor.extract_text(image_data)
                app_logger.info(f"OCR confidence: {confidence:.2f}")
                
                # Log extracted text regardless of confidence
                self.log_extracted_text(text, confidence, success=(confidence >= MobileConfig.OCR_CONFIDENCE_THRESHOLD))
                
                if confidence >= MobileConfig.OCR_CONFIDENCE_THRESHOLD:
                    # Step 2: Parse MCQ
                    question, options = self.text_processor.parse_mcq(text)
                    
                    if self.text_processor.is_valid_question(question, options):
                        app_logger.info(f"Valid question: {question[:50]}...")
                        
                        # Step 3: Search for answer
                        self.status_label.text = "Searching for answer..."
                        answers = self.question_solver.search_question(question, options)
                        
                        # Update UI in main thread
                        Clock.schedule_once(lambda dt: self.display_results(
                            question, options, answers, confidence
                        ))
                    else:
                        Clock.schedule_once(lambda dt: self.display_error(
                            "No valid MCQ format detected"
                        ))
                else:
                    Clock.schedule_once(lambda dt: self.display_error(
                        f"Low text confidence: {confidence:.2f}"
                    ))
                    
            except Exception as e:
                app_logger.error(f"Processing error: {str(e)}")
                # Log the error with empty text to indicate failure
                self.log_extracted_text("EXTRACTION FAILED - " + str(e), 0.0, success=False)
                Clock.schedule_once(lambda dt: self.display_error(str(e)))
            
            finally:
                Clock.schedule_once(lambda dt: self.processing_complete())
        
        # Run processing in background thread
        thread = threading.Thread(target=processing_thread)
        thread.daemon = True
        thread.start()
    
    def display_results(self, question, options, answers, confidence):
        """Display search results"""
        try:
            options_text = "\n".join([f"{k}: {v}" for k, v in options.items()])
            
            if "error" in answers:
                result_text = f"❌ Search Error:\n{answers['error']}"
            elif answers and answers[0] != "Not found":
                answer_text = ", ".join(answers)
                result_text = f"✅ Question:\n{question[:100]}...\n\nOptions:\n{options_text}\n\n🎯 Answer: {answer_text}\n(Confidence: {confidence:.1%})"
                self.show_snackbar("Answer found!")
            else:
                result_text = f"❓ Question:\n{question[:100]}...\n\nOptions:\n{options_text}\n\n🤷 No clear answer found"
                self.show_snackbar("No clear answer found")
            
            self.results_text.text = result_text
            self.status_label.text = "Processing complete!"
            
        except Exception as e:
            app_logger.error(f"Results display error: {str(e)}")
            self.results_text.text = f"Error displaying results: {str(e)}"
    
    def display_error(self, error_msg):
        """Display error message"""
        self.status_label.text = f"Error: {error_msg}"
        self.results_text.text = "Could not process image"
        self.show_snackbar(f"Error: {error_msg}")
        app_logger.error(f"Error displayed: {error_msg}")
    
    def processing_complete(self):
        """Clean up after processing"""
        self.is_processing = False
        self.progress_bar.opacity = 0
        self.progress_bar.stop()
    
    def clear_results(self, instance):
        """Clear results and reset state"""
        self.results_text.text = "Answer will appear here after scanning"
        self.status_label.text = "Ready for next question"
        self.show_snackbar("Results cleared")
        app_logger.info("Results cleared")

class MCQMobileAppClass(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Blue"
        self.title = "MCQ Scanner Mobile"
        return MCQMobileApp()

if __name__ == '__main__':
    try:
        app_logger.info("=== Starting MCQ Mobile Scanner App ===")
        MCQMobileAppClass().run()
    except Exception as e:
        app_logger.error(f"App crashed: {str(e)}")
        raise