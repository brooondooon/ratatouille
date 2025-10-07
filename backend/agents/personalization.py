"""
Personalization Engine Agent

Responsibility: Filter, rank, and select best 2 recipes with reasoning for user.
This agent applies domain expertise to match recipes to user's learning goals.
"""

import os
from typing import List, Dict, Any
from datetime import datetime
from openai import OpenAI
from backend.state import RecipeState


# Technique mapping for learning value scoring
TECHNIQUE_MAP = {
    "pan sauces": ["deglazing", "emulsification", "reduction", "mounting butter"],
    "bread baking": ["kneading", "proofing", "scoring", "fermentation"],
    "knife skills": ["julienne", "brunoise", "chiffonade", "dicing"],
    "roasting": ["searing", "basting", "temperature control", "resting"],
    "pasta": ["dough making", "rolling", "shaping", "sauce pairing"],
}


def personalization_engine_agent(state: RecipeState) -> RecipeState:
    """
    Filter, score, and select top 2 recipes with educational reasoning.

    Process:
    1. Filter recipes by dietary restrictions and skill appropriateness
    2. Score recipes on learning value, skill match, recency, quality
    3. Select top 3 that teach complementary skills
    4. Generate "why this recipe" reasoning for each

    Args:
        state: Current workflow state with raw_recipes populated

    Returns:
        Updated state with final_cards and comparison populated
    """
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    raw_recipes = state["raw_recipes"]
    user_skill = state["skill_level"]
    learning_goal = state["learning_goal"]
    dietary_restrictions = state["dietary_restrictions"]
    excluded_urls = state.get("excluded_urls", [])

    print(f"🎯 Personalization Engine: Processing {len(raw_recipes)} recipes")

    # Filter out excluded URLs first
    if excluded_urls:
        print(f"   ⚠️ Filtering out {len(excluded_urls)} excluded recipes")
        print(f"   📋 Excluded URLs: {excluded_urls[:3]}..." if len(excluded_urls) > 3 else f"   📋 Excluded URLs: {excluded_urls}")
        before_count = len(raw_recipes)
        raw_recipes = [r for r in raw_recipes if r.get("url") not in excluded_urls]
        filtered_count = before_count - len(raw_recipes)
        print(f"   ✓ Filtered out {filtered_count} recipes, {len(raw_recipes)} remaining")

    # Step 1: Filter recipes
    filtered_recipes = _filter_recipes(
        raw_recipes,
        dietary_restrictions,
        user_skill
    )

    if len(filtered_recipes) < 2:
        print(f"   ⚠️ Only {len(filtered_recipes)} recipes after filtering")
        # Loosen dietary filters if needed
        filtered_recipes = _filter_recipes(
            raw_recipes,
            [],  # Remove dietary restrictions
            user_skill
        )

    # Step 2: Score recipes
    scored_recipes = []
    for recipe in filtered_recipes:
        score = _score_recipe(recipe, state)
        scored_recipes.append({
            "recipe": recipe,
            "score": score
        })

    # Sort by score descending
    scored_recipes.sort(key=lambda x: x["score"], reverse=True)

    # Step 3: Select top 3 with diversity
    selected = _select_diverse_recipes(scored_recipes[:6], 3)

    # Step 4: Generate reasoning for each selected recipe
    final_cards = []
    for item in selected:
        reasoning = _generate_reasoning(
            item["recipe"],
            state,
            openai_client
        )
        final_cards.append({
            "recipe": {
                "title": item["recipe"]["title"],
                "url": item["recipe"]["url"],
                "source": item["recipe"]["source"],
                "author": item["recipe"]["author"],
                "published_date": item["recipe"]["published_date"],
                "difficulty": item["recipe"]["difficulty"],
                "time_estimate": item["recipe"]["time_estimate"]
            },
            "reasoning": reasoning["reasoning"],
            "technique_highlights": reasoning["technique_highlights"],
            "score": round(item["score"], 1)
        })

    # Step 5: Generate comparison
    comparison = _generate_comparison(final_cards, openai_client, state)

    # Update state
    state["scored_recipes"] = scored_recipes
    state["final_cards"] = final_cards
    state["comparison"] = comparison

    print(f"✅ Personalization Engine: Selected {len(final_cards)} recipes")

    return state


