"use client"

import { useState } from "react"
import { ChevronLeft, ChevronRight, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

interface IngredientListProps {
  ingredients: string[]
}

export function IngredientList({ ingredients }: IngredientListProps) {
  const [isCollapsed, setIsCollapsed] = useState(false)
  const [checked, setChecked] = useState<Set<number>>(new Set())

  const toggleIngredient = (index: number) => {
    const newChecked = new Set(checked)
    if (newChecked.has(index)) {
      newChecked.delete(index)
    } else {
      newChecked.add(index)
    }
    setChecked(newChecked)
  }

  if (isCollapsed) {
    return (
      <Button
        variant="ghost"
        size="icon"
        onClick={() => setIsCollapsed(false)}
        className="fixed left-4 top-1/2 -translate-y-1/2 z-30 h-12 w-10 bg-white shadow-lg border-2 border-gray-300 hover:bg-gray-50 rounded-lg transition-all duration-300"
      >
        <ChevronRight className="h-5 w-5" />
      </Button>
    )
  }

  return (
    <div className="fixed left-0 top-0 h-full w-[400px] bg-white flex flex-col shadow-2xl border-r-2 border-gray-300 z-30 transition-all duration-300 ease-in-out">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xl font-bold text-gray-900">Ingredients</h2>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsCollapsed(true)}
            className="h-8 w-8"
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
        </div>
        <p className="text-sm text-gray-600">
          {checked.size} of {ingredients.length} gathered
        </p>
      </div>

      {/* Ingredient List */}
      <div className="flex-1 overflow-y-auto p-6 space-y-3">
        {ingredients.map((ingredient, index) => {
          const isChecked = checked.has(index)
          return (
            <button
              key={index}
              onClick={() => toggleIngredient(index)}
              className={cn(
                "w-full text-left px-4 py-3 rounded-lg border-2 transition-all duration-200 ease-in-out group hover:shadow-md",
                isChecked
                  ? "bg-green-50 border-green-300 shadow-sm"
                  : "bg-white border-gray-200 hover:border-gray-300"
              )}
            >
              <div className="flex items-start gap-3">
                <div
                  className={cn(
                    "mt-0.5 flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-all duration-200",
                    isChecked
                      ? "bg-green-500 border-green-500"
                      : "bg-white border-gray-300 group-hover:border-green-400"
                  )}
                >
                  {isChecked && <Check className="h-3 w-3 text-white" />}
                </div>
                <span
                  className={cn(
                    "text-sm leading-relaxed transition-all duration-200",
                    isChecked
                      ? "text-gray-500 line-through"
                      : "text-gray-900"
                  )}
                >
                  {ingredient}
                </span>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
