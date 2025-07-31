from fastapi import APIRouter, HTTPException
from app.schemas.responses import ChatMessage, ChatResponse
from app.services.llm_service import LLMService
from datetime import datetime

router = APIRouter()
llm_service = LLMService()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_data(message: ChatMessage):
    """
    Chat with your data using natural language
    """
    try:
        response = await llm_service.chat_with_data(
            message.dataset_id, 
            message.message
        )
        return response
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@router.get("/chat/{dataset_id}/history")
async def get_chat_history(dataset_id: str, limit: int = 50):
    """
    Get chat history for a dataset
    """
    try:
        history = await llm_service.get_chat_history(dataset_id, limit)
        return {"dataset_id": dataset_id, "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve chat history: {str(e)}")

@router.delete("/chat/{dataset_id}/history")
async def clear_chat_history(dataset_id: str):
    """
    Clear chat history for a dataset
    """
    try:
        await llm_service.clear_chat_history(dataset_id)
        return {"message": "Chat history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear chat history: {str(e)}")

@router.post("/chat/suggestions")
async def get_chat_suggestions(dataset_id: str):
    """
    Get suggested questions based on the dataset
    """
    try:
        suggestions = await llm_service.generate_chat_suggestions(dataset_id)
        return {
            "dataset_id": dataset_id,
            "suggestions": suggestions,
            "timestamp": datetime.now()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate suggestions: {str(e)}")

@router.get("/chat/capabilities")
async def get_chat_capabilities():
    """
    Get available chat capabilities and example questions
    """
    return {
        "capabilities": [
            {
                "category": "Statistical Analysis",
                "examples": [
                    "What is the correlation between sales and marketing spend?",
                    "Show me the distribution of customer ages",
                    "Which variables have the strongest relationships?"
                ]
            },
            {
                "category": "Data Quality",
                "examples": [
                    "How much missing data do I have?",
                    "Are there any outliers in my dataset?",
                    "What columns have data quality issues?"
                ]
            },
            {
                "category": "Pattern Discovery",
                "examples": [
                    "What patterns can you find in the data?",
                    "Are there any seasonal trends?",
                    "Group customers by their behavior"
                ]
            },
            {
                "category": "Business Insights", 
                "examples": [
                    "What factors drive revenue?",
                    "Which customers are most valuable?",
                    "What recommendations do you have for improving performance?"
                ]
            }
        ],
        "supported_formats": [
            "Natural language questions",
            "Statistical queries",
            "Data exploration requests",
            "Visualization suggestions",
            "Business analysis questions"
        ]
    }
