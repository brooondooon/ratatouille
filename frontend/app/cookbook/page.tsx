"use client"

import { Navigation } from "@/components/Navigation"
import { RecipeCard } from "@/components/RecipeCard"
import { useState, useEffect } from "react"
import type { RecipeCard as RecipeCardType } from "@/lib/types"

export default function CookbookPage() {
  const [savedRecipes, setSavedRecipes] = useState<RecipeCardType[]>([])

  useEffect(() => {
    // Load saved recipes from localStorage
    const loadSavedRecipes = () => {
      const saved = JSON.parse(localStorage.getItem('savedRecipes') || '[]')
      setSavedRecipes(saved)
    }

    loadSavedRecipes()

    // Listen for storage changes (when recipes are saved/unsaved)
    window.addEventListener('storage', loadSavedRecipes)

    // Also poll occasionally to catch same-tab changes
    const interval = setInterval(loadSavedRecipes, 1000)

    return () => {
      window.removeEventListener('storage', loadSavedRecipes)
      clearInterval(interval)
    }
  }, [])

  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="space-y-8">
          <div className="text-center space-y-2">
            <h1 className="text-4xl font-bold">My Cookbook</h1>
            <p className="text-gray-600">
              {savedRecipes.length === 0
                ? "Save recipes by clicking the bookmark icon to see them here"
                : `${savedRecipes.length} saved ${savedRecipes.length === 1 ? 'recipe' : 'recipes'}`
              }
            </p>
          </div>

          {savedRecipes.length > 0 && (
            <div className="grid gap-6 md:grid-cols-2">
              {savedRecipes.map((recipe, index) => (
                <RecipeCard key={index} data={recipe} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
