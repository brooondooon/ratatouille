import type { Metadata, Viewport } from "next"
import { Plus_Jakarta_Sans } from "next/font/google"
import "./globals.css"
import { ErrorBoundary } from "@/components/ErrorBoundary"

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta-sans",
  display: "swap"
})

export const metadata: Metadata = {
  title: "🐀 Ratatouille - Your AI Culinary Coach",
  description: "Learn cooking techniques through personalized, AI-curated recipe recommendations",
  keywords: "cooking, recipes, culinary education, techniques, AI",
  authors: [{ name: "Ratatouille Team" }],
  appleWebApp: {
    capable: true,
    statusBarStyle: "default",
    title: "Ratatouille"
  }
}

export const viewport: Viewport = {
  themeColor: "#000000",
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
  userScalable: false,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${plusJakartaSans.variable} antialiased`}>
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  )
}
