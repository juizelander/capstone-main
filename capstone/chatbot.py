import os
import google.generativeai as genai
from django.conf import settings

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
    
    Your role is to:
    1. Answer questions concisely and politely based ONLY on the provided Knowledge Base below to make them interested in our programs.
    2. Encourage visitors to register an account so they can apply for these scholarships.
    3. Be welcoming and act as a helpful guide to the available scholarships.
    4. If a student asks a question that isn't covered in the Knowledge Base, politely tell them that you don't have that specific information and advise them to register or contact the administration.
    
    --- KNOWLEDGE BASE ---
    {KNOWLEDGE_BASE}
    """

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
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
