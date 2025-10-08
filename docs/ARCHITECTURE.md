# Ratatouille Architecture

## System Overview

Ratatouille is a multi-agent recipe recommendation system built with LangGraph that helps users learn cooking techniques through personalized recipe suggestions. The system uses 4 specialized agents that coordinate through shared state to deliver high-quality, educational recipe recommendations.

## High-Level Architecture

```
User Input → Intent Extractor → Multi-Agent Workflow
                                       ↓
                    ┌──────────────────┴──────────────────┐
                    │                                     │
            Research Planner                      Recipe Hunter
                    │                                     │
                    └──────────────┬────────────────────┘
                                   ↓
                    ┌──────────────┴────────────────┐
                    │                               │
            Personalization Engine        Nutrition Analyzer
                    │                               │
                    └──────────────┬────────────────┘
                                   ↓
                            Final Response
```

## Agent System

### Agent 1: Research Planner
**File**: `backend/agents/research_planner.py`

**Responsibility**: Strategic query generation and search planning

**Inputs**:
- Learning goal (e.g., "pan sauces")
- Skill level (beginner/intermediate/advanced)
- Dietary restrictions
- Search strategy signal (`initial` or `broadened`)

**Processing**:
1. Analyzes user's learning goal and skill level
2. Generates 5 diverse search queries using GPT-3.5-turbo
3. Adapts queries if retry signal received (broader, more general terms)
4. Ensures variety in proteins, flavors, and techniques

**Outputs**:
- `search_queries`: List of 5 optimized search strings

**Key Features**:
- Adaptive behavior: Detects `search_strategy='broadened'` and generates wider queries
- Diversity enforcement: Each query uses different ingredients/proteins
- Focus on actual recipes, not technique tutorials

**Example Output**:
```python
[
  "lemon butter pan sauce chicken recipe beginner",
  "mushroom cream pan sauce steak recipe",
  "balsamic pan sauce pork recipe",
  "white wine herb pan sauce fish recipe",
  "shallot red wine pan sauce lamb recipe"
]
```

---

### Agent 2: Recipe Hunter
**File**: `backend/agents/recipe_hunter.py`

**Responsibility**: Recipe retrieval and parsing from web sources

**Inputs**:
- Search queries from Research Planner

**Processing**:
1. Executes Tavily Search API for each query
2. Retrieves top 3 results per query (max 5 queries)
3. Parses recipe snippets into structured format using GPT-3.5-turbo
4. Extracts: title, ingredients, steps, techniques, difficulty, time estimate
5. Limits to top 5 recipes total (1 per query for speed optimization)

**Outputs**:
- `raw_recipes`: List of structured recipe objects
- `tavily_calls`: Count of API calls made

**Key Features**:
- LLM-based parsing: Converts unstructured text to structured JSON
- Score tracking: Preserves Tavily relevance scores
- Error handling: Continues on individual parse failures

**Performance**:
- 5 Tavily API calls (~10s)
- 5 OpenAI parsing calls (~15s)
- Total: ~25s per request

**Example Recipe Object**:
```json
{
  "title": "Pan-Seared Chicken with Lemon Butter Sauce",
  "url": "https://example.com/recipe",
  "source": "Example Site",
  "author": "Chef Name",
  "published_date": "2024-01-15",
  "difficulty": "intermediate",
  "time_estimate": "30 minutes",
  "ingredients": ["1 lb chicken breast", "2 tbsp butter", ...],
  "steps": ["Season chicken...", "Heat pan...", ...],
  "techniques": ["pan searing", "deglazing", "butter emulsion"],
  "tavily_score": 0.85
}
```

---

### Agent 3: Personalization Engine
**File**: `backend/agents/personalization.py`

**Responsibility**: Recipe scoring, filtering, and selection

