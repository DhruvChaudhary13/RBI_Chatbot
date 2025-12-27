import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document

class VectorStoreManager:
    def __init__(self, persist_directory="./faiss_vector_db"):
        self.persist_directory = persist_directory
        self.embeddings = None
        self.vector_store = None
        self.setup_local_embeddings()
    
    def setup_local_embeddings(self):
        """Setup 100% local embeddings - no API"""
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': False}
            )
            print("Local embeddings initialized successfully")
        except Exception as e:
            print(f"Error initializing local embeddings: {e}")
            try:
                self.embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/paraphrase-MiniLM-L6-v2"
                )
                print("Alternative local embeddings initialized successfully")
            except Exception as e2:
                print(f"Failed to load any local embeddings: {e2}")
                raise
    
    def create_vector_store(self, documents):
        """Create FAISS vector store from documents"""
        print("Creating FAISS vector store...")
        try:
            self.vector_store = FAISS.from_documents(documents=documents, embedding=self.embeddings)
            self.vector_store.save_local(self.persist_directory)
            print(f"FAISS vector store created with {len(documents)} documents")
            return self.vector_store
        except Exception as e:
            print(f"Error creating FAISS vector store: {e}")
            return None
    
    def load_vector_store(self):
        """Load existing FAISS vector store"""
        try:
            if os.path.exists(self.persist_directory):
                self.vector_store = FAISS.load_local(
                    self.persist_directory,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                print("FAISS vector store loaded successfully")
                return self.vector_store
            else:
                print("No existing FAISS vector store found")
                return None
        except Exception as e:
            print(f"Error loading FAISS vector store: {e}")
            return None
    
    def similarity_search(self, query, k=5):
        """Search for similar documents"""
        if not self.vector_store:
            self.load_vector_store()
        if self.vector_store:
            try:
                return self.vector_store.similarity_search(query, k=k)
            except Exception as e:
                print(f"Error in FAISS similarity search: {e}")
                return []
        return []
    
    def similarity_search_with_scores(self, query, k=5):
        """Search for similar documents with scores"""
        if not self.vector_store:
            self.load_vector_store()
        if self.vector_store:
            try:
                return self.vector_store.similarity_search_with_score(query, k=k)
            except Exception as e:
                print(f"Error in FAISS similarity search with scores: {e}")
                return []
        return []
    
    def get_retriever(self):
        """Get optimized retriever"""
        if not self.vector_store:
            self.load_vector_store()
        if self.vector_store:
            return self.vector_store.as_retriever(
                search_type="mmr",
                search_kwargs={
                    "k": 8,
                    "fetch_k": 20,
                    "lambda_mult": 0.7,
                    "score_threshold": 0.75
                }
            )
    
    def add_documents(self, documents):
        """Add new documents to vector store"""
        try:
            if not self.vector_store:
                self.load_vector_store()
            if self.vector_store:
                self.vector_store.add_documents(documents)
                self.vector_store.save_local(self.persist_directory)
                print(f"Added {len(documents)} documents to FAISS store")
                return True
            else:
                print("No vector store available to add documents")
                return False
        except Exception as e:
            print(f"Error adding documents: {e}")
            return False
