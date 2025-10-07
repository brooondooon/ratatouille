"use client"

import { useState, useEffect, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Loader2 } from "lucide-react"
import { extractRecipe, APIError } from "@/lib/api"

function CookContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(true)
  const [content, setContent] = useState<string>("")
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const url = searchParams.get("url")

    if (!url) {
      router.push("/")
      return
    }

    const fetchContent = async () => {
      try {
        const result = await extractRecipe(url)
        setContent(result.raw_content)
        setIsLoading(false)
      } catch (err) {
        if (err instanceof APIError) {
          setError(err.message)
        } else {
          setError("Failed to extract recipe")
        }
        setIsLoading(false)
      }
    }

    fetchContent()
  }, [searchParams, router])

  // Loading State
  if (isLoading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center px-6">
        <div className="text-center space-y-6">
          <div className="flex justify-center">
            <Loader2 className="w-12 h-12 animate-spin" />
          </div>
          <h2 className="text-xl font-bold">Extracting recipe...</h2>
          <p className="text-sm text-muted-foreground">
            Getting the full recipe content for you
          </p>
        </div>
      </div>
    )
  }

  // Error State
  if (error) {
    return (
      <div className="min-h-screen bg-white px-6 py-8">
        <div className="max-w-2xl mx-auto space-y-6 text-center">
          <div className="text-6xl">😕</div>
          <h2 className="text-2xl font-bold">Oops! Something went wrong</h2>
          <p className="text-muted-foreground">{error}</p>
          <Button onClick={() => router.back()} variant="default">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Go Back
          </Button>
        </div>
      </div>
    )
  }

  // Success State - Display Recipe Content
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="sticky top-0 bg-white border-b z-10">
        <div className="max-w-4xl mx-auto px-6 py-4 flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.back()}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-lg font-bold">Recipe Guide</h1>
        </div>
      </div>

      {/* Recipe Content */}
      <div className="max-w-4xl mx-auto px-6 py-8">
        <div className="prose prose-sm max-w-none">
          {/* Render markdown content as plain text for now */}
          <pre className="whitespace-pre-wrap font-sans text-sm leading-relaxed">
            {content}
          </pre>
        </div>
      </div>
    </div>
  )
}

export default function CookPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-white flex items-center justify-center">
        <Loader2 className="animate-spin" />
      </div>
    }>
      <CookContent />
    </Suspense>
  )
}
