"use client"

import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Sparkles, Trophy, ArrowLeft } from "lucide-react"
import { useRouter } from "next/navigation"

interface CompletionCardProps {
  techniques: string[]
  xpEarned: number
  badges: string[]
}

export function CompletionCard({ techniques, xpEarned, badges }: CompletionCardProps) {
  const router = useRouter()

  return (
    <div className="h-full w-full flex items-center justify-center">
      {/* Flashcard - Fits within viewport */}
      <div className="w-full max-h-full aspect-square bg-white rounded-2xl border-4 border-gray-300 flex flex-col overflow-hidden">
        {/* Celebration Header */}
        <div className="bg-black px-8 py-8 text-center">
          <div className="text-5xl mb-3 animate-bounce">🎉</div>
          <h2 className="text-2xl font-bold text-white mb-2">
            Congratulations!
          </h2>
          <p className="text-white/90 text-base">
            You've completed this recipe
          </p>
        </div>

        {/* Content */}
        <div className="flex-1 p-6 space-y-6 overflow-y-auto bg-gradient-to-b from-white to-gray-50">
          {/* XP Earned */}
          <div className="bg-black rounded-lg p-4">
            <div className="flex items-center justify-center gap-3">
              <Sparkles className="w-6 h-6 text-white animate-pulse" />
              <div className="text-center">
                <div className="text-3xl font-bold text-white mb-1">
                  +{xpEarned} XP
                </div>
                <div className="text-white/90 text-xs font-medium">
                  Experience Earned
                </div>
              </div>
              <Sparkles className="w-6 h-6 text-white animate-pulse" />
            </div>
          </div>

          {/* Badges Earned */}
          {badges.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-gray-900 flex items-center gap-2">
                <Trophy className="w-4 h-4 text-black" />
                Badges Earned
              </h3>
              <div className="flex flex-wrap gap-2">
                {badges.map((badge, index) => (
                  <Badge
                    key={index}
                    className="bg-black text-white border-black px-3 py-1 text-xs font-semibold"
                  >
                    🏆 {badge}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Techniques Learned */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-gray-900">
              🎓 What You Learned
            </h3>
            <div className="bg-white rounded-lg p-4 border-2 border-gray-200">
              <ul className="space-y-2">
                {techniques.map((technique, index) => (
                  <li key={index} className="flex items-start gap-2">
                    <span className="flex-shrink-0 w-5 h-5 bg-green-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                      ✓
                    </span>
                    <span className="text-gray-800 text-sm leading-relaxed">
                      {technique}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Action Button */}
          <Button
            onClick={() => router.back()}
            className="w-full bg-black hover:bg-gray-800 text-white py-4 text-base font-semibold transition-all duration-200"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            Done Cooking
          </Button>
        </div>
      </div>
    </div>
  )
}
