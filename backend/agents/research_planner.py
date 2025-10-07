"""
Research Planner Agent

Responsibility: Analyze user's learning goal and generate optimal search queries.
This agent decides the search strategy and adapts based on retry signals.
"""

import os
from typing import List
from openai import OpenAI
from backend.state import RecipeState


def research_planner_agent(state: RecipeState) -> RecipeState:
    """
    Generate search queries based on learning goal and skill level.

    Adaptive behavior: If search_strategy == 'broadened', generates wider queries.

    Args:
        state: Current workflow state with user inputs

    Returns:
        Updated state with search_queries populated
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    learning_goal = state["learning_goal"]
    skill_level = state["skill_level"]
    dietary_restrictions = state.get("dietary_restrictions", [])
    search_strategy = state.get("search_strategy", "initial")
    retry_count = state.get("retry_count", 0)

    # Build prompt based on whether this is a retry
    if search_strategy == "broadened":
        strategy_instruction = """
        IMPORTANT: Previous search found insufficient results. Broaden your queries by:
        - Using more general terms (e.g., "pan sauce" → "sauce techniques")
        - Including related techniques (e.g., "pan sauce" → "butter emulsions", "reduction")
        - Adding beginner-friendly variations if original was too advanced
        - Focus on ACTUAL DISH RECIPES, not technique tutorials
        """
    else:
        strategy_instruction = """
        Generate specific, targeted queries for ACTUAL RECIPE DISHES that teach this skill.

        CRITICAL REQUIREMENTS:
        - Focus on SPECIFIC DISHES with the technique, NOT technique tutorials
        - Each query should find a COMPLETE RECIPE for a dish
        - Include dish names + technique + skill level
        - MAXIMIZE VARIETY: Each query must use DIFFERENT ingredients, proteins, or flavor profiles
        - Avoid similar variations (e.g., don't return "red wine pan sauce" AND "red wine reduction")

        DIVERSITY EXAMPLES:
        For "pan sauces":
        - "lemon butter pan sauce chicken recipe" (citrus/butter)
        - "mushroom cream pan sauce steak recipe" (earthy/cream)
        - "balsamic pan sauce pork recipe" (tangy/vinegar)
        - "white wine herb pan sauce fish recipe" (wine/herbs)

        GOOD EXAMPLES:
        - "crispy shallow fried chicken cutlet recipe"
        - "pan fried fish with lemon butter recipe beginner"
        - "japanese tonkatsu shallow frying recipe"

        BAD EXAMPLES (DO NOT USE):
        - "shallow frying technique guide"
        - "how to shallow fry tutorial"
        - "red wine pan sauce" AND "red wine reduction" (too similar)
        """

    # Add dietary restrictions to goal if specified
    goal_with_diet = learning_goal
    if dietary_restrictions:
        diet_str = " ".join(dietary_restrictions)
        goal_with_diet = f"{diet_str} {learning_goal}"

    prompt = f"""You are a culinary education expert. Given a learning goal and skill level,
generate 3-5 specific search queries that will find RECIPE DISHES (not technique guides) teaching this skill.

Learning Goal: {goal_with_diet}
Skill Level: {skill_level}

{strategy_instruction}

Return ONLY a JSON array of search query strings, nothing else.
Example: ["crispy pan-fried chicken cutlet recipe", "shallow fried pork schnitzel beginner", "korean chicken katsu recipe"]
"""

    # Call LLM to generate queries
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7 if search_strategy == "broadened" else 0.5,
        max_tokens=200
    )

    # Parse response
    queries_text = response.choices[0].message.content.strip()

    # Simple JSON parsing (remove brackets and quotes)
    import json
    try:
        search_queries = json.loads(queries_text)
    except json.JSONDecodeError:
        # Fallback: split by newlines or commas
        search_queries = [
            q.strip().strip('"').strip("'")
            for q in queries_text.replace("[", "").replace("]", "").split(",")
        ]

    # Update state
    state["search_queries"] = search_queries
    state["llm_calls"] = state.get("llm_calls", 0) + 1

    # Log for debugging
    print(f"🔍 Research Planner: Generated {len(search_queries)} queries")
    for i, q in enumerate(search_queries, 1):
        print(f"   {i}. {q}")
    if search_strategy == "broadened":
        print(f"   ↳ Retry #{retry_count + 1}: Broadened search strategy")

    return state
