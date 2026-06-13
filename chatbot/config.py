import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys - Only Groq needed
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    # PDF Path
    PDF_PATH = "C:/Users/dhruv/OneDrive/Desktop/rbi_chatbot/RBI_Chatbot/chatbot/rbi_textbook.pdf"
    
    # Vector Store - Using FAISS now
    VECTOR_STORE_PATH = "./faiss_vector_db"
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    
    # Model Names - UPDATED
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Local model
    CHAT_MODEL = "llama-3.1-8b-instant"  # Groq model
    
    # Test Cases
    TEST_CASES = [
        {
            "question": "What is a Non-Banking Financial Company (NBFC)?",
            "expected_answer": "definition of NBFC"
        },
        {
            "question": "What does conducting financial activity as 'principal business' mean?",
            "expected_answer": "50 percent criteria"
        }
    ]