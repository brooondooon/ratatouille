"""
Ratatouille Backend API

FastAPI application that exposes the multi-agent recipe recommendation system.
"""

import os
import time
from typing import List, Optional, Literal
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
from dotenv import load_dotenv

from backend.state import create_initial_state
from backend.graph import workflow_app
from backend import config  # Validates API keys on import
from backend.logger import get_logger
from backend.agents.intent_extractor import extract_intent, answer_follow_up

logger = get_logger("api")

# Initialize FastAPI app
app = FastAPI(
    title="Ratatouille API",
    description="AI-powered culinary learning assistant with multi-agent recipe recommendations",
    version="1.0.0"
)

# Add CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class RecommendationRequest(BaseModel):
    """Request body for recipe recommendations."""
    learning_goal: str = Field(..., min_length=3, max_length=200, description="What the user wants to learn")
    skill_level: Literal["beginner", "intermediate", "advanced"] = Field(..., description="User's skill level")
    dietary_restrictions: List[str] = Field(default=[], max_length=10, description="List of dietary restrictions")

    @field_validator('learning_goal')
    def validate_goal(cls, v):
        if not v.strip():
            raise ValueError('Learning goal cannot be empty')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "learning_goal": "pan sauces",
                "skill_level": "intermediate",
                "dietary_restrictions": ["vegetarian"]
            }
        }


class RecipeCard(BaseModel):
    """A single recipe recommendation with reasoning."""
    recipe: dict
    reasoning: str
    technique_highlights: List[str]
    nutrition: Optional[dict] = None
    score: float


class RecommendationResponse(BaseModel):
    """Response containing recipe recommendations."""
    recipes: List[RecipeCard]
    comparison: Optional[dict]
    metadata: dict


class ChatRequest(BaseModel):
    """Request body for conversational recipe chat."""
    message: str = Field(..., min_length=3, max_length=500, description="Natural language cooking request")

    @field_validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "message": "I want to learn shallow frying without experience and minimize oil usage"
            }
        }


class ChatResponse(BaseModel):
    """Response for conversational chat."""
    reply: str
    recipes: List[RecipeCard]
    metadata: dict


