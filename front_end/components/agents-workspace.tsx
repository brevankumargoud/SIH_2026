'use client'

import { FormEvent, useEffect, useState } from 'react'
import { Activity, AlertTriangle, ArrowRight, Zap, BookOpen, ChevronDown, ChevronRight, Copy, Download, Edit3, Eye, EyeOff, FileText, Gauge, Grid3x3, Info, LockKeyhole, MessageSquare, MoreHorizontal, Network, Plus, RotateCcw, Search, Settings, ShieldCheck, Sparkles, Square, Trash2, Users, X, Play, Pause, Check, AlertCircle, Code2, Database, Cpu, Clock } from 'lucide-react'
import { agentService, workflowService, agentExecutionService, agentHealthService } from '@/lib/services'

type AgentsTab = 'Catalog' | 'Configuration' | 'Run' | 'Orchestration' | 'History' | 'Health'

interface Agent {
  id: string
  name: string
  description: string
  status: 'Online' | 'Standby' | 'Offline'
  model: string
  version?: string
  tools?: string[]
  permissions?: string[]
  lastRun?: string
  runCount?: number
}

interface ExecutionRun {
  id: string
  agentId: string
  agentName: string
  status: 'Running' | 'Complete' | 'Failed' | 'Queued'
  startTime: string
  duration: string
  inputTokens: number
  outputTokens: number
  result?: string
  error?: string
}

interface WorkflowStep {
  id: string
  name: string
  status: 'Pending' | 'Running' | 'Complete' | 'Failed'
  agent: string
  output?: string
}

