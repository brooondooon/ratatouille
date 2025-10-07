"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="border-b border-gray-200 bg-white sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex h-16 items-center justify-between">
          {/* Logo */}
          <Link href="/chat" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <span className="text-2xl">🐀</span>
            <span className="font-bold text-lg">Ratatouille</span>
          </Link>

          {/* Tab Navigation */}
          <div className="flex gap-1">
            <Link href="/chat">
              <Button
                variant={pathname?.startsWith('/chat') ? 'default' : 'ghost'}
                className="transition-all"
              >
                Chat
              </Button>
            </Link>
            <Link href="/cookbook">
              <Button
                variant={pathname?.startsWith('/cookbook') ? 'default' : 'ghost'}
                className="transition-all"
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
