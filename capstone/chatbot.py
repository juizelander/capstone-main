import os
import json
from django.conf import settings
from PIL import Image

# ──────────────────────────────────────────────
#  📚 SCHOLARSYNC KNOWLEDGE BASE
#  Edit the info here and the AI will use it!
# ──────────────────────────────────────────────
KNOWLEDGE_BASE = """
ScholarSync Subic Overview:
- We are a centralized platform connecting students in Subic to local scholarship programs.
- Our core features include: Easy Application (one profile for multiple scholarships), Real-time Updates (notifications on application status), and Secure & Transparent processing.

How to Apply:
1. To apply for any program, visitors must register an account on the landing page first.
2. Once their account is approved by an admin, they can log in, view their dashboard, and submit applications directly to active programs.

Frequently Asked Questions (FAQs):
Q: Who is eligible for scholarships on ScholarSync?
A: Generally, bona fide residents of Subic who are currently enrolled or planning to enroll in college are eligible, though specific requirements vary by program.
Q: Are the scholarships free?
A: Yes, all scholarship applications through ScholarSync Subic are completely free.
Q: How will I know if I get approved?
A: You will receive real-time notifications on your dashboard, and an email update once the admin reviews your application.
Q: Where is the office located?
A: The administrative office is located at the Subic Municipal Hall.
Q: I forgot my password, what do I do?
A: If you cannot log in, please contact the administration directly for assistance with password recovery.
Q: Can I apply for more than one scholarship?
A: Yes! You can apply for as many active programs as you are eligible for using your single student profile.
Q: What if my documents are incomplete?
A: Your application will remain in a 'Pending' or 'Incomplete' status. Our admins will notify you via the dashboard or email about what is missing.
Q: How do I track my application status?
A: Just log in to your Student Dashboard. You'll see the status of every program you've applied for in real-time.
Q: Is there an age limit for the scholarships?
A: Every program has different rules. Most are for college students, but please check the specific 'View Details' section for each scholarship once you register.
Q: Can I use ScholarSync on my phone?
A: Yes! Our website is fully mobile-responsive, so you can apply and check updates anywhere using your smartphone.

Here are the Currently Active Programs on the platform:

1. Program Name: Edukalinga
   - Type: Financial Assistance
   - Application Dates: February 4, 2026 to February 25, 2026
   - Requirements: School ID, Transcript of Records (TOR), Voter's certificate

2. Program Name: Takbo Para Sa Ligtas na Juana
   - Type: Other Event/Program
   - Application Dates: February 2, 2026 to February 3, 2026
   - Requirements: None specified.

3. Program Name: 2026 DOST-SEI Undergraduate Scholarship
   - Type: Scholarship
   - Application Dates: February 20, 2026 to April 11, 2026
   - Requirements: Refer to the DOST-SEI official Facebook page post for full details.
"""

SYSTEM_INSTRUCTION = f"""
You are the official public-facing AI Assistant for 'ScholarSync Subic'.
You are speaking to visitors on our landing page who may not have an account yet.

LANGUAGE SUPPORT:
- You must be able to understand and respond in English, Tagalog, and Taglish (a mix of both).
- Always respond using the same language the user is using. If they ask in Tagalog, answer in Tagalog. If they use Taglish, you may use Taglish to be more relatable.

Your role is to:
1. Answer questions concisely and politely based ONLY on the provided Knowledge Base below to make them interested in our programs.
2. Encourage visitors to register an account so they can apply for these scholarships.
3. Be welcoming and act as a helpful guide to the available scholarships.
4. If a student asks a question that isn't covered in the Knowledge Base, politely tell them that you don't have that specific information and advise them to register or contact the administration.

--- KNOWLEDGE BASE ---
{KNOWLEDGE_BASE}
"""

# ──────────────────────────────────────────────
#  🔧 GEMINI SETUP
# ──────────────────────────────────────────────
_gemini_api_key = None

def _setup_gemini():
    """Load Gemini API key. Returns True if key is available."""
    global _gemini_api_key
    try:
        api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.environ.get('GEMINI_API_KEY', '')
        if not api_key:
            return False
        _gemini_api_key = api_key
        print("OK: Gemini API configured (via REST).")
        return True
    except Exception as e:
        print(f"WARN: Gemini setup failed: {e}")
        return False

