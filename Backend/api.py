from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import Optional
import uvicorn
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

# Import your existing modules
from Backend.main import setup_chatbot, rebuild_system
from Backend.chatbot import RBI_Chatbot

# Global chatbot instance
chatbot = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup-0x
    global chatbot
    print("🚀 Starting up RBI Chatbot API...")
    
    # Try to setup chatbot using your existing main.py function
    try:
        chatbot = setup_chatbot()
        if chatbot:
            print("✅ Chatbot initialized successfully using main.py")
        else:
            print("⚠️ Chatbot initialization failed - API will still work but needs setup")
    except Exception as e:
        print(f"❌ Failed to initialize chatbot: {e}")
        print("💡 Run 'python main.py' and choose option 1 to setup system first")
    
    yield
    
    # Shutdown
    print("👋 Shutting down RBI Chatbot API...")
    chatbot = None

# Create FastAPI app
app = FastAPI(
    title="RBI Regulatory Chatbot API",
    description="API for RBI Regulatory Chatbot - Powered by your existing main.py",
    version="1.0.0",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ SERVE FRONTEND ============
# Get the frontend path
frontend_path = Path(__file__).parent.parent / "Frontend"

# Mount static files if frontend exists
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    print(f"✅ Frontend static files mounted from: {frontend_path}")
else:
    print(f"⚠️ Frontend folder not found at: {frontend_path}")

# Request/Response Models
class Question(BaseModel):
    question: str
    session_id: Optional[str] = None

class Answer(BaseModel):
    answer: str
    sources_count: int
    has_sources: bool
    answer_length: int
    response_time: Optional[float] = None

class SystemStatus(BaseModel):
    status: str
    chatbot_ready: bool
    vector_store_loaded: bool
    message: Optional[str] = None

# ============ FRONTEND ENDPOINTS ============
@app.get("/")
async def root():
    """Serve the frontend HTML or API info"""
    index_path = frontend_path / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    else:
        # Fallback to API info if frontend not found
        return {
            "name": "RBI Regulatory Chatbot API",
            "version": "1.0.0",
            "status": "online",
            "frontend_status": "Not deployed",
            "endpoints": [
                "/ask - POST (Ask questions)",
                "/health - GET (Check system health)",
                "/rebuild - POST (Rebuild vector database)",
                "/status - GET (Get system status)"
            ]
        }

# ============ API ENDPOINTS ============
@app.get("/api")
async def api_root():
    """API information endpoint"""
    return {
        "name": "RBI Regulatory Chatbot API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "ask": {"method": "POST", "path": "/ask", "description": "Ask a question"},
            "health": {"method": "GET", "path": "/health", "description": "System health"},
            "rebuild": {"method": "POST", "path": "/rebuild", "description": "Rebuild database"},
            "status": {"method": "GET", "path": "/status", "description": "Detailed status"}
        }
    }

@app.get("/health", response_model=SystemStatus)
async def health_check():
    """Check system health and chatbot status"""
    global chatbot
    
    # Check if chatbot is ready
    chatbot_ready = chatbot is not None
    vector_loaded = False
    
    if chatbot_ready:
        try:
            # Check if vector store is loaded
            vector_loaded = chatbot.vector_mgr.vector_store is not None
        except:
            vector_loaded = False
    
    status = "healthy" if chatbot_ready and vector_loaded else "degraded"
    
    return SystemStatus(
        status=status,
        chatbot_ready=chatbot_ready,
        vector_store_loaded=vector_loaded,
        message="System is ready" if chatbot_ready else "Please rebuild the system first (Option 1 in main.py)"
    )

@app.post("/ask", response_model=Answer)
async def ask_question(question: Question):
    """Ask a question to the RBI chatbot"""
    global chatbot
    
    if not chatbot:
        raise HTTPException(
            status_code=503, 
            detail="Chatbot not initialized. Please run 'python main.py' and select option 1 to setup the system first."
        )
    
    try:
        # Use your existing chatbot's ask_question method
        response = chatbot.ask_question(question.question)
        
        return Answer(
            answer=response["answer"],
            sources_count=response.get("sources_count", 0),
            has_sources=response.get("sources_count", 0) > 0,
            answer_length=len(response["answer"]),
            response_time=response.get("response_time", 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.post("/rebuild")
async def rebuild_system_endpoint():
    """Rebuild the entire vector database system"""
    global chatbot
    
    try:
        # Import rebuild function from main.py
        from Backend.main import rebuild_system
        
        # Rebuild the system
        success = rebuild_system()
        
        if success:
            # Re-initialize chatbot after rebuild
            from Backend.main import setup_chatbot
            chatbot = setup_chatbot()
            
            return {
                "status": "success",
                "message": "System rebuilt successfully",
                "chatbot_ready": chatbot is not None
            }
        else:
            return {
                "status": "failed",
                "message": "System rebuild failed"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")

@app.get("/status")
async def get_status():
    """Get detailed system status"""
    global chatbot
    
    status_info = {
        "chatbot_initialized": chatbot is not None,
        "vector_store_path": "./faiss_vector_db",
        "vector_store_exists": os.path.exists("./faiss_vector_db"),
        "frontend_exists": frontend_path.exists()
    }
    
    if chatbot:
        try:
            # Check if vector store is loaded
            status_info["vector_store_loaded"] = chatbot.vector_mgr.vector_store is not None
            status_info["llm_model"] = chatbot.llm.model_name if hasattr(chatbot, 'llm') else "Unknown"
        except Exception as e:
            status_info["vector_store_loaded"] = False
            status_info["error"] = str(e)
    
    return status_info

if __name__ == "__main__":
    print("=" * 60)
    print("RBI CHATBOT API SERVER")
    print("=" * 60)
    print("Starting API server with your existing main.py...")
    print("API will be available at: http://localhost:8000")
    print("Frontend will be available at: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 60)
    
    # Run with uvicorn
    uvicorn.run(
        "Backend.api:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 7860)),
        reload=False
    )