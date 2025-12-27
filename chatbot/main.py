from data_processing import DataProcessor
from vector_store import VectorStoreManager
from chatbot import RBI_Chatbot
from add_definitions import add_standard_definitions
from config import Config
import os
import shutil

def setup_chatbot():
    """Setup the complete chatbot system with FAISS vector database"""
    print("Setting up RBI Chatbot with FAISS Vector Database...")
    
    vector_mgr = VectorStoreManager()
    existing_store = vector_mgr.load_vector_store()
    
    if not existing_store:
        print("No existing FAISS vector store found. Processing PDF...")
        processor = DataProcessor()
        chunks = processor.process_pdf(Config.PDF_PATH)
        
        if chunks:
            vector_mgr.create_vector_store(chunks)
            print("FAISS Vector store created successfully")
            
            try:
                add_standard_definitions()
            except Exception as e:
                print(f"Could not add definitions: {e}")
        else:
            print("Failed to process PDF")
            return None
    
    try:
        chatbot = RBI_Chatbot()
        print("Chatbot setup completed with FAISS Vector Database")
        return chatbot
    except Exception as e:
        print(f"Error initializing chatbot: {e}")
        return None

def rebuild_system():
    """Completely rebuild the FAISS vector database"""
    print("Rebuilding entire system with FAISS...")
    
    if os.path.exists("data/vector_store"):
        shutil.rmtree("data/vector_store")
    if os.path.exists("./faiss_vector_db"):
        shutil.rmtree("./faiss_vector_db")
    
    processor = DataProcessor()
    chunks = processor.process_pdf(Config.PDF_PATH)
    
    if chunks:
        vector_mgr = VectorStoreManager()
        vector_store = vector_mgr.create_vector_store(chunks)
        
        if vector_store:
            try:
                add_standard_definitions()
            except Exception as e:
                print(f"Could not add definitions: {e}")
            print("FAISS System rebuilt successfully")
            return True
    
    print("System rebuild failed")
    return False

def test_system():
    """Test the complete FAISS system"""
    print("Testing Complete FAISS System...")
    
    vector_mgr = VectorStoreManager()
    results = vector_mgr.similarity_search("NBFC capital requirements", k=2)
    
    if results:
        print("FAISS Vector Database: WORKING")
        for i, result in enumerate(results):
            content_preview = result.page_content[:100] + "..." if len(result.page_content) > 100 else result.page_content
            print(f"{i+1}. {content_preview}")
        
        try:
            chatbot = RBI_Chatbot()
            response = chatbot.ask_question("What is NBFC?")
            print("Chatbot: WORKING")
            print(f"Response: {response['answer']}")
            print(f"Sources: {response['sources_count']} documents found")
        except Exception as e:
            print(f"Chatbot: NOT WORKING - {e}")
    else:
        print("FAISS Vector Database: NOT WORKING")

def main():
    """Main function"""
    print("=" * 60)
    print("           RBI NBFC CHATBOT (FAISS + Groq)")
    print("=" * 60)
    
    
    print("\n1. Setup/Rebuild System")
    print("2. Chat Interface") 
    print("3. Test System")
    print("4. Add Definitions Only")
    print("5. Exit")
    
    choice = input("\nChoose option (1-5): ")
    
    if choice == "1":
        if rebuild_system():
            print("FAISS System ready")
    
    elif choice == "2":
        chatbot = setup_chatbot()
        if chatbot:
            chatbot.chat_interface()
        else:
            print("Chatbot initialization failed. Please rebuild system first.")
    
    elif choice == "3":
        test_system()
    
    elif choice == "4":
        try:
            add_standard_definitions()
            print("Definitions added to FAISS database")
        except Exception as e:
            print(f"Failed to add definitions: {e}")
    
    elif choice == "5":
        print("Goodbye")
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
