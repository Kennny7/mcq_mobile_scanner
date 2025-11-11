# buildozer.spec (key sections)
[app]
title = MCQ Scanner Mobile
package.name = mcqscanner
package.domain = com.yourname.mcqscanner

[buildozer]
log_level = 2

[requirements]
python3, kivy, kivymd, opencv, numpy, requests, beautifulsoup4, googlesearch-python, easyocr

[android]
permissions = CAMERA, INTERNET, WRITE_EXTERNAL_STORAGE

# Add these for OCR
android.add_src = ./src
android.add_resources = ./assets