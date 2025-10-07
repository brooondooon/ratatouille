"use client"

import { useState, useEffect, useCallback, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Loader2, ChevronLeft, ChevronRight } from "lucide-react"
import { extractRecipe, generateCookGuide, APIError, type CookGuide } from "@/lib/api"
import { Timer } from "@/components/Timer"
import { IngredientList } from "@/components/IngredientList"
import { StepCard } from "@/components/StepCard"
import { CompletionCard } from "@/components/CompletionCard"
import useEmblaCarousel from "embla-carousel-react"

function CookContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [cookGuide, setCookGuide] = useState<CookGuide | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [currentStep, setCurrentStep] = useState(0)
  const [timerResetKey, setTimerResetKey] = useState(0)
  const [isTimerRunning, setIsTimerRunning] = useState(true)

  // Embla carousel setup
  const [emblaRef, emblaApi] = useEmblaCarousel({
    loop: false,
    skipSnaps: false
  })

  // Sync carousel with current step
  useEffect(() => {
    if (!emblaApi) return

    const onSelect = () => {
      const index = emblaApi.selectedScrollSnap()
      setCurrentStep(index)
      setTimerResetKey(prev => prev + 1)
    }

    emblaApi.on("select", onSelect)
    return () => {
      emblaApi.off("select", onSelect)
    }
  }, [emblaApi])

  // Navigation handlers
  const scrollPrev = useCallback(() => {
    if (emblaApi) emblaApi.scrollPrev()
  }, [emblaApi])

  const scrollNext = useCallback(() => {
    if (emblaApi) emblaApi.scrollNext()
  }, [emblaApi])

  const canScrollPrev = emblaApi?.canScrollPrev() ?? false
  const canScrollNext = emblaApi?.canScrollNext() ?? false

  useEffect(() => {
    const url = searchParams.get("url")

    if (!url) {
      router.push("/")
      return
    }

    const fetchCookGuide = async () => {
      try {
        // Step 1: Extract recipe
        const extractResult = await extractRecipe(url)

        // Step 2: Generate cook guide with LLM
        // Get user preferences from localStorage or use defaults
        const skillLevel = localStorage.getItem("skillLevel") || "intermediate"
        const learningGoal = localStorage.getItem("learningGoal") || "improve cooking techniques"

        const guide = await generateCookGuide(
          extractResult.raw_content,
          skillLevel,
          learningGoal
        )

        setCookGuide(guide)
        setIsLoading(false)
      } catch (err) {
        if (err instanceof APIError) {
          setError(err.message)
        } else {
          setError("Failed to generate cooking guide")
        }
        setIsLoading(false)
      }
    }

    fetchCookGuide()
  }, [searchParams, router])

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-6">
        <div className="text-center space-y-6">
          <div className="w-32 h-32 flex items-center justify-center mx-auto">
            <video
              autoPlay
              loop
              muted
              playsInline
              className="w-full h-full"
            >
              <source src="/loading-animation.mp4" type="video/mp4" />
            </video>
          </div>
          <h2 className="text-2xl font-bold text-black">
            Crafting the perfect plan…
          </h2>
          <p className="text-sm text-muted-foreground max-w-md">
            Ratatouille is working hard to organize the recipe and provide his expert tips
          </p>
        </div>
      </div>
    )
  }

  // Error State
  if (error) {
    const recipeUrl = searchParams.get("url")
    const isAccessDeniedError = error.includes("blocks automated access")

    return (
      <div className="min-h-screen bg-white px-6 py-8">
        <div className="max-w-2xl mx-auto space-y-6 text-center">
          <div className="text-6xl">{isAccessDeniedError ? "🔒" : "😕"}</div>
          <h2 className="text-2xl font-bold">
            {isAccessDeniedError ? "Recipe Site Blocked" : "Oops! Something went wrong"}
          </h2>
          <p className="text-muted-foreground">{error}</p>
          <div className="flex gap-3 justify-center">
            <Button onClick={() => router.back()} variant="outline">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Go Back
            </Button>
            {recipeUrl && isAccessDeniedError && (
              <Button onClick={() => window.open(recipeUrl, '_blank')} variant="default">
                Visit Recipe Site
              </Button>
            )}
          </div>
        </div>
      </div>
    )
  }

  if (!cookGuide) return null

  const totalSlides = cookGuide.steps.length + 1 // steps + completion card
  const isOnCompletionCard = currentStep === cookGuide.steps.length

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b z-20">
        <div className="px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => router.back()}
            >
              <ArrowLeft className="h-5 w-5" />
            </Button>
            <div>
              <h1 className="text-lg font-bold text-black">
                Interactive Cooking Guide
              </h1>
              <p className="text-xs text-muted-foreground">
                Step {Math.min(currentStep + 1, cookGuide.steps.length)} of {cookGuide.steps.length}
              </p>
            </div>
          </div>
          <Timer
            isRunning={isTimerRunning && !isOnCompletionCard}
            key={timerResetKey}
          />
        </div>
      </div>

      {/* Ingredient List Overlay */}
      <IngredientList ingredients={cookGuide.ingredients} />

      {/* Main Layout - Centered Flashcard */}
      <div className="flex-1 flex items-center justify-center overflow-hidden">
        <div className="flex flex-col items-center gap-6 max-w-[600px] w-full px-4">
          {/* Carousel Container */}
          <div className="overflow-hidden w-full" ref={emblaRef}>
            <div className="flex">
              {/* Step Cards */}
              {cookGuide.steps.map((step, index) => (
                <div key={index} className="flex-[0_0_100%] min-w-0 flex items-center justify-center">
                  <div className="w-[500px] h-[500px]">
                    <StepCard
                      step={step}
                      stepNumber={index + 1}
                      totalSteps={cookGuide.steps.length}
                    />
                  </div>
                </div>
              ))}

              {/* Completion Card */}
              <div className="flex-[0_0_100%] min-w-0 flex items-center justify-center">
                <div className="w-[500px] h-[500px]">
                  <CompletionCard
                    techniques={cookGuide.techniques_learned}
                    xpEarned={cookGuide.xp_earned}
                    badges={cookGuide.badges}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Navigation Controls - Under flashcard */}
          <div className="flex gap-2">
            {Array.from({ length: totalSlides }).map((_, index) => (
              <button
                key={index}
                onClick={() => emblaApi?.scrollTo(index)}
                className={`h-2 rounded-full transition-all duration-300 ${
                  index === currentStep
                    ? "w-8 bg-black"
                    : "w-2 bg-gray-300 hover:bg-gray-400"
                }`}
                aria-label={`Go to step ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default function CookPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-white flex items-center justify-center">
        <Loader2 className="animate-spin w-12 h-12 text-black" />
      </div>
    }>
      <CookContent />
    </Suspense>
  )
}
