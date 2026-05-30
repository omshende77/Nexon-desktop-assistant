import { useState, useRef, useCallback, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { groupThreadsByDate } from '../hooks/useThreads.js'

/**
 * ThreadSidebar — ChatGPT-style conversation thread list.
 *
 * Props:
 *   threads         — Thread[]
 *   activeThreadId  — string | null
 *   onSelect        — (threadId) => void
 *   onNew           — () => void
 *   onDelete        — (threadId) => void
 *   onRename        — (threadId, title) => void
 *   isOpen          — boolean
 *   onClose         — () => void (mobile)
 */
export default function ThreadSidebar({
  threads,
  activeThreadId,
  onSelect,
  onNew,
  onDelete,
  onRename,
  isOpen,
  onClose,
}) {
  const groups = groupThreadsByDate(threads)

  return (
    <>
      {/* ── Mobile backdrop ──────────────────────────────────────────────── */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            key="backdrop"
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-30 lg:hidden"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />
        )}
      </AnimatePresence>

      {/* ── Sidebar panel ────────────────────────────────────────────────── */}
      <motion.aside
        className={`h-full flex flex-col bg-[#0a0a14] border-r border-white/5 overflow-hidden z-40
                    ${isOpen ? 'fixed lg:relative top-0 left-0' : 'fixed top-0 left-0 lg:hidden'}`}
        style={{ width: '260px' }}
        initial={false}
        animate={{ 
          x: isOpen ? 0 : '-100%',
          width: isOpen ? 260 : 0
        }}
        transition={{ type: 'spring', stiffness: 300, damping: 35 }}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-4 border-b border-white/5 shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-700 flex items-center justify-center text-[10px] font-bold text-white">
              N
            </div>
            <span className="text-sm font-semibold text-slate-200">Conversations</span>
          </div>
          {/* Close on mobile */}
          <button
            onClick={onClose}
            className="lg:hidden w-7 h-7 rounded-lg glass flex items-center justify-center text-slate-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* New Chat button */}
        <div className="px-3 py-3 shrink-0">
          <motion.button
            onClick={() => { onNew(); onClose() }}
            id="new-chat-btn"
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl
                       glass border border-white/8 hover:border-violet-500/40
                       text-slate-300 hover:text-white text-sm font-medium
                       transition-all duration-200 group"
            whileHover={{ scale: 1.01 }}
            whileTap={{ scale: 0.98 }}
          >
            <span className="w-6 h-6 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-700
                             flex items-center justify-center text-white text-base
                             shadow-lg shadow-violet-500/20 group-hover:shadow-violet-500/40
                             transition-shadow shrink-0">
              +
            </span>
            New Chat
          </motion.button>
        </div>

        {/* Thread list */}
        <div className="flex-1 overflow-y-auto px-2 pb-4 space-y-4 custom-scrollbar">
          {threads.length === 0 ? (
            <div className="px-3 py-8 text-center">
              <p className="text-slate-600 text-xs">No conversations yet.</p>
              <p className="text-slate-700 text-xs mt-1">Start talking to create your first thread.</p>
            </div>
          ) : (
            Object.entries(groups).map(([label, group]) =>
              group.length > 0 ? (
                <div key={label}>
                  <p className="px-3 py-1 text-[10px] font-semibold uppercase tracking-widest text-slate-600">
                    {label}
                  </p>
                  <div className="space-y-0.5">
                    {group.map(thread => (
                      <ThreadItem
                        key={thread.id}
                        thread={thread}
                        isActive={thread.id === activeThreadId}
                        onSelect={() => { onSelect(thread.id); onClose() }}
                        onDelete={() => onDelete(thread.id)}
                        onRename={(title) => onRename(thread.id, title)}
                      />
                    ))}
                  </div>
                </div>
              ) : null
            )
          )}
        </div>
      </motion.aside>
    </>
  )
}

/* ── Thread item ─────────────────────────────────────────────────────────── */

function ThreadItem({ thread, isActive, onSelect, onDelete, onRename }) {
  const [isEditing, setEditing] = useState(false)
  const [editTitle, setEditTitle] = useState(thread.title)
  const inputRef = useRef(null)

  useEffect(() => {
    if (isEditing) inputRef.current?.focus()
  }, [isEditing])

  const commitRename = useCallback(() => {
    setEditing(false)
    if (editTitle.trim() && editTitle !== thread.title) {
      onRename(editTitle.trim())
    } else {
      setEditTitle(thread.title)
    }
  }, [editTitle, thread.title, onRename])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') commitRename()
    if (e.key === 'Escape') { setEditing(false); setEditTitle(thread.title) }
  }

  return (
    <motion.div
      className={`relative group flex items-center gap-2 px-3 py-2.5 rounded-xl
                  cursor-pointer transition-all duration-150
                  ${isActive
                    ? 'bg-violet-500/15 border border-violet-500/25 text-slate-100'
                    : 'hover:bg-white/4 border border-transparent text-slate-400 hover:text-slate-200'
                  }`}
      onClick={!isEditing ? onSelect : undefined}
      whileHover={{ x: 2 }}
      layout
    >
      {/* Chat icon */}
      <span className="shrink-0 text-sm opacity-60">◈</span>

      {/* Title / edit input */}
      <div className="flex-1 min-w-0">
        {isEditing ? (
          <input
            ref={inputRef}
            value={editTitle}
            onChange={e => setEditTitle(e.target.value)}
            onBlur={commitRename}
            onKeyDown={handleKeyDown}
            onClick={e => e.stopPropagation()}
            className="w-full bg-transparent text-xs text-slate-100 focus:outline-none border-b border-violet-500/50"
          />
        ) : (
          <p
            className="text-xs truncate"
            onDoubleClick={(e) => { e.stopPropagation(); setEditing(true) }}
            title={thread.title}
          >
            {thread.title}
          </p>
        )}
      </div>

      {/* Action buttons — only on hover */}
      {!isEditing && (
        <div className="hidden group-hover:flex items-center gap-1 shrink-0">
          <button
            onClick={e => { e.stopPropagation(); setEditing(true) }}
            className="w-5 h-5 flex items-center justify-center rounded text-slate-500 hover:text-slate-200 transition-colors"
            title="Rename"
          >
            ✎
          </button>
          <button
            onClick={e => { e.stopPropagation(); onDelete() }}
            className="w-5 h-5 flex items-center justify-center rounded text-slate-500 hover:text-red-400 transition-colors"
            title="Delete"
          >
            🗑
          </button>
        </div>
      )}
    </motion.div>
  )
}
