"""
Intent Extractor Agent

Responsibility: Parse natural language user input into structured search parameters.
This agent enables conversational UX by extracting learning_goal, skill_level, and
dietary restrictions from free-form text.
"""

import os
import json
from openai import OpenAI
from backend.logger import get_logger

logger = get_logger("intent_extractor")


def answer_follow_up(message: str) -> str:
    """
    Answer a follow-up question about cooking using GPT.

    This is used when the user asks a question rather than requesting new recipes.

    Args:
        message: The user's follow-up question

    Returns:
        A conversational answer to the question
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
        messages=[
            {
                "role": "system",
                "content": "You are Ratatouille, a friendly culinary education assistant. Answer cooking questions concisely and helpfully. Keep responses to 2-3 sentences unless more detail is needed. Be warm and encouraging."
            },
            {
                "role": "user",
                "content": message
            }
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()


def extract_intent(message: str) -> dict:
    """
    Parse natural language cooking request into structured parameters.

    Examples:
    - "I want to shallow fry without experience and minimize oil"
      → learning_goal="shallow frying", skill_level="beginner"

    - "Show me advanced bread baking techniques"
      → learning_goal="bread baking", skill_level="advanced"

    - "vegetarian pan sauces for intermediate cooks"
      → learning_goal="pan sauces", skill_level="intermediate", dietary=["vegetarian"]

    Args:
        message: Natural language user input

    Returns:
        dict with learning_goal, skill_level, dietary_restrictions, constraints
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""You are a culinary education assistant. Parse this cooking recipe request into structured data.

User message: "{message}"

Extract the following information:

1. **learning_goal** (required): The main cooking technique, dish, or skill they want to learn
   - Examples: "pan sauces", "shallow frying", "bread baking", "knife skills", "pasta", "fried rice"
   - Be specific but concise (2-4 words max)

2. **skill_level** (required): Infer their experience level from context
   - "beginner": No experience, learning basics, mentions "first time", "never done", "new to", "easy", "simple"
   - "intermediate": Some experience, wants to improve, no qualifiers = default to this
   - "advanced": Mentions "advanced", "master", "professional", or complex techniques

3. **dietary_restrictions** (optional): Any dietary constraints mentioned
   - Possible values: "vegetarian", "vegan", "gluten-free", "dairy-free", "kosher", "halal"
   - Return empty list if none mentioned

4. **constraints** (optional): Special requirements like "quick", "minimal oil", "budget-friendly"
   - Extract any mentioned, empty list if none

Return ONLY valid JSON in this exact format:
{{
  "learning_goal": "pan sauces",
  "skill_level": "intermediate",
  "dietary_restrictions": ["vegetarian"],
  "constraints": ["minimal oil"]
}}

CRITICAL: Return ONLY the JSON object, no markdown, no explanations."""

    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temp for consistent parsing
            max_tokens=200
        )

        parsed_text = response.choices[0].message.content.strip()

        # Remove markdown code blocks if present
        if parsed_text.startswith("```"):
            parsed_text = parsed_text.split("```")[1]
            if parsed_text.startswith("json"):
                parsed_text = parsed_text[4:]

        intent_data = json.loads(parsed_text)

        # Validate required fields
        if "learning_goal" not in intent_data or not intent_data["learning_goal"]:
            raise ValueError("Missing learning_goal in parsed intent")

        if "skill_level" not in intent_data:
            intent_data["skill_level"] = "intermediate"  # Default

        if "dietary_restrictions" not in intent_data:
            intent_data["dietary_restrictions"] = []

        if "constraints" not in intent_data:
            intent_data["constraints"] = []

        # Normalize skill_level to allowed values
        skill = intent_data["skill_level"].lower()
        if skill not in ["beginner", "intermediate", "advanced"]:
            logger.warning(f"Invalid skill_level '{skill}', defaulting to intermediate")
            intent_data["skill_level"] = "intermediate"

        logger.info(f"Extracted intent: {intent_data['learning_goal']} ({intent_data['skill_level']})")

        return intent_data

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON from LLM: {e}")
        logger.error(f"LLM response was: {parsed_text}")
        raise ValueError(f"Failed to parse intent from message: {message}")

    except Exception as e:
        logger.error(f"Intent extraction error: {e}")
        raise ValueError(f"Failed to extract intent: {str(e)}")
