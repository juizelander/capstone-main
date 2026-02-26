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
    1. Students must first Register an account on the landing page.
    2. Wait for an Administrator to approve the account.
    3. Once approved, log in and view the "Dashboard" or "Active Programs" section.
    4. Submit an application and upload the required supporting documents for the specific program.

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
    You are the official AI Assistant for 'ScholarSync Subic'.
    
    Your role is to:
    1. Answer questions concisely and politely based ONLY on the provided Knowledge Base below.
    2. Guide students on how to use the platform.
    3. If a student asks a question that isn't covered in the Knowledge Base, politely tell them that you don't have that specific information and advise them to log in to their student dashboard or contact the administration.
    
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
