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
    is_follow_up: bool = Field(default=False, description="Whether this is a follow-up question (vs initial recipe request)")
    excluded_urls: List[str] = Field(default=[], description="List of recipe URLs to exclude from results")

    @field_validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()

    class Config:
        json_schema_extra = {
            "example": {
                "message": "I want to learn shallow frying without experience and minimize oil usage",
                "is_follow_up": False,
                "excluded_urls": []
            }
        }


class ChatResponse(BaseModel):
    """Response for conversational chat."""
    reply: str
    recipes: List[RecipeCard]
    metadata: dict


class ExtractRequest(BaseModel):
    """Request body for recipe extraction."""
    url: str = Field(..., description="Recipe URL to extract content from")

    @field_validator('url')
    def validate_url(cls, v):
        if not v.strip():
            raise ValueError('URL cannot be empty')
        if not v.startswith('http'):
            raise ValueError('URL must start with http:// or https://')
        return v.strip()


class ExtractResponse(BaseModel):
    """Response for recipe extraction."""
    raw_content: str
    success: bool


class CookGuideRequest(BaseModel):
    """Request body for cook guide generation."""
    raw_content: str = Field(..., description="Extracted recipe markdown content")
    skill_level: str = Field(..., description="User's skill level")
    learning_goal: str = Field(..., description="What the user wants to learn")


class CookingStep(BaseModel):
    """A single cooking step with tips."""
    title: str
    content: str
    tips: str


class CookGuideResponse(BaseModel):
    """Response containing structured cooking guide."""
    ingredients: List[str]
    steps: List[CookingStep]
    techniques_learned: List[str]
    xp_earned: int
    badges: List[str]


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