def _filter_recipes(
    recipes: List[Dict[str, Any]],
    dietary_restrictions: List[str],
    skill_level: str
) -> List[Dict[str, Any]]:
    """Filter recipes by dietary restrictions and skill appropriateness."""
    filtered = []

    for recipe in recipes:
        skip_recipe = False

        # Check dietary restrictions (simple keyword matching)
        if dietary_restrictions:
            try:
                ingredients = recipe.get("ingredients", [])

                # Recursively flatten any nested structure into a single list of strings
                def flatten_to_strings(obj):
                    """Recursively flatten nested lists/tuples to list of strings"""
                    if isinstance(obj, (list, tuple)):
                        result = []
                        for item in obj:
                            result.extend(flatten_to_strings(item))
                        return result
                    else:
                        return [str(obj)]

                # Flatten and convert all to strings
                flat_ingredients = flatten_to_strings(ingredients)

                # Join into a single string for searching
                ingredients_text = " ".join(flat_ingredients).lower()

                # Final safety check
                if not isinstance(ingredients_text, str):
                    print(f"   ⚠️ WARNING: ingredients_text is {type(ingredients_text)}, forcing to string")
                    ingredients_text = str(ingredients_text)

                # Skip if restricted ingredients found
                restrictions_map = {
                    "vegetarian": ["chicken", "beef", "pork", "fish", "meat"],
                    "vegan": ["chicken", "beef", "pork", "fish", "meat", "egg", "dairy", "milk", "cheese", "butter"],
                    "gluten-free": ["flour", "wheat", "bread", "pasta"],
                }

                for restriction in dietary_restrictions:
                    forbidden = restrictions_map.get(restriction.lower(), [])
                    if any(word in ingredients_text for word in forbidden):
                        skip_recipe = True
                        break

            except Exception as e:
                print(f"   ⚠️ Error processing dietary restrictions for {recipe.get('title', 'unknown')}: {e}")
                print(f"   ⚠️ Ingredients data: {recipe.get('ingredients', [])}")
                # Skip this recipe on error to be safe
                skip_recipe = True

        if skip_recipe:
            continue

        # Keep recipe
        filtered.append(recipe)

    return filtered


def _score_recipe(recipe: Dict[str, Any], state: RecipeState) -> float:
    """
    Score recipe based on learning value, skill match, recency, and quality.

    Scoring breakdown:
    - Learning value: 30 points (technique relevance)
    - Skill appropriateness: 25 points
    - Recency: 20 points
    - Source quality: 15 points (Tavily score)
    - Technique diversity: 10 points
    """
    score = 0.0

    learning_goal = state["learning_goal"].lower()
    skill_level = state["skill_level"]

    # 1. Learning value (max 30 points)
    # Flatten techniques in case LLM returns nested lists
    raw_techniques = recipe.get("techniques", [])
    recipe_techniques = []
    for t in raw_techniques:
        if isinstance(t, list):
            recipe_techniques.extend([str(x).lower() for x in t])
        else:
            recipe_techniques.append(str(t).lower())

    # Get relevant techniques and ensure they're also flattened
    relevant_techniques_raw = TECHNIQUE_MAP.get(learning_goal, learning_goal.split())
    if isinstance(relevant_techniques_raw, str):
        relevant_techniques = [relevant_techniques_raw]
    elif isinstance(relevant_techniques_raw, list):
        # Flatten in case it's a nested list
        relevant_techniques = []
        for item in relevant_techniques_raw:
            if isinstance(item, list):
                relevant_techniques.extend([str(x) for x in item])
            else:
                relevant_techniques.append(str(item))
    else:
        relevant_techniques = [str(relevant_techniques_raw)]

    matches = sum(1 for tech in relevant_techniques if any(tech in rt for rt in recipe_techniques))
    score += min(matches * 10, 30)

    # 2. Skill appropriateness (max 25 points)
    # Strongly penalize mismatches
    skill_scores = {
        'beginner': {'beginner': 25, 'intermediate': 8, 'advanced': -10},
        'intermediate': {'beginner': 3, 'intermediate': 25, 'advanced': 12},
        'advanced': {'beginner': -10, 'intermediate': 8, 'advanced': 25}
    }
    recipe_difficulty = recipe.get("difficulty", "intermediate")
    score += skill_scores.get(skill_level, {}).get(recipe_difficulty, 10)

    # 3. Recency (max 20 points) - newer is better
    published = recipe.get("published_date", "")
    if published and published != "Unknown":
        try:
            # Simple year extraction
            if "2024" in published or "2025" in published:
                score += 20
            elif "2023" in published:
                score += 15
            elif "2022" in published:
                score += 10
            else:
                score += 5
        except:
            score += 10

    # 4. Tavily relevance score (max 15 points)
    tavily_score = recipe.get("tavily_score", 0.5)
    score += tavily_score * 15

    # 5. Technique diversity bonus (max 10 points)
    if len(recipe_techniques) >= 3:
        score += 10
    elif len(recipe_techniques) >= 2:
        score += 5

    return score


