from data_processing import DataProcessor
from vector_store import VectorStoreManager
from config import Config

def setup_local_system():
    print("🚀 Setting up RBI Chatbot with Local PDF...")
    
    # Step 1: Process Local PDF
    print("\n📄 Step 1: Processing Local PDF...")
    processor = DataProcessor()
    chunks = processor.process_pdf(Config.PDF_PATH)
    
    if not chunks:
        print("❌ PDF processing failed")
        return False
    
    # Step 2: Create Vector Store
    print("\n🗄️ Step 2: Creating Vector Database...")
    vector_mgr = VectorStoreManager()
    vector_store = vector_mgr.create_vector_store(chunks)
    
    if not vector_store:
        print("❌ Vector store creation failed")
        return False
    
    # Step 3: Test
    print("\n🧪 Step 3: Testing...")
    results = vector_mgr.similarity_search("What is NBFC?")
    print(f"✅ Test search found {len(results)} documents")
    
    print("\n🎉 Local PDF system setup completed!")
    print("Run: python main.py and choose option 2 to chat!")
    return True

if __name__ == "__main__":
    setup_local_system()