@app.post("/api/extract", response_model=ExtractResponse)
async def extract_recipe(request: ExtractRequest):
    """
    Extract full recipe content from a URL using Tavily Extract API.

    This endpoint:
    1. Takes a single recipe URL
    2. Calls Tavily Extract API with basic depth
    3. Returns markdown content

    This is called on-demand when user clicks "Let's cook!" on a recipe.
    """
    from tavily import TavilyClient

    logger.info(f"Extract request for URL: {request.url}")

    try:
        tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

        # Call Tavily Extract API
        result = tavily_client.extract(
            urls=[request.url],
            extract_depth="basic"
        )

        # Extract response structure: {"results": [{"url": ..., "raw_content": ...}], "failed_results": []}
        if result.get("failed_results"):
            logger.error(f"Tavily extract failed for {request.url}: {result['failed_results']}")
            # Check if it's an access denied error
            failed = result['failed_results'][0] if result['failed_results'] else {}
            error_msg = failed.get('error', '')
            if 'Access denied' in error_msg or 'Unable to retrieve content' in error_msg:
                raise HTTPException(
                    status_code=403,
                    detail="This recipe site blocks automated access. Please visit the recipe directly using the link button."
                )
            raise HTTPException(
                status_code=500,
                detail="Failed to extract recipe content from URL"
            )

        results = result.get("results", [])
        if not results:
            raise HTTPException(
                status_code=404,
                detail="No content extracted from URL"
            )

        raw_content = results[0].get("raw_content", "")

        logger.info(f"Successfully extracted {len(raw_content)} characters from {request.url}")

        return ExtractResponse(
            raw_content=raw_content,
            success=True
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extract request failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/cook-guide", response_model=CookGuideResponse)
async def generate_cook_guide(request: CookGuideRequest):
    """
    Generate an interactive cooking guide from extracted recipe content.

    Uses LLM to:
    1. Parse ingredients from markdown
    2. Split numbered steps with generated titles
    3. Generate personalized chef's tips for each step
    4. Identify key techniques learned
    5. Calculate XP and badges
    """
    from openai import OpenAI

    logger.info(f"Cook guide request for {request.skill_level} learning {request.learning_goal}")

    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        prompt = f"""Parse this recipe into a structured cooking guide for a {request.skill_level} cook learning {request.learning_goal}.

Recipe Content:
{request.raw_content[:4000]}

Return ONLY valid JSON with this EXACT structure (all fields are REQUIRED):
{{
  "ingredients": ["ingredient 1", "ingredient 2"],
  "steps": [
    {{
      "title": "Step Title Here",
      "content": "Full step instructions here",
      "tips": "Helpful tip here"
    }}
  ],
  "techniques_learned": ["technique1", "technique2"],
  "xp_earned": 100,
  "badges": ["Badge Name"]
}}

CRITICAL REQUIREMENTS:
- EVERY step MUST have all 3 fields: "title", "content", AND "tips"
- The "tips" field is REQUIRED for every step - do not omit it
- Extract ALL ingredients from the recipe
- Each numbered step becomes a separate step object with title, content, AND tips
- Tips should be 1-2 sentences, specific to {request.skill_level} level
- Include 3-5 techniques learned
- XP: 50 (simple), 100 (medium), 150+ (complex)
- Badges: creative names like "Sauté Master", "Knife Skills"
- Return ONLY valid JSON, no markdown code blocks"""

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=2000
        )

        result_text = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()

        import json
        parsed = json.loads(result_text)

        # Validate that all steps have required fields
        for i, step in enumerate(parsed.get('steps', [])):
            if 'tips' not in step or not step['tips']:
                step['tips'] = f"Take your time with this step and follow the instructions carefully."
            if 'title' not in step or not step['title']:
                step['title'] = f"Step {i+1}"
            if 'content' not in step or not step['content']:
                raise ValueError(f"Step {i+1} is missing content")

        logger.info(f"Generated cook guide: {len(parsed['steps'])} steps, {parsed['xp_earned']} XP")

        return CookGuideResponse(**parsed)

    except Exception as e:
        logger.error(f"Cook guide generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate cooking guide: {str(e)}"
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Conversational endpoint that accepts natural language cooking requests.

    This endpoint:
    1. Detects if it's a follow-up question or a new recipe request
    2. For follow-ups: answers with GPT (no workflow)
    3. For new requests: runs the full multi-agent workflow

    Examples:
    - "I want to learn shallow frying without experience" → New request (workflow)
    - "How do I make sure my sushi rice is good?" → Follow-up (GPT answer)
    """
    start_time = time.time()

    logger.info(f"Chat request: {request.message}")

    try:
        # Step 1: Check if this is a follow-up question (based on client flag)
        if request.is_follow_up:
            logger.info("Follow-up question detected, answering with GPT")

            # Answer the question directly with GPT (no workflow)
            reply = answer_follow_up(request.message)

            processing_time_ms = round((time.time() - start_time) * 1000)

            # Return answer with no recipes
            response = ChatResponse(
                reply=reply,
                recipes=[],
                metadata={
                    "is_follow_up": True,
                    "llm_calls": 1,
                    "processing_time_ms": processing_time_ms
                }
            )

            logger.info(f"Follow-up answered in {processing_time_ms}ms")
            return response

        # Step 2: It's a new recipe request - extract intent
        logger.info("Detected recipe request, running workflow")
        intent = extract_intent(request.message)

        # Step 3: Create initial state from extracted intent
        initial_state = create_initial_state(
            learning_goal=intent["learning_goal"],
            skill_level=intent["skill_level"],
            dietary_restrictions=intent.get("dietary_restrictions", [])
        )

        # Add excluded URLs to state if provided
        if request.excluded_urls:
            initial_state["excluded_urls"] = request.excluded_urls

        # Step 4: Run the existing multi-agent workflow
        final_state = workflow_app.invoke(initial_state)

        # Check if we got results
        if not final_state.get("final_cards"):
            raise HTTPException(
                status_code=404,
                detail="No recipes found matching your criteria. Try rephrasing your request or broadening your search."
            )

        # Calculate processing time
        processing_time_ms = round((time.time() - start_time) * 1000)

        # Step 5: Generate conversational reply
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
                "is_follow_up": False,
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
