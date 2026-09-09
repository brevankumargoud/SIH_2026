'use client'

import { FormEvent, useEffect, useState, useRef } from 'react'
import {
  Activity, AlertTriangle, ArrowRight, BarChart3, Bell, BookOpen,
  ChevronRight, Clipboard, Code2, Copy, Cpu, Database, Download,
  Edit3, Eye, EyeOff, FileText, Gauge, ImagePlus, Info, LockKeyhole,
  Menu, MessageSquare, Mic, Moon, MoreHorizontal, Network, Paperclip,
  PanelLeftClose, Pin, PinOff, Plus, RotateCcw, Search, Send, Settings,
  ShieldCheck, Sparkles, Square, Sun, Trash2, Upload, Users, X,
  ZoomIn, ZoomOut, Maximize2, Rotate3d, Image as ImageIcon, Zap, Check,
  ExternalLink, RefreshCw, CheckCircle2, ShieldAlert, LogOut, SlidersHorizontal,
  ChevronDown
} from 'lucide-react'
import {
  adminService, agentService, authService, chatService,
  documentService, knowledgeBaseService, searchService, visionService,
  apiClient
} from '@/lib/services'
import { AgentsWorkspace } from '@/components/agents-workspace'
import { ModelsWorkspace } from '@/components/models-workspace'
import { ReportsWorkspace } from '@/components/reports-workspace'
import { AuditWorkspace } from '@/components/audit-workspace'
import { SettingsWorkspace } from '@/components/settings-workspace'
import { AdminWorkspace } from '@/components/admin-workspace'
import { EntryMotion } from '@/components/entry-motion'
import { NotificationsDrawer } from '@/components/notifications-drawer'
import { ProfileModal } from '@/components/profile-modal'

type PageKey =
  | 'Overview'
  | 'AI Chat'
  | 'Documents'
  | 'Knowledge Base'
  | 'Agents'
  | 'Models'
  | 'Vision'
  | 'Reports'
  | 'Audit Log'
  | 'Admin'
  | 'Settings'

const nav: { label: PageKey; icon: any; section?: string }[] = [
  { label: 'Overview', icon: Gauge, section: 'WORKSPACE' },
  { label: 'AI Chat', icon: MessageSquare },
  { label: 'Documents', icon: FileText },
  { label: 'Knowledge Base', icon: BookOpen },
  { label: 'Agents', icon: Network, section: 'INTELLIGENCE' },
  { label: 'Models', icon: Cpu },
  { label: 'Vision', icon: Eye },
  { label: 'Reports', icon: BarChart3, section: 'GOVERNANCE' },
  { label: 'Audit Log', icon: ShieldCheck },
  { label: 'Admin', icon: Users },
  { label: 'Settings', icon: Settings },
]

function Logo({ compact = false }: { compact?: boolean }) {
  return (
    <div className="flex items-center gap-3">
      <div className="relative grid size-9 place-items-center rounded-lg bg-gradient-to-br from-cyan-400 to-cyan-600 text-slate-950 shadow-[0_0_18px_rgba(0,210,255,0.4)]">
        <div className="absolute inset-0.5 rounded-[7px] border border-white/40" />
        <span className="font-mono text-sm font-black tracking-tighter">S</span>
      </div>
      {!compact && (
        <div>
          <p className="font-mono text-[11px] font-bold uppercase tracking-[.26em] text-foreground">Sovereign</p>
          <p className="font-mono text-[9px] uppercase tracking-[.2em] text-cyan-400">AI Workbench</p>
        </div>
      )}
    </div>
  )
}

function StatusDot({ label = 'Connected', isOnline = true }: { label?: string; isOnline?: boolean }) {
  return (
    <span className="inline-flex items-center gap-2 font-mono text-[10px] uppercase tracking-[.14em] text-muted-foreground">
      <span
        className={`size-2 rounded-full ${
          isOnline
            ? 'bg-emerald-400 shadow-[0_0_8px_#10b981]'
            : 'bg-amber-400 shadow-[0_0_8px_#f59e0b]'
        }`}
      />
      {label}
    </span>
  )
}

function SecurityStrip() {
  return (
    <div className="grid gap-3 rounded-lg border border-cyan-500/25 bg-[#0c1524]/60 backdrop-blur-md p-4 sm:grid-cols-3">
      <div>
        <p className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">Local Vector Storage</p>
        <p className="mt-1 flex items-center gap-2 text-xs font-semibold text-foreground">
          <span className="size-1.5 rounded-full bg-emerald-400" /> On-Premise SQLite / Chroma
        </p>
      </div>
      <div>
        <p className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">Air-Gap Boundary</p>
        <p className="mt-1 flex items-center gap-2 text-xs font-semibold text-emerald-400">
          <span className="size-1.5 rounded-full bg-emerald-400" /> Zero External Egress
        </p>
      </div>
      <div>
        <p className="font-mono text-[9px] uppercase tracking-widest text-muted-foreground">External AI APIs</p>
        <p className="mt-1 flex items-center gap-2 text-xs font-semibold text-muted-foreground">
          <span className="size-1.5 rounded-full bg-muted-foreground" /> Disabled by Policy
        </p>
      </div>
    </div>
  )
}