def _select_diverse_recipes(
    scored_recipes: List[Dict[str, Any]],
    count: int = 3
) -> List[Dict[str, Any]]:
    """
    Select top N recipes that teach complementary (diverse) techniques and have distinct dishes.
    """
    if len(scored_recipes) <= count:
        return scored_recipes

    selected = [scored_recipes[0]]  # Always take the top one

    # For remaining slots, prefer recipes with different techniques AND different dishes
    for candidate in scored_recipes[1:]:
        if len(selected) >= count:
            break

        # Check for title similarity (avoid duplicate dishes)
        candidate_title = candidate["recipe"].get("title", "").lower()
        is_similar_dish = False

        for s in selected:
            selected_title = s["recipe"].get("title", "").lower()
            # Extract key dish words (remove common words)
            common_words = {"with", "and", "the", "in", "for", "to", "recipe", "easy", "simple", "best", "a", "an", "how", "make", "homemade"}
            candidate_words = set(word for word in candidate_title.split() if word not in common_words)
            selected_words = set(word for word in selected_title.split() if word not in common_words)

            # Check for shared key ingredients/types (e.g., both mention "red wine")
            key_ingredients = candidate_words & selected_words

            # If they share 2+ key words (like "red" + "wine"), they're too similar
            if len(key_ingredients) >= 2:
                is_similar_dish = True
                break

            # Otherwise, if more than 30% of meaningful words overlap, consider it similar
            if candidate_words and selected_words:
                overlap = len(candidate_words & selected_words) / min(len(candidate_words), len(selected_words))
                if overlap > 0.3:
                    is_similar_dish = True
                    break

        # Skip if it's a similar dish
        if is_similar_dish:
            print(f"   🔄 Skipping similar recipe: {candidate_title} (too similar to already selected)")
            continue

        # Check for technique diversity
        candidate_techniques = set(candidate["recipe"].get("techniques", []))
        selected_techniques = set()
        for s in selected:
            selected_techniques.update(s["recipe"].get("techniques", []))

        # Prefer recipes with at least 1 unique technique
        if candidate_techniques - selected_techniques or len(selected) < count:
            selected.append(candidate)

    # If we didn't get enough diverse recipes, fill with remaining top-scored ones
    if len(selected) < count:
        for candidate in scored_recipes:
            if len(selected) >= count:
                break
            if candidate not in selected:
                selected.append(candidate)

    return selected


def _generate_reasoning(
    recipe: Dict[str, Any],
    state: RecipeState,
    openai_client: OpenAI
) -> Dict[str, Any]:
    """Generate educational reasoning for why this recipe fits the user."""

    prompt = f"""You are a professional chef and culinary educator. Generate a concise explanation
for why this recipe is perfect for the user's learning goals.

User context:
- Skill level: {state['skill_level']}
- Learning goal: {state['learning_goal']}

Recipe:
- Title: {recipe['title']}
- Techniques: {', '.join(recipe.get('techniques', []))}
- Difficulty: {recipe['difficulty']}

Generate:
1. "Why this recipe" (2-3 sentences, learning-focused and encouraging)
2. Key technique highlights (3-4 bullet points, specific skills they'll practice)

Return ONLY valid JSON with no markdown:
{{
  "reasoning": "Your 2-3 sentence explanation here",
  "technique_highlights": ["Specific technique 1", "Specific technique 2", "Specific technique 3"]
}}"""

    try:
        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )

        import json
        result = response.choices[0].message.content.strip()

        # Clean markdown if present
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]

        parsed = json.loads(result)
        state["llm_calls"] = state.get("llm_calls", 0) + 1

        return parsed

    except Exception as e:
        print(f"   ⚠️ Reasoning generation failed: {e}")
        return {
            "reasoning": f"This recipe teaches {', '.join(recipe.get('techniques', ['essential cooking skills']))}.",
            "technique_highlights": recipe.get("techniques", ["See recipe for details"])[:3]
        }


def _generate_comparison(
    final_cards: List[Dict[str, Any]],
    openai_client: OpenAI,
    state: RecipeState
) -> Dict[str, str]:
    """Generate comparison notes between the two selected recipes."""

    if len(final_cards) < 2:
        return {
            "recipe_1_focus": "N/A",
            "recipe_2_focus": "N/A",
            "shared_techniques": []
        }

    recipe1 = final_cards[0]["recipe"]
    recipe2 = final_cards[1]["recipe"]

    # Simple technique comparison
    techniques1 = set(final_cards[0]["technique_highlights"])
    techniques2 = set(final_cards[1]["technique_highlights"])
    shared = list(techniques1 & techniques2)

    return {
        "recipe_1_focus": recipe1["title"],
        "recipe_2_focus": recipe2["title"],
        "shared_techniques": shared[:3] if shared else []
    }
