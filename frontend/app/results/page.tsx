"use client"

import { useState, useEffect, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { RecipeCard } from "@/components/RecipeCard"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Loader2 } from "lucide-react"
import type { RecommendationResponse, RecommendationRequest } from "@/lib/types"
import { cn } from "@/lib/utils"
import { fetchRecipes as apiFetchRecipes, APIError } from "@/lib/api"

const AGENT_STEPS = [
  { label: "Planning search...", agent: "Research Planner" },
  { label: "Hunting recipes...", agent: "Recipe Hunter" },
  { label: "Validating techniques...", agent: "Technique Validator" },
  { label: "Personalizing for you...", agent: "Personalization" },
  { label: "Adding nutrition...", agent: "Nutrition Analyzer" }
]

function ResultsContent() {
  const searchParams = useSearchParams()
  const router = useRouter()

  const [isLoading, setIsLoading] = useState(true)
  const [loadingStep, setLoadingStep] = useState(0)
  const [data, setData] = useState<RecommendationResponse | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activeCard, setActiveCard] = useState(0)
  const [hasFetched, setHasFetched] = useState(false)

  useEffect(() => {
    if (hasFetched) return // Only fetch once
    const fetchRecipes = async () => {
      const learningGoal = searchParams.get("learning_goal")
      const skillLevel = searchParams.get("skill_level") as "beginner" | "intermediate" | "advanced"
      const dietaryStr = searchParams.get("dietary_restrictions") || ""
      const dietary_restrictions = dietaryStr ? dietaryStr.split(",") : []

      if (!learningGoal || !skillLevel) {
        router.push("/")
        return
      }

      // Simulate agent progress (actual API call takes 30-45s)
      const progressInterval = setInterval(() => {
        setLoadingStep(prev => Math.min(prev + 1, AGENT_STEPS.length - 1))
      }, 8000) // Update every 8 seconds

      try {
        const requestBody: RecommendationRequest = {
          learning_goal: learningGoal,
          skill_level: skillLevel,
          dietary_restrictions
        }

        const result = await apiFetchRecipes(requestBody)

        clearInterval(progressInterval)
        setData(result)
        setIsLoading(false)
        setHasFetched(true)
      } catch (err) {
        clearInterval(progressInterval)
        if (err instanceof APIError) {
          setError(err.message)
        } else {
          setError("Failed to fetch recipes")
        }
        setIsLoading(false)
        setHasFetched(true)
      }
    }

    fetchRecipes().catch(() => {})
  }, [searchParams, router])

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-6">
        <div className="text-center space-y-8 max-w-md w-full">
          {/* Animated Chef Hat */}
          <div className="flex justify-center">
            <div className="w-24 h-24 bg-black rounded-full flex items-center justify-center animate-pulse">
              <span className="text-5xl">🐀</span>
            </div>
          </div>

          {/* Title */}
          <h2 className="text-2xl font-bold">
            Finding your recipes...
          </h2>

          {/* Progress Indicator */}
          <div className="space-y-4">
            <div className="flex justify-center gap-2">
              {AGENT_STEPS.map((_, index) => (
                <div
                  key={index}
                  className={cn(
                    "w-3 h-3 rounded-full border-2 border-black transition-all",
                    index <= loadingStep ? "bg-black" : "bg-white"
                  )}
                />
              ))}
            </div>
            <p className="text-sm text-muted-foreground">
              Step {loadingStep + 1} of {AGENT_STEPS.length}
            </p>
            <p className="text-base font-medium flex items-center justify-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              {AGENT_STEPS[loadingStep].label}
            </p>
          </div>
        </div>
      </div>
    )
  }

  // Error State
  if (error) {
    return (
      <div className="min-h-screen bg-white px-6 py-8">
        <div className="max-w-md mx-auto space-y-6 text-center">
          <div className="text-6xl">😕</div>
          <h2 className="text-2xl font-bold">Oops! Something went wrong</h2>
          <p className="text-muted-foreground">{error}</p>
          <Button onClick={() => router.push("/")} variant="default">
            <ArrowLeft className="mr-2" />
            Try Again
          </Button>
        </div>
      </div>
    )
  }

  // No Results
  if (!data || data.recipes.length === 0) {
    return (
      <div className="min-h-screen bg-white px-6 py-8">
        <div className="max-w-md mx-auto space-y-6 text-center">
          <div className="text-6xl">😕</div>
          <h2 className="text-2xl font-bold">No recipes found</h2>
          <p className="text-muted-foreground">
            Try broadening your search, removing dietary filters, or trying a different skill level.
          </p>
          <Button onClick={() => router.push("/")} variant="default">
            <ArrowLeft className="mr-2" />
            Start Over
          </Button>
        </div>
      </div>
    )
  }

  // Success State - Show Carousel
  return (
    <div className="min-h-screen bg-white px-6 py-8 pb-20 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => router.push("/")}
        >
          <ArrowLeft />
        </Button>
        <h1 className="text-xl font-bold">Your Recipes</h1>
        <div className="w-10" /> {/* Spacer */}
      </div>

      {/* Carousel */}
      <div className="flex-1 flex flex-col space-y-6">
        {/* Cards - Horizontal Scroll */}
        <div className="flex gap-4 overflow-x-auto snap-x snap-mandatory pb-4 scrollbar-hide">
          {data.recipes.map((recipe, index) => (
            <div
              key={index}
              className="flex-shrink-0 w-[85vw] snap-center"
              onTouchStart={() => setActiveCard(index)}
            >
              <RecipeCard data={recipe} />
            </div>
          ))}
        </div>

        {/* Progress Dots */}
        <div className="flex justify-center gap-2">
          {data.recipes.map((_, index) => (
            <button
              key={index}
              onClick={() => {
                // Scroll to card
                const container = document.querySelector(".overflow-x-auto")
                const card = container?.children[index] as HTMLElement
                card?.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" })
                setActiveCard(index)
              }}
              className={cn(
                "w-2 h-2 rounded-full transition-all",
                index === activeCard ? "bg-black w-6" : "bg-black/30"
              )}
              aria-label={`Go to recipe ${index + 1}`}
            />
          ))}
        </div>

        {/* Metadata */}
        <div className="text-center text-xs text-muted-foreground space-y-1 pt-4">
          <p>
            Found {data.recipes.length} recipes in {(data.metadata.processing_time_ms / 1000).toFixed(1)}s
          </p>
          <p className="opacity-60">
            {data.metadata.llm_calls} AI calls • {data.metadata.tavily_calls} searches
          </p>
        </div>
      </div>
    </div>
  )
}

export default function ResultsPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-white flex items-center justify-center">
      <Loader2 className="animate-spin" />
    </div>}>
      <ResultsContent />
    </Suspense>
  )
}
