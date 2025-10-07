import { Card, CardContent, CardHeader } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { ExternalLink, Clock, Star, ChevronDown, Bookmark, ChefHat } from "lucide-react"
import type { RecipeCard as RecipeCardType } from "@/lib/types"
import Image from "next/image"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"

interface RecipeCardProps {
  data: RecipeCardType
  compact?: boolean
}

const difficultyStars = {
  beginner: 1,
  intermediate: 2,
  advanced: 3
}

export function RecipeCard({ data, compact = false }: RecipeCardProps) {
  const { recipe, reasoning, technique_highlights, nutrition } = data
  const stars = difficultyStars[recipe.difficulty]
  const [instructionsOpen, setInstructionsOpen] = useState(false)
  const [isSaved, setIsSaved] = useState(false)
  const router = useRouter()

  // Check if recipe is saved on mount
  useEffect(() => {
    const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes') || '[]')
    setIsSaved(savedRecipes.some((r: RecipeCardType) => r.recipe.url === recipe.url))
  }, [recipe.url])

  const toggleSave = () => {
    const savedRecipes = JSON.parse(localStorage.getItem('savedRecipes') || '[]')

    if (isSaved) {
      // Remove from saved
      const filtered = savedRecipes.filter((r: RecipeCardType) => r.recipe.url !== recipe.url)
      localStorage.setItem('savedRecipes', JSON.stringify(filtered))
      setIsSaved(false)
    } else {
      // Add to saved
      savedRecipes.push(data)
      localStorage.setItem('savedRecipes', JSON.stringify(savedRecipes))
      setIsSaved(true)
    }
  }

  const handleLetsCook = () => {
    // Navigate to cook page with recipe URL
    router.push(`/cook?url=${encodeURIComponent(recipe.url)}`)
  }

  return (
    <Card className="w-full min-h-[500px] flex flex-col relative overflow-hidden">
      {/* Top decorative line */}
      <div className="absolute top-0 left-0 right-0 h-2">
        <Image
          src="/border-assets/Line-top.svg"
          alt=""
          fill
          className="object-cover"
        />
      </div>

      <CardHeader className="pt-8 space-y-3">
        {/* Title with emoji and action icons */}
        <div className="flex items-start gap-2">
          <h2 className="text-2xl font-bold leading-tight flex items-start gap-2 flex-1">
            <span className="text-2xl">🍳</span>
            <span className="flex-1">{recipe.title}</span>
          </h2>
          <div className="flex gap-1 shrink-0">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => window.open(recipe.url, '_blank')}
              className="h-8 w-8"
              title="View original recipe"
            >
              <ExternalLink className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleSave}
              className="h-8 w-8"
              title={isSaved ? "Unsave recipe" : "Save recipe"}
            >
              <Bookmark className={`h-5 w-5 ${isSaved ? 'fill-current' : ''}`} />
            </Button>
          </div>
        </div>

        {/* Metadata row */}
        <div className="flex flex-wrap items-center gap-x-3 gap-y-2 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <span className="font-medium">Difficulty:</span>
            <div className="flex">
              {Array.from({ length: 5 }).map((_, i) => (
                <Star
                  key={i}
                  className={`w-3 h-3 ${
                    i < stars ? "fill-black stroke-black" : "stroke-black fill-white"
                  }`}
                />
              ))}
            </div>
            <span className="ml-1 capitalize">{recipe.difficulty}</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="w-3 h-3" />
            <span>{recipe.time_estimate}</span>
          </div>
          <span className="text-xs">|</span>
          <span>{recipe.source}</span>
        </div>
      </CardHeader>

      <CardContent className="flex-1 space-y-6 pb-6">
        {/* Divider */}
        <div className="h-px bg-black w-full" />

        {/* Why This Recipe */}
        <div className="space-y-2">
          <h3 className="text-base font-semibold flex items-center gap-2">
            <span>🎯</span>
            Why This Recipe:
          </h3>
          <p className="text-sm leading-relaxed text-foreground/90">
            {reasoning}
          </p>
        </div>

        {/* Techniques You'll Learn */}
        <div className="space-y-2">
          <h3 className="text-base font-semibold flex items-center gap-2">
            <span>🔥</span>
            Techniques You'll Learn:
          </h3>
          <ul className="space-y-1">
            {technique_highlights.map((technique, index) => (
              <li key={index} className="flex items-start gap-2 text-sm">
                <span className="mt-1 text-black">•</span>
                <span className="flex-1">{technique}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Ingredients */}
        {recipe.ingredients && recipe.ingredients.length > 0 && (
          <div className="space-y-2">
            <h3 className="text-base font-semibold flex items-center gap-2">
              <span>🥘</span>
              Ingredients:
            </h3>
            <ul className="space-y-1">
              {recipe.ingredients.map((ingredient, index) => (
                <li key={index} className="flex items-start gap-2 text-sm">
                  <span className="mt-1 text-black">•</span>
                  <span className="flex-1">{ingredient}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Instructions - Collapsible */}
        {recipe.instructions && recipe.instructions.length > 0 && (
          <Collapsible open={instructionsOpen} onOpenChange={setInstructionsOpen}>
            <div className="space-y-2">
              <CollapsibleTrigger asChild>
                <button className="w-full text-left">
                  <h3 className="text-base font-semibold flex items-center gap-2 hover:text-foreground/80 transition-colors">
                    <span>📝</span>
                    Instructions:
                    <ChevronDown
                      className={`w-4 h-4 transition-transform ml-auto ${
                        instructionsOpen ? "rotate-180" : ""
                      }`}
                    />
                  </h3>
                </button>
              </CollapsibleTrigger>
              <CollapsibleContent className="space-y-2">
                <ol className="space-y-2">
                  {recipe.instructions.map((instruction, index) => (
                    <li key={index} className="flex items-start gap-2 text-sm">
                      <span className="font-medium min-w-[1.5rem]">{index + 1}.</span>
                      <span className="flex-1">{instruction}</span>
                    </li>
                  ))}
                </ol>
              </CollapsibleContent>
            </div>
          </Collapsible>
        )}

        {/* Nutrition */}
        {nutrition.calories && (
          <div className="space-y-2">
            <h3 className="text-base font-semibold flex items-center gap-2">
              <span>🥗</span>
              Nutrition (per serving):
            </h3>
            <div className="flex flex-wrap gap-x-4 gap-y-1 text-sm">
              <span className="font-medium">{nutrition.calories} cal</span>
              {nutrition.protein_g && <span>{nutrition.protein_g}g protein</span>}
              {nutrition.carbs_g && <span>{nutrition.carbs_g}g carbs</span>}
              {nutrition.fat_g && <span>{nutrition.fat_g}g fat</span>}
              {nutrition.fiber_g && <span>{nutrition.fiber_g}g fiber</span>}
            </div>
            <p className="text-xs text-muted-foreground italic">
              {nutrition.disclaimer}
            </p>
          </div>
        )}

        {/* Divider */}
        <div className="h-px bg-black w-full" />

        {/* Let's Cook Button */}
        <Button
          variant="default"
          className="w-full bg-black hover:bg-black/90"
          onClick={handleLetsCook}
        >
          <ChefHat className="w-4 h-4 mr-2" />
          Let's cook!
        </Button>
      </CardContent>

      {/* Bottom decorative line */}
      <div className="absolute bottom-0 left-0 right-0 h-2">
        <Image
          src="/border-assets/Line-bottom.svg"
          alt=""
          fill
          className="object-cover"
        />
      </div>
    </Card>
  )
}
