"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export function Navigation() {
  const pathname = usePathname()

  const handleLogoClick = () => {
    // Clear chat state when logo is clicked
    localStorage.removeItem('chatMessages')
    localStorage.removeItem('chatRecipes')

    // Trigger storage event manually for same-window updates
    window.dispatchEvent(new Event('storage'))
  }

  return (
    <nav className="border-b border-gray-200 bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link
            href="/chat"
            onClick={handleLogoClick}
            className="flex items-center gap-2 hover:opacity-80 transition-opacity"
          >
            <img
              src="/ratatouille-logo.svg"
              alt="Ratatouille"
              className="w-8 h-8"
            />
            <span className="font-bold text-lg">Ratatouille</span>
          </Link>

          {/* Tab Navigation */}
          <div className="flex gap-1">
            <Link href="/chat">
              <Button
                variant={pathname?.startsWith('/chat') ? 'default' : 'ghost'}
                className={cn(
                  "transition-all",
                  pathname?.startsWith('/chat') && "pointer-events-none"
                )}
              >
                Chat
              </Button>
            </Link>
            <Link href="/cookbook">
              <Button
                variant={pathname?.startsWith('/cookbook') ? 'default' : 'ghost'}
                className={cn(
                  "transition-all",
                  pathname?.startsWith('/cookbook') && "pointer-events-none"
                )}
              >
                Cookbook
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
