# 🐀 Ratatouille - AI Culinary Coach

An intelligent recipe recommendation system that helps home cooks learn culinary techniques through personalized recipe suggestions and interactive cooking guidance.

**Try it live**: [https://tinyurl.com/ratatouillechef](https://tinyurl.com/ratatouillechef)

## Overview

**Problem:** Home cooks searching for recipes to learn specific techniques face a frustrating challenge—generic recipe search returns thousands of results with no way to filter by skill level or learning value. A beginner searching "pan sauces" gets the same results as an expert, buried in food blogs and ads, with no guarantee the recipe actually teaches the technique properly.

**Solution:** Ratatouille is a **multi-agent system with 4 specialized sub-agents** built with LangGraph that solves this by combining **real-time web search** (Tavily API) with **intelligent filtering and personalization**. Instead of static recipe databases, Ratatouille searches the live web for the most recent, high-quality recipes, then uses specialized sub-agents to:

1. **Validate** recipes genuinely teach your target technique (not just keyword matches)
2. **Score** recipes on educational value, skill appropriateness, and technique diversity
3. **Personalize** by selecting the top 3 recipes that match your exact skill level and learning goals
4. **Enrich** with nutritional data and technique highlights

## Demo Video

https://github.com/brooondooon/ratatouille/assets/Demo%20Video.mp4

### Key Features

- 🎯 **Smart Recipe Discovery** - Conversational interface for natural language requests
- 🧑‍🍳 **Interactive Cooking Mode** - Step-by-step guidance with timers and XP rewards
- 📚 **Personal Cookbook** - Bookmark and organize favorite recipes
- 🤖 **4 Specialized Sub-Agents** - Research planner, recipe hunter, personalization engine, and nutrition analyzer
- ⚡ **Real-Time Search** - Tavily API ensures fresh, up-to-date recipes from across the web
- 🍎 **Nutrition Intelligence** - Automatic nutrition estimation per serving

## Quick Start

### Prerequisites

- **Python 3.10+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **OpenAI API key** ([Get one here](https://platform.openai.com/api-keys))
- **Tavily API key** ([Get one here](https://tavily.com))

### Quick Installation

```bash
# 1. Clone repository
git clone https://github.com/brooondooon/ratatouille.git
cd ratatouille-project

# 2. Backend setup
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys

# 3. Frontend setup
cd frontend
npm install
cd ..

# 4. Start backend (terminal 1)
export PYTHONPATH=$(pwd)
python3 backend/app.py

# 5. Start frontend (terminal 2)
cd frontend && npm run dev
```

**Access the app**: http://localhost:3000

**Detailed setup instructions**: See [docs/SETUP.md](docs/SETUP.md)

## Architecture

### Multi-Agent System with 4 Specialized Sub-Agents

1. **Research Planner** - Generates optimal search queries based on learning goals
2. **Recipe Hunter** - Searches Tavily API and parses recipes into structured format
3. **Personalization Engine** - Scores, filters, and selects top 3 recipes with reasoning
4. **Nutrition Analyzer** - Estimates nutritional information using GPT

**Sub-Agent Coordination**: Conditional routing with automatic retry logic when insufficient results are found.

### Technology Stack

**Backend**:
- **Orchestration**: LangGraph 0.6.8 (multi-agent state management)
- **LLM**: OpenAI GPT-3.5-turbo
- **Search**: Tavily API
- **Framework**: FastAPI + Uvicorn
- **Language**: Python 3.10+

**Frontend**:
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI**: Shadcn UI + Tailwind CSS
- **Icons**: Lucide React

## Documentation

📚 **Complete documentation** in `/docs`:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Detailed system design and agent workflows
- **[SETUP.md](docs/SETUP.md)** - Installation and configuration guide
- **[API_REFERENCE.md](docs/API_REFERENCE.md)** - Complete API endpoint documentation
- **[FRONTEND.md](docs/FRONTEND.md)** - Frontend components and features

## Performance

- **Response Time**: 30-32 seconds per recipe request
- **Tavily Calls**: 5 searches per request
- **LLM Calls**: 12 GPT-3.5-turbo completions per request
- **Cost**: ~$0.017 per request ($0.005 Tavily + $0.012 OpenAI)
- **Optimization**: 60-70% faster than v1.0 (removed technique validator, limited to 5 recipes)

## Project Structure

```
ratatouille-project/
├── backend/
│   ├── agents/                    # 4 specialized agents + intent extractor
│   │   ├── research_planner.py   # Query generation
│   │   ├── recipe_hunter.py      # Tavily search + parsing
│   │   ├── personalization.py    # Scoring and selection
│   │   ├── nutrition_analyzer.py # Nutrition estimation
│   │   └── intent_extractor.py   # User intent parsing
│   ├── app.py                     # FastAPI application
│   ├── graph.py                   # LangGraph workflow definition
│   ├── state.py                   # RecipeState schema
│   ├── config.py                  # Configuration
│   └── logger.py                  # Logging setup
├── frontend/
│   ├── app/                       # Next.js pages (App Router)
│   │   ├── chat/                 # Main chat interface
│   │   ├── cook/                 # Interactive cooking mode
│   │   └── cookbook/             # Saved recipes
│   ├── components/               # React components
│   │   ├── RecipeCard.tsx
│   │   ├── Navigation.tsx
│   │   ├── Timer.tsx
│   │   └── ...
│   ├── lib/                      # Utilities and types
│   │   ├── api.ts               # API client
│   │   └── types.ts             # TypeScript definitions
│   └── public/                  # Static assets
├── docs/                        # Comprehensive documentation
│   ├── ARCHITECTURE.md         # System design
│   ├── SETUP.md                # Installation guide
│   ├── API_REFERENCE.md        # API documentation
│   └── FRONTEND.md             # Frontend guide
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
└── README.md                  # This file
```

## Features Deep Dive

### 🎯 Chat with Ratatouille
- Natural language recipe requests
- Conversational follow-up Q&A
- Agent progress visualization
- Recipe bookmarking and exclusion
- Persistent chat history (localStorage)

### 🧑‍🍳 Interactive Cooking Mode
- Step-by-step guided cooking
- Built-in timers for each step
- Ingredient checklists
- XP rewards and gamification
- Key technique highlights

### 📚 Personal Cookbook
- Save favorite recipes
- View all bookmarked recipes
- Quick access to "Let's Cook" mode
- Persistent storage

### 🤖 Multi-Agent Backend with Specialized Sub-Agents
- **Research Planner**: Generates 5 diverse search queries
- **Recipe Hunter**: Searches and parses recipes from Tavily
- **Personalization Engine**: Scores recipes on learning value, skill match, recency
- **Nutrition Analyzer**: Estimates nutrition using GPT

### 🔄 Smart Sub-Agent Coordination
- Automatic retry with broader search if < 2 recipes found
- Conditional routing based on sub-agent results
- Shared state management via LangGraph

## Example Workflow

**User**: "I want to learn pan sauces for beginners"

**1. Research Planner** generates queries:
```
1. "garlic butter pan sauce chicken recipe beginner"
2. "red wine shallot pan sauce steak recipe easy"
3. "mushroom cream pan sauce pork recipe simple"
...
```

**2. Recipe Hunter** searches and returns 5 structured recipes

**3. Personalization** scores and selects top 3 with reasoning

**4. Nutrition Analyzer** adds nutrition data to each recipe:
```json
{
  "recipe": {
    "title": "Steak with Red Wine Pan Sauce",
    "difficulty": "intermediate",
    "time_estimate": "45 minutes"
  },
  "reasoning": "This recipe teaches fundamental pan sauce techniques including deglazing, reduction, and butter mounting - essential skills for any home cook.",
  "technique_highlights": [
    "Pan deglazing with red wine",
    "Butter emulsion (mounting butter)",
    "Proper temperature control for searing"
  ],
  "nutrition": {
    "calories": 450,
    "protein_g": 25,
    "carbs_g": 35,
    "fat_g": 18,
    "servings": 4
  },
  "score": 87.5
}
```

**Result**: 3 personalized recipes with nutrition in 30 seconds

---

## Contributing

Contributions welcome! See the [architecture docs](docs/ARCHITECTURE.md) for system design details.

**Areas for improvement**:
- Add unit tests for agents
- Implement real nutrition database
- Add recipe caching
- Parallel LLM calls for better performance

## Known Issues

- **Response time**: 30s is still slow for demos (inherent to multiple LLM calls)
- **No authentication**: Not production-ready without user accounts

## License

MIT

## Authors

**Brandon Qin** - [GitHub](https://github.com/brooondooon)

## Acknowledgments

**Technologies**:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration
- [Tavily](https://tavily.com) - Search API
- [OpenAI](https://openai.com) - GPT-3.5-turbo
- [Shadcn UI](https://ui.shadcn.com) - Component library
- [Next.js](https://nextjs.org) - React framework
- [FastAPI](https://fastapi.tiangolo.com) - Python web framework
