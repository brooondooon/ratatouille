"""
LangGraph State Schema for Ratatouille Multi-Agent System

This module defines the shared state that flows between agents.
Each agent reads from and writes to this state, enabling coordination.
"""

from typing import TypedDict, List, Dict, Any, Optional


class RecipeState(TypedDict):
    """
    Shared state for the multi-agent recipe recommendation workflow.

    State flows through agents:
    1. User inputs → Research Planner
    2. Search queries → Recipe Hunter
    3. Raw recipes → Personalization Engine
    4. Final cards → API Response
    """

    # User inputs
    learning_goal: str  # e.g., "pan sauces", "bread baking"
    skill_level: str  # "beginner" | "intermediate" | "advanced"
    dietary_restrictions: List[str]  # e.g., ["vegetarian", "kosher"]

    # Agent 1 (Research Planner) outputs
    search_queries: List[str]  # Generated search queries for Tavily
    search_strategy: str  # "initial" | "broadened" | "technique_focused"

    # Agent 2 (Recipe Hunter) outputs
    raw_recipes: List[Dict[str, Any]]  # Parsed recipes from Tavily

    # Agent 3 (Personalization Engine) outputs
    scored_recipes: List[Dict[str, Any]]  # Scored and ranked recipes
    final_cards: List[Dict[str, Any]]  # Top 2 recipes with reasoning
    comparison: Optional[Dict[str, str]]  # Comparison notes between recipes

    # Metadata for debugging and optimization
    errors: List[str]  # Error messages from any agent
    tavily_calls: int  # Count of Tavily API calls
    llm_calls: int  # Count of LLM API calls
    retry_count: int  # Number of retry attempts


def create_initial_state(
    learning_goal: str,
    skill_level: str,
    dietary_restrictions: List[str] = None
) -> RecipeState:
    """
    Create initial state from user input.

    Args:
        learning_goal: What the user wants to learn (e.g., "pan sauces")
        skill_level: User's cooking skill level
        dietary_restrictions: Optional list of dietary constraints

    Returns:
        RecipeState with user inputs populated
    """
    return RecipeState(
        # User inputs
        learning_goal=learning_goal,
        skill_level=skill_level,
        dietary_restrictions=dietary_restrictions or [],

        # Initialize empty agent outputs
        search_queries=[],
        search_strategy="initial",
        raw_recipes=[],
        scored_recipes=[],
        final_cards=[],
        comparison=None,

        # Initialize metadata
        errors=[],
        tavily_calls=0,
        llm_calls=0,
        retry_count=0
    )