export function AgentsWorkspace({ onNavigate }: { onNavigate?: (page: string) => void }) {
  const [tab, setTab] = useState<AgentsTab>('Catalog')
  const [agents, setAgents] = useState<Agent[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [selected, setSelected] = useState<Agent | null>(null)
  const [showCreate, setShowCreate] = useState(false)
  const [query, setQuery] = useState('')
  const [notice, setNotice] = useState('')

  // Configuration state
  const [editName, setEditName] = useState('')
  const [editModel, setEditModel] = useState('')
  const [selectedTools, setSelectedTools] = useState<string[]>([])
  const [selectedPermissions, setSelectedPermissions] = useState<string[]>([])

  // Run state
  const [runInput, setRunInput] = useState('')
  const [runLoading, setRunLoading] = useState(false)
  const [runs, setRuns] = useState<ExecutionRun[]>([])

  // Orchestration state
  const [workflow, setWorkflow] = useState<WorkflowStep[]>([])
  const [orchestrating, setOrchestrating] = useState(false)

  // Health state
  const [health, setHealth] = useState<any[]>([])

  const availableTools = ['Web Search', 'Code Execution', 'File Access', 'API Calls', 'Knowledge Base Query', 'Vision Analysis', 'Document Processing']
  const availablePermissions = ['Read', 'Write', 'Execute', 'Admin', 'Network', 'Storage', 'External APIs']

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const result = await agentService.list()
        setAgents(result.data as Agent[])
        const healthResult = await agentHealthService.getHealth()
        setHealth(healthResult.data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load agents')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const filtered = agents.filter(
    a => `${a.name} ${a.description}`.toLowerCase().includes(query.toLowerCase())
  )

  const handleSelectAgent = (agent: Agent) => {
    setSelected(agent)
    setEditName(agent.name)
    setEditModel(agent.model)
    setSelectedTools(agent.tools || [])
    setSelectedPermissions(agent.permissions || [])
    setRuns([])
  }

  const handleCreateAgent = async () => {
    if (!editName.trim()) {
      setError('Agent name is required')
      return
    }
    try {
      const result = await agentService.create({
        name: editName,
        description: `Custom agent for ${editName}`,
        model: editModel,
        tools: selectedTools,
        permissions: selectedPermissions,
      })
      const newAgent = result.data as Agent
      setAgents([newAgent, ...agents])
      setSelected(newAgent)
      setShowCreate(false)
      setNotice(`Agent "${editName}" created successfully`)
      setTimeout(() => setNotice(''), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create agent')
    }
  }

  const handleDuplicate = async () => {
    if (!selected) return
    try {
      const result = await agentService.duplicate(selected.id)
      const duplicated = result.data as Agent
      setAgents([duplicated, ...agents])
      setSelected(duplicated)
      setNotice(`Agent duplicated as "${duplicated.name}"`)
      setTimeout(() => setNotice(''), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to duplicate agent')
    }
  }

  const handleSaveConfiguration = async () => {
    if (!selected) return
    try {
      await agentService.update(selected.id, {
        tools: selectedTools,
        permissions: selectedPermissions,
      })
      setAgents(prev => prev.map(a => a.id === selected.id ? { ...a, tools: selectedTools, permissions: selectedPermissions } : a))
      setNotice(`Configuration saved for agent "${selected.name}".`)
      setTimeout(() => setNotice(''), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save configuration')
    }
  }

  const handleDeleteAgent = () => {
    if (!selected) return
    const name = selected.name
    setAgents(prev => prev.filter(a => a.id !== selected.id))
    setSelected(agents.find(a => a.id !== selected.id) || null)
    setNotice(`Agent "${name}" removed from local registry.`)
    setTimeout(() => setNotice(''), 3000)
  }

  const handleRunAgent = async (e?: FormEvent) => {
    if (e) e.preventDefault()
    if (!selected || !runInput.trim()) return
    setRunLoading(true)
    setError('')
    try {
      const result = await agentExecutionService.run({
        agentId: selected.id,
        input: runInput,
      })
      const execution = result.data as ExecutionRun
      setRuns([execution, ...runs])
      setRunInput('')
      setNotice('Agent execution queued')
      setTimeout(() => setNotice(''), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to execute agent')
    } finally {
      setRunLoading(false)
    }
  }

  const handleRunWorkflow = async () => {
    if (agents.length < 2) {
      setError('At least 2 agents required for orchestration')
      return
    }
    setOrchestrating(true)
    setError('')
    try {
      const result = await workflowService.runOrchestration({
        agents: agents.slice(0, 3).map(a => a.id),
        input: 'Analyze operational data and generate recommendations',
      })
      setWorkflow(result.data)
      setNotice('Workflow orchestration started')
      setTimeout(() => setNotice(''), 3000)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to orchestrate workflow')
    } finally {
      setOrchestrating(false)
    }
  }

  if (loading) {
    return (
      <div className="animate-rise flex flex-col gap-6">
        <div className="h-12 animate-pulse rounded border bg-card" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-48 animate-pulse rounded border bg-card" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="animate-rise flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
        <div>
          <p className="font-mono text-[10px] uppercase tracking-[.2em] text-accent">
            Intelligence / agents
          </p>
          <h1 className="mt-2 text-3xl font-semibold tracking-tight">AI Agents</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Deploy, orchestrate, and monitor autonomous intelligence services
          </p>
        </div>
        <button
          onClick={() => {
            setShowCreate(true)
            setEditName('')
            setEditModel('Sovereign-32B')
            setSelectedTools([])
            setSelectedPermissions([])
          }}
          className="flex items-center justify-center gap-2 rounded bg-primary px-4 py-2.5 font-mono text-[10px] font-bold uppercase tracking-widest text-primary-foreground"
        >
          <Plus className="size-4" /> Create Agent
        </button>
      </div>

      {/* Notices */}
      {error && (
        <div className="rounded border border-destructive/50 bg-destructive/10 p-3 text-xs text-destructive">
          {error}
        </div>
      )}
      {notice && (
        <div className="rounded border border-accent/50 bg-accent/10 p-3 font-mono text-[10px] text-accent">
          {notice}
        </div>
      )}

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {(['Catalog', 'Configuration', 'Run', 'Orchestration', 'History', 'Health'] as AgentsTab[]).map(t => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-3 font-mono text-[10px] uppercase tracking-widest transition ${
              tab === t
                ? 'border-b-2 border-accent text-accent'
                : 'border-b-2 border-transparent text-muted-foreground hover:text-foreground'
            }`}
          >
            {t}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="flex flex-col gap-6">
        {/* Catalog Tab */}
        {tab === 'Catalog' && (
          <div>
            <div className="mb-4 flex gap-2">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="Search agents..."
                  value={query}
                  onChange={e => setQuery(e.target.value)}
                  className="w-full rounded border bg-muted px-3 py-2 font-mono text-[10px] text-foreground placeholder-muted-foreground focus:border-accent focus:outline-none"
                />
              </div>
            </div>

            {showCreate && (
              <div className="mb-6 rounded border border-accent/30 bg-accent/5 p-6">
                <h3 className="mb-4 font-semibold">Create New Agent</h3>
                <div className="flex flex-col gap-4">
                  <div>
                    <label className="text-xs font-medium">Agent Name</label>
                    <input
                      type="text"
                      value={editName}
                      onChange={e => setEditName(e.target.value)}
                      placeholder="e.g., Operations Assistant"
                      className="mt-1 w-full rounded border bg-muted px-3 py-2 text-sm focus:border-accent focus:outline-none"
                    />
                  </div>
                  <div>
                    <label className="text-xs font-medium">Base Model</label>
                    <select
                      value={editModel}
                      onChange={e => setEditModel(e.target.value)}
                      className="mt-1 w-full rounded border bg-muted px-3 py-2 text-sm focus:border-accent focus:outline-none"
                    >
                      <option>Sovereign-32B</option>
                      <option>Sovereign-14B</option>
                      <option>Vision-7B</option>
                    </select>
                  </div>
                  <div>
                    <label className="mb-2 block text-xs font-medium">Tools</label>
                    <div className="grid gap-2">
                      {availableTools.map(tool => (
                        <label key={tool} className="flex items-center gap-2 text-xs">
                          <input
                            type="checkbox"
                            checked={selectedTools.includes(tool)}
                            onChange={e => {
                              if (e.target.checked) {
                                setSelectedTools([...selectedTools, tool])
                              } else {
                                setSelectedTools(selectedTools.filter(t => t !== tool))
                              }
                            }}
                            className="rounded border"
                          />
                          {tool}
                        </label>
                      ))}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={handleCreateAgent}
                      className="flex-1 rounded bg-accent px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-widest text-accent-foreground"
                    >
                      Create Agent
                    </button>
                    <button
                      onClick={() => setShowCreate(false)}
                      className="flex-1 rounded border px-3 py-2 font-mono text-[10px] font-bold uppercase tracking-widest"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {filtered.map(agent => (
                <div
                  key={agent.id}
                  onClick={() => handleSelectAgent(agent)}
                  className={`cursor-pointer rounded border p-4 transition ${
                    selected?.id === agent.id
                      ? 'border-accent bg-accent/5'
                      : 'border-border hover:border-accent/50'
                  }`}
                >
                  <div className="mb-3 flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold">{agent.name}</h3>
                      <p className="mt-1 text-xs text-muted-foreground">{agent.description}</p>
                    </div>
                    <span
                      className={`rounded px-2 py-1 font-mono text-[9px] uppercase tracking-widest ${
                        agent.status === 'Online'
                          ? 'bg-emerald-500/20 text-emerald-600'
                          : agent.status === 'Standby'
                            ? 'bg-amber-500/20 text-amber-600'
                            : 'bg-muted text-muted-foreground'
                      }`}
                    >
                      {agent.status}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[10px]">
                    <span className="font-mono text-muted-foreground">{agent.model}</span>
                    {agent.runCount && (
                      <span className="text-muted-foreground">{agent.runCount} runs</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Configuration Tab */}
        {tab === 'Configuration' && selected && (
          <div className="space-y-6">
            <div>
              <p className="mb-4 font-mono text-[10px] uppercase tracking-[.2em] text-accent">
                Agent details
              </p>
              <div className="rounded border bg-card p-6">
                <div className="mb-6 flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-semibold">{selected.name}</h2>
                    <p className="mt-1 text-sm text-muted-foreground">{selected.description}</p>
                  </div>
                  <span
                    className={`rounded px-3 py-1 font-mono text-[10px] uppercase tracking-widest ${
                      selected.status === 'Online'
                        ? 'bg-emerald-500/20 text-emerald-600'
                        : 'bg-amber-500/20 text-amber-600'
                    }`}
                  >
                    {selected.status}
                  </span>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <p className="text-xs font-medium">Model</p>
                    <p className="mt-2 font-mono text-sm text-muted-foreground">{selected.model}</p>
                  </div>
                  <div>
                    <p className="text-xs font-medium">Last Run</p>
                    <p className="mt-2 font-mono text-sm text-muted-foreground">
                      {selected.lastRun || 'Never'}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <p className="mb-4 font-mono text-[10px] uppercase tracking-[.2em] text-accent">
                Tool access
              </p>
              <div className="rounded border bg-card p-6">
                <div className="grid gap-2">
                  {availableTools.map(tool => (
                    <label key={tool} className="flex items-center gap-3 text-sm">
                      <input
                        type="checkbox"
                        checked={selectedTools.includes(tool)}
                        onChange={e => {
                          if (e.target.checked) {
                            setSelectedTools([...selectedTools, tool])
                          } else {
                            setSelectedTools(selectedTools.filter(t => t !== tool))
                          }
                        }}
                        className="rounded border"
                      />
                      {tool}
                    </label>
                  ))}
                </div>
                <button
                  onClick={handleSaveConfiguration}
                  className="mt-6 rounded bg-primary px-4 py-2 font-mono text-[10px] font-bold uppercase tracking-widest text-primary-foreground hover:brightness-110 transition"
                >
                  Save Configuration
                </button>
              </div>
            </div>

            <div>
              <p className="mb-4 font-mono text-[10px] uppercase tracking-[.2em] text-accent">
                Permissions
              </p>
              <div className="rounded border bg-card p-6">
                <div className="grid gap-2">
                  {availablePermissions.map(perm => (
                    <label key={perm} className="flex items-center gap-3 text-sm">
                      <input
                        type="checkbox"
                        checked={selectedPermissions.includes(perm)}
                        onChange={e => {
                          if (e.target.checked) {
                            setSelectedPermissions([...selectedPermissions, perm])
                          } else {
                            setSelectedPermissions(selectedPermissions.filter(p => p !== perm))
                          }
                        }}
                        className="rounded border"
                      />
                      {perm}
                    </label>
                  ))}
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleDuplicate}
                className="flex items-center justify-center gap-2 rounded border px-4 py-2 font-mono text-[10px] font-bold uppercase tracking-widest hover:bg-muted"
              >
                <Copy className="size-4" /> Duplicate
              </button>
              <button
                onClick={handleDeleteAgent}
                className="flex items-center justify-center gap-2 rounded border border-red-500/30 text-red-400 px-4 py-2 font-mono text-[10px] font-bold uppercase tracking-widest hover:bg-red-500/10 transition"
              >
                <Trash2 className="size-4" /> Delete Agent
              </button>
            </div>
          </div>
        )}

        {/* Run Tab */}
        {tab === 'Run' && selected && (
          <div className="space-y-6">
            <div className="rounded border bg-card p-6">
              <p className="mb-4 font-mono text-[10px] uppercase tracking-[.2em] text-accent">
                Execute agent
              </p>
              <form onSubmit={handleRunAgent} className="flex flex-col gap-4">
                <div>
                  <label className="text-xs font-medium">Input / Prompt</label>
                  <textarea
                    value={runInput}
                    onChange={e => setRunInput(e.target.value)}
                    placeholder="Enter the task or query for the agent..."
                    className="mt-2 w-full rounded border bg-muted p-3 font-mono text-[10px] text-foreground placeholder-muted-foreground focus:border-accent focus:outline-none"
                    rows={4}
                  />
                </div>
                <button
                  disabled={runLoading || !runInput.trim()}
                  className="flex items-center justify-center gap-2 rounded bg-accent px-4 py-2.5 font-mono text-[10px] font-bold uppercase tracking-widest text-accent-foreground disabled:opacity-60"
                >
                  <Play className="size-4" /> Run Agent
                </button>
              </form>
            </div>

            {runs.length > 0 && (
              <div className="rounded border bg-card p-6">
                <p className="mb-4 font-mono text-[10px] uppercase tracking-[.2em] text-accent">
                  Execution history
                </p>
                <div className="space-y-3">
                  {runs.map(run => (
                    <div key={run.id} className="rounded border border-border/50 bg-muted/30 p-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <p className="text-sm font-medium">{run.agentName}</p>
                          <div className="mt-2 flex gap-4 text-[10px] text-muted-foreground">
                            <span>Tokens in: {run.inputTokens}</span>
                            <span>Tokens out: {run.outputTokens}</span>
                            <span>Duration: {run.duration}</span>
                          </div>
                        </div>
                        <span
                          className={`rounded px-2 py-1 font-mono text-[9px] uppercase tracking-widest ${
                            run.status === 'Complete'
                              ? 'bg-emerald-500/20 text-emerald-600'
                              : run.status === 'Running'
                                ? 'bg-blue-500/20 text-blue-600'
                                : run.status === 'Failed'
                                  ? 'bg-destructive/20 text-destructive'
                                  : 'bg-muted text-muted-foreground'
                          }`}
                        >
                          {run.status}
                        </span>
                      </div>
                      {run.result && (
                        <div className="mt-3 rounded bg-background p-2 text-xs text-foreground">
                          <p className="font-mono text-[9px] text-muted-foreground">Result:</p>
                          <p className="mt-1 line-clamp-3">{run.result}</p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Orchestration Tab */}
        {tab === 'Orchestration' && (
          <div>
            <div className="mb-6 rounded border bg-card p-6">
              <p className="mb-4 font-mono text-[10px] uppercase tracking-[.2em] text-accent">
                Multi-agent workflow
              </p>
              <p className="mb-6 text-sm text-muted-foreground">
                Chain multiple agents together to solve complex tasks requiring sequential reasoning and
                tool use.
              </p>
              <button
                onClick={handleRunWorkflow}
                disabled={orchestrating || agents.length < 2}
                className="flex items-center justify-center gap-2 rounded bg-primary px-4 py-2.5 font-mono text-[10px] font-bold uppercase tracking-widest text-primary-foreground disabled:opacity-60"
              >
                {orchestrating ? <span className="size-4 animate-spin rounded-full border-2 border-current border-t-transparent" /> : <Zap className="size-4" />}
                {orchestrating ? 'Running...' : 'Run Orchestration'}
              </button>
            </div>

            {workflow.length > 0 && (
              <div className="rounded border bg-card p-6">
                <p className="mb-4 font-mono text-[10px] uppercase tracking-[.2em] text-accent">
                  Workflow execution
                </p>
                <div className="space-y-4">
                  {workflow.map((step, idx) => (
                    <div key={step.id} className="flex gap-3">
                      <div className="flex flex-col items-center">
                        <div
                          className={`grid size-8 place-items-center rounded border ${
                            step.status === 'Complete'
                              ? 'border-emerald-500 bg-emerald-500/10 text-emerald-600'
                              : step.status === 'Running'
                                ? 'border-blue-500 bg-blue-500/10 text-blue-600 animate-pulse'
                                : 'border-border bg-muted text-muted-foreground'
                          }`}
                        >
                          {step.status === 'Complete' ? (
                            <Check className="size-4" />
                          ) : step.status === 'Running' ? (
                            <span className="size-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
                          ) : (
                            <span className="text-[10px]">{idx + 1}</span>
                          )}
                        </div>
                        {idx < workflow.length - 1 && <div className="my-1 h-6 border-l border-border" />}
                      </div>
                      <div className="flex-1 pt-1">
                        <p className="font-semibold text-sm">{step.name}</p>
                        <p className="mt-1 text-[10px] text-muted-foreground">{step.agent}</p>
                        {step.output && (
                          <p className="mt-2 text-xs text-foreground">{step.output}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* History Tab */}
        {tab === 'History' && (
          <div className="rounded border bg-card p-6">
            <p className="mb-4 font-mono text-[10px] uppercase tracking-[.2em] text-accent">
              Recent executions
            </p>
            <div className="space-y-2">
              {runs.length === 0 ? (
                <div className="flex min-h-[200px] items-center justify-center rounded border border-dashed">
                  <p className="text-sm text-muted-foreground">No execution history yet</p>
                </div>
              ) : (
                runs.slice(0, 10).map(run => (
                  <div key={run.id} className="flex items-center justify-between rounded border border-border/50 p-3">
                    <div>
                      <p className="text-sm font-medium">{run.agentName}</p>
                      <p className="mt-1 text-[10px] text-muted-foreground">{run.startTime}</p>
                    </div>
                    <span
                      className={`rounded px-2 py-1 font-mono text-[9px] uppercase tracking-widest ${
                        run.status === 'Complete'
                          ? 'bg-emerald-500/20 text-emerald-600'
                          : 'bg-muted text-muted-foreground'
                      }`}
                    >
                      {run.status}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}

        {/* Health Tab */}
        {tab === 'Health' && (
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {health.map(item => (
              <div key={item.id} className="rounded border bg-card p-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-sm">{item.component}</h3>
                  <span
                    className={`size-2 rounded-full ${
                      item.status === 'Healthy'
                        ? 'bg-emerald-500'
                        : item.status === 'Warning'
                          ? 'bg-amber-500'
                          : 'bg-red-500'
                    }`}
                  />
                </div>
                <p className="mt-3 text-[10px] text-muted-foreground">
                  Uptime: <span className="text-foreground">{item.uptime}</span>
                </p>
                <p className="mt-2 text-[10px] text-muted-foreground">
                  Latency: <span className="text-foreground">{item.latency}</span>
                </p>
                {item.details && (
                  <p className="mt-2 text-[10px] text-muted-foreground">{item.details}</p>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
