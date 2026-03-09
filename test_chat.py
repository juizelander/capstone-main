import os
import sys
import django

# Set up Django environment
sys.path.append(r"c:\Users\Justin Lorenz\Downloads\capstone-main")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capstone.settings')
django.setup()

from capstone.chatbot import get_chatbot_response, _setup_gemini, _setup_groq

print("Testing Gemini Setup...")
print("Gemini Ready:", _setup_gemini())

print("Testing Groq Setup...")
print("Groq Ready:", _setup_groq())

print("Testing Response...")
try:
    response = get_chatbot_response("Hello, what scholarships are available?")
    print("Response:", response)
except Exception as e:
    print("Error:", e)