# ──────────────────────────────────────────────
#  🔧 GROQ SETUP (via direct HTTP - no extra package needed)
# ──────────────────────────────────────────────
_groq_api_key = None

def _setup_groq():
    """Load Groq API key. Returns True if key is available."""
    global _groq_api_key
    try:
        import requests  # already installed with Django
        key = getattr(settings, 'GROQ_API_KEY', None) or os.environ.get('GROQ_API_KEY', '')
        if not key:
            print("WARN: Groq: No API key found, skipping.")
            return False
        _groq_api_key = key
        print("OK: Groq AI ready (via requests).")
        return True
    except Exception as e:
        print(f"WARN: Groq setup failed: {e}")
        return False

# Initialize both on startup
_gemini_ready = _setup_gemini()
_groq_ready = _setup_groq()

# ──────────────────────────────────────────────
#  💬 MAIN CHATBOT FUNCTION (Gemini → Groq fallback)
# ──────────────────────────────────────────────
def get_chatbot_response(user_message):
    """
    Sends a message to the AI and returns the response.
    Tries Gemini first; if it fails, automatically falls back to Groq.
    Creates a fresh session each request to avoid state corruption.
    """
    # ── Try Gemini first ──
    if _gemini_ready and _gemini_api_key:
        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={_gemini_api_key}"
            payload = {
                "system_instruction": {
                    "parts": {"text": SYSTEM_INSTRUCTION}
                },
                "contents": [
                    {"role": "user", "parts": [{"text": user_message}]}
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1024
                }
            }
            gemini_res = requests.post(url, json=payload, headers={'Content-Type': 'application/json'}, timeout=15)
            gemini_res.raise_for_status()
            data = gemini_res.json()
            if 'candidates' in data and len(data['candidates']) > 0:
                return data['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            print(f"WARN: Gemini REST failed (switching to Groq): {e}")

    # ── Fallback to Groq (via direct HTTP) ──
    if _groq_ready and _groq_api_key:
        try:
            import requests
            groq_response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {_groq_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": SYSTEM_INSTRUCTION},
                        {"role": "user", "content": user_message},
                    ],
                    "max_tokens": 1024,
                    "temperature": 0.7,
                },
                timeout=15,
            )
            groq_response.raise_for_status()
            return groq_response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"WARN: Groq also failed: {e}")

    # ── Both failed ──
    return "I'm sorry, I'm having trouble connecting right now. Please try again in a moment, or contact the administration for help!"


# ──────────────────────────────────────────────
#  📄 DOCUMENT VALIDATION (Gemini Vision)
# ──────────────────────────────────────────────
def validate_document(file_obj, expected_type="Document"):
    """
    Uses Gemini Vision to validate the quality and type of an uploaded document.
    Returns a dictionary: {'is_valid': bool, 'reason': str}
    """
    if not _gemini_ready or not _gemini_model:
        # Fallback if Gemini is not configured
        return {'is_valid': True, 'reason': 'AI validation skipped (not configured)'}

    try:
        img = Image.open(file_obj)

        prompt = f"""
        Analyze this uploaded image for a scholarship application.
        The student says this is a: {expected_type}.

        Your task:
        1. Check if the image is clear, readable, and not overly blurry.
        2. Verify if the content of the image matches a '{expected_type}' (e.g., Birth Certificate, Transcript of Records, Voter's Certificate, or School ID).
        3. If it looks like a completely different document (e.g., a selfie, a landscape, or a random object), mark it as invalid.

        Respond ONLY in a strict JSON format:
        {{
            "is_valid": true/false,
            "reason": "A brief explanation in English or Taglish if it is invalid (e.g., 'The image is too blurry' or 'This does not look like a Birth Certificate')"
        }}
        """

        response = _gemini_model.generate_content([prompt, img])

        cleaned_text = response.text.strip()
        if '```json' in cleaned_text:
            cleaned_text = cleaned_text.split('```json')[1].split('```')[0].strip()
        elif '```' in cleaned_text:
            cleaned_text = cleaned_text.split('```')[1].strip()

        result = json.loads(cleaned_text)
        return {
            'is_valid': result.get('is_valid', True),
            'reason': result.get('reason', 'Document accepted.')
        }

    except Exception as e:
        print(f"WARN: AI Document Validation Error: {e}")
        return {'is_valid': True, 'reason': 'AI validation unavailable, pending manual review.'}
