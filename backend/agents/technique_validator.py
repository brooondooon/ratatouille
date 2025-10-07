"""
Technique Validator Agent

Responsibility: Understand what the learning goal technique actually means,
then validate that recipes genuinely teach this technique (not just keyword matches).

This agent prevents false positives like "fried rice" for "pan sauces".
"""

import os
import json
from typing import List, Dict, Any
from openai import OpenAI
from backend.state import RecipeState


def technique_validator_agent(state: RecipeState) -> RecipeState:
    """
    Validate that recipes actually teach the requested technique.

    Process:
    1. Use LLM to understand what the learning goal technique means
    2. For each recipe, analyze if it genuinely teaches this technique
    3. Filter out false positives (keyword matches that aren't actually relevant)

    Args:
        state: Current workflow state with raw_recipes populated

    Returns:
        Updated state with validated_recipes (subset of raw_recipes)
    """
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    learning_goal = state["learning_goal"]
    raw_recipes = state["raw_recipes"]

    print(f"🔍 Technique Validator: Validating {len(raw_recipes)} recipes for '{learning_goal}'")

    # Step 1: Define what the technique actually means
    technique_definition = _define_technique(learning_goal, openai_client, state)

    print(f"   📖 Technique definition: {technique_definition[:100]}...")

    # Step 2: Validate each recipe
    validated_recipes = []
    for recipe in raw_recipes:
        is_valid = _validate_recipe_teaches_technique(
            recipe,
            learning_goal,
            technique_definition,
            openai_client,
            state
        )

        if is_valid:
            validated_recipes.append(recipe)
        else:
            print(f"   ❌ Rejected: {recipe.get('title', 'Unknown')} (doesn't teach {learning_goal})")

    # Update state with validated recipes
    state["raw_recipes"] = validated_recipes  # Replace with validated subset

    print(f"✅ Technique Validator: {len(validated_recipes)}/{len(raw_recipes)} recipes are valid")

    return state


def _define_technique(
    learning_goal: str,
    openai_client: OpenAI,
    state: RecipeState
) -> str:
    """
    Use LLM to define what the learning goal technique actually means.

    Example:
    - Input: "pan sauces"
    - Output: "A pan sauce is made by deglazing a pan after searing meat/vegetables,
               using the fond (browned bits) to create a flavorful sauce through
               reduction and emulsification..."
    """
    prompt = f"""You are a professional chef and culinary educator. Define what the cooking technique "{learning_goal}" actually means.

Provide a clear, specific definition that explains:
1. What the technique is
2. The key steps involved
3. What distinguishes it from similar techniques

Be concise (2-3 sentences). Focus on the CORE TECHNIQUE, not variations.

Example for "pan sauces":
"A pan sauce is made by deglazing the fond (browned bits) left in a pan after searing protein. The technique involves adding liquid (wine, stock, etc.) to dissolve the fond, then reducing and often finishing with butter or cream to create an emulsified sauce. The key is using the caramelized drippings as the flavor base."

Now define: "{learning_goal}"

Return ONLY the definition, no extra text."""

    try:
        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temp for consistent definitions
            max_tokens=200
        )

        definition = response.choices[0].message.content.strip()
        state["llm_calls"] = state.get("llm_calls", 0) + 1

        return definition

    except Exception as e:
        print(f"   ⚠️ Failed to define technique: {e}")
        return f"Recipes that teach {learning_goal}"


def _validate_recipe_teaches_technique(
    recipe: Dict[str, Any],
    learning_goal: str,
    technique_definition: str,
    openai_client: OpenAI,
    state: RecipeState
) -> bool:
    """
    Use LLM to determine if a recipe actually teaches the technique.

    Returns:
        True if recipe genuinely teaches the technique, False if it's a false positive
    """
    recipe_title = recipe.get("title", "Unknown")
    recipe_steps = recipe.get("steps", [])[:5]  # First 5 steps
    recipe_techniques = recipe.get("techniques", [])

    # Quick heuristic: if recipe has no steps AND no techniques, reject
    if not recipe_steps and not recipe_techniques:
        return False

    prompt = f"""You are a culinary expert evaluating if a recipe teaches a specific technique.

TECHNIQUE: {learning_goal}
DEFINITION: {technique_definition}

RECIPE TO EVALUATE:
Title: {recipe_title}
Techniques listed: {', '.join(recipe_techniques)}
Steps: {' '.join(recipe_steps[:3])}

QUESTION: Does this recipe teach "{learning_goal}"?

Be LENIENT - accept if the recipe is related or teaches this skill, even partially.
Only reject obvious false positives (e.g., "fried rice" for "pan sauces").

Answer with ONLY "YES" or "NO" followed by a brief reason.

Examples:
"YES - Sourdough teaches bread baking fundamentals."
"NO - Fried rice doesn't involve making pan sauces."

Your answer:"""

    try:
        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # Low temp for consistent validation
            max_tokens=100
        )

        answer = response.choices[0].message.content.strip()
        state["llm_calls"] = state.get("llm_calls", 0) + 1

        # Parse YES/NO from response
        is_valid = answer.upper().startswith("YES")

        return is_valid

    except Exception as e:
        print(f"   ⚠️ Validation error for {recipe_title}: {e}")
        # On error, be permissive (keep the recipe)
        return True
