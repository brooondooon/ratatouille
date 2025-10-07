# API Reference

## Base URL

```
http://localhost:8000
```

---

## Endpoints

### Health Check

**GET** `/health`

Check API status and configuration.

**Response:**
```json
{
  "status": "healthy",
  "openai_configured": true,
  "tavily_configured": true
}
```

---

### Get Recipe Recommendations

**POST** `/api/recommend`

Retrieve personalized recipe recommendations based on learning goals.

**Request Body:**
```json
{
  "learning_goal": "string",
  "skill_level": "beginner" | "intermediate" | "advanced",
  "dietary_restrictions": ["string"] // optional
}
```

**Request Example:**
```json
{
  "learning_goal": "pan sauces",
  "skill_level": "intermediate",
  "dietary_restrictions": ["vegetarian"]
}
```

**Response:** (200 OK)
```json
{
  "recipes": [
    {
      "recipe": {
        "title": "string",
        "url": "string",
        "source": "string",
        "author": "string",
        "published_date": "string",
        "difficulty": "beginner" | "intermediate" | "advanced",
        "time_estimate": "string"
      },
      "reasoning": "string",
      "technique_highlights": ["string"],
      "nutrition": {
        "calories": number,
        "protein_g": number,
        "carbs_g": number,
        "fat_g": number,
        "fiber_g": number,
        "sodium_mg": number,
        "servings": number,
        "disclaimer": "string"
      },
      "score": number
    }
  ],
  "comparison": {
    "recipe_1_focus": "string",
    "recipe_2_focus": "string",
    "shared_techniques": ["string"]
  },
  "metadata": {
    "tavily_calls": number,
    "llm_calls": number,
    "retry_count": number,
    "processing_time_ms": number,
    "errors": ["string"]
  }
}
```

**Error Responses:**

400 Bad Request - Invalid skill level
```json
{
  "detail": "Invalid skill_level. Must be one of: beginner, intermediate, advanced"
}
```

404 Not Found - No recipes found
```json
{
  "detail": "No recipes found matching your criteria. Try broadening your search or changing filters."
}
```

500 Internal Server Error
```json
{
  "detail": "Internal server error: {error_message}"
}
```

---

## Interactive Documentation

Visit `http://localhost:8000/docs` for Swagger UI with interactive API testing.
