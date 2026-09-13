'use client'

import { useEffect, useState } from 'react'
import { ShieldCheck, Cpu, Lock, Sparkles } from 'lucide-react'

interface EntryMotionProps {
  onComplete?: () => void
}

export function EntryMotion({ onComplete }: EntryMotionProps) {
  const [stage, setStage] = useState<'boot' | 'ready' | 'exit'>('boot')
  const [visible, setVisible] = useState(false)
  const [progress, setProgress] = useState(5)
  const [statusText, setStatusText] = useState('VERIFYING SECURE AIR-GAP PERIMETER...')

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const alreadyPlayed = sessionStorage.getItem('sovereign_entry_played')
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

      // If user specifically requested 5s entry motion, don't silently skip unless reduced motion
      if (prefersReducedMotion) {
        onComplete?.()
        return
      }

      // If already played in this exact tab session, allow skip unless reloaded with reset
      if (alreadyPlayed && !window.location.search.includes('replay=true')) {
        // Still allow playing once per browser tab load if requested
      }

      setVisible(true)

      // Smooth progress bar incrementing over 5 seconds (5000ms)
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(progressInterval)
            return 100
          }
          return Math.min(prev + 2, 100)
        })
      }, 95)

      // Stepwise 5-stage boot sequence over 5 seconds
      // 0.0s - 1.0s: Stage 1
      const t1 = setTimeout(() => {
        setStatusText('INITIALIZING SECURE HARDWARE REGISTERS & ENCLAVE...')
      }, 1000)

      // 1.0s - 2.0s: Stage 2
      const t2 = setTimeout(() => {
        setStatusText('MOUNTING ON-PREMISE VECTOR EMBEDDINGS & CHROMA...')
      }, 2000)

      // 2.0s - 3.2s: Stage 3
      const t3 = setTimeout(() => {
        setStatusText('LOADING QUANTIZED LOCAL MODEL WEIGHTS (INT8 / vLLM)...')
      }, 3200)

      // 3.2s - 4.2s: Stage 4
      const t4 = setTimeout(() => {
        setStatusText('SYNCHRONIZING ZERO-EGRESS AGENT ORCHESTRATOR...')
      }, 4200)

      // 4.2s - 4.7s: Stage 5 Ready
      const t5 = setTimeout(() => {
        setStatusText('SOVEREIGN AI WORKBENCH OPERATIONAL — ZERO EGRESS CONFIRMED')
        setStage('ready')
        setProgress(100)
      }, 4600)

      // 4.7s - 5.0s: Exit transition
      const tExit = setTimeout(() => {
        setStage('exit')
      }, 4850)

      // 5.0s completion
      const tComplete = setTimeout(() => {
        sessionStorage.setItem('sovereign_entry_played', 'true')
        setVisible(false)
        onComplete?.()
      }, 5200)

      // Keydown listener for instant [Esc] skip
      const onKeyDown = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          sessionStorage.setItem('sovereign_entry_played', 'true')
          setVisible(false)
          onComplete?.()
        }
      }
      window.addEventListener('keydown', onKeyDown)

      return () => {
        clearInterval(progressInterval)
        clearTimeout(t1)
        clearTimeout(t2)
        clearTimeout(t3)
        clearTimeout(t4)
        clearTimeout(t5)
        clearTimeout(tExit)
        clearTimeout(tComplete)
        window.removeEventListener('keydown', onKeyDown)
      }
    }
  }, [onComplete])

  const handleSkip = () => {
    sessionStorage.setItem('sovereign_entry_played', 'true')
    setVisible(false)
    onComplete?.()
  }

  if (!visible) return null

  return (
    <div
      role="status"
      aria-label="Application 5-second entry boot sequence"
      className={`fixed inset-0 z-[9999] flex flex-col items-center justify-center bg-[#060b13] text-white transition-all duration-350 ease-out ${
        stage === 'exit' ? 'opacity-0 scale-[1.03] pointer-events-none' : 'opacity-100 scale-100'
      }`}
    >
      {/* Background cyber grid & radial glow effects */}
      <div className="absolute inset-0 cyber-grid opacity-35" />
      <div className="absolute size-[42rem] rounded-full bg-cyan-500/10 blur-[140px] pointer-events-none" />
      <div className="absolute size-[32rem] rounded-full bg-violet-600/10 blur-[120px] pointer-events-none" />

      {/* Center 3D Holographic Core */}
      <div className="relative flex flex-col items-center z-10 px-6 text-center max-w-xl">
        {/* Animated 3D Ring Structure */}
        <div className="relative size-32 flex items-center justify-center mb-8">
          {/* Outer rotating dashed ring */}
          <div className="absolute inset-0 rounded-full border-2 border-cyan-400/40 border-dashed animate-[spin_8s_linear_infinite]" />
          {/* Middle counter-rotating ring */}
          <div className="absolute inset-2 rounded-full border border-violet-400/50 animate-[spin_5s_linear_infinite_reverse]" />
          {/* Pulsating glowing core aura */}
          <div className="absolute inset-5 rounded-full bg-gradient-to-br from-cyan-500/30 to-violet-600/30 blur-md animate-pulse" />
          
          {/* Center 3D emblem */}
          <div className="relative size-16 rounded-2xl bg-[#0c1524] border border-cyan-400/60 shadow-[0_0_35px_rgba(0,210,255,0.45)] flex items-center justify-center">
            <div className="font-mono text-2xl font-black tracking-tighter text-cyan-400">
              S
            </div>
          </div>
        </div>

        {/* Title & Branding */}
        <div className="flex items-center gap-2 mb-2.5">
          <span className="size-2 rounded-full bg-cyan-400 shadow-[0_0_10px_#00d2ff] animate-ping" />
          <p className="font-mono text-[11px] font-bold uppercase tracking-[0.32em] text-cyan-400">
            ENTERPRISE AIR-GAP SYSTEM • 5S INITIALIZATION
          </p>
        </div>

        <h1 className="text-3xl sm:text-4xl font-bold tracking-tight text-white mt-1">
          Sovereign AI <span className="gradient-text-cyan">Workbench</span>
        </h1>

        <p className="mt-2.5 font-mono text-[11px] uppercase tracking-[0.2em] text-white/50">
          Autonomous Local Intelligence & On-Premise Operations
        </p>

        {/* 5-Second Animated Progress Bar */}
        <div className="mt-8 w-full max-w-md">
          <div className="flex items-center justify-between font-mono text-[10px] text-cyan-300 mb-2">
            <span className="flex items-center gap-1.5">
              <Sparkles className="size-3 text-cyan-400" />
              SYSTEM BOOT TELEMETRY
            </span>
            <span className="font-bold text-cyan-400">{progress}%</span>
          </div>

          <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/10 border border-white/5">
            <div
              className="h-full bg-gradient-to-r from-cyan-400 via-cyan-300 to-violet-500 rounded-full transition-all duration-100 ease-out shadow-[0_0_12px_rgba(0,210,255,0.6)]"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* Loading status pill */}
          <div className="mt-4 flex items-center justify-center gap-3 px-4 py-2 rounded-lg border border-white/10 bg-[#0c1524]/90 backdrop-blur-md shadow-lg">
            <span className="size-2 rounded-full bg-cyan-400 animate-pulse shrink-0" />
            <span className="font-mono text-[10px] tracking-wider text-cyan-300 truncate">
              {statusText}
            </span>
          </div>
        </div>

        {/* Feature badges */}
        <div className="mt-8 flex flex-wrap justify-center items-center gap-5 text-[10px] font-mono uppercase tracking-widest text-white/40">
          <span className="flex items-center gap-1.5">
            <ShieldCheck className="size-3.5 text-cyan-400" /> Zero Cloud Egress
          </span>
          <span className="flex items-center gap-1.5">
            <Cpu className="size-3.5 text-violet-400" /> Local vLLM Cluster
          </span>
          <span className="flex items-center gap-1.5">
            <Lock className="size-3.5 text-emerald-400" /> Hardware Enclave
          </span>
        </div>
      </div>

      {/* Accessible skip button */}
      <button
        onClick={handleSkip}
        className="absolute bottom-6 right-6 font-mono text-[10px] uppercase tracking-widest text-white/40 hover:text-white px-3 py-1.5 rounded border border-white/10 hover:border-cyan-400/40 transition bg-white/[0.02]"
      >
        Skip [Esc]
      </button>
    </div>
  )
}
