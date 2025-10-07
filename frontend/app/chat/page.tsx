"use client"

import { useState } from "react"
import { Navigation } from "@/components/Navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { RecipeCard } from "@/components/RecipeCard"
import { Loader2, Send } from "lucide-react"
import { sendChatMessage, APIError } from "@/lib/api"
import type { Message, RecipeCard as RecipeCardType, AgentStep } from "@/lib/types"
import { cn } from "@/lib/utils"

// Fake agent progress - updates every 6 seconds (30s / 5 agents = 6s each)
const AGENT_STEPS: AgentStep[] = [
  { label: "Planning search", status: "pending" },
  { label: "Hunting recipes", status: "pending" },
  { label: "Validating techniques", status: "pending" },
  { label: "Personalizing for you", status: "pending" },
  { label: "Adding nutrition", status: "pending" },
]

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [recipes, setRecipes] = useState<RecipeCardType[]>([])
  const [agentSteps, setAgentSteps] = useState<AgentStep[]>(AGENT_STEPS)

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput("")
    setError(null)

    // Add user message to history
    const newUserMessage: Message = {
      role: "user",
      content: userMessage
    }
    setMessages(prev => [...prev, newUserMessage])
    setIsLoading(true)

    // Reset agent progress
    setAgentSteps(AGENT_STEPS)

    // Simulate agent progress
    const progressInterval = setInterval(() => {
      setAgentSteps(prev => {
        const nextPending = prev.findIndex(step => step.status === "pending")
        if (nextPending === -1) return prev

        return prev.map((step, i) => {
          if (i < nextPending) return { ...step, status: "complete" as const }
          if (i === nextPending) return { ...step, status: "running" as const }
          return step
        })
      })
    }, 6000) // Update every 6 seconds

    try {
      const response = await sendChatMessage({ message: userMessage })

      clearInterval(progressInterval)

      // Mark all steps complete
      setAgentSteps(prev => prev.map(step => ({ ...step, status: "complete" as const })))

      // Add assistant response
      const assistantMessage: Message = {
        role: "assistant",
        content: response.reply,
        recipes: response.recipes
      }
      setMessages(prev => [...prev, assistantMessage])

      // Only update recipes if we got new ones (not a follow-up question)
      if (response.recipes.length > 0) {
        setRecipes(response.recipes)
      }
    } catch (err) {
      clearInterval(progressInterval)

      if (err instanceof APIError) {
        setError(err.message)
      } else {
        setError("Failed to get response")
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // Landing view - before first message
  if (messages.length === 0) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <Navigation />
        <div className="flex-1 flex items-center justify-center px-6">
          <div className="max-w-2xl w-full space-y-8">
            {/* Hero */}
            <div className="text-center space-y-4">
              <div className="inline-block p-4 bg-black rounded-full mb-4">
                <span className="text-5xl">🐀</span>
              </div>
              <h1 className="text-4xl font-bold">Ratatouille</h1>
              <p className="text-lg text-gray-600">
                Your AI sous chef for learning cooking through great recipes
              </p>
            </div>

            {/* Input */}
            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me anything... (e.g., I want to learn shallow frying)"
                  className="flex-1 h-12 text-base"
                  disabled={isLoading}
                />
                <Button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  className="h-12 px-6"
                >
                  {isLoading ? (
                    <Loader2 className="w-5 h-5 animate-spin" />
                  ) : (
                    <Send className="w-5 h-5" />
                  )}
                </Button>
              </div>

              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-sm text-red-600">
                  {error}
                </div>
              )}
            </div>

            {/* Example prompts */}
            <div className="space-y-2">
              <p className="text-sm text-gray-500 text-center">Try asking:</p>
              <div className="flex flex-wrap gap-2 justify-center">
                {[
                  "I want to learn pan sauces for beginners",
                  "Show me vegetarian knife skills",
                  "Advanced bread baking techniques"
                ].map((example, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(example)}
                    className="px-3 py-1.5 text-sm border border-gray-300 rounded-full hover:bg-gray-50 transition-colors"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Chat view with loading - keep centered during loading
  if (isLoading && recipes.length === 0) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <Navigation />
        <div className="flex-1 flex items-center justify-center px-6">
          <div className="max-w-md w-full space-y-6">
            <div className="flex justify-center">
              <div className="w-16 h-16 bg-black rounded-full flex items-center justify-center">
                <span className="text-3xl">🐀</span>
              </div>
            </div>

            <h2 className="text-2xl font-bold text-center">
              Finding recipes...
            </h2>

            {/* Agent Progress */}
            <div className="space-y-3">
              {agentSteps.map((step, i) => (
                <div key={i} className="flex items-center gap-3">
                  <div className={cn(
                    "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-all",
                    step.status === "complete" && "bg-black border-black",
                    step.status === "running" && "border-black",
                    step.status === "pending" && "border-gray-300"
                  )}>
                    {step.status === "running" && (
                      <Loader2 className="w-3 h-3 animate-spin" />
                    )}
                    {step.status === "complete" && (
                      <span className="text-white text-xs">✓</span>
                    )}
                  </div>
                  <span className={cn(
                    "text-sm transition-colors",
                    step.status === "complete" && "text-black font-medium",
                    step.status === "running" && "text-black",
                    step.status === "pending" && "text-gray-400"
                  )}>
                    {step.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Split screen view - after recipes loaded
  return (
    <div className="min-h-screen bg-white flex flex-col">
      <Navigation />
      <div className="flex-1 flex flex-col lg:flex-row">
        {/* Left: Chat History (40%) */}
        <div className="lg:w-2/5 border-r flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((msg, i) => (
              <div
                key={i}
                className={cn(
                  "flex gap-3",
                  msg.role === "user" ? "justify-end" : "justify-start"
                )}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-full bg-black flex items-center justify-center flex-shrink-0">
                    <span className="text-lg">🐀</span>
                  </div>
                )}
                <div className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-2",
                  msg.role === "user" ? "bg-black text-white" : "bg-gray-100 text-black"
                )}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                    <span className="text-lg">👤</span>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Input */}
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a follow-up question..."
                className="flex-1"
                disabled={isLoading}
              />
              <Button
                onClick={handleSend}
                disabled={!input.trim() || isLoading}
                size="icon"
              >
                {isLoading ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Send className="w-4 h-4" />
                )}
              </Button>
            </div>
            {error && (
              <div className="mt-2 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-600">
                {error}
              </div>
            )}
          </div>
        </div>

        {/* Right: Recipes (60%) */}
        <div className="lg:w-3/5 overflow-y-auto p-6">
          {recipes.length > 0 ? (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold">Your Recipes</h2>
              <div className="grid gap-6">
                {recipes.map((recipeCard, i) => (
                  <RecipeCard key={i} data={recipeCard} />
                ))}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-400">
              <p>Recipes will appear here</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
