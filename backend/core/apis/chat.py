from fastapi import APIRouter, HTTPException
from core.schemas.requests.chat import ChatRequest
from core.schemas.responses.chat import ChatResponse
from core.handlers.chat import ChatHandler
from utils.logger_utility import logger


router_chat = APIRouter(prefix="/chat")


@router_chat.post("/chat", response_model=ChatResponse)
async def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat request and return the response
    
    Args:
        request: ChatRequest containing user_id, question_id, and prompt
        
    Returns:
        ChatResponse containing user_id, question_id, and markdown response
        
    Raises:
        HTTPException: If there's an error processing the chat
    """
    try:
        logger.debug(f"Received chat request for user {request.user_id}, question {request.question_id}")

        chat_handler = ChatHandler()
        # Process the chat request
        response = chat_handler.process_chat(
            user_id=request.user_id,
            question_id=request.question_id,
            prompt=request.prompt
        )
        
        logger.debug(f"Successfully processed chat for user {request.user_id}")
        
        # Convert to response model
        return ChatResponse(
            user_id=response["user_id"],
            question_id=response["question_id"],
            response=response["response"]
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process chat request: {str(e)}"
        )
