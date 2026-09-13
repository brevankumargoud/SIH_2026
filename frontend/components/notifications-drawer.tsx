'use client'

import { useState } from 'react'
import { Bell, ShieldCheck, AlertTriangle, Info, Check, Trash2, X } from 'lucide-react'

export interface NotificationItem {
  id: string
  title: string
  desc: string
  time: string
  type: 'security' | 'system' | 'model'
  read: boolean
}

interface NotificationsDrawerProps {
  isOpen: boolean
  onClose: () => void
}

export function NotificationsDrawer({ isOpen, onClose }: NotificationsDrawerProps) {
  const [notifications, setNotifications] = useState<NotificationItem[]>([
    {
      id: 'notif-1',
      title: 'Air-Gap Security Verified',
      desc: 'Cryptographic zero-egress hardware boundary confirmed operational.',
      time: '5m ago',
      type: 'security',
      read: false,
    },
    {
      id: 'notif-2',
      title: 'Vector Store Re-indexed',
      desc: 'Plant Operations knowledge base synced 12,842 local chunks.',
      time: '32m ago',
      type: 'system',
      read: false,
    },
    {
      id: 'notif-3',
      title: 'Local Model Sovereign-32B Active',
      desc: 'Inference runtime initialized with INT8 quantization on local device.',
      time: '1h ago',
      type: 'model',
      read: true,
    },
    {
      id: 'notif-4',
      title: 'Audit Stream Encrypted',
      desc: 'Append-only ledger updated with 42 new verified operational events.',
      time: '2h ago',
      type: 'security',
      read: true,
    },
  ])

  if (!isOpen) return null

  const markAllAsRead = () => {
    setNotifications(notifications.map(n => ({ ...n, read: true })))
  }

  const clearAll = () => {
    setNotifications([])
  }

  const unreadCount = notifications.filter(n => !n.read).length

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-xs">
      <div className="flex h-full w-full max-w-md flex-col border-l border-white/10 bg-[#0c1524] text-foreground shadow-2xl animate-rise">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-white/10 p-5">
          <div className="flex items-center gap-2.5">
            <div className="grid size-9 place-items-center rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Bell className="size-4" />
            </div>
            <div>
              <h2 className="text-sm font-semibold">Security & System Alerts</h2>
              <p className="font-mono text-[10px] text-cyan-400">
                {unreadCount} Unread Telemetry Signal{unreadCount !== 1 ? 's' : ''}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            aria-label="Close notifications"
            className="rounded p-1.5 text-muted-foreground hover:bg-muted hover:text-foreground transition"
          >
            <X className="size-4" />
          </button>
        </div>

        {/* Action toolbar */}
        <div className="flex items-center justify-between border-b border-white/5 bg-white/[0.02] px-5 py-2.5 text-[10px] font-mono uppercase tracking-wider">
          <button
            onClick={markAllAsRead}
            disabled={unreadCount === 0}
            className="text-cyan-400 hover:underline disabled:opacity-40 disabled:no-underline"
          >
            Mark all read
          </button>
          <button
            onClick={clearAll}
            disabled={notifications.length === 0}
            className="text-muted-foreground hover:text-red-400 disabled:opacity-40"
          >
            Clear all
          </button>
        </div>

        {/* Notifications list */}
        <div className="flex-1 overflow-y-auto divide-y divide-white/5 p-4 space-y-2">
          {notifications.length === 0 ? (
            <div className="grid min-h-64 place-items-center text-center text-xs text-muted-foreground">
              <div>
                <Check className="mx-auto size-8 text-cyan-400 mb-2" />
                <p className="font-medium text-foreground">No alerts active</p>
                <p className="text-[11px] mt-1">All perimeter systems nominal.</p>
              </div>
            </div>
          ) : (
            notifications.map(item => (
              <div
                key={item.id}
                className={`rounded-lg border p-3.5 transition ${
                  item.read
                    ? 'border-white/5 bg-card/40 opacity-80'
                    : 'border-cyan-500/30 bg-cyan-500/5 shadow-[0_0_15px_rgba(0,210,255,0.05)]'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {item.type === 'security' && <ShieldCheck className="size-3.5 text-cyan-400 shrink-0" />}
                    {item.type === 'system' && <Info className="size-3.5 text-violet-400 shrink-0" />}
                    {item.type === 'model' && <AlertTriangle className="size-3.5 text-amber-400 shrink-0" />}
                    <h3 className="text-xs font-semibold text-foreground">{item.title}</h3>
                  </div>
                  <span className="font-mono text-[9px] text-muted-foreground shrink-0">{item.time}</span>
                </div>
                <p className="mt-1.5 text-xs text-muted-foreground leading-relaxed">{item.desc}</p>
              </div>
            ))
          )}
        </div>

        {/* Footer info */}
        <div className="border-t border-white/10 p-4 text-center font-mono text-[9px] text-muted-foreground uppercase tracking-wider">
          Sovereign Security Stream • Air-Gapped
        </div>
      </div>
    </div>
  )
}
