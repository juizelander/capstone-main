import os
import requests
import json

gemini_key = os.environ.get('GEMINI_API_KEY', 'AIzaSyAm5d4iCLHTbmnI-GPGNt1hk6bzwydC5aU')
groq_key = os.environ.get('GROQ_API_KEY', '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')

print("=== Testing Gemini ===")
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
payload = {
    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
}
res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
print("Status:", res.status_code)
print("Response:", res.text)

print("\n=== Testing Groq ===")
res2 = requests.post(
    "https://api.groq.com/openai/v1/chat/completions",
    headers={"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
    json={
        "model": "llama3-8b-8192",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 1024,
    }
)
print("Status:", res2.status_code)
try:
    print("Response:", json.dumps(res2.json(), indent=2))
except:
    print("Response:", res2.text)
