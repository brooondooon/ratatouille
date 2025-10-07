# 🐀 Ratatouille - AI Culinary Coach

An intelligent recipe recommendation system that helps home cooks learn culinary techniques through personalized, validated recipe suggestions.

## Overview

Ratatouille uses a **5-agent multi-agent system** with semantic understanding to recommend recipes that genuinely teach cooking techniques. Unlike traditional recipe search that relies on keywords, Ratatouille validates that recipes actually teach the requested technique (e.g., filters out "fried rice" when searching for "pan sauces").

### Key Features

- ✅ **Semantic Technique Validation** - LLM-powered filtering eliminates false positives
- ✅ **Educational Focus** - Recipes scored on learning value, not just relevance
- ✅ **Adaptive Coordination** - Agents retry with broader search when needed
- ✅ **Nutrition Intelligence** - Automatic nutrition estimation per serving
- ✅ **Source Transparency** - Citations with dates and author attribution

## Quick Start

### Prerequisites

- Python 3.10+
- OpenAI API key ([get one here](https://platform.openai.com/api-keys))
- Tavily API key ([get one here](https://tavily.com))

### Installation

```bash
# Clone repository
git clone <repo-url>
cd ratatouille-project

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your API keys
```

### Running the Backend

```bash
python3 -m backend.app
```

Backend runs on `http://localhost:8000`

### Testing the API

Visit `http://localhost:8000/docs` for interactive API documentation.

**Example request:**
```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "learning_goal": "pan sauces",
    "skill_level": "intermediate",
    "dietary_restrictions": []
  }'
```

## Architecture

### 5-Agent System

1. **Research Planner** - Generates optimal search queries from learning goals
2. **Recipe Hunter** - Searches Tavily API and parses recipes with LLM
3. **Technique Validator** - Validates recipes genuinely teach the technique
4. **Personalization Engine** - Scores and selects top 3 recipes
5. **Nutrition Analyzer** - Estimates nutritional information

### Technology Stack

- **Orchestration:** LangGraph (multi-agent state management)
- **LLM:** OpenAI GPT-3.5-turbo
- **Search:** Tavily API
- **Backend:** FastAPI
- **Language:** Python 3.10+

## Documentation

- **[System Overview](docs/SYSTEM_OVERVIEW.md)** - Complete architecture and agent details
- **[API Reference](docs/API_REFERENCE.md)** - Endpoint documentation

## Performance

- **Latency:** 30-45 seconds per request
- **API Calls:** 3 Tavily searches, 20-30 OpenAI completions
- **Cost:** ~$0.015 per request
- **Accuracy:** 0% false positive rate (validated)

## Project Structure

```
ratatouille-project/
├── backend/
│   ├── agents/
│   │   ├── research_planner.py
│   │   ├── recipe_hunter.py
│   │   ├── technique_validator.py
│   │   ├── personalization.py
│   │   └── nutrition_analyzer.py
│   ├── app.py              # FastAPI application
│   ├── graph.py            # LangGraph workflow
│   └── state.py            # State schema
├── docs/
│   ├── SYSTEM_OVERVIEW.md
│   └── API_REFERENCE.md
├── requirements.txt
├── .env.example
└── README.md
```

## Example Output

```json
{
  "recipes": [
    {
      "recipe": {
        "title": "Pan-Seared Chicken with Lemon Butter Sauce",
        "difficulty": "intermediate",
        "time_estimate": "45 minutes"
      },
      "reasoning": "Perfect for mastering pan sauce fundamentals...",
      "technique_highlights": [
        "Pan deglazing with wine",
        "Butter emulsion (mounting)",
        "Temperature control"
      ],
      "nutrition": {
        "calories": 450,
        "protein_g": 25,
        "servings": 4
      }
    }
  ]
}
```

## License

MIT

## Authors

Brandon Qin

---

**Built with [LangGraph](https://github.com/langchain-ai/langgraph) and [Tavily](https://tavily.com)**
