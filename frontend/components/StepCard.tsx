"use client"

import { Badge } from "@/components/ui/badge"
import { Lightbulb } from "lucide-react"
import type { CookingStep } from "@/lib/api"

interface StepCardProps {
  step: CookingStep
  stepNumber: number
  totalSteps: number
}

export function StepCard({ step, stepNumber, totalSteps }: StepCardProps) {
  return (
    <div className="h-full w-full flex items-center justify-center">
      {/* Flashcard - Fits within viewport */}
      <div className="w-full max-h-full aspect-square bg-white rounded-2xl border-4 border-gray-300 flex flex-col overflow-hidden">
        {/* Step Header */}
        <div className="bg-black px-6 py-4">
          <div className="flex items-center justify-between mb-2">
            <Badge className="bg-white/20 text-white border-white/30 px-3 py-1 text-xs">
              Step {stepNumber} of {totalSteps}
            </Badge>
          </div>
          <h2 className="text-xl font-bold text-white leading-tight">
            {step.title}
          </h2>
        </div>

        {/* Card Content */}
        <div className="flex-1 p-8 space-y-6 overflow-y-auto bg-gradient-to-b from-white to-gray-50">
          {/* Instructions */}
          <div className="prose prose-sm max-w-none">
            <p className="text-base leading-relaxed text-gray-800">
              {step.content}
            </p>
          </div>

          {/* Chef's Tips */}
          <div className="bg-gray-100 border-2 border-gray-300 rounded-lg p-5 mt-auto">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-8 h-8 bg-black rounded-lg flex items-center justify-center">
                <Lightbulb className="w-4 h-4 text-white" />
              </div>
              <div className="flex-1">
                <h3 className="text-xs font-bold text-black mb-2 uppercase tracking-wide">
                  Chef's Tips
                </h3>
                <p className="text-sm leading-relaxed text-gray-700">
                  {step.tips}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
