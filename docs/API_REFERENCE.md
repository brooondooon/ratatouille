# Ratatouille API Reference

Complete REST API documentation for the Ratatouille backend.

**Base URL**: `http://localhost:8000`

**Interactive Docs**: http://localhost:8000/docs

---

## Endpoints

### POST /api/chat

Primary conversational endpoint for recipe requests and follow-up questions.

**Request Body**:
```json
{
  "message": "I want to learn pan sauces for beginners",
  "is_follow_up": false,
  "excluded_urls": []
}
```

**Parameters**:
- `message` (string, required): User's cooking request or question
- `is_follow_up` (boolean, optional): Whether this is a follow-up question (default: false)
- `excluded_urls` (array, optional): List of recipe URLs to exclude from results

**Response (Recipe Request)**:
```json
{
  "reply": "I found 3 great recipes for learning pan sauces. Check them out below!",
  "recipes": [
    {
      "recipe": {
        "title": "Steak with Red Wine Pan Sauce",
        "url": "https://example.com/recipe",
        "source": "Example Site",
        "author": "Chef Name",
        "published_date": "2024-01-15",
        "difficulty": "intermediate",
        "time_estimate": "45 minutes"
      },
      "reasoning": "This recipe is perfect for your learning goals...",
      "technique_highlights": [
        "Pan deglazing with wine",
        "Butter emulsion (mounting)",
        "Temperature control"
      ],
      "nutrition": {
        "calories": 450,
        "protein_g": 25,
        "carbs_g": 35,
        "fat_g": 18,
        "fiber_g": 5,
        "sodium_mg": 600,
        "servings": 4,
        "disclaimer": "Estimated values - actual nutrition may vary"
      },
      "score": 87.5
    }
    // ... 2 more recipes
  ],
  "metadata": {
    "is_follow_up": false,
    "extracted_intent": {
      "learning_goal": "pan sauces",
      "skill_level": "beginner",
      "dietary_restrictions": [],
      "constraints": []
    },
    "tavily_calls": 5,
    "llm_calls": 12,
    "retry_count": 0,
    "processing_time_ms": 31200,
    "errors": []
  }
}
```

**Response (Follow-up Question)**:
```json
{
  "reply": "To make your pan sauce less acidic, try adding a pinch of sugar...",
  "recipes": [],
  "metadata": {
    "is_follow_up": true,
    "processing_time_ms": 850
  }
}
```

**Status Codes**:
- `200` - Success
- `400` - Invalid request (e.g., empty message)
- `422` - Validation error
- `500` - Server error

**Performance**:
- Recipe requests: 30-32 seconds
- Follow-up questions: <1 second

**Example Usage**:

```bash
# Recipe request
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to learn pan sauces for beginners",
    "is_follow_up": false
  }'

# Follow-up question
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "How do I prevent my pan sauce from breaking?",
    "is_follow_up": true
  }'

# Exclude previously seen recipes
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I want to learn pan sauces",
    "is_follow_up": false,
    "excluded_urls": [
      "https://example.com/recipe1",
      "https://example.com/recipe2"
    ]
  }'
```

---

### POST /api/recommend

Structured recipe recommendation endpoint (legacy format).

**Request Body**:
```json
{
  "learning_goal": "pan sauces",
  "skill_level": "intermediate",
  "dietary_restrictions": ["vegetarian"]
}
```

**Parameters**:
- `learning_goal` (string, required): Cooking technique or dish to learn
- `skill_level` (string, required): `"beginner"` | `"intermediate"` | `"advanced"`
- `dietary_restrictions` (array, optional): List of restrictions (e.g., `["vegetarian", "gluten-free"]`)

**Response**:
Same format as `/api/chat` recipe response

**Example**:
```bash
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "learning_goal": "knife skills for vegetables",
    "skill_level": "beginner",
    "dietary_restrictions": []
  }'
```

---

### POST /api/extract

Extract full recipe content from a URL using Tavily Extract API.

**Request Body**:
```json
{
  "url": "https://www.foodnetwork.com/recipes/recipe-name"
}
```

**Parameters**:
- `url` (string, required): Recipe URL to extract

**Response**:
```json
{
  "content": "# Recipe Title\n\n## Ingredients\n- 1 lb chicken...",
  "raw_content": "Full extracted HTML/text content"
}
```

**Error Responses**:

**403 Forbidden** - Site blocks automated access:
```json
{
  "detail": "This recipe site blocks automated access. Please visit the recipe directly using the link button."
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Failed to extract recipe content from URL"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/extract \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.foodnetwork.com/recipes/food-network-kitchen/steak-with-red-wine-shallot-sauce-recipe-1972846"
  }'
```

**Known Issues**:
- Tavily Extract API sometimes misses ingredient lists (see `TAVILY_BUG_REPORT.md`)
- Some sites block automated access (CookingClassy, FloraAndVino, etc.)

---

### POST /api/cook-guide

Generate interactive step-by-step cooking guide from recipe content.

**Request Body**:
```json
{
  "recipe_content": "# Steak with Pan Sauce\n\n## Ingredients...",
  "skill_level": "intermediate",
  "learning_focus": "pan sauces"
}
```

