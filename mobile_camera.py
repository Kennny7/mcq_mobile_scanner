# mobile_camera.py
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.graphics.texture import Texture
import time
from utils.logger import app_logger
from utils.config import MobileConfig

class MobileCameraController:
    def __init__(self):
        self.camera = None
        self.is_camera_available = False
        self.current_frame = None
        self.frame_counter = 0
        self.capture_callback = None
        
        app_logger.info("MobileCameraController initialized")
    
    def initialize_camera(self):
        """Initialize mobile camera with error handling"""
        try:
            self.camera = Camera(
                resolution=MobileConfig.CAMERA_RESOLUTION,
                play=True,
                index=0  # Use back camera
            )
            self.is_camera_available = True
            app_logger.info("Camera initialized successfully")
            return True
            
        except Exception as e:
            app_logger.error(f"Camera initialization failed: {str(e)}")
            self.is_camera_available = False
            return False
    
    def capture_frame(self):
        """Capture current frame as image data"""
        if not self.is_camera_available or not self.camera.texture:
            return None
        
        try:
            # Get texture data
            texture = self.camera.texture
            buffer = texture.pixels
            return buffer, texture.size
            
        except Exception as e:
            app_logger.error(f"Frame capture error: {str(e)}")
            return None
    
    def capture_image(self):
        """Capture image and return as bytes for OCR"""
        frame_data = self.capture_frame()
        if frame_data:
            buffer, size = frame_data
            # Convert texture to JPEG bytes
            from PIL import Image
            import io
            
            # Convert buffer to PIL Image
            image = Image.frombytes('RGBA', size, buffer)
            # Convert to RGB and then to JPEG bytes
            rgb_image = image.convert('RGB')
            
            img_byte_arr = io.BytesIO()
            rgb_image.save(img_byte_arr, format='JPEG', quality=85)
            img_byte_arr.seek(0)
            
            app_logger.info("Image captured successfully")
            return img_byte_arr.getvalue()
        
        return None
    
    def set_capture_callback(self, callback):
        """Set callback for auto-capture mode"""
        self.capture_callback = callback
    
    def start_auto_capture(self):
        """Start automatic capture at intervals"""
        if self.capture_callback:
            Clock.schedule_interval(self.auto_capture, MobileConfig.AUTO_CAPTURE_INTERVAL)
    
    def stop_auto_capture(self):
        """Stop automatic capture"""
        Clock.unschedule(self.auto_capture)
    
    def auto_capture(self, dt):
        """Auto-capture callback"""
        if self.capture_callback:
            image_data = self.capture_image()
            if image_data:
                self.capture_callback(image_data)
    
    def stop_camera(self):
        """Stop camera and cleanup"""
        if self.camera:
            self.camera.play = False
            self.is_camera_available = False
            self.stop_auto_capture()
            app_logger.info("Camera stopped")