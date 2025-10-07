"""
Nutrition Analyzer Agent

Responsibility: Estimate nutritional information for selected recipes.
This agent uses LLM to analyze ingredients and provide nutrition estimates.
"""

import os
import json
from typing import Dict, Any, List
from openai import OpenAI
from backend.state import RecipeState


def nutrition_analyzer_agent(state: RecipeState) -> RecipeState:
    """
    Analyze nutritional content of final selected recipes.

    Process:
    1. For each final recipe card, extract ingredients
    2. Use LLM to estimate nutrition (calories, protein, carbs, fat, fiber)
    3. Add nutrition data to each recipe card

    Args:
        state: Current workflow state with final_cards populated

    Returns:
        Updated state with nutrition data added to final_cards
    """
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    final_cards = state["final_cards"]

    print(f"🥗 Nutrition Analyzer: Analyzing {len(final_cards)} recipes")

    # Analyze nutrition for each recipe
    for card in final_cards:
        # Find the full recipe data from raw_recipes
        recipe_title = card["recipe"]["title"]
        full_recipe = _find_recipe_by_title(
            recipe_title,
            state["raw_recipes"]
        )

        if not full_recipe:
            print(f"   ⚠️ Could not find full recipe data for {recipe_title}")
            card["nutrition"] = _default_nutrition()
            continue

        # Estimate nutrition using LLM
        nutrition = _estimate_nutrition_with_llm(
            full_recipe,
            openai_client,
            state
        )

        card["nutrition"] = nutrition

    print(f"✅ Nutrition Analyzer: Added nutrition data to all recipes")

    return state


def _find_recipe_by_title(
    title: str,
    raw_recipes: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Find full recipe data from raw_recipes by matching title."""
    for recipe in raw_recipes:
        if recipe.get("title") == title:
            return recipe
    return None


def _estimate_nutrition_with_llm(
    recipe: Dict[str, Any],
    openai_client: OpenAI,
    state: RecipeState
) -> Dict[str, Any]:
    """
    Use LLM to estimate nutritional values based on ingredients.

    Note: This is an estimate, not exact nutrition data. For production,
    use a nutrition database API like USDA FoodData Central or Edamam.
    """

    ingredients = recipe.get("ingredients", [])
    servings = _estimate_servings(recipe)

    prompt = f"""You are a nutritionist. Estimate the nutritional information PER SERVING for this recipe.

Recipe: {recipe.get('title')}
Estimated Servings: {servings}
Ingredients: {', '.join(ingredients[:15])}

Provide reasonable estimates based on typical portion sizes and cooking methods.

Return ONLY valid JSON with no markdown:
{{
  "calories": 450,
  "protein_g": 25,
  "carbs_g": 35,
  "fat_g": 18,
  "fiber_g": 5,
  "sodium_mg": 600,
  "servings": {servings},
  "disclaimer": "Estimated values - actual nutrition may vary"
}}

Be realistic with estimates. Return ONLY the JSON object."""

    try:
        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for consistent estimates
            max_tokens=250
        )

        result = response.choices[0].message.content.strip()

        # Clean markdown if present
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]

        nutrition = json.loads(result)
        state["llm_calls"] = state.get("llm_calls", 0) + 1

        return nutrition

    except Exception as e:
        print(f"   ⚠️ Nutrition estimation failed: {e}")
        return _default_nutrition()


def _estimate_servings(recipe: Dict[str, Any]) -> int:
    """
    Estimate number of servings from recipe text.

    Simple heuristic: look for serving mentions in steps or default to 4.
    """
    steps_text = " ".join(recipe.get("steps", [])).lower()
    ingredients_text = " ".join(recipe.get("ingredients", [])).lower()

    import re

    # Look for "serves X" or "X servings"
    patterns = [
        r"serves?\s+(\d+)",
        r"(\d+)\s+servings?",
        r"makes\s+(\d+)\s+portions?"
    ]

    for pattern in patterns:
        match = re.search(pattern, steps_text + " " + ingredients_text)
        if match:
            return int(match.group(1))

    # Default to 4 servings
    return 4


def _default_nutrition() -> Dict[str, Any]:
    """Return default nutrition data when estimation fails."""
    return {
        "calories": None,
        "protein_g": None,
        "carbs_g": None,
        "fat_g": None,
        "fiber_g": None,
        "sodium_mg": None,
        "servings": 4,
        "disclaimer": "Nutrition data unavailable"
    }
