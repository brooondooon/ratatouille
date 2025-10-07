// API Types matching backend response

export interface Recipe {
  title: string
  url: string
  source: string
  author: string
  published_date: string
  difficulty: "beginner" | "intermediate" | "advanced"
  time_estimate: string
  ingredients: string[]
  instructions: string[]
}

export interface Nutrition {
  calories: number | null
  protein_g: number | null
  carbs_g: number | null
  fat_g: number | null
  fiber_g: number | null
  sodium_mg: number | null
  servings: number
  disclaimer: string
}

export interface RecipeCard {
  recipe: Recipe
  reasoning: string
  technique_highlights: string[]
  nutrition: Nutrition
  score: number
}

export interface RecommendationResponse {
  recipes: RecipeCard[]
  comparison: {
    recipe_1_focus: string
    recipe_2_focus: string
    shared_techniques: string[]
  } | null
  metadata: {
    tavily_calls: number
    llm_calls: number
    retry_count: number
    processing_time_ms: number
    errors: string[]
  }
}

export interface RecommendationRequest {
  learning_goal: string
  skill_level: "beginner" | "intermediate" | "advanced"
  dietary_restrictions: string[]
}

// Chat API types
export interface ChatRequest {
  message: string
  is_follow_up?: boolean
}

export interface ChatResponse {
  reply: string
  recipes: RecipeCard[]
  metadata: {
    extracted_intent: {
      learning_goal: string
      skill_level: string
      dietary_restrictions: string[]
      constraints: string[]
    }
    tavily_calls: number
    llm_calls: number
    retry_count: number
    processing_time_ms: number
    errors: string[]
  }
}

// Message types for chat history
export interface Message {
  role: "user" | "assistant"
  content: string
  recipes?: RecipeCard[]
}

// Agent progress tracking
export interface AgentStep {
  label: string
  status: "pending" | "running" | "complete"
}
