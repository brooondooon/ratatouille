"""
LangGraph Workflow Definition

This module defines the multi-agent workflow using LangGraph.
Agents coordinate through shared state and conditional routing.
"""

from langgraph.graph import StateGraph, END
from backend.state import RecipeState
from backend.agents.research_planner import research_planner_agent
from backend.agents.recipe_hunter import recipe_hunter_agent
from backend.agents.technique_validator import technique_validator_agent
from backend.agents.personalization import personalization_engine_agent
from backend.agents.nutrition_analyzer import nutrition_analyzer_agent


def route_after_recipe_hunter(state: RecipeState) -> str:
    """
    Agent coordination logic: decide whether to retry search or proceed.

    If Recipe Hunter finds insufficient results, signal Research Planner
    to broaden search strategy. This demonstrates true multi-agent
    coordination where agents adapt based on other agents' outputs.

    Args:
        state: Current workflow state

    Returns:
        Next node name ("research_planner" for retry, "technique_validator" to continue)
    """
    recipe_count = len(state.get('raw_recipes', []))
    retry_count = state.get('retry_count', 0)

    # If we found fewer than 2 recipes and haven't retried too many times
    if recipe_count < 2 and retry_count < 2:
        print(f"⚠️ Only {recipe_count} recipes found. Retrying with broader search...")

        # Signal to Research Planner to broaden search
        state['search_strategy'] = 'broadened'
        state['retry_count'] = retry_count + 1
        state['errors'].append(f"Low recipe count ({recipe_count}), retrying with broader search")

        return "research_planner"  # Loop back for retry

    # Enough recipes found or max retries reached - proceed to validation
    print(f"✓ Found {recipe_count} recipes, proceeding to technique validation")
    return "technique_validator"


def create_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow.

    Workflow structure:
    1. Research Planner → generates search queries
    2. Recipe Hunter → searches and parses recipes
    3. [Conditional] If insufficient recipes → retry Research Planner
    4. Technique Validator → filters out false positives using LLM understanding
    5. Personalization Engine → scores and selects top 2
    6. Nutrition Analyzer → adds nutrition estimates
    7. END → return final results

    Returns:
        Compiled LangGraph workflow
    """
    # Initialize graph with state schema
    workflow = StateGraph(RecipeState)

    # Add agent nodes (now 5 agents!)
    workflow.add_node("research_planner", research_planner_agent)
    workflow.add_node("recipe_hunter", recipe_hunter_agent)
    workflow.add_node("technique_validator", technique_validator_agent)
    workflow.add_node("personalization", personalization_engine_agent)
    workflow.add_node("nutrition_analyzer", nutrition_analyzer_agent)

    # Define flow
    workflow.set_entry_point("research_planner")

    # Linear flow: Research Planner → Recipe Hunter
    workflow.add_edge("research_planner", "recipe_hunter")

    # Conditional routing: Recipe Hunter → (retry OR validate)
    # This is the key coordination mechanism - agents adapt based on results
    workflow.add_conditional_edges(
        "recipe_hunter",
        route_after_recipe_hunter,
        {
            "research_planner": "research_planner",      # Retry with broader search
            "technique_validator": "technique_validator"  # Continue to validation
        }
    )

    # Linear flow: Technique Validator → Personalization → Nutrition Analyzer → END
    workflow.add_edge("technique_validator", "personalization")
    workflow.add_edge("personalization", "nutrition_analyzer")
    workflow.add_edge("nutrition_analyzer", END)

    # Compile workflow
    app = workflow.compile()

    print("✅ LangGraph workflow compiled successfully")
    print("   Flow: Research Planner → Recipe Hunter → [retry check] → Technique Validator → Personalization → Nutrition → END")

    return app


# Create the compiled workflow (singleton)
workflow_app = create_workflow()
