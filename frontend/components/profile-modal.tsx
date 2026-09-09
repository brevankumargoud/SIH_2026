'use client'

import { ShieldCheck, Lock, User, LogOut, Settings, X, Key, Award } from 'lucide-react'

interface ProfileModalProps {
  isOpen: boolean
  onClose: () => void
  onNavigateSettings: () => void
  onLogout: () => void
}

export function ProfileModal({ isOpen, onClose, onNavigateSettings, onLogout }: ProfileModalProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/65 p-4 backdrop-blur-sm animate-rise">
      <div className="w-full max-w-md rounded-xl border border-white/10 bg-[#0c1524] text-foreground p-6 shadow-2xl space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between border-b border-white/10 pb-4">
          <div className="flex items-center gap-3">
            <div className="grid size-12 place-items-center rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-lg font-bold font-mono">
              JE
            </div>
            <div>
              <h2 className="text-base font-semibold">Jordan Ellis</h2>
              <p className="font-mono text-xs text-cyan-400">Operations Intelligence Lead</p>
              <p className="text-[11px] text-muted-foreground">jordan.ellis@sovereign.local</p>
            </div>
          </div>
          <button onClick={onClose} aria-label="Close profile" className="rounded p-1 text-muted-foreground hover:bg-muted">
            <X className="size-4" />
          </button>
        </div>

        {/* Clearance Card */}
        <div className="rounded-lg border border-cyan-500/30 bg-cyan-500/5 p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="font-mono text-[9px] uppercase tracking-wider text-muted-foreground flex items-center gap-1.5">
              <Award className="size-3.5 text-cyan-400" /> Operational Clearance
            </span>
            <span className="font-mono text-[9px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              ACTIVE
            </span>
          </div>
          <p className="text-xs font-semibold text-foreground">
            Level 4 — Top Secret Air-Gapped Operations
          </p>
          <p className="text-[11px] text-muted-foreground leading-relaxed">
            Authorized for on-premise inference, autonomous multi-agent execution, and vector-grounded industrial analysis.
          </p>
        </div>

        {/* Security parameters */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="rounded-lg border border-white/10 bg-card/40 p-3">
            <span className="font-mono text-[9px] text-muted-foreground uppercase flex items-center gap-1">
              <Key className="size-3 text-violet-400" /> Session ID
            </span>
            <p className="mt-1 font-mono text-[11px] text-foreground truncate">sess-9842a-sov</p>
          </div>
          <div className="rounded-lg border border-white/10 bg-card/40 p-3">
            <span className="font-mono text-[9px] text-muted-foreground uppercase flex items-center gap-1">
              <ShieldCheck className="size-3 text-emerald-400" /> Egress Lock
            </span>
            <p className="mt-1 font-mono text-[11px] text-emerald-400">100% Air-Gapped</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col gap-2 pt-2 border-t border-white/10">
          <button
            onClick={() => {
              onClose()
              onNavigateSettings()
            }}
            className="flex items-center justify-center gap-2 rounded-lg border border-white/15 bg-white/[0.03] py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-foreground hover:bg-white/[0.08] transition"
          >
            <Settings className="size-3.5 text-cyan-400" /> Open System Settings
          </button>

          <button
            onClick={() => {
              onClose()
              onLogout()
            }}
            className="flex items-center justify-center gap-2 rounded-lg border border-red-500/30 bg-red-500/10 py-2.5 font-mono text-xs font-semibold uppercase tracking-wider text-red-400 hover:bg-red-500/20 transition"
          >
            <LogOut className="size-3.5" /> Terminate Session & Logout
          </button>
        </div>
      </div>
    </div>
  )
}