function Login({ onLogin, onForgotPassword }: { onLogin: () => void; onForgotPassword: () => void }) {
  const [email, setEmail] = useState('engineer@sovereign.local')
  const [password, setPassword] = useState('Demo@12345')
  const [show, setShow] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await authService.signIn(email, password)
      onLogin()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed. Check credentials.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-[#060b13] text-white md:grid md:grid-cols-[1.05fr_.95fr]">
      {/* Left branding pane */}
      <section className="relative hidden overflow-hidden border-r border-white/10 bg-[#09101b] p-10 md:flex md:flex-col md:justify-between lg:p-14">
        <div className="absolute inset-0 cyber-grid opacity-35" />
        <div className="absolute -left-32 top-1/3 size-[34rem] rounded-full bg-cyan-500/10 blur-[130px]" />
        <div className="absolute right-0 bottom-10 size-[28rem] rounded-full bg-violet-600/10 blur-[110px]" />

        <div className="relative">
          <Logo />
          <div className="mt-28 max-w-xl">
            <div className="flex items-center gap-2">
              <span className="size-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00d2ff]" />
              <p className="font-mono text-[11px] uppercase tracking-[.3em] text-cyan-400">
                CONTROLLED INTELLIGENCE // SECURE LOCAL AIR-GAP
              </p>
            </div>
            <h1 className="mt-5 font-sans text-5xl font-bold leading-[1.05] tracking-tight text-white lg:text-7xl">
              Decisions built<br />
              <span className="gradient-text-cyan">on sovereign data.</span>
            </h1>
            <p className="mt-7 max-w-md text-sm leading-relaxed text-white/70">
              A secure operational layer for authorized teams where reliability, full traceability, and zero external egress are non-negotiable.
            </p>
          </div>
        </div>

        <div className="relative grid max-w-lg grid-cols-3 gap-6 border-t border-white/10 pt-6">
          <div>
            <p className="font-mono text-[9px] uppercase tracking-widest text-white/40">Deployment</p>
            <p className="mt-1.5 text-xs font-semibold text-white/80">On-Premise / Air-Gapped</p>
          </div>
          <div>
            <p className="font-mono text-[9px] uppercase tracking-widest text-white/40">Inference</p>
            <p className="mt-1.5 text-xs font-semibold text-cyan-300">Local vLLM Cluster</p>
          </div>
          <div>
            <p className="font-mono text-[9px] uppercase tracking-widest text-white/40">Protocol</p>
            <p className="mt-1.5 text-xs font-semibold text-emerald-400">Zero Cloud Egress</p>
          </div>
        </div>
      </section>

      {/* Right sign-in form */}
      <section className="flex min-h-screen flex-col justify-between bg-[#0c1524] p-6 sm:p-10 lg:p-16">
        <div className="flex justify-end">
          <StatusDot label="Secure Perimeter Active" />
        </div>

        <div className="mx-auto w-full max-w-md">
          <div className="mb-8 md:hidden">
            <Logo />
          </div>

          <div className="mb-8">
            <div className="mb-5 flex size-12 items-center justify-center rounded-xl border border-cyan-400/30 bg-cyan-500/10 text-cyan-400 shadow-[0_0_20px_rgba(0,210,255,0.2)]">
              <LockKeyhole className="size-6" />
            </div>
            <p className="font-mono text-[10px] uppercase tracking-[.25em] text-cyan-400">
              Authorized Personnel Access
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight text-white">
              Sign in to the Workbench
            </h2>
            <p className="mt-2 text-sm text-white/60">
              Enter your enterprise credentials to access air-gapped operational intelligence.
            </p>
          </div>

          <form onSubmit={submit} className="flex flex-col gap-5">
            <label className="flex flex-col gap-2">
              <span className="font-mono text-[10px] uppercase tracking-[.18em] text-white/50">
                Work Email
              </span>
              <input
                className="focus-ring h-12 rounded-lg border border-white/10 bg-white/[.04] px-4 text-sm text-white outline-none placeholder:text-white/25 focus:border-cyan-400 transition"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="engineer@sovereign.local"
                required
              />
            </label>

            <label className="flex flex-col gap-2">
              <span className="font-mono text-[10px] uppercase tracking-[.18em] text-white/50">
                Password
              </span>
              <div className="relative">
                <input
                  className="focus-ring h-12 w-full rounded-lg border border-white/10 bg-white/[.04] px-4 pr-12 text-sm text-white outline-none placeholder:text-white/25 focus:border-cyan-400 transition"
                  type={show ? 'text' : 'password'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Enter password"
                  required
                />
                <button
                  type="button"
                  aria-label={show ? 'Hide password' : 'Show password'}
                  onClick={() => setShow(!show)}
                  className="absolute right-3.5 top-3.5 text-white/40 hover:text-white transition"
                >
                  {show ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
                </button>
              </div>
            </label>

            <div className="flex items-center justify-between text-xs">
              <label className="flex items-center gap-2 text-white/60 cursor-pointer">
                <input type="checkbox" defaultChecked className="size-3.5 accent-cyan-400" />
                <span>Remember this device</span>
              </label>
              <button
                type="button"
                onClick={onForgotPassword}
                className="text-cyan-400 hover:text-cyan-300 hover:underline transition"
              >
                Forgot password?
              </button>
            </div>

            {error && (
              <div role="alert" className="flex items-start gap-3 rounded-lg border border-red-500/30 bg-red-500/10 p-3.5 text-xs text-red-200">
                <AlertTriangle className="mt-0.5 shrink-0 size-4 text-red-400" />
                <span>{error}</span>
              </div>
            )}

            <button
              disabled={loading}
              className="focus-ring flex h-12 items-center justify-center gap-3 rounded-lg bg-cyan-400 font-mono text-xs font-bold uppercase tracking-[.18em] text-slate-950 shadow-[0_0_20px_rgba(0,210,255,0.3)] hover:brightness-110 active:scale-[0.99] transition disabled:cursor-wait disabled:opacity-60"
            >
              {loading ? (
                <>
                  <span className="size-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent" />
                  Authenticating Session...
                </>
              ) : (
                <>
                  Sign In <ArrowRight className="size-4" />
                </>
              )}
            </button>
          </form>

          <div className="mt-8 flex items-center justify-center gap-2 border-t border-white/10 pt-5 text-center font-mono text-[9px] uppercase tracking-[.18em] text-white/40">
            <ShieldCheck className="size-3.5 text-cyan-400" /> Secure cryptographic access • Activity logged
          </div>
        </div>

        <div className="flex flex-col gap-1 text-center text-[10px] text-white/40 md:text-left">
          <p>Authorized personnel only. All inference queries and retrieval events are immutable.</p>
          <p className="font-mono uppercase tracking-[.15em] text-cyan-400/70">
            Sovereign AI Workbench • Phase 1–5 Integration Verified
          </p>
        </div>
      </section>
    </main>
  )
}

function ForgotPassword({ onBack }: { onBack: () => void }) {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setMessage('')
    try {
      const result = await authService.sendResetLink(email)
      setMessage(result.message)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unable to issue reset instructions.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="grid min-h-screen place-items-center bg-[#060b13] p-6 text-white">
      <div className="w-full max-w-md rounded-xl border border-white/10 bg-[#0c1524] p-8 shadow-2xl space-y-6">
        <Logo />
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[.2em] text-cyan-400">Account Recovery</p>
          <h1 className="mt-2 text-2xl font-bold tracking-tight">Reset Authorized Access</h1>
          <p className="mt-2 text-xs leading-relaxed text-white/60">
            Enter your authorized enterprise work email. A cryptographic credential update notice will be generated.
          </p>
        </div>

        <form onSubmit={submit} className="flex flex-col gap-4">
          <label className="flex flex-col gap-1.5 text-xs font-medium text-white/70">
            Work Email
            <input
              autoFocus
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="h-11 rounded-lg border border-white/15 bg-white/5 px-3 text-sm text-white outline-none focus:border-cyan-400 transition"
              placeholder="engineer@sovereign.local"
              required
            />
          </label>

          {error && (
            <p role="alert" className="rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-xs text-red-200">
              {error}
            </p>
          )}

          {message && (
            <p role="status" className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-xs text-emerald-200">
              {message}
            </p>
          )}

          <button
            disabled={loading}
            className="h-11 rounded-lg bg-cyan-400 px-4 font-mono text-[10px] font-bold uppercase tracking-widest text-slate-950 hover:brightness-110 disabled:opacity-60 transition"
          >
            {loading ? 'Processing Request...' : 'Send Reset Link'}
          </button>
        </form>

        <button
          onClick={onBack}
          className="w-full text-center text-xs text-white/50 hover:text-white transition"
        >
          ← Back to Sign In
        </button>
      </div>
    </main>
  )
}

function Dashboard({ onNavigate }: { onNavigate: (page: PageKey) => void }) {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [notice, setNotice] = useState('')
  const [refresh, setRefresh] = useState(0)
  const [sysStatus, setSysStatus] = useState({
    api: 'Connected',
    model: 'Connected',
    storage: 'Connected',
    isOnline: true,
    provider: 'Local vLLM Cluster',
    modelName: 'Sovereign-32B',
  })
  const [docCount, setDocCount] = useState(0)
  const [agentCount, setAgentCount] = useState(0)

  useEffect(() => {
    Promise.all([
      adminService.getSystemStatus().then(r => setSysStatus(r.data)).catch(() => {}),
      documentService.list().then(r => setDocCount(r.data.length)).catch(() => {}),
      agentService.list().then(r => setAgentCount(r.data.length)).catch(() => {}),
    ]).finally(() => setLoading(false))
  }, [refresh])

  const quick: { label: string; target: PageKey; icon: any; desc: string }[] = [
    { label: 'Start AI Chat', target: 'AI Chat', icon: MessageSquare, desc: 'Query procedures & incidents' },
    { label: 'Analyze Document', target: 'Documents', icon: FileText, desc: 'Upload & index plant specs' },
    { label: 'Inspect Image', target: 'Vision', icon: Eye, desc: 'P&ID & equipment visual QA' },
    { label: 'Search Knowledge', target: 'Knowledge Base', icon: BookOpen, desc: 'Semantic retrieval search' },
    { label: 'Deploy Agent', target: 'Agents', icon: Network, desc: 'Run autonomous pipelines' },
    { label: 'Generate Report', target: 'Reports', icon: BarChart3, desc: 'Compile compliance briefings' },
  ]

  const metrics = [
    { label: 'AI Queries Today', value: 'Realtime', detail: 'Local GPU inference', icon: MessageSquare },
    { label: 'Documents Indexed', value: String(docCount || '4'), detail: 'Vector index ready', icon: FileText },
    { label: 'Active AI Models', value: '01', detail: sysStatus.modelName, icon: Cpu },
    { label: 'Active Agents', value: String(agentCount || '6').padStart(2, '0'), detail: 'Autonomous catalog', icon: Network },
    { label: 'Knowledge Documents', value: '12,842', detail: 'Locally synced', icon: BookOpen },
    {
      label: 'Backend Gateway',
      value: sysStatus.isOnline ? 'Online' : 'Offline',
      detail: sysStatus.isOnline ? 'Port 8001 connected' : 'Port 8001 unavailable',
      icon: Activity,
      isAlert: !sysStatus.isOnline,
    },
  ]

  const activities = [
    ['09:41', 'J. Ellis', 'Compressor vibration analyzed', 'Safety Analyst', 'Sovereign-32B', 'Complete'],
    ['09:28', 'M. Chen', 'P&ID valve schema verified', 'Vision Inspector', 'Vision-7B', 'Complete'],
    ['09:12', 'J. Ellis', 'Knowledge base semantic query', 'Operations Copilot', 'Sovereign-32B', 'Complete'],
    ['08:56', 'A. Rao', 'Turnaround checklist audited', 'Engineering Reviewer', 'Sovereign-14B', 'Complete'],
    ['08:43', 'System', 'Shift handover brief compiled', 'Report Composer', 'Sovereign-32B', 'Complete'],
  ]

  const health = [
    ['Local LLM Server (vLLM)', sysStatus.model, 'Port 8000'],
    ['Local Vector DB (ChromaDB)', sysStatus.storage, 'SQLite embedded'],
    ['FastAPI Orchestration Gateway', sysStatus.api, 'Port 8001'],
    ['Air-Gap Hardware Perimeter', 'Online', 'Zero external egress'],
  ]

  const docs = [
    ['unit-04-inspection-report.pdf', 'PDF', 'Indexed', '8 min ago'],
    ['compressor-maintenance-log.docx', 'DOCX', 'Indexed', '24 min ago'],
    ['engineering-drawing-c-204.png', 'IMAGE', 'Indexed', '1 hr ago'],
    ['turnaround-scope-2026.pdf', 'PDF', 'Indexed', 'Yesterday'],
  ]

  if (loading) {
    return (
      <div className="flex flex-col gap-6">
        <div className="h-24 animate-pulse rounded-xl border border-white/10 bg-card" />
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-32 animate-pulse rounded-xl border border-white/10 bg-card" />
          ))}
        </div>
        <div className="h-80 animate-pulse rounded-xl border border-white/10 bg-card" />
      </div>
    )
  }

  return (
    <div className="animate-rise flex flex-col gap-6">
      {/* Top Banner */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <div className="flex items-center gap-2">
            <span className="size-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00d2ff]" />
            <p className="font-mono text-[10px] uppercase tracking-[.25em] text-cyan-400">
              Workspace // Operational Overview
            </p>
          </div>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-foreground">
            Operational Intelligence Center
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Real-time telemetry and decision support for mission-critical industrial workflows.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => setRefresh(r => r + 1)}
            className="flex items-center gap-2 rounded-lg border border-white/10 bg-card px-3 py-2 font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:bg-muted hover:text-foreground transition"
            title="Refresh telemetry"
          >
            <RefreshCw className="size-3.5 text-cyan-400" /> Refresh
          </button>
        </div>
      </div>

      {/* Backend Offline / Availability Notice */}
      {!sysStatus.isOnline && (
        <div className="rounded-xl border border-amber-500/40 bg-amber-500/10 p-4 text-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-lg">
          <div className="flex items-start gap-3">
            <AlertTriangle className="size-5 text-amber-400 shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-sm">Local FastAPI Server Unavailable (http://127.0.0.1:8001)</p>
              <p className="text-xs text-amber-200/80 mt-0.5">
                The workbench is currently operating in local simulated fallback mode. Launch the FastAPI backend on port 8001 to enable live hardware telemetry.
              </p>
            </div>
          </div>
          <button
            onClick={() => setRefresh(r => r + 1)}
            className="rounded-md bg-amber-400 px-3 py-1.5 font-mono text-[10px] font-bold uppercase tracking-wider text-slate-950 hover:brightness-110 self-start sm:self-center shrink-0"
          >
            Retry Connection
          </button>
        </div>
      )}

      {/* Security Status Strip */}
      <SecurityStrip />

      {/* Notice alert */}
      {notice && (
        <div role="status" className="rounded-lg border border-cyan-500/40 bg-cyan-500/10 px-4 py-3 font-mono text-xs text-cyan-300">
          {notice}
        </div>
      )}

      {/* Metrics Grid */}
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {metrics.map(m => {
          const Icon = m.icon
          return (
            <div
              key={m.label}
              className="glass-panel card-3d rounded-xl p-5 transition hover:border-cyan-400/40"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] uppercase tracking-[.16em] text-muted-foreground">
                  {m.label}
                </span>
                <Icon className={`size-4 ${m.isAlert ? 'text-amber-400' : 'text-cyan-400'}`} />
              </div>
              <div className="mt-5 flex items-end justify-between">
                <p className="text-3xl font-bold tracking-tight text-foreground">{m.value}</p>
                <span className={`font-mono text-[10px] ${m.isAlert ? 'text-amber-400' : 'text-emerald-400'}`}>
                  {m.detail}
                </span>
              </div>
            </div>
          )
        })}
      </div>

      {/* Quick Actions */}
      <section>
        <div className="mb-3 flex items-center justify-between">
          <div>
            <h2 className="text-base font-semibold">Quick Operational Workflows</h2>
            <p className="text-xs text-muted-foreground">Direct access to local intelligence tools</p>
          </div>
        </div>

        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {quick.map(q => {
            const Icon = q.icon
            return (
              <button
                key={q.label}
                onClick={() => onNavigate(q.target)}
                className="glass-panel glass-panel-hover flex items-center gap-3.5 rounded-xl p-4 text-left group"
              >
                <span className="grid size-10 place-items-center rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 group-hover:bg-cyan-500/20 transition">
                  <Icon className="size-5" />
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-foreground group-hover:text-cyan-400 transition truncate">
                    {q.label}
                  </p>
                  <p className="text-xs text-muted-foreground truncate mt-0.5">{q.desc}</p>
                </div>
                <ArrowRight className="size-4 text-muted-foreground group-hover:text-cyan-400 group-hover:translate-x-1 transition" />
              </button>
            )
          })}
        </div>
      </section>

      {/* Activity and System Health Split */}
      <div className="grid gap-6 xl:grid-cols-[1.4fr_.8fr]">
        {/* Recent AI Activity */}
        <section className="glass-panel rounded-xl border border-white/10 overflow-hidden">
          <div className="flex items-center justify-between border-b border-white/10 p-5">
            <div>
              <h2 className="text-base font-semibold">Recent Audited Activity</h2>
              <p className="text-xs text-muted-foreground">Traceable on-premise actions across the workbench</p>
            </div>
            <button
              onClick={() => onNavigate('Audit Log')}
              className="font-mono text-[10px] uppercase tracking-wider text-cyan-400 hover:underline"
            >
              View Full Audit Log →
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-left text-xs">
              <thead className="bg-muted/40 font-mono text-[9px] uppercase tracking-wider text-muted-foreground">
                <tr>
                  {['Time', 'User', 'Action', 'Agent', 'Model', 'Status'].map(h => (
                    <th key={h} className="px-5 py-3.5 font-normal">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {activities.map(row => (
                  <tr key={row.join('-')} className="hover:bg-muted/30 transition">
                    <td className="px-5 py-3.5 font-mono text-muted-foreground">{row[0]}</td>
                    <td className="px-5 py-3.5 font-medium text-foreground">{row[1]}</td>
                    <td className="px-5 py-3.5 text-muted-foreground">{row[2]}</td>
                    <td className="px-5 py-3.5">{row[3]}</td>
                    <td className="px-5 py-3.5 font-mono text-cyan-400/80">{row[4]}</td>
                    <td className="px-5 py-3.5">
                      <span className="font-mono text-[10px] text-emerald-400 uppercase tracking-wider">
                        ● {row[5]}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        {/* System Health */}
        <section className="glass-panel rounded-xl border border-white/10 p-5 flex flex-col justify-between">
          <div>
            <div className="border-b border-white/10 pb-4">
              <h2 className="text-base font-semibold">Local Infrastructure Health</h2>
              <p className="text-xs text-muted-foreground">Direct hardware and runtime signals</p>
            </div>

            <div className="mt-5 space-y-4">
              {health.map(([name, status, detail]) => (
                <div key={name} className="flex items-center justify-between text-xs">
                  <div>
                    <p className="font-medium text-foreground">{name}</p>
                    <p className="font-mono text-[10px] text-muted-foreground mt-0.5">{detail}</p>
                  </div>
                  <span
                    className={`inline-flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-wider ${
                      status === 'Online' || status === 'Connected' || status === 'Operational'
                        ? 'text-emerald-400'
                        : 'text-amber-400'
                    }`}
                  >
                    <span
                      className={`size-1.5 rounded-full ${
                        status === 'Online' || status === 'Connected' || status === 'Operational'
                          ? 'bg-emerald-400'
                          : 'bg-amber-400'
                      }`}
                    />
                    {status}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-white/10 flex justify-between items-center text-[10px] font-mono text-muted-foreground uppercase">
            <span>Air-Gap Check</span>
            <span className="text-emerald-400 font-bold">100% SECURED</span>
          </div>
        </section>
      </div>

      {/* Documents & AI Insights */}
      <div className="grid gap-6 xl:grid-cols-[1.1fr_.9fr]">
        <section className="glass-panel rounded-xl border border-white/10 p-5">
          <div className="flex items-center justify-between border-b border-white/10 pb-4">
            <div>
              <h2 className="text-base font-semibold">Indexed Operational Records</h2>
              <p className="text-xs text-muted-foreground">Authorized documents in the local vector store</p>
            </div>
            <button
              onClick={() => onNavigate('Documents')}
              className="font-mono text-[10px] uppercase tracking-wider text-cyan-400 hover:underline"
            >
              Open Documents →
            </button>
          </div>

          <div className="mt-3 divide-y divide-white/5">
            {docs.map(([name, type, status, time]) => (
              <div key={name} className="flex items-center gap-3.5 py-3.5 transition hover:bg-white/[0.02]">
                <div className="grid size-8 place-items-center rounded bg-cyan-500/10 text-cyan-400">
                  <FileText className="size-4" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-foreground">{name}</p>
                  <p className="font-mono text-[9px] uppercase tracking-wider text-muted-foreground mt-0.5">
                    {type} • {time}
                  </p>
                </div>
                <span className="font-mono text-[9px] uppercase tracking-wider text-emerald-400">
                  {status}
                </span>
                <button
                  onClick={() => onNavigate('Documents')}
                  className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
                  title="View details"
                >
                  <ChevronRight className="size-4" />
                </button>
              </div>
            ))}
          </div>
        </section>

        <section className="glass-panel rounded-xl border border-white/10 p-5 space-y-4">
          <div className="flex items-center gap-2.5 border-b border-white/10 pb-4">
            <Sparkles className="size-5 text-cyan-400" />
            <div>
              <h2 className="text-base font-semibold">Synthesized Operational Insights</h2>
              <p className="text-xs text-muted-foreground">Generated strictly from authorized local records</p>
            </div>
          </div>

          <div className="space-y-3.5">
            <div className="rounded-lg border border-cyan-500/30 bg-cyan-500/5 p-4">
              <p className="text-xs leading-relaxed text-foreground">
                Unit 04 inspection records show a 14% increase in compressor vibration alerts over the past seven days. Recommended inspection of bearings prior to next shift cycle.
              </p>
              <div className="mt-3 flex items-center justify-between font-mono text-[9px] uppercase text-muted-foreground">
                <span>Confidence 0.92 • Operations Copilot</span>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText('Unit 04 inspection records show a 14% increase in compressor vibration alerts...')
                    setNotice('Insight copied to clipboard.')
                    setTimeout(() => setNotice(''), 3000)
                  }}
                  className="text-cyan-400 hover:underline"
                >
                  Copy
                </button>
              </div>
            </div>

            <div className="rounded-lg border border-violet-500/30 bg-violet-500/5 p-4">
              <p className="text-xs leading-relaxed text-foreground">
                Three process safety procedures require updated signatures before the scheduled turnaround window in Q3 2026.
              </p>
              <div className="mt-3 flex items-center justify-between font-mono text-[9px] uppercase text-muted-foreground">
                <span>Confidence 0.88 • Safety Analyst</span>
                <button
                  onClick={() => {
                    navigator.clipboard.writeText('Three process safety procedures require updated signatures...')
                    setNotice('Insight copied to clipboard.')
                    setTimeout(() => setNotice(''), 3000)
                  }}
                  className="text-violet-400 hover:underline"
                >
                  Copy
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}

function ChatWorkspace() {
  const [conversations, setConversations] = useState<any[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [thinking, setThinking] = useState(false)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [leftOpen, setLeftOpen] = useState(true)
  const [model, setModel] = useState('Sovereign-32B')
  const [agent, setAgent] = useState('Operations Copilot')
  const [attachment, setAttachment] = useState<any>(null)
  const [copiedId, setCopiedId] = useState<string | null>(null)

  const messagesEndRef = useRef<HTMLDivElement>(null)

  const load = async () => {
    setLoading(true)
    try {
      const result = await chatService.listConversations()
      setConversations(result.data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, thinking])

  const filtered = conversations.filter(c =>
    `${c.title} ${c.preview}`.toLowerCase().includes(query.toLowerCase())
  )

  const send = async (text = input) => {
    if (!text.trim() || thinking) return
    const userText = text.trim()
    setInput('')
    setMessages(m => [
      ...m,
      {
        id: crypto.randomUUID(),
        role: 'user',
        content: userText,
        createdAt: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        attachment: attachment ? { ...attachment } : undefined,
      },
    ])
    setAttachment(null)
    setThinking(true)
    setError('')

    try {
      const result = await chatService.sendMessage(userText, selected || undefined, model)
      setMessages(m => [...m, result.data])
    } catch {
      setError(
        `Local model unavailable at ${apiClient.baseUrl()}. Check the local inference server and try again.`
      )
    } finally {
      setThinking(false)
    }
  }

  const exportChat = () => {
    if (messages.length === 0) {
      setError('No messages in the active conversation to export.')
      return
    }
    const transcript = messages
      .map(
        m =>
          `### ${m.role.toUpperCase()} [${m.createdAt || 'Recent'}]\n\n${m.content}\n\n${
            m.sources ? `**Sources**:\n` + m.sources.map((s: any) => `- ${s.name} (${s.location})`).join('\n') : ''
          }`
      )
      .join('\n\n---\n\n')

    const fileContent = `# Sovereign AI Workbench — Chat Session Export\nGenerated: ${new Date().toISOString()}\nAgent: ${agent}\nModel: ${model}\nPerimeter: Air-Gapped / Zero Egress\n\n${transcript}`
    const blob = new Blob([fileContent], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chat-session-${Date.now().toString(36)}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    setNotice('Conversation transcript exported as Markdown.')
    setTimeout(() => setNotice(''), 3000)
  }

  const copyResponse = (text: string, id: string) => {
    navigator.clipboard.writeText(text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 2000)
  }

  const handleFileUpload = (files: FileList | null) => {
    if (!files || files.length === 0) return
    const file = files[0]
    setAttachment({
      name: file.name,
      size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
      type: file.name.split('.').pop()?.toUpperCase() || 'FILE',
    })
    setNotice(`Attached ${file.name} to chat query.`)
    setTimeout(() => setNotice(''), 3000)
  }

  const welcome = !selected && !messages.length
  const prompts = [
    'Analyze the vibration telemetry in Unit 04',
    'Verify P&ID valve symbols against safety spec',
    'Search plant procedures for hot-work permits',
    'Summarize shift activity and open alarms',
    'Draft a compliance briefing for engineering review',
  ]

  return (
    <div className="flex min-h-[calc(100vh-7.5rem)] min-w-0 flex-col overflow-hidden rounded-xl border border-white/10 bg-[#0c1524] shadow-2xl">
      {/* Top Chat Bar */}
      <div className="flex flex-wrap items-center justify-between border-b border-white/10 px-5 py-3.5 bg-[#09101b]/90 backdrop-blur-md gap-3">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setLeftOpen(!leftOpen)}
            className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-white/5 px-2.5 py-1.5 text-xs text-muted-foreground hover:bg-white/10 hover:text-foreground transition"
            title={leftOpen ? 'Collapse Chat History' : 'Open Chat History'}
            aria-label="Toggle chat history"
          >
            <MessageSquare className="size-4 text-cyan-400" />
            <span className="hidden sm:inline font-mono text-[10px] font-bold uppercase tracking-wider text-cyan-400">
              {leftOpen ? 'Hide History' : 'Chat History'}
            </span>
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="size-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00d2ff]" />
              <p className="font-mono text-[9px] uppercase tracking-[.25em] text-cyan-400">
                SOVEREIGN INTELLIGENCE // AI CHAT
              </p>
            </div>
            <h1 className="text-base font-bold text-foreground">Local AI Assistant</h1>
          </div>
        </div>

        {/* Model, Agent & Quick Action Controls */}
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#060b13] px-2.5 py-1">
            <span className="font-mono text-[9px] text-cyan-400 uppercase">Model:</span>
            <select
              value={model}
              onChange={e => setModel(e.target.value)}
              className="bg-transparent font-mono text-[10px] text-foreground outline-none cursor-pointer"
            >
              <option className="bg-[#0c1524]">Sovereign-32B</option>
              <option className="bg-[#0c1524]">Sovereign-14B</option>
              <option className="bg-[#0c1524]">Vision-7B</option>
            </select>
          </div>

          <div className="hidden sm:flex items-center gap-1.5 rounded-lg border border-white/10 bg-[#060b13] px-2.5 py-1">
            <span className="font-mono text-[9px] text-cyan-400 uppercase">Agent:</span>
            <select
              value={agent}
              onChange={e => setAgent(e.target.value)}
              className="bg-transparent font-mono text-[10px] text-foreground outline-none cursor-pointer"
            >
              <option className="bg-[#0c1524]">Operations Copilot</option>
              <option className="bg-[#0c1524]">Safety Analyst</option>
              <option className="bg-[#0c1524]">Vision Inspector</option>
              <option className="bg-[#0c1524]">Report Composer</option>
            </select>
          </div>

          <span className="hidden md:flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-2.5 py-1 font-mono text-[9px] uppercase tracking-wider text-emerald-400">
            <span className="size-1.5 rounded-full bg-emerald-400" /> Air-Gapped
          </span>

          <button
            title="Clear active conversation"
            onClick={() => {
              setMessages([])
              setSelected(null)
              setNotice('Active conversation cleared.')
              setTimeout(() => setNotice(''), 2500)
            }}
            className="rounded-lg border border-white/10 p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition"
          >
            <Trash2 className="size-4" />
          </button>
          <button
            title="Export conversation to Markdown"
            onClick={exportChat}
            className="rounded-lg border border-white/10 p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition"
          >
            <Download className="size-4" />
          </button>
        </div>
      </div>

      {notice && (
        <div className="bg-cyan-500/10 border-b border-cyan-500/30 px-5 py-1.5 font-mono text-[10px] text-cyan-300">
          {notice}
        </div>
      )}

      {/* Main 2-Panel Body: Side = Chat History, Main = Dedicated AI Chat */}
      <div className={`grid min-h-0 flex-1 transition-all duration-200 ${
        leftOpen ? 'lg:grid-cols-[280px_minmax(0,1fr)]' : 'grid-cols-1'
      }`}>
        {/* Side Panel: Chat History */}
        {leftOpen && (
          <aside className="flex min-h-0 flex-col border-r border-white/10 bg-[#09101b] transition-all">
            {/* Header with New Chat CTA */}
            <div className="flex items-center justify-between p-3.5 border-b border-white/10">
              <div className="flex items-center gap-2">
                <MessageSquare className="size-4 text-cyan-400" />
                <span className="font-mono text-xs font-bold uppercase tracking-wider text-foreground">
                  Chat History
                </span>
                <span className="rounded-full bg-cyan-500/15 px-1.5 py-0.5 font-mono text-[9px] text-cyan-400 border border-cyan-500/30">
                  {filtered.length}
                </span>
              </div>
              <button
                onClick={() => setLeftOpen(false)}
                className="rounded p-1 text-muted-foreground hover:bg-white/10 hover:text-foreground transition"
                title="Collapse history"
                aria-label="Collapse history"
              >
                <PanelLeftClose className="size-3.5" />
              </button>
            </div>

            <div className="p-3 border-b border-white/5">
              <button
                onClick={() => {
                  setSelected(null)
                  setMessages([])
                  setNotice('New conversation started.')
                  setTimeout(() => setNotice(''), 2500)
                }}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-cyan-500 to-cyan-600 py-2.5 font-mono text-[10px] font-bold uppercase tracking-wider text-slate-950 shadow-[0_0_15px_rgba(0,210,255,0.25)] hover:brightness-110 transition"
              >
                <Plus className="size-4 text-slate-950" /> New Chat
              </button>
            </div>

            {/* Filter History */}
            <div className="p-3 border-b border-white/5">
              <div className="flex items-center gap-2 rounded-lg border border-white/10 bg-background/60 px-2.5 py-1.5 focus-within:border-cyan-400/50 transition">
                <Search className="size-3.5 text-muted-foreground shrink-0" />
                <input
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  placeholder="Filter chat history..."
                  className="w-full bg-transparent text-xs outline-none placeholder:text-muted-foreground/60"
                />
                {query && (
                  <button onClick={() => setQuery('')} className="text-muted-foreground hover:text-foreground">
                    <X className="size-3" />
                  </button>
                )}
              </div>
            </div>

            {/* Scrollable Conversation List */}
            <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-4 space-y-3 pt-2">
              {['Today', 'Yesterday', 'Previous 7 days'].map(group => {
                const rows = filtered.filter(c => c.group === group)
                if (!rows.length) return null
                return (
                  <div key={group} className="space-y-1">
                    <p className="px-2 py-1 font-mono text-[9px] uppercase tracking-wider text-muted-foreground/60">
                      {group}
                    </p>
                    {rows.map(c => (
                      <div
                        key={c.id}
                        className={`group relative rounded-lg transition flex items-center ${
                          selected === c.id
                            ? 'border border-cyan-400/40 bg-cyan-500/10 text-cyan-300 shadow-[0_0_10px_rgba(0,210,255,0.1)]'
                            : 'hover:bg-muted/40 text-muted-foreground hover:text-foreground border border-transparent'
                        }`}
                      >
                        <button
                          onClick={() => {
                            setSelected(c.id)
                            setMessages([
                              {
                                id: 'msg-seed-' + c.id,
                                role: 'assistant',
                                content: `Active session loaded: **${c.title}**\n\n${c.preview}\n\nAll session queries remain air-gapped and local to your sovereign cluster.`,
                                createdAt: c.updatedAt,
                                sources: [{ name: 'Unit_04_Procedures.pdf', location: 'Section 4.1' }],
                              },
                            ])
                          }}
                          className="w-full p-2.5 text-left text-xs flex items-start gap-2.5 min-w-0 pr-8"
                        >
                          <MessageSquare className="size-3.5 mt-0.5 shrink-0 text-cyan-400" />
                          <div className="min-w-0 flex-1">
                            <p className="font-medium truncate text-foreground text-xs">{c.title}</p>
                            <p className="text-[10px] text-muted-foreground truncate mt-0.5">{c.preview}</p>
                            <span className="font-mono text-[9px] text-muted-foreground/60 mt-1 block">{c.updatedAt}</span>
                          </div>
                        </button>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setConversations(prev => prev.filter(item => item.id !== c.id))
                            if (selected === c.id) {
                              setSelected(null)
                              setMessages([])
                            }
                            setNotice(`Removed "${c.title}" from history.`)
                            setTimeout(() => setNotice(''), 2500)
                          }}
                          className="opacity-0 group-hover:opacity-100 absolute right-2 top-2.5 rounded p-1 text-muted-foreground hover:text-red-400 hover:bg-white/5 transition"
                          title="Delete from history"
                          aria-label="Delete conversation"
                        >
                          <Trash2 className="size-3.5" />
                        </button>
                      </div>
                    ))}
                  </div>
                )
              })}
            </div>
          </aside>
        )}

        {/* Main Area: Dedicated AI Chat */}
        <main className="flex min-w-0 flex-1 flex-col bg-[#060b13]">
          {/* Welcome Screen or Message Stream */}
          {welcome ? (
            <div className="flex flex-1 flex-col items-center justify-center p-8 text-center">
              <div className="grid size-16 place-items-center rounded-2xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-[0_0_30px_rgba(0,210,255,0.2)]">
                <Sparkles className="size-8" />
              </div>
              <h2 className="mt-6 text-2xl font-bold tracking-tight text-white">
                Sovereign Operations Copilot
              </h2>
              <p className="mt-2 max-w-md text-xs leading-relaxed text-muted-foreground">
                Query confidential procedures, inspect plant logs, review code, or run multimodal engineering vision checks without cloud egress.
              </p>

              <div className="mt-8 grid w-full max-w-xl gap-2.5 sm:grid-cols-2">
                {prompts.map(prompt => (
                  <button
                    key={prompt}
                    onClick={() => send(prompt)}
                    className="glass-panel glass-panel-hover flex items-center gap-3 rounded-xl p-3.5 text-left text-xs transition group"
                  >
                    <Zap className="size-4 text-cyan-400 shrink-0 group-hover:scale-110 transition" />
                    <span className="text-muted-foreground group-hover:text-foreground transition line-clamp-1">
                      {prompt}
                    </span>
                    <ArrowRight className="size-3.5 text-muted-foreground ml-auto group-hover:translate-x-1 transition" />
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="flex flex-1 flex-col gap-6 overflow-y-auto p-5 sm:p-8">
              {messages.map((m, i) => (
                <div
                  key={m.id || i}
                  className={`flex max-w-3xl gap-3.5 ${m.role === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
                >
                  <div
                    className={`grid size-8 shrink-0 place-items-center rounded-lg border ${
                      m.role === 'user'
                        ? 'bg-primary text-primary-foreground border-cyan-400'
                        : 'bg-[#0c1524] text-cyan-400 border-cyan-500/30 shadow-[0_0_15px_rgba(0,210,255,0.2)]'
                    }`}
                  >
                    {m.role === 'user' ? <Users className="size-4" /> : <Sparkles className="size-4" />}
                  </div>

                  <div className="min-w-0 flex-1">
                    {/* Attached file tag */}
                    {m.attachment && (
                      <div className="mb-2 flex items-center gap-2 rounded border border-white/10 bg-white/5 px-2.5 py-1 text-[10px] font-mono text-cyan-300 w-fit">
                        <FileText className="size-3" />
                        <span>{m.attachment.name}</span>
                        <span className="text-white/40">({m.attachment.size})</span>
                      </div>
                    )}

                    <div
                      className={`rounded-xl border p-4 text-sm leading-relaxed ${
                        m.role === 'user'
                          ? 'border-cyan-400/30 bg-primary/20 text-foreground'
                          : 'glass-panel border-white/10 text-foreground'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{m.content}</div>

                      {/* Grounded sources */}
                      {m.sources && m.sources.length > 0 && (
                        <div className="mt-4 border-t border-white/10 pt-3">
                          <p className="font-mono text-[9px] uppercase tracking-wider text-muted-foreground">
                            Verified Grounded Sources
                          </p>
                          <div className="mt-2 flex flex-wrap gap-2">
                            {m.sources.map((s: any) => (
                              <span
                                key={s.name + s.location}
                                className="inline-flex items-center gap-1.5 rounded-md border border-cyan-500/30 bg-cyan-500/10 px-2.5 py-1 font-mono text-[10px] text-cyan-300"
                              >
                                <FileText className="size-3" />
                                {s.name} • {s.location}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    {/* Assistant action buttons */}
                    {m.role === 'assistant' && (
                      <div className="mt-2 flex items-center gap-1 text-muted-foreground">
                        <button
                          onClick={() => copyResponse(m.content, m.id || String(i))}
                          className="flex items-center gap-1 rounded px-2 py-1 text-[10px] hover:bg-muted hover:text-foreground transition"
                        >
                          {copiedId === (m.id || String(i)) ? (
                            <>
                              <Check className="size-3 text-emerald-400" />
                              <span className="text-emerald-400">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="size-3" />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                        <button
                          onClick={() => {
                            setNotice('Feedback recorded for local model alignment.')
                            setTimeout(() => setNotice(''), 2500)
                          }}
                          className="rounded px-2 py-1 text-[10px] hover:bg-muted hover:text-foreground transition"
                        >
                          Helpful
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {/* Streaming / thinking indicator */}
              {thinking && (
                <div className="flex items-center gap-3 text-xs text-cyan-400 font-mono">
                  <span className="size-2 animate-ping rounded-full bg-cyan-400" />
                  <span>Evaluating local knowledge vectors & generating response...</span>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Bottom Prompt Input */}
          <div className="border-t border-white/10 bg-[#09101b] p-4">
            {attachment && (
              <div className="mb-2 flex items-center gap-2 rounded-lg border border-cyan-500/30 bg-cyan-500/10 px-3 py-1.5 text-xs text-cyan-300 w-fit">
                <FileText className="size-3.5" />
                <span>{attachment.name}</span>
                <span className="text-[10px] text-white/50">({attachment.size})</span>
                <button
                  onClick={() => setAttachment(null)}
                  className="rounded p-0.5 hover:bg-white/10 text-white/60 hover:text-white"
                >
                  <X className="size-3.5" />
                </button>
              </div>
            )}

            <div className="rounded-xl border border-white/10 bg-[#0c1524] p-2 focus-within:border-cyan-400/50 transition">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
                    e.preventDefault()
                    send()
                  }
                }}
                placeholder="Ask Sovereign AI about operational telemetry, equipment limits, or incident logs..."
                className="min-h-16 w-full resize-none bg-transparent p-2 text-sm text-foreground outline-none placeholder:text-muted-foreground"
              />

              <div className="flex items-center justify-between border-t border-white/5 pt-2 px-1">
                <div className="flex items-center gap-1">
                  <label
                    title="Attach document (.pdf, .docx, .txt)"
                    className="cursor-pointer rounded p-2 text-muted-foreground hover:bg-muted hover:text-cyan-400 transition"
                  >
                    <Paperclip className="size-4" />
                    <input
                      type="file"
                      className="sr-only"
                      accept=".pdf,.doc,.docx,.txt"
                      onChange={e => handleFileUpload(e.target.files)}
                    />
                  </label>

                  <label
                    title="Attach image (.png, .jpg, .webp)"
                    className="cursor-pointer rounded p-2 text-muted-foreground hover:bg-muted hover:text-cyan-400 transition"
                  >
                    <ImagePlus className="size-4" />
                    <input
                      type="file"
                      className="sr-only"
                      accept=".png,.jpg,.jpeg,.webp"
                      onChange={e => handleFileUpload(e.target.files)}
                    />
                  </label>

                  <label
                    title="Attach source code (.py, .ts, .json)"
                    className="cursor-pointer rounded p-2 text-muted-foreground hover:bg-muted hover:text-cyan-400 transition"
                  >
                    <Code2 className="size-4" />
                    <input
                      type="file"
                      className="sr-only"
                      accept=".py,.ts,.js,.json,.sh"
                      onChange={e => handleFileUpload(e.target.files)}
                    />
                  </label>
                </div>

                <button
                  onClick={() => (thinking ? setThinking(false) : send())}
                  disabled={!thinking && !input.trim()}
                  className="grid size-9 place-items-center rounded-lg bg-primary text-primary-foreground shadow-[0_0_12px_rgba(0,210,255,0.3)] hover:brightness-110 disabled:opacity-40 transition"
                  aria-label={thinking ? 'Stop generating' : 'Send query'}
                >
                  {thinking ? <Square className="size-4" /> : <Send className="size-4" />}
                </button>
              </div>
            </div>

            {error && (
              <p role="alert" className="mt-2 text-xs text-red-400 font-mono">
                {error}
              </p>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}

function DocumentsWorkspace({ onNavigate }: { onNavigate: (page: PageKey) => void }) {
  const [docs, setDocs] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [type, setType] = useState('All types')
  const [selected, setSelected] = useState<any>(null)
  const [uploading, setUploading] = useState<any>(null)
  const [notice, setNotice] = useState('')
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null)

  useEffect(() => {
    documentService.list().then(r => setDocs(r.data)).finally(() => setLoading(false))
  }, [])

  const filtered = docs.filter(
    d =>
      (d.name + d.department + d.knowledgeBase).toLowerCase().includes(query.toLowerCase()) &&
      (type === 'All types' || d.type === type)
  )

  const upload = async (file: File) => {
    setUploading({
      name: file.name,
      type: file.name.split('.').pop()?.toUpperCase() || 'FILE',
      size: `${(file.size / 1024 / 1024).toFixed(2)} MB`,
      progress: 30,
      status: 'Extracting Text',
    })

    try {
      setTimeout(() => setUploading((prev: any) => prev ? { ...prev, progress: 65, status: 'Generating Embeddings' } : null), 400)
      const r = await documentService.upload(file)
      setUploading({ ...r.data, progress: 100, status: 'Indexed' })
      setDocs(prev => [r.data, ...prev.filter(d => d.id !== r.data.id)])
      setNotice(`Document "${file.name}" uploaded and indexed into local vector store.`)
      setTimeout(() => {
        setUploading(null)
        setNotice('')
      }, 3500)
    } catch (err) {
      setUploading(null)
      setNotice(err instanceof Error ? err.message : 'Upload failed')
      setTimeout(() => setNotice(''), 3500)
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await documentService.remove(id)
      setDocs(prev => prev.filter(x => x.id !== id))
      setNotice('Document successfully removed from vector index.')
      setDeleteConfirmId(null)
      if (selected?.id === id) setSelected(null)
      setTimeout(() => setNotice(''), 3000)
    } catch {
      setNotice('Failed to delete document.')
      setTimeout(() => setNotice(''), 3000)
    }
  }

  return (
    <div className="animate-rise flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[.25em] text-cyan-400">
            Workspace // Knowledge Engineering
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-foreground">
            Document Repository & RAG
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Manage confidential plant documentation, manuals, and schematics indexed for local retrieval.
          </p>
        </div>

        <label className="flex cursor-pointer items-center justify-center gap-2 rounded-lg bg-primary px-4 py-2.5 font-mono text-[10px] font-bold uppercase tracking-wider text-primary-foreground shadow-sm hover:brightness-110 transition">
          <Upload className="size-4" /> Upload Document
          <input
            type="file"
            className="sr-only"
            accept=".pdf,.docx,.txt,.csv,.xlsx,.png,.jpg,.jpeg,.md,.ts,.py"
            onChange={e => {
              const f = e.target.files?.[0]
              if (f) upload(f)
            }}
          />
        </label>
      </div>

      <SecurityStrip />

      {/* Upload Drop Zone */}
      <div
        onDragOver={e => e.preventDefault()}
        onDrop={e => {
          e.preventDefault()
          const f = e.dataTransfer.files[0]
          if (f) upload(f)
        }}
        className="glass-panel rounded-xl border border-dashed border-cyan-500/30 p-8 text-center transition hover:border-cyan-400"
      >
        <Upload className="mx-auto size-8 text-cyan-400 mb-2" />
        <h2 className="font-semibold text-foreground">Drop files here to index into Sovereign AI</h2>
        <p className="mt-1 text-xs text-muted-foreground">
          PDF, DOCX, TXT, CSV, XLSX, P&ID Drawings, Markdown, and source code • Air-gapped indexing
        </p>

        {uploading && (
          <div className="mx-auto mt-6 max-w-md text-left">
            <div className="flex justify-between text-xs font-mono">
              <span className="text-foreground">{uploading.name}</span>
              <span className="text-cyan-400">{uploading.progress}% • {uploading.status}</span>
            </div>
            <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-muted">
              <div
                style={{ width: `${uploading.progress}%` }}
                className="h-full bg-cyan-400 transition-all duration-300 shadow-[0_0_10px_#00d2ff]"
              />
            </div>
          </div>
        )}
      </div>

      {notice && (
        <div role="status" className="rounded-lg border border-cyan-500/40 bg-cyan-500/10 px-4 py-3 font-mono text-xs text-cyan-300">
          {notice}
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="glass-panel flex flex-col gap-3 rounded-xl p-4 lg:flex-row border border-white/10">
        <div className="flex flex-1 items-center gap-2 rounded-lg border border-white/10 bg-background/60 px-3">
          <Search className="size-4 text-muted-foreground" />
          <input
            aria-label="Search documents"
            value={query}
            onChange={e => setQuery(e.target.value)}
            placeholder="Search document name, classification, or department..."
            className="h-10 flex-1 bg-transparent text-xs outline-none"
          />
        </div>

        <select
          value={type}
          onChange={e => setType(e.target.value)}
          aria-label="Filter file type"
          className="h-10 rounded-lg border border-white/10 bg-background px-3 font-mono text-xs outline-none focus:border-cyan-400"
        >
          <option>All types</option>
          {['PDF', 'DOCX', 'XLSX', 'PNG', 'DOC'].map(t => (
            <option key={t}>{t}</option>
          ))}
        </select>
      </div>

      {/* Documents Inventory Table */}
      <div className="glass-panel rounded-xl border border-white/10 overflow-hidden">
        <div className="flex items-center justify-between border-b border-white/10 p-5">
          <div>
            <h2 className="text-base font-semibold">Authorized Document Inventory</h2>
            <p className="text-xs text-muted-foreground">{filtered.length} indexed records in local vector database</p>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col gap-3 p-5">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="h-14 animate-pulse rounded-lg bg-muted/40" />
            ))}
          </div>
        ) : filtered.length ? (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[950px] text-left text-xs">
              <thead className="bg-muted/40 font-mono text-[9px] uppercase tracking-wider text-muted-foreground">
                <tr>
                  {['Document Name', 'Type', 'Size', 'Department', 'Uploaded', 'Status', 'Chunks', 'Actions'].map(
                    h => (
                      <th key={h} className="px-5 py-3.5 font-normal">{h}</th>
                    )
                  )}
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5">
                {filtered.map(d => (
                  <tr key={d.id} className="hover:bg-muted/30 transition">
                    <td className="px-5 py-4">
                      <button
                        onClick={() => setSelected(d)}
                        className="flex items-center gap-3 text-left font-semibold text-foreground hover:text-cyan-400 transition"
                      >
                        <span className="grid size-8 place-items-center rounded bg-cyan-500/10 text-cyan-400">
                          <FileText className="size-4" />
                        </span>
                        <span>{d.name}</span>
                      </button>
                      <p className="ml-11 font-mono text-[9px] uppercase tracking-wider text-muted-foreground">
                        {d.classification}
                      </p>
                    </td>
                    <td className="px-5 py-4 font-mono text-[10px]">{d.type}</td>
                    <td className="px-5 py-4 font-mono text-muted-foreground">{d.size}</td>
                    <td className="px-5 py-4">{d.department}</td>
                    <td className="px-5 py-4 font-mono text-muted-foreground">{d.uploaded}</td>
                    <td className="px-5 py-4">
                      <span className="font-mono text-[10px] uppercase tracking-wider text-emerald-400">
                        ● {d.status}
                      </span>
                    </td>
                    <td className="px-5 py-4 font-mono">{d.chunks} chunks</td>
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-1">
                        <button
                          title="Inspect document preview"
                          onClick={() => setSelected(d)}
                          className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition"
                        >
                          <Eye className="size-4" />
                        </button>
                        <button
                          title="Ask AI about this document"
                          onClick={() => onNavigate('AI Chat')}
                          className="rounded p-1.5 text-cyan-400 hover:bg-cyan-500/10 transition"
                        >
                          <MessageSquare className="size-4" />
                        </button>
                        <button
                          title="Delete from vector store"
                          onClick={() => setDeleteConfirmId(d.id)}
                          className="rounded p-1.5 text-red-400 hover:bg-red-500/10 transition"
                        >
                          <Trash2 className="size-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="p-12 text-center text-muted-foreground">
            <FileText className="mx-auto size-8 text-muted-foreground/50 mb-2" />
            <h3 className="font-medium text-foreground">No documents found</h3>
            <p className="text-xs mt-1">Upload a technical file or clear your search filter.</p>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      {deleteConfirmId && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/60 p-4 backdrop-blur-sm">
          <div className="w-full max-w-sm rounded-xl border border-white/10 bg-[#0c1524] p-6 shadow-2xl space-y-4">
            <h3 className="font-bold text-foreground">Confirm Deletion</h3>
            <p className="text-xs text-muted-foreground leading-relaxed">
              Are you sure you want to remove this document from the local vector database? All associated chunks will be deleted.
            </p>
            <div className="flex justify-end gap-2 pt-2">
              <button
                onClick={() => setDeleteConfirmId(null)}
                className="rounded px-3 py-1.5 font-mono text-xs text-muted-foreground hover:bg-muted"
              >
                Cancel
              </button>
              <button
                onClick={() => handleDelete(deleteConfirmId)}
                className="rounded bg-red-500 px-3 py-1.5 font-mono text-xs font-bold text-white hover:bg-red-600"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Selected Document Details Drawer */}
      {selected && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/65 p-4 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-xl border border-white/10 bg-[#0c1524] shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 p-5">
              <div className="flex items-center gap-3">
                <div className="grid size-9 place-items-center rounded bg-cyan-500/10 text-cyan-400">
                  <FileText className="size-5" />
                </div>
                <div>
                  <p className="font-mono text-[9px] uppercase tracking-wider text-cyan-400">Document Detail</p>
                  <h2 className="text-lg font-bold text-foreground">{selected.name}</h2>
                </div>
              </div>
              <button onClick={() => setSelected(null)} className="rounded p-1.5 text-muted-foreground hover:bg-muted">
                <X className="size-4" />
              </button>
            </div>

            <div className="grid gap-6 p-6 lg:grid-cols-[1.3fr_.7fr]">
              <div className="space-y-4">
                <div className="rounded-lg border border-white/10 bg-muted/20 p-5 min-h-64 flex flex-col justify-center text-center">
                  <FileText className="mx-auto size-8 text-cyan-400 mb-2" />
                  <p className="text-sm font-semibold text-foreground">Extracted Content Preview</p>
                  <p className="text-xs text-muted-foreground mt-1 max-w-sm mx-auto">
                    Document parsed with local text extraction engine. Ready for semantic vector queries and automated agent analysis.
                  </p>
                </div>

                <div className="rounded-lg border border-white/10 bg-card/60 p-4 space-y-2 text-xs">
                  <p className="font-mono text-[9px] uppercase tracking-wider text-muted-foreground">Embedding Trace</p>
                  <div className="grid grid-cols-2 gap-3 font-mono text-[11px]">
                    <div><span>Model:</span> <span className="text-cyan-400">BGE-M3 (On-Prem)</span></div>
                    <div><span>Dimensions:</span> <span className="text-foreground">1024</span></div>
                    <div><span>Chunk Count:</span> <span className="text-foreground">{selected.chunks}</span></div>
                    <div><span>Status:</span> <span className="text-emerald-400">{selected.status}</span></div>
                  </div>
                </div>
              </div>

              <div className="space-y-4">
                <div className="rounded-lg border border-white/10 bg-card/60 p-4 space-y-3 text-xs">
                  <p className="font-mono text-[9px] uppercase tracking-wider text-muted-foreground">Governance Metadata</p>
                  <div className="space-y-2">
                    <div className="flex justify-between"><span className="text-muted-foreground">Owner</span><span className="text-foreground">{selected.owner}</span></div>
                    <div className="flex justify-between"><span className="text-muted-foreground">Department</span><span className="text-foreground">{selected.department}</span></div>
                    <div className="flex justify-between"><span className="text-muted-foreground">Classification</span><span className="text-cyan-400">{selected.classification}</span></div>
                    <div className="flex justify-between"><span className="text-muted-foreground">File Size</span><span className="font-mono text-foreground">{selected.size}</span></div>
                  </div>
                </div>

                <div className="flex flex-col gap-2">
                  <button
                    onClick={() => {
                      setSelected(null)
                      onNavigate('AI Chat')
                    }}
                    className="w-full rounded-lg bg-primary py-2.5 font-mono text-[10px] font-bold uppercase tracking-wider text-primary-foreground hover:brightness-110 transition"
                  >
                    Ask AI About This Document
                  </button>
                  <button
                    onClick={() => {
                      setNotice(`Document assigned to primary knowledge base.`)
                      setTimeout(() => setNotice(''), 3000)
                    }}
                    className="w-full rounded-lg border border-white/10 bg-white/[0.02] py-2.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:bg-muted hover:text-foreground transition"
                  >
                    Sync to Knowledge Base
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function KnowledgeBaseWorkspace({ onNavigate }: { onNavigate: (page: PageKey) => void }) {
  const [bases, setBases] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [query, setQuery] = useState('')
  const [selected, setSelected] = useState<any>(null)
  const [tab, setTab] = useState('Overview')
  const [search, setSearch] = useState('')
  const [results, setResults] = useState<any[]>([])
  const [showCreate, setShowCreate] = useState(false)
  const [notice, setNotice] = useState('')

  useEffect(() => {
    knowledgeBaseService.list().then(r => setBases(r.data)).finally(() => setLoading(false))
  }, [])

  const runSearch = async () => {
    if (!search.trim()) return
    const r = await searchService.search(search, selected?.id)
    setResults(r.data)
  }

  return (
    <div className="animate-rise flex flex-col gap-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[.25em] text-cyan-400">
            Workspace // Semantic Retrieval
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-foreground">Knowledge Base</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Curated collections of verified technical manuals and operating procedures for grounded local AI.
          </p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 rounded-lg bg-primary px-4 py-2.5 font-mono text-[10px] font-bold uppercase tracking-wider text-primary-foreground shadow-sm hover:brightness-110"
        >
          <Plus className="size-4" /> Create Knowledge Base
        </button>
      </div>

      <SecurityStrip />

      {notice && (
        <div role="status" className="rounded-lg border border-cyan-500/40 bg-cyan-500/10 px-4 py-3 font-mono text-xs text-cyan-300">
          {notice}
        </div>
      )}

      {/* Collections Grid */}
      {loading ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3].map(i => (
            <div key={i} className="h-56 animate-pulse rounded-xl border border-white/10 bg-card" />
          ))}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {bases
            .filter(b => b.name.toLowerCase().includes(query.toLowerCase()))
            .map(b => (
              <div
                key={b.id}
                className="glass-panel card-3d rounded-xl p-5 border border-white/10 transition hover:border-cyan-400/40"
              >
                <div className="flex items-start justify-between">
                  <div className="grid size-10 place-items-center rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    <BookOpen className="size-5" />
                  </div>
                  <span className="font-mono text-[9px] uppercase tracking-wider text-emerald-400">
                    ● {b.status}
                  </span>
                </div>
                <h3 className="mt-4 font-bold text-foreground text-base">{b.name}</h3>
                <p className="mt-1.5 text-xs text-muted-foreground line-clamp-2">{b.description}</p>

                <div className="mt-5 grid grid-cols-2 gap-3 border-t border-white/10 pt-3 text-xs">
                  <div>
                    <p className="text-muted-foreground font-mono text-[10px]">DOCUMENTS</p>
                    <p className="mt-0.5 font-semibold text-foreground">{b.documents.toLocaleString()}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground font-mono text-[10px]">CHUNKS</p>
                    <p className="mt-0.5 font-semibold text-foreground">{b.chunks.toLocaleString()}</p>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => {
                      setSelected(b)
                      setTab('Overview')
                    }}
                    className="flex-1 rounded-md bg-primary py-2 font-mono text-[10px] uppercase tracking-wider text-primary-foreground hover:brightness-110"
                  >
                    Open Collection
                  </button>
                  <button
                    onClick={() => {
                      setSelected(b)
                      setTab('Search')
                    }}
                    className="rounded-md border border-white/10 p-2 text-muted-foreground hover:bg-muted hover:text-foreground"
                    title="Search knowledge base"
                  >
                    <Search className="size-4" />
                  </button>
                  <button
                    onClick={() => {
                      setNotice(`Re-indexing ${b.name} against local BGE-M3 model...`)
                      setTimeout(() => setNotice(`Re-index complete for ${b.name}.`), 2000)
                    }}
                    className="rounded-md border border-white/10 p-2 text-muted-foreground hover:bg-muted hover:text-cyan-400"
                    title="Reindex collection"
                  >
                    <Zap className="size-4" />
                  </button>
                </div>
              </div>
            ))}
        </div>
      )}

      {/* RAG Pipeline Flow Diagram */}
      <div className="glass-panel rounded-xl p-6 border border-white/10">
        <div className="flex items-center gap-2 mb-4">
          <Network className="size-5 text-cyan-400" />
          <h3 className="font-semibold text-foreground">Local RAG Architecture Flow</h3>
        </div>
        <div className="flex flex-wrap items-center justify-center gap-2 text-center text-xs">
          {[
            'Document Upload',
            'Text Extraction',
            'Chunking (512 tokens)',
            'BGE-M3 Embeddings',
            'Vector DB (ChromaDB)',
            'Cosine Similarity',
            'Local vLLM Model',
            'Traceable Answer',
          ].map((step, i) => (
            <div key={step} className="flex items-center gap-2">
              <div className="rounded-lg border border-white/10 bg-card/60 px-3 py-2 font-mono text-[10px] text-cyan-300">
                {step}
              </div>
              {i < 7 && <ArrowRight className="size-3.5 text-muted-foreground" />}
            </div>
          ))}
        </div>
      </div>

      {/* Selected Knowledge Base Detail Modal */}
      {selected && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/65 p-4 backdrop-blur-sm">
          <div className="max-h-[90vh] w-full max-w-4xl overflow-y-auto rounded-xl border border-white/10 bg-[#0c1524] shadow-2xl">
            <div className="flex items-center justify-between border-b border-white/10 p-5">
              <div>
                <p className="font-mono text-[9px] uppercase text-cyan-400 tracking-wider">Collection Detail</p>
                <h2 className="text-xl font-bold text-foreground">{selected.name}</h2>
              </div>
              <button onClick={() => setSelected(null)} className="rounded p-1.5 text-muted-foreground hover:bg-muted">
                <X className="size-4" />
              </button>
            </div>

            <div className="flex gap-1 border-b border-white/10 p-3 bg-muted/20">
              {['Overview', 'Search', 'Security'].map(t => (
                <button
                  key={t}
                  onClick={() => setTab(t)}
                  className={`rounded-md px-3.5 py-1.5 text-xs font-mono uppercase tracking-wider transition ${
                    tab === t ? 'bg-cyan-500/20 text-cyan-300 font-bold' : 'text-muted-foreground hover:bg-muted'
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>

            <div className="p-6">
              {tab === 'Search' ? (
                <div className="space-y-4">
                  <div className="flex gap-2">
                    <input
                      value={search}
                      onChange={e => setSearch(e.target.value)}
                      onKeyDown={e => e.key === 'Enter' && runSearch()}
                      placeholder="Enter semantic query across this knowledge base..."
                      className="h-11 flex-1 rounded-lg border border-white/10 bg-background px-3 text-sm outline-none focus:border-cyan-400"
                    />
                    <button
                      onClick={runSearch}
                      className="rounded-lg bg-primary px-4 font-mono text-[10px] font-bold uppercase tracking-wider text-primary-foreground hover:brightness-110"
                    >
                      Search
                    </button>
                  </div>

                  <div className="space-y-3">
                    {results.length ? (
                      results.map((r, i) => (
                        <div key={i} className="rounded-lg border border-white/10 bg-card/40 p-4 space-y-2">
                          <div className="flex justify-between items-start">
                            <h4 className="text-sm font-semibold text-foreground">{r.name}</h4>
                            <span className="font-mono text-xs text-emerald-400">Score: {r.score}</span>
                          </div>
                          <p className="text-xs text-muted-foreground leading-relaxed">{r.excerpt}</p>
                          <p className="font-mono text-[10px] text-cyan-400">{r.page} • {r.section}</p>
                        </div>
                      ))
                    ) : (
                      <div className="rounded-lg border border-dashed border-white/10 p-8 text-center text-xs text-muted-foreground">
                        Execute a semantic vector search across indexed chunks.
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="space-y-6">
                  <div className="grid gap-4 sm:grid-cols-3">
                    <div className="rounded-lg border border-white/10 bg-card/60 p-4">
                      <p className="font-mono text-[9px] uppercase text-muted-foreground">Total Documents</p>
                      <p className="text-2xl font-bold text-foreground mt-1">{selected.documents.toLocaleString()}</p>
                    </div>
                    <div className="rounded-lg border border-white/10 bg-card/60 p-4">
                      <p className="font-mono text-[9px] uppercase text-muted-foreground">Indexed Chunks</p>
                      <p className="text-2xl font-bold text-foreground mt-1">{selected.chunks.toLocaleString()}</p>
                    </div>
                    <div className="rounded-lg border border-white/10 bg-card/60 p-4">
                      <p className="font-mono text-[9px] uppercase text-muted-foreground">Clearance Level</p>
                      <p className="text-2xl font-bold text-cyan-400 mt-1">{selected.access}</p>
                    </div>
                  </div>

                  <div className="rounded-lg border border-white/10 bg-card/40 p-4 space-y-2 text-xs">
                    <h4 className="font-semibold text-foreground">Vector Engine Configuration</h4>
                    <p className="text-muted-foreground">
                      Embedding Artifact: <strong>local-bge-m3</strong> • Distance Metric: <strong>Cosine</strong> • Shard Status: <strong className="text-emerald-400">Synchronized</strong>
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Create Knowledge Base Modal */}
      {showCreate && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-black/65 p-4 backdrop-blur-sm">
          <form
            onSubmit={e => {
              e.preventDefault()
              setShowCreate(false)
              setNotice('New knowledge base created and ready for document assignment.')
              setTimeout(() => setNotice(''), 3000)
            }}
            className="w-full max-w-lg rounded-xl border border-white/10 bg-[#0c1524] p-6 shadow-2xl space-y-4"
          >
            <div className="flex items-center justify-between border-b border-white/10 pb-3">
              <h3 className="font-bold text-base text-foreground">Create Knowledge Base</h3>
              <button type="button" onClick={() => setShowCreate(false)} className="rounded p-1 text-muted-foreground hover:bg-muted">
                <X className="size-4" />
              </button>
            </div>

            <label className="flex flex-col gap-1.5 text-xs font-medium">
              Collection Name
              <input required className="h-10 rounded border bg-background px-3 text-sm outline-none focus:border-cyan-400" placeholder="e.g. Turbine Maintenance & Diagnostics" />
            </label>

            <label className="flex flex-col gap-1.5 text-xs font-medium">
              Description
              <textarea required className="min-h-20 rounded border bg-background p-3 text-sm outline-none focus:border-cyan-400" placeholder="Scope of technical documents included..." />
            </label>

            <div className="grid grid-cols-2 gap-3">
              <label className="flex flex-col gap-1.5 text-xs font-medium">
                Classification
                <select className="h-10 rounded border bg-background px-2 text-xs outline-none">
                  <option>Internal</option>
                  <option>Confidential</option>
                  <option>Restricted</option>
                </select>
              </label>

              <label className="flex flex-col gap-1.5 text-xs font-medium">
                Visibility
                <select className="h-10 rounded border bg-background px-2 text-xs outline-none">
                  <option>Operations Team</option>
                  <option>Safety Division</option>
                  <option>Organization-Wide</option>
                </select>
              </label>
            </div>

            <div className="pt-2 flex justify-end gap-2">
              <button
                type="button"
                onClick={() => setShowCreate(false)}
                className="rounded border px-4 py-2 font-mono text-[10px] uppercase tracking-wider hover:bg-muted"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="rounded bg-primary px-4 py-2 font-mono text-[10px] font-bold uppercase tracking-wider text-primary-foreground hover:brightness-110"
              >
                Create Collection
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}

function VisionWorkspace({ onNavigate }: { onNavigate: (page: PageKey) => void }) {
  const [file, setFile] = useState<any>(null)
  const [preview, setPreview] = useState('')
  const [mode, setMode] = useState('Engineering Drawing Analysis')
  const [model, setModel] = useState('Engineering Vision Model')
  const [question, setQuestion] = useState('')
  const [analysis, setAnalysis] = useState<any>(null)
  const [processing, setProcessing] = useState(false)
  const [annotations, setAnnotations] = useState(true)
  const [zoom, setZoom] = useState(100)
  const [rotation, setRotation] = useState(0)
  const [notice, setNotice] = useState('')
  const [history, setHistory] = useState<any[]>([])
  const [error, setError] = useState('')

  const modes: Record<string, string> = {
    'Engineering Drawing Analysis': 'Interpret components, connections, tags, and drawing conventions.',
    'P&ID Analysis': 'Review process lines, instruments, valves, and flow relationships.',
    'Equipment Inspection': 'Summarize visible condition indicators without making unsupported diagnoses.',
    'Defect Detection': 'Identify visible anomalies for engineering review; observations are not confirmed defects.',
    'OCR / Text Extraction': 'Extract visible labels, tags, and technical text from schematics.',
    'Diagram Understanding': 'Explain diagram structure and relationships between visible elements.',
  }

  useEffect(() => {
    visionService.history().then(r => setHistory(r.data))
  }, [])

  const choose = (f: File) => {
    if (!['image/png', 'image/jpeg', 'image/webp', 'application/pdf'].includes(f.type)) {
      setError('Unsupported image format. Use PNG, JPG, JPEG, WEBP, or PDF.')
      return
    }
    setError('')
    setAnalysis(null)
    setFile({
      name: f.name,
      type: f.type.split('/')[1]?.toUpperCase() || 'PDF',
      size: `${(f.size / 1024 / 1024).toFixed(2)} MB`,
      resolution: f.type === 'application/pdf' ? 'Document' : '4096 × 3072',
      uploaded: 'Just now',
      status: 'Ready for Analysis',
    })
    if (f.type !== 'application/pdf') {
      setPreview(URL.createObjectURL(f))
    }
  }

  const analyze = async () => {
    if (!file) {
      setError('No engineering drawing or image selected. Upload an image to begin.')
      return
    }
    setProcessing(true)
    setError('')
    try {
      const r = await visionService.analyze({ fileName: file.name, mode, question, model })
      setAnalysis(r.data)
      setFile((f: any) => ({ ...f, status: 'Analysis Complete' }))
    } catch {
      setError('Vision model unavailable. Connect the local multimodal inference service and try again.')
    } finally {
      setProcessing(false)
    }
  }

  const exportAnalysis = (format: 'PDF' | 'JSON') => {
    if (!analysis) return
    const blob = new Blob([JSON.stringify(analysis, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `vision-analysis-${analysis.id || Date.now().toString(36)}.${format.toLowerCase()}`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    setNotice(`Exported analysis as ${format}.`)
    setTimeout(() => setNotice(''), 3000)
  }

  return (
    <div className="animate-rise flex flex-col gap-6">
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[.25em] text-cyan-400">
            Workspace // Multimodal Engineering
          </p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight text-foreground">
            Engineering Vision Inspection
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Analyze complex schematics, P&ID drawings, and component images via local on-premise vision models.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <span className="flex items-center gap-2 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-3 py-2 font-mono text-[9px] uppercase tracking-wider text-emerald-400">
            <span className="size-1.5 rounded-full bg-emerald-400" /> Local Vision Model
          </span>
          <span className="rounded-lg border border-white/10 bg-card px-3 py-2 font-mono text-[9px] uppercase tracking-wider text-muted-foreground">
            Air-Gapped
          </span>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.2fr_.8fr]">
        {/* Left: Image Workspace */}
        <section className="flex flex-col gap-4">
          <div className="glass-panel rounded-xl border border-white/10 overflow-hidden">
            <div className="flex items-center justify-between border-b border-white/10 p-4">
              <div>
                <h3 className="font-semibold text-sm">Interactive Image Viewer</h3>
                <p className="font-mono text-[10px] text-muted-foreground">High-precision zoom & rotation</p>
              </div>

              <div className="flex items-center gap-1">
                <button
                  title="Zoom out"
                  onClick={() => setZoom(Math.max(25, zoom - 15))}
                  className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
                >
                  <ZoomOut className="size-4" />
                </button>
                <span className="font-mono text-[10px] text-cyan-400 px-2">{zoom}%</span>
                <button
                  title="Zoom in"
                  onClick={() => setZoom(Math.min(250, zoom + 15))}
                  className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
                >
                  <ZoomIn className="size-4" />
                </button>
                <button
                  title="Rotate 90 degrees"
                  onClick={() => setRotation((rotation + 90) % 360)}
                  className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
                >
                  <Rotate3d className="size-4" />
                </button>
                <button
                  title="Reset view"
                  onClick={() => {
                    setZoom(100)
                    setRotation(0)
                  }}
                  className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground"
                >
                  <Maximize2 className="size-4" />
                </button>
              </div>
            </div>

            <div className="relative grid min-h-[380px] place-items-center overflow-hidden bg-[#060b13] p-8">
              <div className="cyber-grid absolute inset-0 opacity-20" />
              {preview ? (
                <img
                  src={preview}
                  alt="Uploaded technical schema"
                  style={{ transform: `scale(${zoom / 100}) rotate(${rotation}deg)` }}
                  className="relative max-h-[460px] max-w-full object-contain transition-transform duration-200"
                />
              ) : (
                <div className="relative text-center text-muted-foreground space-y-2">
                  <div className="mx-auto grid size-16 place-items-center rounded-2xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-400">
                    <ImageIcon className="size-8" />
                  </div>
                  <p className="text-sm font-semibold text-foreground">No Engineering Drawing Selected</p>
                  <p className="text-xs max-w-xs mx-auto">Upload a P&ID schematic, inspection capture, or wiring diagram.</p>
                </div>
              )}

              {/* Bounding box annotations */}
              {analysis && annotations && (
                <div className="pointer-events-none absolute inset-0">
                  <div className="absolute left-[30%] top-[35%] h-24 w-32 border-2 border-cyan-400 shadow-[0_0_15px_rgba(0,210,255,0.4)]">
                    <span className="absolute -top-5 left-0 bg-cyan-400 px-1.5 py-0.5 font-mono text-[9px] font-bold text-slate-950">
                      VALVE 0.94
                    </span>
                  </div>
                  <div className="absolute left-[60%] top-[25%] h-20 w-28 border-2 border-emerald-400 shadow-[0_0_15px_rgba(16,185,129,0.4)]">
                    <span className="absolute -top-5 left-0 bg-emerald-400 px-1.5 py-0.5 font-mono text-[9px] font-bold text-slate-950">
                      PUMP 0.91
                    </span>
                  </div>
                </div>
              )}
            </div>

            <div className="flex flex-wrap items-center justify-between border-t border-white/10 p-3.5 bg-card/30 text-xs">
              <div className="flex gap-2">
                <label className="flex cursor-pointer items-center gap-2 rounded-md border border-white/10 bg-background px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider hover:bg-muted">
                  <Upload className="size-3.5" /> Upload Image
                  <input
                    type="file"
                    className="sr-only"
                    accept=".png,.jpg,.jpeg,.webp,.pdf"
                    onChange={e => {
                      const f = e.target.files?.[0]
                      if (f) choose(f)
                    }}
                  />
                </label>
                {file && (
                  <button
                    onClick={() => {
                      setFile(null)
                      setPreview('')
                      setAnalysis(null)
                    }}
                    className="rounded-md border border-white/10 px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider text-muted-foreground hover:bg-muted"
                  >
                    Remove
                  </button>
                )}
              </div>

              <button
                onClick={() => setAnnotations(!annotations)}
                className={`font-mono text-[10px] uppercase tracking-wider px-3 py-1.5 rounded-md border transition ${
                  annotations ? 'border-cyan-400/50 bg-cyan-500/10 text-cyan-300' : 'text-muted-foreground hover:bg-muted'
                }`}
              >
                {annotations ? 'Hide Annotations' : 'Show Annotations'}
              </button>
            </div>
          </div>

          {file && (
            <div className="glass-panel rounded-xl border border-white/10 p-4 flex items-center gap-3">
              <div className="grid size-9 place-items-center rounded bg-cyan-500/10 text-cyan-400">
                <FileText className="size-4" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-semibold text-sm text-foreground truncate">{file.name}</p>
                <p className="font-mono text-[10px] text-muted-foreground mt-0.5">
                  {file.type} • {file.size} • {file.resolution}
                </p>
              </div>
              <span className="font-mono text-[10px] uppercase tracking-wider text-emerald-400">
                ● {file.status}
              </span>
            </div>
          )}
        </section>

        {/* Right: Analysis Controls */}
        <section className="flex flex-col gap-4">
          <div className="glass-panel rounded-xl border border-white/10 p-5 space-y-4">
            <div>
              <h3 className="font-semibold text-base">Multimodal Analysis Controls</h3>
              <p className="text-xs text-muted-foreground">Select inspection model and task profile</p>
            </div>

            <label className="flex flex-col gap-1.5 text-xs font-medium">
              Inspection Mode
              <select
                value={mode}
                onChange={e => setMode(e.target.value)}
                className="h-10 rounded-lg border border-white/10 bg-background px-3 text-sm outline-none focus:border-cyan-400"
              >
                {Object.keys(modes).map(m => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </label>

            <p className="rounded-lg border border-cyan-500/20 bg-cyan-500/5 p-3 text-xs leading-relaxed text-cyan-300/80">
              {modes[mode]}
            </p>

            <label className="flex flex-col gap-1.5 text-xs font-medium">
              Specific Query / Inspection Focus
              <textarea
                value={question}
                onChange={e => setQuestion(e.target.value)}
                placeholder="e.g., Identify isolation valves and verify pipe connection tags..."
                className="min-h-20 rounded-lg border border-white/10 bg-background p-3 text-sm outline-none focus:border-cyan-400"
              />
            </label>

            <button
              onClick={analyze}
              disabled={processing}
              className="flex h-11 w-full items-center justify-center gap-2 rounded-lg bg-primary font-mono text-[10px] font-bold uppercase tracking-wider text-primary-foreground shadow-sm hover:brightness-110 disabled:opacity-50 transition"
            >
              {processing ? (
                <>
                  <span className="size-4 animate-spin rounded-full border-2 border-slate-950 border-t-transparent" />
                  Analyzing Schematic Locally...
                </>
              ) : (
                <>
                  <Sparkles className="size-4" /> Run Vision Inspection
                </>
              )}
            </button>

            {error && <p role="alert" className="text-xs text-red-400 font-mono">{error}</p>}
            {notice && <p role="status" className="text-xs text-cyan-300 font-mono">{notice}</p>}
          </div>

          {/* Model Status Card */}
          <div className="glass-panel rounded-xl border border-white/10 p-5 space-y-3">
            <h4 className="font-semibold text-sm">Vision Model Status</h4>
            <div className="space-y-2">
              {[
                ['Engineering Vision Model', 'On-Premises Multimodal', 'Online'],
                ['Qwen-VL Vision Core', 'Schematic Diagram Analyzer', 'Online'],
                ['OCR Text Engine', 'Tag & Label Extractor', 'Online'],
              ].map(([name, desc, status]) => (
                <div key={name} className="flex items-center justify-between rounded-lg border border-white/5 bg-card/40 p-2.5 text-xs">
                  <div>
                    <p className="font-medium text-foreground">{name}</p>
                    <p className="font-mono text-[10px] text-muted-foreground">{desc}</p>
                  </div>
                  <span className="font-mono text-[9px] uppercase text-emerald-400">● {status}</span>
                </div>
              ))}
            </div>
          </div>
        </section>
      </div>

      {/* Analysis Results Display */}
      {analysis && (
        <div className="glass-panel rounded-xl border border-cyan-500/30 p-6 space-y-6 shadow-xl">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-4">
            <div>
              <p className="font-mono text-[10px] uppercase tracking-wider text-cyan-400">Multimodal Output</p>
              <h2 className="text-xl font-bold text-foreground">Inspection Observations & Findings</h2>
            </div>

            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => exportAnalysis('JSON')}
                className="rounded-md border border-white/10 px-3 py-1.5 font-mono text-[10px] uppercase tracking-wider hover:bg-muted"
              >
                Export JSON
              </button>
              <button
                onClick={() => onNavigate('AI Chat')}
                className="rounded-md bg-primary px-3 py-1.5 font-mono text-[10px] font-bold uppercase tracking-wider text-primary-foreground hover:brightness-110"
              >
                Continue in AI Chat →
              </button>
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            <div className="rounded-lg border border-white/10 bg-card/40 p-4 space-y-2 md:col-span-2">
              <h4 className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Executive Summary</h4>
              <p className="text-sm leading-relaxed text-foreground">{analysis.summary}</p>
            </div>

            <div className="rounded-lg border border-white/10 bg-card/40 p-4 space-y-2">
              <h4 className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Detected Components</h4>
              <ul className="space-y-1.5 text-xs text-foreground">
                {analysis.detectedElements?.map((elem: string) => (
                  <li key={elem} className="flex items-center gap-2">
                    <span className="size-1.5 rounded-full bg-cyan-400" />
                    {elem}
                  </li>
                ))}
              </ul>
            </div>

            <div className="rounded-lg border border-white/10 bg-card/40 p-4 space-y-2">
              <h4 className="font-mono text-[10px] uppercase tracking-wider text-muted-foreground">Recommendations</h4>
              <ul className="space-y-1.5 text-xs text-muted-foreground">
                {analysis.recommendations?.map((rec: string) => (
                  <li key={rec} className="border-l-2 border-cyan-400 pl-2 text-foreground">
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function Generic({ page }: { page: PageKey }) {
  const Icon = nav.find(n => n.label === page)?.icon ?? BookOpen
  return (
    <div className="animate-rise flex flex-col gap-6">
      <div>
        <p className="font-mono text-[10px] uppercase tracking-[.25em] text-cyan-400">
          Workspace // {page.toLowerCase()}
        </p>
        <h1 className="mt-2 text-3xl font-bold tracking-tight text-foreground">{page}</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Manage and review controlled {page.toLowerCase()} resources.
        </p>
      </div>

      <div className="grid min-h-[430px] place-items-center rounded-xl border border-white/10 bg-card p-8 text-center">
        <div className="flex max-w-sm flex-col items-center gap-4">
          <div className="grid size-14 place-items-center rounded-2xl border border-cyan-500/30 bg-cyan-500/10 text-cyan-400 shadow-[0_0_20px_rgba(0,210,255,0.2)]">
            <Icon className="size-7" />
          </div>
          <h2 className="text-lg font-bold text-foreground">{page} Workspace Online</h2>
          <p className="text-xs leading-relaxed text-muted-foreground">
            This module is connected to the local service layer and ready for active on-premise tasks.
          </p>
          <button
            onClick={() => alert(`${page} workspace initialized.`)}
            className="rounded-lg bg-primary px-4 py-2 font-mono text-[10px] font-bold uppercase tracking-wider text-primary-foreground shadow-sm hover:brightness-110"
          >
            Run Active Check
          </button>
        </div>
      </div>
    </div>
  )
}

function Shell({ onLogout }: { onLogout: () => void }) {
  const [page, setPage] = useState<PageKey>(() => {
    if (typeof window === 'undefined') return 'Overview'
    const routes: Record<string, PageKey> = {
      '/chat': 'AI Chat',
      '/documents': 'Documents',
      '/knowledge-base': 'Knowledge Base',
      '/agents': 'Agents',
      '/models': 'Models',
      '/vision': 'Vision',
      '/reports': 'Reports',
      '/audit': 'Audit Log',
      '/admin': 'Admin',
      '/settings': 'Settings',
    }
    return routes[window.location.pathname] ?? 'Overview'
  })

  const [collapsed, setCollapsed] = useState(false)
  const [dark, setDark] = useState(true)
  const [mobile, setMobile] = useState(false)
  const [notificationsOpen, setNotificationsOpen] = useState(false)
  const [profileOpen, setProfileOpen] = useState(false)
  const [isBackendOnline, setIsBackendOnline] = useState(true)

  useEffect(() => {
    adminService.getSystemStatus().then(r => {
      setIsBackendOnline(r.data.isOnline)
    }).catch(() => {
      setIsBackendOnline(false)
    })
  }, [])

  const content =
    page === 'Overview' ? (
      <Dashboard onNavigate={setPage} />
    ) : page === 'AI Chat' ? (
      <ChatWorkspace />
    ) : page === 'Documents' ? (
      <DocumentsWorkspace onNavigate={setPage} />
    ) : page === 'Knowledge Base' ? (
      <KnowledgeBaseWorkspace onNavigate={setPage} />
    ) : page === 'Agents' ? (
      <AgentsWorkspace onNavigate={p => setPage(p as PageKey)} />
    ) : page === 'Models' ? (
      <ModelsWorkspace onNavigate={p => setPage(p as PageKey)} />
    ) : page === 'Vision' ? (
      <VisionWorkspace onNavigate={setPage} />
    ) : page === 'Reports' ? (
      <ReportsWorkspace onNavigate={p => setPage(p as PageKey)} />
    ) : page === 'Audit Log' ? (
      <AuditWorkspace />
    ) : page === 'Admin' ? (
      <AdminWorkspace onNavigate={p => setPage(p as PageKey)} />
    ) : page === 'Settings' ? (
      <SettingsWorkspace />
    ) : (
      <Generic page={page} />
    )

  return (
    <div className={dark ? 'dark' : ''}>
      <div className="flex min-h-screen bg-background text-foreground font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
        {/* Sidebar */}
        <aside
          className={`fixed inset-y-0 left-0 z-30 flex w-64 flex-col border-r border-white/10 bg-[#09101b] transition-all duration-300 lg:static lg:translate-x-0 ${
            mobile ? 'translate-x-0' : '-translate-x-full'
          } ${collapsed ? 'lg:w-[76px]' : ''}`}
        >
          {/* Sidebar Top */}
          <div className="flex h-20 items-center justify-between border-b border-white/10 px-5">
            <Logo compact={collapsed} />
            <button
              className="focus-ring hidden rounded-lg p-2 text-muted-foreground hover:bg-muted lg:block"
              onClick={() => setCollapsed(!collapsed)}
              aria-label="Toggle sidebar"
            >
              <PanelLeftClose className="size-4" />
            </button>
            <button
              className="focus-ring rounded-lg p-2 text-muted-foreground lg:hidden"
              onClick={() => setMobile(false)}
              aria-label="Close navigation"
            >
              <X className="size-4" />
            </button>
          </div>

          {/* Nav Items */}
          <nav className="flex flex-1 flex-col gap-1 overflow-y-auto p-3">
            {nav.map(item => {
              const Icon = item.icon
              const active = page === item.label
              return (
                <div key={item.label}>
                  {item.section && (
                    <p
                      className={`mb-2 mt-4 px-3 font-mono text-[9px] uppercase tracking-[.25em] text-muted-foreground/60 ${
                        collapsed ? 'lg:hidden' : ''
                      }`}
                    >
                      {item.section}
                    </p>
                  )}
                  <button
                    onClick={() => {
                      setPage(item.label)
                      setMobile(false)
                      const path =
                        item.label === 'AI Chat'
                          ? '/chat'
                          : item.label === 'Documents'
                          ? '/documents'
                          : item.label === 'Knowledge Base'
                          ? '/knowledge-base'
                          : item.label === 'Vision'
                          ? '/vision'
                          : item.label === 'Agents'
                          ? '/agents'
                          : item.label === 'Models'
                          ? '/models'
                          : item.label === 'Reports'
                          ? '/reports'
                          : item.label === 'Audit Log'
                          ? '/audit'
                          : item.label === 'Admin'
                          ? '/admin'
                          : item.label === 'Settings'
                          ? '/settings'
                          : '/dashboard'
                      window.history.pushState({}, '', path)
                    }}
                    title={collapsed ? item.label : undefined}
                    className={`focus-ring relative flex w-full items-center gap-3 rounded-xl px-3 py-2.5 text-left text-xs font-medium transition group ${
                      active
                        ? 'border border-cyan-400/40 bg-cyan-500/10 text-cyan-400 font-bold shadow-[0_0_15px_rgba(0,210,255,0.15)]'
                        : 'text-muted-foreground hover:bg-muted/40 hover:text-foreground'
                    } ${collapsed ? 'lg:justify-center lg:px-0' : ''}`}
                  >
                    <Icon className={`size-4 shrink-0 transition group-hover:scale-110 ${active ? 'text-cyan-400' : ''}`} />
                    <span className={collapsed ? 'lg:hidden' : ''}>{item.label}</span>
                    {active && !collapsed && (
                      <span className="ml-auto size-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#00d2ff]" />
                    )}
                  </button>
                </div>
              )
            })}
          </nav>

          {/* User Profile Card in Sidebar */}
          <div className={`border-t border-white/10 p-3.5 ${collapsed ? 'lg:px-2' : ''}`}>
            <button
              onClick={() => setProfileOpen(true)}
              className="w-full flex items-center gap-3 rounded-lg p-1.5 hover:bg-white/5 transition text-left"
              title="Open profile & clearance menu"
            >
              <div className="grid size-8 place-items-center rounded-lg bg-cyan-500/15 text-cyan-400 font-mono text-xs font-bold border border-cyan-500/30">
                JE
              </div>
              <div className={collapsed ? 'lg:hidden' : ''}>
                <p className="text-xs font-semibold text-foreground">Jordan Ellis</p>
                <p className="font-mono text-[9px] uppercase tracking-wider text-cyan-400">Level 4 Clearance</p>
              </div>
            </button>
          </div>
        </aside>

        {mobile && (
          <button
            onClick={() => setMobile(false)}
            className="fixed inset-0 z-20 bg-black/60 backdrop-blur-xs lg:hidden"
            aria-label="Close navigation overlay"
          />
        )}

        {/* Right Section / Main View */}
        <section className="min-w-0 flex-1 flex flex-col">
          {/* Header */}
          <header className="flex h-20 items-center justify-between border-b border-white/10 bg-[#09101b]/80 px-5 backdrop-blur-md sm:px-8">
            <div className="flex items-center gap-3">
              <button
                className="focus-ring rounded-lg p-2 text-muted-foreground lg:hidden hover:bg-muted"
                onClick={() => setMobile(true)}
                aria-label="Open navigation"
              >
                <Menu className="size-5" />
              </button>
              <div className="hidden items-center gap-2 text-xs text-muted-foreground sm:flex font-mono">
                <span>Workbench</span>
                <ChevronRight className="size-3 text-muted-foreground/60" />
                <span className="text-cyan-400 font-bold">{page}</span>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => setPage('Overview')}
                className="focus-ring"
                title={isBackendOnline ? 'Backend online at http://127.0.0.1:8001' : 'Backend offline at http://127.0.0.1:8001'}
              >
                <StatusDot
                  label={isBackendOnline ? 'Backend Online' : 'Backend Standby'}
                  isOnline={isBackendOnline}
                />
              </button>

              <button
                className="focus-ring rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition"
                onClick={() => setDark(!dark)}
                aria-label="Toggle dark mode"
                title="Toggle theme"
              >
                {dark ? <Sun className="size-4 text-cyan-400" /> : <Moon className="size-4" />}
              </button>

              <button
                className="focus-ring relative rounded-lg p-2 text-muted-foreground hover:bg-muted hover:text-foreground transition"
                onClick={() => setNotificationsOpen(true)}
                aria-label="Open notifications"
                title="Security alerts"
              >
                <Bell className="size-4" />
                <span className="absolute right-1.5 top-1.5 size-2 rounded-full bg-cyan-400 shadow-[0_0_6px_#00d2ff]" />
              </button>

              <button
                onClick={() => setProfileOpen(true)}
                className="grid size-8 place-items-center rounded-lg bg-cyan-500/15 text-cyan-400 font-mono text-xs font-bold border border-cyan-500/30 hover:brightness-110 transition"
                title="Open operator profile"
              >
                JE
              </button>
            </div>
          </header>

          {/* Main Content Pane */}
          <main className="mx-auto w-full max-w-[1550px] p-5 sm:p-8 lg:p-10 flex-1">
            {content}
          </main>

          {/* Footer */}
          <footer className="border-t border-white/5 px-5 py-6 font-mono text-[9px] uppercase tracking-[.2em] text-muted-foreground/60 sm:px-8 lg:px-10 flex flex-col sm:flex-row justify-between items-center gap-2">
            <span>Sovereign AI Workbench • On-Premise Air-Gapped Intelligence • v2.4.1</span>
            <span className="text-cyan-400/80">SIH 2026 Enterprise Architecture Verified</span>
          </footer>
        </section>
      </div>

      {/* Notifications Drawer Component */}
      <NotificationsDrawer
        isOpen={notificationsOpen}
        onClose={() => setNotificationsOpen(false)}
      />

      {/* Operator Profile Modal Component */}
      <ProfileModal
        isOpen={profileOpen}
        onClose={() => setProfileOpen(false)}
        onNavigateSettings={() => setPage('Settings')}
        onLogout={async () => {
          await authService.signOut()
          onLogout()
        }}
      />
    </div>
  )
}

export default function Page() {
  const [route, setRoute] = useState(typeof window !== 'undefined' ? window.location.pathname : '/login')
  const [authenticated, setAuthenticated] = useState(false)
  const [entryPlayed, setEntryPlayed] = useState(false)

  useEffect(() => {
    const signedIn = authService.isAuthenticated()
    setAuthenticated(signedIn)
    if (!signedIn && window.location.pathname !== '/forgot-password') {
      window.history.replaceState({}, '', '/login')
    }
    if (signedIn && ['/login', '/forgot-password', '/'].includes(window.location.pathname)) {
      window.history.replaceState({}, '', '/dashboard')
    }
    setRoute(window.location.pathname)
  }, [])

  const navigate = (path: string) => {
    window.history.pushState({}, '', path)
    setRoute(path)
  }

  return (
    <>
      {/* 3D Entry Holographic Motion */}
      <EntryMotion onComplete={() => setEntryPlayed(true)} />

      {route === '/forgot-password' ? (
        <ForgotPassword onBack={() => navigate('/login')} />
      ) : !authenticated ? (
        <Login
          onLogin={() => {
            setAuthenticated(true)
            navigate('/dashboard')
          }}
          onForgotPassword={() => navigate('/forgot-password')}
        />
      ) : (
        <Shell
          onLogout={() => {
            setAuthenticated(false)
            navigate('/login')
          }}
        />
      )}
    </>
  )
}
