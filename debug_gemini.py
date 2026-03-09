import os
import sys
import django

sys.path.append(r"c:\Users\Justin Lorenz\Downloads\capstone-main")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from capstone.chatbot import get_chatbot_response, _setup_gemini

print("Testing Internal REST Setup...")
print("Gemini Ready:", _setup_gemini())

print("\nSending Test Query...")
try:
    response = get_chatbot_response("Hello, what scholarships are available?")
    print("\nSUCCESS Response:", response)
except Exception as e:
    print("\nFAILED Error:", e)
