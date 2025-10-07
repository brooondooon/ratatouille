"""
Recipe Hunter Agent

Responsibility: Retrieve recipes from the web using Tavily API and parse into structured format.
This agent calls Tavily to find recipes, then uses LLM to parse unstructured text into JSON.
"""

import os
import json
from typing import List, Dict, Any
from tavily import TavilyClient
from openai import OpenAI
from backend.state import RecipeState


def recipe_hunter_agent(state: RecipeState) -> RecipeState:
    """
    Search for recipes using Tavily API and parse them into structured format.

    Flow:
    1. Run Tavily Search for each query
    2. Parse search result snippets with LLM (NO EXTRACT API)
    3. Return top 2 recipes

    Args:
        state: Current workflow state with search_queries populated

    Returns:
        Updated state with raw_recipes populated
    """
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    search_queries = state["search_queries"]
    all_recipes = []
    tavily_call_count = 0

    print(f"🔎 Recipe Hunter: Searching with {len(search_queries)} queries")

    # Search and parse recipes from snippets
    for query in search_queries[:3]:
        try:
            results = tavily_client.search(
                query=query + " recipe",
                search_depth="advanced",
                max_results=5,
                days=730
            )
            tavily_call_count += 1

            # Parse top results from this query
            for result in results.get("results", [])[:2]:
                parsed_recipe = _parse_recipe_from_snippet(result, openai_client, state)
                if parsed_recipe:
                    all_recipes.append(parsed_recipe)

                # Stop if we have enough recipes
                if len(all_recipes) >= 2:
                    break

        except Exception as e:
            error_msg = f"Tavily search failed for '{query}': {str(e)}"
            print(f"   ⚠️ {error_msg}")
            state["errors"].append(error_msg)

        # Stop if we have enough recipes
        if len(all_recipes) >= 2:
            break

    # Update state
    state["raw_recipes"] = all_recipes[:2]  # Ensure max 2 recipes
    state["tavily_calls"] = state.get("tavily_calls", 0) + tavily_call_count

    print(f"✅ Recipe Hunter: Found {len(state['raw_recipes'])} recipes")

    return state


def _parse_recipe_from_snippet(
    tavily_result: Dict[str, Any],
    openai_client: OpenAI,
    state: RecipeState
) -> Dict[str, Any]:
    """
    Parse recipe from Tavily Search result snippet using LLM.
    NO EXTRACT API - just use the snippet content.

    Args:
        tavily_result: Result from Tavily Search API
        openai_client: OpenAI client instance
        state: Current state (for tracking LLM calls)

    Returns:
        Parsed recipe dict or None if parsing fails
    """
    url = tavily_result.get("url", "")
    title = tavily_result.get("title", "")
    snippet = tavily_result.get("content", "")

    if not url or not snippet:
        return None

    try:
        # Parse recipe from snippet with LLM
        parse_prompt = f"""Extract recipe information from this search result and return ONLY valid JSON.

Title: {title}
Content: {snippet}

Return this exact JSON format:
{{
  "title": "Recipe title",
  "difficulty": "beginner|intermediate|advanced",
  "techniques": ["technique1", "technique2"],
  "ingredients": ["ingredient1", "ingredient2"],
  "instructions": ["Step 1", "Step 2"],
  "time_estimate": "X minutes"
}}

If information is missing, make reasonable inferences based on the content.
Return ONLY the JSON object, nothing else."""

        response = openai_client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": parse_prompt}],
            temperature=0.2,
            max_tokens=1200
        )

        parsed_text = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if parsed_text.startswith("```"):
            parsed_text = parsed_text.split("```")[1]
            if parsed_text.startswith("json"):
                parsed_text = parsed_text[4:]

        recipe_data = json.loads(parsed_text)

        # Add metadata from Tavily Search result
        recipe_data["url"] = url
        recipe_data["source"] = _extract_source_from_url(url)
        recipe_data["published_date"] = tavily_result.get("published_date", "Unknown")
        recipe_data["tavily_score"] = tavily_result.get("score", 0.5)
        recipe_data["author"] = "Unknown"

        # Track LLM call for parsing
        state["llm_calls"] = state.get("llm_calls", 0) + 1

        return recipe_data

    except json.JSONDecodeError as e:
        error_msg = f"JSON parse error for {url}: {str(e)}"
        print(f"   ⚠️ {error_msg}")
        state["errors"].append(error_msg)
        return None
    except Exception as e:
        error_msg = f"Recipe parsing error for {url}: {str(e)}"
        print(f"   ⚠️ {error_msg}")
        state["errors"].append(error_msg)
        return None


def _extract_source_from_url(url: str) -> str:
    """Extract source name from URL."""
    from urllib.parse import urlparse

    if not url:
        return "Unknown"

    domain = urlparse(url).netloc.lower()

    source_map = {
        "seriouseats.com": "Serious Eats",
        "www.seriouseats.com": "Serious Eats",
        "bonappetit.com": "Bon Appetit",
        "www.bonappetit.com": "Bon Appetit",
        "foodnetwork.com": "Food Network",
        "www.foodnetwork.com": "Food Network",
        "allrecipes.com": "Allrecipes",
        "www.allrecipes.com": "Allrecipes",
        "epicurious.com": "Epicurious",
        "www.epicurious.com": "Epicurious",
        "kingarthurbaking.com": "King Arthur Baking",
        "www.kingarthurbaking.com": "King Arthur Baking",
        "nytimes.com": "NY Times Cooking",
        "cooking.nytimes.com": "NY Times Cooking",
    }

    return source_map.get(domain, domain.replace("www.", "").split(".")[0].title())
