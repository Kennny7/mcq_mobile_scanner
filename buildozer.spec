[app]

# ====================
# BASIC APP INFORMATION
# ====================

# (str) Title of your application
title = MCQ Scanner Mobile

# (str) Package name
package.name = mcqscanner

# (str) Package domain (needed for android/ios packaging)
package.domain = com.kennny.mcqscanner

# (str) Source code where the main.py live
source.dir = .

# (str) Application versioning (method 1)
version = 1.0.0

# ====================
# SOURCE FILE MANAGEMENT
# ====================

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,jpeg,kv,atlas,txt,ttf,json,md

# (list) List of inclusions using pattern matching
source.include_patterns = assets/*,utils/*,logs/*,data/*

# (list) Source files to exclude (let empty to not exclude anything)
source.exclude_exts = spec,pyc,pyo

# (list) List of directory to exclude (let empty to not exclude anything)
source.exclude_dirs = bin,venv,__pycache__,*.egg-info,.git,.github,tests,docs

# (list) List of exclusions using pattern matching
source.exclude_patterns = license,images/*/*.jpg

# ====================
# APP DEPENDENCIES
# ====================

# (list) Application requirements
requirements = 
    python3,
    kivy==2.3.1,
    kivymd==1.2.0,
    # numpy,
    # opencv-python-headless,
    requests==2.32.5,
    beautifulsoup4==4.14.2,
    googlesearch_python==1.3.0,
    pillow,
    chardet==5.2.0,
    urllib3==2.0.7,
    setuptools==68.2.2,
    cython==0.29.36,
    hostpython3,
    android
    # openblas
    # torch==2.9.0,
    # torchvision==0.24.0,
    # easyocr==1.7.2,

# ====================
# APP APPEARANCE
# ====================

# (str) Presplash of the application
presplash.filename = assets/presplash.png

# (str) Icon of the application
icon.filename = assets/icon.png

# (list) Supported orientations
# Options: landscape, portrait, portrait-reverse, landscape-reverse
orientation = portrait

# ====================
# ANDROID SPECIFIC
# ====================

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = 
    CAMERA,
    INTERNET,
    READ_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE,
    ACCESS_NETWORK_STATE,
    WAKE_LOCK

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK / AAB will support.
android.minapi = 21

# (list) The Android archs to build for
# Choices: armeabi-v7a, arm64-v8a, x86, x86_64
# android.archs = arm64-v8a, armeabi-v7a
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (bool) Indicate whether the screen should stay on
android.wakelock = True

# (list) Gradle dependencies to add
android.gradle_dependencies = 
    androidx.appcompat:appcompat:1.6.1,
    androidx.camera:camera-core:1.2.3,
    androidx.camera:camera-camera2:1.2.3,
    androidx.camera:camera-lifecycle:1.2.3,
    androidx.camera:camera-view:1.2.3

# (bool) Enable AndroidX support
android.enable_androidx = True

# (list) Java compile options for modern Java features
android.add_compile_options = 
    "sourceCompatibility = 1.8",
    "targetCompatibility = 1.8"

# (list) Put these files or directories in the apk assets directory.
android.add_assets = assets

# (str) The format used to package the app for release mode (aab or apk)
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk)
android.debug_artifact = apk

# (list) Android additional libraries to copy
# android.add_libs_armeabi_v7a = libs/android-v7/*.so
# android.add_libs_arm64_v8a = libs/android-v8/*.so

# ====================
# PYTHON FOR ANDROID (P4A) SPECIFIC
# ====================

# (str) Bootstrap to use for android builds
p4a.bootstrap = sdl2

# Control passing the --use-setup-py vs --ignore-setup-py to p4a
p4a.setup_py = false

# ====================
# IOS SPECIFIC
# ====================

# (str) python-for-ios URL to use for checkout
ios.kivy_ios_url = https://github.com/kivy/kivy-ios
ios.kivy_ios_branch = master

# Another platform dependency: ios-deploy
ios.ios_deploy_url = https://github.com/phonegap/ios-deploy
ios.ios_deploy_branch = 1.10.0

# ====================
# BUILD PROCESS CONFIGURATION
# ====================

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .aab, .ipa) storage
bin_dir = ./bin

java.heap.size = 2g

# And optionally:
android.gradle_version = 7.0.2
android.compile_sdk_version = 33
android.min_sdk_version = 21
android.target_sdk_version = 33

# ====================
# PROFILES (OPTIONAL)
# ====================

# Uncomment and modify below for different build profiles

# [app@demo]
# title = MCQ Scanner Mobile (Demo)
# 
# [app:source.exclude_patterns@demo]
# data/sensitive/*
# 
# [app:requirements@demo]
# python3,kivy==2.3.1,kivymd==1.2.0,numpy,opencv-python,easyocr

# ====================
# CUSTOM RECIPES (IF NEEDED)
# ====================

# Uncomment and add custom recipes if any dependency needs special handling

# [buildozer]
# p4a.local_recipes = ./recipes