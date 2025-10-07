"use client"

import { useState, useEffect } from "react"
import { Navigation } from "@/components/Navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { RecipeCard } from "@/components/RecipeCard"
import { Loader2, Send, RefreshCcw } from "lucide-react"
import { sendChatMessage, APIError } from "@/lib/api"
import type { Message, RecipeCard as RecipeCardType, AgentStep } from "@/lib/types"
import { cn } from "@/lib/utils"
import Image from "next/image"

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
  const [loadingPhraseIndex, setLoadingPhraseIndex] = useState(0)
  const [excludedRecipes, setExcludedRecipes] = useState<string[]>([]) // Track recipe URLs to exclude

  const loadingPhrases = [
    "Searching for the perfect recipes...",
    "Putting on my tiny chef hat...",
    "Saying \"Yes Chef!\" as loud as I can...",
    "Doing my best Carmy impression...",
    "Putting out a kitchen fire..."
  ]

  // Load chat state from localStorage on mount and when storage changes
  useEffect(() => {
    const loadChatState = () => {
      const savedMessages = localStorage.getItem('chatMessages')
      const savedRecipes = localStorage.getItem('chatRecipes')

      if (savedMessages) {
        setMessages(JSON.parse(savedMessages))
      } else {
        setMessages([])
      }

      if (savedRecipes) {
        setRecipes(JSON.parse(savedRecipes))
      } else {
        setRecipes([])
      }
    }

    // Load on mount
    loadChatState()

    // Listen for storage changes (e.g., when logo is clicked)
    window.addEventListener('storage', loadChatState)

    return () => {
      window.removeEventListener('storage', loadChatState)
    }
  }, [])

  // Save chat state to localStorage whenever it changes
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chatMessages', JSON.stringify(messages))
    }
  }, [messages])

  useEffect(() => {
    if (recipes.length > 0) {
      localStorage.setItem('chatRecipes', JSON.stringify(recipes))
    }
  }, [recipes])

  // Cycle through loading phrases
  useEffect(() => {
    if (!isLoading) return

    const interval = setInterval(() => {
      setLoadingPhraseIndex((prev) => (prev + 1) % loadingPhrases.length)
    }, 2000) // Change phrase every 2 seconds

    return () => clearInterval(interval)
  }, [isLoading, loadingPhrases.length])

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
      // If we already have recipes, this is a follow-up question
      const isFollowUp = recipes.length > 0

      const response = await sendChatMessage({
        message: userMessage,
        is_follow_up: isFollowUp
      })

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

  const handleRegenerate = async () => {
    if (isLoading || messages.length === 0) return

    // Add current recipe URLs to excluded list
    const currentRecipeUrls = recipes.map(r => r.recipe.url)
    const newExcluded = [...excludedRecipes, ...currentRecipeUrls]
    setExcludedRecipes(newExcluded)

    // Find the last user message (the original query)
    const lastUserMessage = [...messages].reverse().find(m => m.role === "user")
    if (!lastUserMessage) return

    setError(null)
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
    }, 6000)

    try {
      const response = await sendChatMessage({
        message: lastUserMessage.content,
        is_follow_up: false,
        excluded_urls: newExcluded
      })

      clearInterval(progressInterval)

      // Mark all steps complete
      setAgentSteps(prev => prev.map(step => ({ ...step, status: "complete" as const })))

      // Replace recipes with new ones
      if (response.recipes.length > 0) {
        setRecipes(response.recipes)

        // Add a system message indicating regeneration
        const systemMessage: Message = {
          role: "assistant",
          content: response.reply,
          recipes: response.recipes
        }
        setMessages(prev => [...prev, systemMessage])
      }
    } catch (err) {
      clearInterval(progressInterval)

      if (err instanceof APIError) {
        setError(err.message)
      } else {
        setError("Failed to regenerate recipes")
      }
    } finally {
      setIsLoading(false)
    }
  }

  // Landing view - before first message
  if (messages.length === 0) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <Navigation />
        <div className="flex-1 flex items-center justify-center px-6 pb-32">
          <div className="max-w-2xl w-full space-y-8">
            {/* Hero */}
            <div className="text-center space-y-4">
              <div className="inline-flex items-center justify-center mb-4">
                <img
                  src="/ratatouille-logo.svg"
                  alt="Ratatouille"
                  className="w-40 h-40"
                />
              </div>
              <h1 className="text-4xl font-bold">Ratatouille</h1>
              <p className="text-lg text-gray-600">
                Your personal sous chef to improve your cooking
              </p>
            </div>

            {/* Input */}
            <div className="space-y-4">
              <div className="flex gap-2">
                <Input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask the chef... (e.g., I want an advanced pancake recipe)"
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
                  "Show me recipes that improve my knife skills",
                  "Advanced sourdough recipes"
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
          <div className="max-w-md w-full space-y-8">
            <div className="flex justify-center">
              <div className="w-32 h-32 flex items-center justify-center">
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
            </div>

            <div className="text-center">
              <h2
                key={loadingPhraseIndex}
                className="text-2xl font-bold text-black animate-fade-in"
              >
                {loadingPhrases[loadingPhraseIndex]}
              </h2>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Split screen view - after recipes loaded
  return (
    <div className="h-screen bg-white flex flex-col overflow-hidden">
      <Navigation />
      <div className="flex-1 flex flex-col lg:flex-row overflow-hidden">
        {/* Left: Chat History (40%) */}
        <div className="lg:w-2/5 border-r flex flex-col h-full">
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
                  <div className="w-8 h-8 flex items-center justify-center flex-shrink-0">
                    <Image
                      src="/ratatouille-logo.svg"
                      alt="Assistant"
                      width={32}
                      height={32}
                    />
                  </div>
                )}
                <div className={cn(
                  "max-w-[80%] rounded-2xl px-4 py-2",
                  msg.role === "user" ? "bg-black text-white" : "bg-gray-100 text-black"
                )}>
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
                {msg.role === "user" && (
                  <div className="w-8 h-8 flex items-center justify-center flex-shrink-0">
                    <Image
                      src="/chef-icon.svg"
                      alt="User"
                      width={32}
                      height={32}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Input - Fixed at bottom */}
          <div className="p-4 border-t bg-white">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask the chef about the recipes..."
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

        {/* Right: Recipes Carousel (60%) */}
        <div className="lg:w-3/5 flex flex-col h-full overflow-hidden">
          {recipes.length > 0 ? (
            <div className="flex-1 flex flex-col p-6 overflow-hidden">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold">Your Recipes</h2>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleRegenerate}
                  disabled={isLoading}
                  className="flex items-center gap-2"
                >
                  <RefreshCcw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
                  Regenerate
                </Button>
              </div>
              {/* Horizontal scrolling carousel */}
              <div className="flex-1 overflow-x-auto overflow-y-hidden">
                <div className="flex gap-6 h-full pb-4">
                  {recipes.map((recipeCard, i) => (
                    <div key={i} className="flex-shrink-0 w-[400px] h-full overflow-y-auto">
                      <RecipeCard data={recipeCard} />
                    </div>
                  ))}
                </div>
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
