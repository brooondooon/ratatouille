"use client"

import { useState, useEffect } from "react"
import { Timer as TimerIcon } from "lucide-react"

interface TimerProps {
  isRunning: boolean
  onReset?: () => void
}

export function Timer({ isRunning, onReset }: TimerProps) {
  const [seconds, setSeconds] = useState(0)

  useEffect(() => {
    if (!isRunning) return

    const interval = setInterval(() => {
      setSeconds(s => s + 1)
    }, 1000)

    return () => clearInterval(interval)
  }, [isRunning])

  useEffect(() => {
    // Reset timer when onReset changes (triggered by step change)
    setSeconds(0)
  }, [onReset])

  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60

  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 border border-gray-300 rounded-lg">
      <TimerIcon className="w-5 h-5 text-black" />
      <div className="text-lg font-mono font-semibold text-black tabular-nums">
        {String(minutes).padStart(2, '0')}:{String(remainingSeconds).padStart(2, '0')}
      </div>
    </div>
  )
}