# API Endpoints
@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "🐀 Ratatouille API is running",
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check with API key validation."""
    health_status = {
        "status": "healthy",
        "openai_configured": bool(os.getenv("OPENAI_API_KEY")),
        "tavily_configured": bool(os.getenv("TAVILY_API_KEY"))
    }
    return health_status


@app.post("/api/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get personalized recipe recommendations based on learning goals.

    This endpoint orchestrates 4 agents:
    1. Research Planner - generates search queries
    2. Recipe Hunter - finds recipes via Tavily
    3. Personalization Engine - scores and selects top 2
    4. Nutrition Analyzer - estimates nutrition data

    Returns 2 recipe cards with reasoning, techniques, and nutrition info.
    """
    start_time = time.time()

    # Create initial state from request
    initial_state = create_initial_state(
        learning_goal=request.learning_goal,
        skill_level=request.skill_level,
        dietary_restrictions=request.dietary_restrictions
    )

    logger.info(f"New request: {request.learning_goal} ({request.skill_level})")

    try:
        # Run the multi-agent workflow
        final_state = workflow_app.invoke(initial_state)

        # Check if we got results
        if not final_state.get("final_cards"):
            raise HTTPException(
                status_code=404,
                detail="No recipes found matching your criteria. Try broadening your search or changing filters."
            )

        # Calculate processing time
        processing_time_ms = round((time.time() - start_time) * 1000)

        # Build response
        response = RecommendationResponse(
            recipes=[
                RecipeCard(
                    recipe=card["recipe"],
                    reasoning=card["reasoning"],
                    technique_highlights=card["technique_highlights"],
                    nutrition=card.get("nutrition"),
                    score=card["score"]
                )
                for card in final_state["final_cards"]
            ],
            comparison=final_state.get("comparison"),
            metadata={
                "tavily_calls": final_state.get("tavily_calls", 0),
                "llm_calls": final_state.get("llm_calls", 0),
                "retry_count": final_state.get("retry_count", 0),
                "processing_time_ms": processing_time_ms,
                "errors": final_state.get("errors", [])
            }
        )

        logger.info(f"Request complete: {len(response.recipes)} recipes in {processing_time_ms}ms | Tavily: {response.metadata['tavily_calls']} | LLM: {response.metadata['llm_calls']}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Request failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversational endpoint that accepts natural language cooking requests.

    This endpoint:
    1. Extracts intent from natural language (via LLM)
    2. Calls the existing recommendation workflow
    3. Returns recipes with a conversational reply

    Examples:
    - "I want to learn shallow frying without experience"
    - "Show me vegetarian pan sauce recipes for beginners"
    - "Advanced bread baking techniques"
    """
    start_time = time.time()

    logger.info(f"Chat request: {request.message}")

    try:
        # Step 1: Extract intent from natural language
        intent = extract_intent(request.message)

        # Step 2: Create initial state from extracted intent
        initial_state = create_initial_state(
            learning_goal=intent["learning_goal"],
            skill_level=intent["skill_level"],
            dietary_restrictions=intent.get("dietary_restrictions", [])
        )

        # Step 3: Run the existing multi-agent workflow
        final_state = workflow_app.invoke(initial_state)

        # Check if we got results
        if not final_state.get("final_cards"):
            raise HTTPException(
                status_code=404,
                detail="No recipes found matching your criteria. Try rephrasing your request or broadening your search."
            )

        # Calculate processing time
        processing_time_ms = round((time.time() - start_time) * 1000)

        # Step 4: Generate conversational reply
        num_recipes = len(final_state["final_cards"])
        learning_goal = intent["learning_goal"]
        skill_level = intent["skill_level"]

        reply = f"I found {num_recipes} great {'recipes' if num_recipes > 1 else 'recipe'} for learning {learning_goal}"

        if skill_level == "beginner":
            reply += " that are perfect for beginners"
        elif skill_level == "advanced":
            reply += " with advanced techniques"

        reply += ". Check them out below!"

        # Build response
        response = ChatResponse(
            reply=reply,
            recipes=[
                RecipeCard(
                    recipe=card["recipe"],
                    reasoning=card["reasoning"],
                    technique_highlights=card["technique_highlights"],
                    nutrition=card.get("nutrition"),
                    score=card["score"]
                )
                for card in final_state["final_cards"]
            ],
            metadata={
                "extracted_intent": intent,
                "tavily_calls": final_state.get("tavily_calls", 0),
                "llm_calls": final_state.get("llm_calls", 0) + 1,  # +1 for intent extraction
                "retry_count": final_state.get("retry_count", 0),
                "processing_time_ms": processing_time_ms,
                "errors": final_state.get("errors", [])
            }
        )

        logger.info(f"Chat complete: {num_recipes} recipes in {processing_time_ms}ms")

        return response

    except HTTPException:
        raise
    except ValueError as e:
        # Intent extraction failed
        logger.error(f"Intent extraction failed: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Could not understand your request. Please try rephrasing: {str(e)}"
        )
    except Exception as e:
        import traceback
        logger.error(f"Chat request failed: {str(e)}")
        logger.error(f"Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


# Run the app
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))

    print("\n" + "="*60)
    print("🐀 Starting Ratatouille API Server")
    print("="*60)
    print(f"   URL: http://localhost:{port}")
    print(f"   Docs: http://localhost:{port}/docs")
    print(f"   OpenAI: {'✓' if os.getenv('OPENAI_API_KEY') else '✗'}")
    print(f"   Tavily: {'✓' if os.getenv('TAVILY_API_KEY') else '✗'}")
    print("="*60 + "\n")

    uvicorn.run(
        "backend.app:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Auto-reload on code changes
    )
