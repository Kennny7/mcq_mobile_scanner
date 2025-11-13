############################################################
# Buildozer Specification for MCQ Mobile Scanner
# (Generated for: C:\Users\ACER\Desktop\mcq_mobile_scanner)
############################################################

[app]
# Basic app info
title = MCQ Scanner Mobile
package.name = mcqscanner
package.domain = com.kennny.mcqscanner

# Main entry point
source.dir = .
entrypoint = main.py

# App version
version = 1.0.0

# Files to include in build
source.include_exts = py,kv,png,jpg,jpeg,txt,md,json,log

# Include extra folders (optional)
source.include_patterns = assets/*, utils/*, logs/*

# Kivy requirements and OCR dependencies
# requirements = python3,kivy==2.3.1,kivymd,opencv-python,numpy==2.3.4,requests==2.32.5,beautifulsoup4==4.14.2,googlesearch_python==1.3.0,easyocr==1.7.2,torch,torchvision

requirements = python3,kivy==2.3.1,kivymd==1.2.0,numpy==2.2.6,beautifulsoup4==4.14.2,requests==2.32.5,easyocr==1.7.2,googlesearch_python==1.3.0,opencv-python==4.12.0.88,torch==2.9.0,torchvision==0.24.0


# Orientation / display settings
orientation = portrait
fullscreen = 0

# App icon and presplash (optional), icon size is 1024×1024 px and preplash size 1080 × 1920 px portrait
icon.filename = assets/icon.png
presplash.filename = assets/presplash.png

# Supported architecture
android.archs = armeabi-v7a, arm64-v8a

# Android permissions
android.permissions = CAMERA, INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Extra Android-specific options
android.allow_backup = True
android.debug = True

# Minimum and target Android API
android.api = 33
android.minapi = 21

# Optional: prevent automatic screen rotation
android.orientation = portrait

############################################################
# Buildozer global configuration
############################################################

[buildozer]
log_level = 2
warn_on_root = 1

############################################################
# Android packaging
############################################################

[android]
# Optional gradle dependencies for camera and compatibility
android.gradle_dependencies = com.android.support:appcompat-v7:28.0.0
android.add_src = ./src
android.add_resources = ./assets

# Optional if you use camera / OpenCV features
android.enable_androidx = True

############################################################
# iOS (if ever needed)
############################################################

[ios]
# Empty for now; can be configured later if porting to iOS
