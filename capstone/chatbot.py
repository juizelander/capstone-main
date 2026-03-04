import os
import google.generativeai as genai
from django.conf import settings
from PIL import Image
import io
import json

# Initialize the Gemini API client
# We try to get the API key from Django settings, or fallback to environment variables
api_key = getattr(settings, 'GEMINI_API_KEY', os.environ.get('GEMINI_API_KEY'))

if api_key:
    genai.configure(api_key=api_key)
    
    # Set up the model with a system prompt
    generation_config = {
      "temperature": 0.7,
      "top_p": 0.95,
      "top_k": 40,
      "max_output_tokens": 8192,
    }

    # ----------------------------------------------------------------------
    # 🧠 SCHOLARSYNC KNOWLEDGE BASE
    # ----------------------------------------------------------------------
    # You can paste all the information about your scholarships, deadlines, 
    # requirements, and FAQ answers right here between these triple quotes.
    # The AI will read this and use it to answer student questions!
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

    
    # Define the system instruction to give the chatbot its personality and rules
    system_instruction = f"""
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

    model = genai.GenerativeModel(
        model_name="gemini-flash-latest",
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    
    # Start a chat session (this won't maintain state across requests by default, 
    # but provides the structure if we want to pass history later)
    chat_session = model.start_chat(history=[])
else:
    model = None
    chat_session = None

def get_chatbot_response(user_message):
    """
    Sends a message to the Gemini API and returns the text response.
    Returns an error message if the API key is not configured or an error occurs.
    """
    if not api_key or not chat_session:
        return "I apologize, but my AI services are not fully configured right now. Please check that the GEMINI_API_KEY is set."
        
    try:
        response = chat_session.send_message(user_message)
        return response.text
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return "I'm having a little trouble connecting right now. Please try again later!"

def validate_document(file_obj, expected_type="Document"):
    """
    Uses Gemini Vision to validate the quality and type of an uploaded document.
    Returns a dictionary: {'is_valid': bool, 'reason': str}
    """
    if not api_key or not model:
        # Fallback if API is not configured
        return {'is_valid': True, 'reason': 'AI validation skipped (not configured)'}

    try:
        # Open the image using PIL
        img = Image.open(file_obj)
        
        # Determine the prompt based on expected type
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
        
        # Use the same model but with the vision prompt
        # Note: gemini-flash-latest supports multimodal input
        response = model.generate_content([prompt, img])
        
        # Clean up the response text (sometimes Gemini adds ```json ... ```)
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
        print(f"AI Document Validation Error: {str(e)}")
        # If AI fails for technical reasons, we fallback to manual review (True) 
        # to not block students completely, but log the error.
        return {'is_valid': True, 'reason': 'AI validation unavailable, pending manual review.'}
