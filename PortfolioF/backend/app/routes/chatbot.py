from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.schemas import ChatbotQuery, ChatbotResponse
from app.services.chatbot_service import ChatbotService

router = APIRouter()
chatbot_service = ChatbotService()

@router.post("/query", response_model=ChatbotResponse)
async def query_chatbot(query: ChatbotQuery):
    """
    Process a chatbot query and return a response.
    
    Args:
        query: The user's message to the chatbot
    """
    if not query.message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    response = chatbot_service.get_response(query.message)
    
    return JSONResponse(content=response)

@router.get("/context")
async def get_chatbot_context():
    """
    Get contextual information for the chatbot.
    """
    # Load basic context information
    context = {
        "name": "Hemant Singh Sidar",
        "title": "Software Engineer",
        "location": "India",
        "available_topics": [
            "skills",
            "projects",
            "experience",
            "contact"
        ],
        "example_questions": [
            "What are your skills?",
            "Tell me about your projects",
            "What technologies do you work with?",
            "How can I contact you?",
            "What's your background?"
        ],
        "social_links": {
            "x": "https://twitter.com/yourusername",
            "reddit": "https://reddit.com/user/yourusername",
            "linkedin": "https://linkedin.com/in/yourusername",
            "huggingface": "https://huggingface.co/yourusername",
            "github": "https://github.com/yourusername"
        }
    }
    
    return JSONResponse(content=context) 