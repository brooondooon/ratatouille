"use client"

import { Navigation } from "@/components/Navigation"

export default function CookbookPage() {
  return (
    <div className="min-h-screen bg-white">
      <Navigation />
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="text-center space-y-6">
          <h1 className="text-4xl font-bold">Cookbook Page</h1>
          <p className="text-gray-600">Bookmarked recipes will appear here</p>
        </div>
      </div>
    </div>
  )
}