**Inputs**:
- Raw recipes from Recipe Hunter
- User skill level
- Dietary restrictions
- Excluded recipe URLs (from user's previous selections)

**Processing**:
1. **Filters** recipes by dietary restrictions
2. **Scores** each recipe on 5 dimensions (max 100 points):
   - Learning value: 30 pts (technique relevance)
   - Skill appropriateness: 25 pts (matches user level)
   - Recency: 20 pts (newer recipes preferred)
   - Tavily relevance: 15 pts
   - Technique diversity: 10 pts
3. **Selects** top 3 diverse recipes (avoids duplicates)
4. **Generates** "why this recipe" reasoning with GPT-3.5-turbo
5. **Highlights** key techniques for each recipe

**Outputs**:
- `final_cards`: 3 recipe cards with reasoning and technique highlights
- `scored_recipes`: Full list with scores for debugging

**Scoring Algorithm**:
```python
score = 0

# Learning value (max 30)
score += matches_with_relevant_techniques * 10  # up to 30

# Skill appropriateness (max 25)
skill_match_scores = {
    'beginner': {'beginner': 25, 'intermediate': 8, 'advanced': -10},
    'intermediate': {'beginner': 3, 'intermediate': 25, 'advanced': 12},
    'advanced': {'beginner': -10, 'intermediate': 8, 'advanced': 25}
}
score += skill_match_scores[user_level][recipe_difficulty]

# Recency (max 20)
if published in "2024-2025": score += 20
elif published in "2023": score += 15
elif published in "2022": score += 10
else: score += 5

# Tavily relevance (max 15)
score += tavily_score * 15

# Technique diversity (max 10)
if len(techniques) >= 3: score += 10
elif len(techniques) >= 2: score += 5
```

**Key Features**:
- Diversity enforcement: Avoids recipes with 30%+ word overlap in titles
- Dietary filtering: Keyword-based (vegetarian, vegan, gluten-free)
- Excluded URLs: Filters out recipes user has already seen

**Example Output**:
```json
{
  "recipe": {
    "title": "Pan-Seared Chicken with Lemon Butter Sauce",
    "url": "https://example.com/recipe",
    "difficulty": "intermediate",
    "time_estimate": "30 minutes"
  },
  "reasoning": "This recipe is perfect for mastering fundamental pan sauce techniques. You'll learn deglazing, reduction, and butter emulsion - three essential skills for any home cook.",
  "technique_highlights": [
    "Pan deglazing with white wine",
    "Butter emulsion (mounting butter)",
    "Temperature control for proper searing"
  ],
  "score": 87.5
}
```

---

### Agent 4: Nutrition Analyzer
**File**: `backend/agents/nutrition_analyzer.py`

**Responsibility**: Nutritional information estimation

**Inputs**:
- Final recipe cards from Personalization Engine
- Full recipe data (ingredients, servings)

**Processing**:
1. Extracts ingredients from recipe
2. Estimates servings from recipe text (defaults to 4)
3. Uses GPT-3.5-turbo to estimate nutrition per serving
4. Adds nutrition object to each recipe card

**Outputs**:
- Updated `final_cards` with nutrition data

**Estimation Approach**:
- LLM-based: Uses GPT to estimate from ingredients
- Per-serving: All values calculated per serving
- Realistic estimates: GPT trained on typical portion sizes

**Example Output**:
```json
{
  "calories": 450,
  "protein_g": 25,
  "carbs_g": 35,
  "fat_g": 18,
  "fiber_g": 5,
  "sodium_mg": 600,
  "servings": 4,
  "disclaimer": "Estimated values - actual nutrition may vary"
}
```

**Note**: For production use, this should be replaced with a nutrition database API (e.g., USDA FoodData Central, Edamam) for accurate values.

---

## LangGraph Workflow

**File**: `backend/graph.py`

### Workflow Definition

```python
Research Planner → Recipe Hunter → [Conditional Check] → Personalization → Nutrition → END
                        ↑                    ↓
                        └─────── Retry ───────┘
```

### Conditional Routing Logic

After Recipe Hunter completes, the workflow checks:

```python
def route_after_recipe_hunter(state: RecipeState) -> str:
    recipe_count = len(state['raw_recipes'])
    retry_count = state.get('retry_count', 0)
    
    # Insufficient recipes? Retry with broader search
    if recipe_count < 2 and retry_count < 2:
        state['search_strategy'] = 'broadened'
        state['retry_count'] = retry_count + 1
        return "research_planner"  # Loop back
    
    # Success or max retries - proceed
    return "personalization"
```

**Retry Behavior**:
- Trigger: < 2 recipes found
- Max retries: 2
- Signal: Sets `search_strategy='broadened'`
- Research Planner response: Generates wider, more general queries

---

## State Management

**File**: `backend/state.py`

### RecipeState Schema

```python
class RecipeState(TypedDict):
    # User inputs
    learning_goal: str              # e.g., "pan sauces"
    skill_level: str                # "beginner" | "intermediate" | "advanced"
    dietary_restrictions: List[str] # e.g., ["vegetarian"]
    excluded_urls: List[str]        # URLs to filter out
    
    # Agent coordination
    search_strategy: str            # "initial" | "broadened"
    retry_count: int                # Current retry attempt
    
    # Intermediate data
    search_queries: List[str]       # From Research Planner
    raw_recipes: List[Dict]         # From Recipe Hunter
    scored_recipes: List[Dict]      # From Personalization
    final_cards: List[Dict]         # From Personalization (enriched by Nutrition)
    
    # Metadata
    tavily_calls: int               # API call count
    llm_calls: int                  # OpenAI call count
    errors: List[str]               # Error messages
```

All agents read from and write to this shared state, enabling coordination without direct agent-to-agent communication.

---

## API Layer

**File**: `backend/app.py`

### Intent Extractor (Pre-Workflow)

Before the multi-agent workflow runs, the Intent Extractor analyzes the user's message:

```python
def extract_intent(message: str) -> Dict:
    # Uses GPT to extract:
    # - learning_goal: The cooking technique/dish
    # - skill_level: beginner/intermediate/advanced
    # - dietary_restrictions: List of restrictions
    # - constraints: Any specific requirements
```

### Workflow Execution

```python
1. User sends message → /api/chat
2. Intent Extractor parses request
3. Initialize RecipeState with extracted intent
4. Execute LangGraph workflow
5. Return final_cards to user
```

### Endpoints

**POST /api/chat**
- Primary conversation endpoint
- Detects recipe requests vs follow-up questions
- Executes full workflow for recipe requests
- Uses simple GPT call for follow-up questions

**POST /api/recommend** (Legacy)
- Structured request format
- Direct workflow execution
- Used for programmatic access

**POST /api/extract**
- Tavily Extract API wrapper
- Used by "Let's Cook" feature
- Returns full recipe content for cooking mode

**POST /api/cook-guide**
- Generates step-by-step cooking guide
- Uses GPT to create structured guide with timers
- Returns interactive cooking instructions

---

## Data Flow Example

### Full Request Trace

**User Input**: "I want to learn pan sauces for beginners"

**Step 1: Intent Extraction**
```json
{
  "learning_goal": "pan sauces",
  "skill_level": "beginner",
  "dietary_restrictions": [],
  "constraints": []
}
```

**Step 2: Research Planner**
```json
{
  "search_queries": [
    "garlic butter pan sauce chicken recipe beginner",
    "red wine shallot pan sauce steak recipe easy",
    "mushroom cream pan sauce pork recipe simple",
    "lemon herb pan sauce fish recipe novice",
    "balsamic honey pan sauce salmon recipe basic"
  ]
}
```

**Step 3: Recipe Hunter**
- Tavily search: 5 queries → 15 results
- Parse top 5 recipes → structured format
- Output: 5 recipe objects

**Step 4: Personalization Engine**
- Score 5 recipes
- Select top 3 with diversity
- Generate reasoning for each
- Output: 3 final recipe cards

**Step 5: Nutrition Analyzer**
- Estimate nutrition for 3 recipes
- Add nutrition data to cards
- Output: 3 enriched recipe cards

**Final Response**:
```json
{
  "reply": "I found 3 great recipes for learning pan sauces...",
  "recipes": [
    {
      "recipe": {...},
      "reasoning": "...",
      "technique_highlights": [...],
      "nutrition": {...},
      "score": 87.5
    },
    // 2 more recipes
  ],
  "metadata": {
    "processing_time_ms": 31200,
    "llm_calls": 12,
    "tavily_calls": 5
  }
}
```

---

## Performance Characteristics

### Latency Breakdown

Total: ~30-32 seconds

| Component | Time | LLM Calls | API Calls |
|-----------|------|-----------|-----------|
| Intent Extraction | 2s | 1 | 0 |
| Research Planner | 3s | 1 | 0 |
| Recipe Hunter | 25s | 5 | 5 (Tavily) |
| Personalization | 12s | 3 | 0 |
| Nutrition | 10s | 3 | 0 |

**Bottleneck**: Recipe Hunter (LLM parsing of 5 recipes)

### Optimization History

**Original**: 50-110 seconds (18 LLM calls)
- Had Technique Validator: 10 additional LLM calls
- Parsed 10 recipes instead of 5

**Current**: 30-32 seconds (12 LLM calls)
- Removed Technique Validator (trust Tavily relevance)
- Limited to 5 recipes (1 per query)
- Faster, but slightly lower relevance on edge cases

### Cost Per Request

- Tavily API: 5 calls × $0.001 = $0.005
- OpenAI GPT-3.5-turbo: 12 calls × ~1000 tokens avg = ~$0.012
- **Total**: ~$0.017 per request

---

## Error Handling

### Agent-Level Errors

Each agent has try/catch blocks that:
1. Log error message
2. Add to `state['errors']`
3. Return gracefully (don't crash workflow)

### Retry Mechanism

- Automatic retry on insufficient results (< 2 recipes)
- Max 2 retries to prevent infinite loops
- Broadens search strategy on each retry

### User-Facing Errors

- 403: Recipe site blocks automated access (Tavily Extract)
- 500: Internal server error (logged with details)
- Timeout: 60s max per request

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Orchestration | LangGraph | Multi-agent state management |
| LLM | OpenAI GPT-3.5-turbo | Intent extraction, parsing, reasoning |
| Search | Tavily API | Recipe search |
| Backend | FastAPI | REST API server |
| Frontend | Next.js 14 | React web application |
| UI | Shadcn UI + Tailwind | Component library |
| Language | Python 3.10+ | Backend logic |
| Language | TypeScript | Frontend type safety |

---

## Key Design Decisions

### 1. Why LangGraph?
- **State management**: Centralized RecipeState shared across agents
- **Conditional routing**: Dynamic workflow based on results
- **Observability**: Built-in logging and state inspection

### 2. Why Remove Technique Validator?
- **Performance**: Saved 20-30s (biggest bottleneck)
- **Relevance**: Was too strict, rejected valid recipes
- **Tradeoff**: Trust Tavily search ranking instead

### 3. Why Limit to 5 Recipes?
- **Speed**: 50% fewer LLM parsing calls
- **Quality**: Top 1 result per query is usually best
- **Tradeoff**: Less variety to choose from

### 4. Why GPT-3.5 Instead of GPT-4?
- **Cost**: 20x cheaper (~$0.012 vs $0.24 per request)
- **Speed**: 2-3x faster responses
- **Quality**: Sufficient for recipe parsing and reasoning

---

## Future Enhancements

### Performance
- [ ] Parallel LLM calls (batch processing)
- [ ] Recipe caching (avoid re-parsing)
- [ ] Streaming responses (show recipes as they're found)

### Accuracy
- [ ] Real nutrition database (replace LLM estimation)
- [ ] User feedback loop (improve scoring)
- [ ] Recipe deduplication (detect similar recipes)

### Features
- [ ] Difficulty progression (easier → harder recipes)
- [ ] Technique prerequisites (e.g., learn searing before pan sauces)
- [ ] Video integration (link to technique videos)
- [ ] Shopping list generation

### Scalability
- [ ] Async agent execution
- [ ] Horizontal scaling (multiple workers)
- [ ] Database for recipe caching
- [ ] Rate limiting and quotas