**Parameters**:
- `recipe_content` (string, required): Full recipe text (from extract endpoint)
- `skill_level` (string, required): User's skill level
- `learning_focus` (string, required): What technique they're learning

**Response**:
```json
{
  "title": "Master Pan Sauce with Red Wine Steak",
  "estimated_time": "45 minutes",
  "difficulty": "intermediate",
  "xp_reward": 100,
  "steps": [
    {
      "step_number": 1,
      "title": "Prep and Season Steak",
      "instruction": "Pat steak dry with paper towels. Season generously with salt and pepper...",
      "duration_minutes": 5,
      "key_technique": "proper seasoning",
      "tips": ["Room temperature meat sears better", "Don't skip the drying step"],
      "timer_suggested": false
    },
    {
      "step_number": 2,
      "title": "Sear the Steak",
      "instruction": "Heat pan over medium-high heat. Add oil and wait for shimmer...",
      "duration_minutes": 8,
      "key_technique": "pan searing",
      "tips": ["Don't move the steak while searing", "Listen for the sizzle"],
      "timer_suggested": true
    }
    // ... more steps
  ],
  "ingredients": [
    {
      "item": "New York strip steak",
      "amount": "1 lb",
      "preparation": "room temperature"
    }
    // ... more ingredients
  ]
}
```

**Example**:
```bash
# First extract recipe
CONTENT=$(curl -s -X POST http://localhost:8000/api/extract \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/recipe"}' | jq -r '.content')

# Then generate cooking guide
curl -X POST http://localhost:8000/api/cook-guide \
  -H "Content-Type: application/json" \
  -d "{
    \"recipe_content\": \"$CONTENT\",
    \"skill_level\": \"intermediate\",
    \"learning_focus\": \"pan sauces\"
  }"
```

---

## Data Models

### RecipeCard

```typescript
{
  recipe: {
    title: string;
    url: string;
    source: string;
    author: string;
    published_date: string;
    difficulty: "beginner" | "intermediate" | "advanced";
    time_estimate: string;
  };
  reasoning: string;
  technique_highlights: string[];
  nutrition: {
    calories: number;
    protein_g: number;
    carbs_g: number;
    fat_g: number;
    fiber_g: number;
    sodium_mg: number;
    servings: number;
    disclaimer: string;
  };
  score: number;
}
```

### Metadata

```typescript
{
  is_follow_up: boolean;
  extracted_intent?: {
    learning_goal: string;
    skill_level: string;
    dietary_restrictions: string[];
    constraints: string[];
  };
  tavily_calls: number;
  llm_calls: number;
  retry_count: number;
  processing_time_ms: number;
  errors: string[];
}
```

---

## Rate Limits

No built-in rate limiting. Limited by:
- OpenAI API: ~3500 requests/min
- Tavily API: Depends on plan (free tier: 1000 requests/month)

Recommended: Add rate limiting for production use.

---

## Error Handling

### Standard Error Response

```json
{
  "detail": "Error message here"
}
```

### Common Errors

| Code | Error | Cause |
|------|-------|-------|
| 400 | Bad Request | Missing required fields, invalid format |
| 401 | Unauthorized | Invalid API keys (OpenAI/Tavily) |
| 403 | Forbidden | Recipe site blocks access |
| 422 | Validation Error | Invalid parameter types |
| 500 | Internal Server Error | LLM failures, network issues |
| 504 | Gateway Timeout | Request exceeded 60s timeout |

### Retry Logic

The system automatically retries on insufficient results:
- Trigger: < 2 recipes found
- Max retries: 2
- Strategy: Broader search queries

No retry on API failures (e.g., 401, 403).

---

## Authentication

Currently no authentication required. For production:
- Add API key authentication
- Implement user accounts
- Track usage per user

---

## CORS Configuration

CORS is enabled for all origins:

```python
allow_origins=["*"]
```

For production, restrict to specific frontend domains:

```python
allow_origins=["https://your-frontend.vercel.app"]
```

---

## Performance Optimization

### Caching

No caching implemented. Recommendations:
- Cache recipe search results (1 hour TTL)
- Cache parsed recipes (24 hour TTL)
- Use Redis for distributed caching

### Parallelization

Currently sequential LLM calls. Can optimize:
- Batch personalization reasoning (3 calls → 1 call)
- Parallel nutrition estimation
- Async Tavily searches

### Monitoring

Add monitoring for:
- Request latency (p50, p95, p99)
- Error rates by endpoint
- API cost per request
- Cache hit rates

---

## Cost Tracking

Metadata includes API call counts:

```json
{
  "tavily_calls": 5,
  "llm_calls": 12
}
```

Estimated cost per request:
- Tavily: 5 calls × $0.001 = $0.005
- OpenAI: ~12k tokens × $0.001/1k = $0.012
- **Total**: ~$0.017

---

## Development

### Interactive API Docs

FastAPI provides auto-generated docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Testing Endpoints

Use the `/docs` interface for quick testing, or:

```bash
# Test with curl
bash scripts/test_api.sh

# Test with Python
python scripts/test_api.py
```

---

## Changelog

### v1.1 (Current)
- Removed Technique Validator for performance (50s → 30s)
- Limited to 5 recipes instead of 10
- Added excluded_urls parameter

### v1.0
- Initial release with 5-agent system
- Full recipe workflow
- Tavily integration
