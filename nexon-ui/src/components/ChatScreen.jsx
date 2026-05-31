import { useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import MessageBubble from './MessageBubble.jsx'
import ChatInput from './ChatInput.jsx'
import StatusBadge from './StatusBadge.jsx'

/**
 * ChatScreen — thread-aware scrollable conversation view.
 *
 * - Displays messages from the active thread (passed as `messages`).
 * - TTS is handled by the voice session (useVoiceSession) when active;
 *   this screen handles the fallback non-voice TTS playback.
 * - Voice session remains active after image generation.
 */
export default function ChatScreen({
  messages,
  status,
  onSend,
  ttsReady,
  config,
  isVoiceSessionActive,
  threadTitle,
}) {
  const bottomRef       = useRef(null)
  const audioRef        = useRef(null)
  // Track the last ttsReady counter value we actually played.
  // Initialise to the CURRENT value so that on mount we skip any
  // TTS events that already fired while this screen was unmounted.
  const lastPlayedRef   = useRef(ttsReady)
  const isProcessing    = status !== 'Available...' && status !== 'Connecting...'

  /* ── Auto-scroll ─────────────────────────────────────────────────────── */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' })
  }, [messages, isProcessing])

  /* ── TTS fallback playback (only when voice session is NOT active) ────── */
  useEffect(() => {
    // Skip if voice session is handling TTS
    if (isVoiceSessionActive) return
    // Skip if this is not a NEW tts event (prevents replay on re-mount)
    if (ttsReady === 0 || ttsReady <= lastPlayedRef.current) return

    lastPlayedRef.current = ttsReady
    let isCancelled = false

    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.src = ''
      audioRef.current = null
    }

    fetch(`/api/tts/audio?t=${Date.now()}`)
      .then(res => res.blob())
      .then(blob => {
        if (isCancelled) return
        const url   = URL.createObjectURL(blob)
        const audio = new Audio(url)
        audioRef.current = audio
        audio.play().catch(e => {
          console.warn('[TTS] Autoplay blocked:', e.message)
        })
      })
      .catch(e => console.error('[TTS Error]', e))

    return () => {
      isCancelled = true
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.src = ''
      }
    }
  }, [ttsReady, isVoiceSessionActive])

  const isEmpty = messages.length === 0

  return (
    <div className="h-full flex flex-col overflow-hidden">

      {/* ── Status bar ──────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between px-5 py-2.5 border-b border-white/5 shrink-0">
        <div className="flex items-center gap-3">
          <StatusBadge status={status} />
          {/* Thread title */}
          {threadTitle && threadTitle !== 'New Chat' && (
            <span className="text-xs text-slate-600 font-medium truncate max-w-[200px]">
              {threadTitle}
            </span>
          )}
        </div>

        <div className="flex items-center gap-3">
          {/* Voice active badge */}
          {isVoiceSessionActive && (
            <motion.div
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/25"
            >
              <motion.div
                className="w-1.5 h-1.5 rounded-full bg-cyan-400"
                animate={{ scale: [1, 1.4, 1] }}
                transition={{ duration: 1.2, repeat: Infinity }}
              />
              <span className="text-[10px] font-semibold text-cyan-400 uppercase tracking-widest">
                Voice Active
              </span>
            </motion.div>
          )}

          {/* Typing indicator dots */}
          {isProcessing && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex gap-1 items-center"
            >
              {[0, 1, 2].map(i => (
                <motion.div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-violet-500"
                  animate={{ y: [0, -4, 0] }}
                  transition={{ duration: 0.8, repeat: Infinity, delay: i * 0.16, ease: 'easeInOut' }}
                />
              ))}
            </motion.div>
          )}
        </div>
      </div>

      {/* ── Message List ────────────────────────────────────────────────── */}
      <div className="flex-1 overflow-y-auto px-4 py-5 space-y-5 scroll-smooth">

        {/* Empty state */}
        {isEmpty && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="h-full flex flex-col items-center justify-center gap-4 text-center py-16"
          >
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-700 flex items-center justify-center text-3xl shadow-xl shadow-violet-500/20">
              ✦
            </div>
            <div>
              <p className="text-slate-300 font-semibold text-lg">Start a conversation</p>
              <p className="text-slate-600 text-sm mt-1 max-w-xs">
                Type a message or use voice mode to talk with {config?.assistantname ?? 'Nexon'}
              </p>
            </div>

            <div className="flex flex-wrap gap-2 justify-center mt-2 max-w-sm">
              {QUICK_PROMPTS.map(prompt => (
                <motion.button
                  key={prompt}
                  onClick={() => onSend(prompt)}
                  className="px-3 py-1.5 glass rounded-xl text-xs text-slate-400 hover:text-slate-200 hover:border-violet-500/40 transition-colors"
                  whileHover={{ scale: 1.03 }}
                  whileTap={{ scale: 0.97 }}
                >
                  {prompt}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {/* Messages */}
        <AnimatePresence initial={false}>
          {messages.map(msg => (
            <MessageBubble key={msg.id} message={msg} config={config} />
          ))}
        </AnimatePresence>

        {/* Processing indicator */}
        <AnimatePresence>
          {isProcessing && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              className="flex items-center gap-3 px-1"
            >
              <div className="w-8 h-8 rounded-2xl bg-gradient-to-br from-violet-600 to-fuchsia-600 flex items-center justify-center text-xs font-bold shrink-0">
                {(config?.assistantname ?? 'N')[0].toUpperCase()}
              </div>
              <div className="glass px-4 py-3 rounded-2xl rounded-tl-sm flex items-center h-[44px]">
                <div className="flex gap-1">
                  {[0, 1, 2].map(i => (
                    <div key={i} className="typing-dot" style={{ animationDelay: `${i * 0.2}s` }} />
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div ref={bottomRef} className="h-1" />
      </div>

      {/* ── Input Bar ───────────────────────────────────────────────────── */}
      <ChatInput
        onSend={onSend}
        isProcessing={isProcessing}
        config={config}
        isVoiceSessionActive={isVoiceSessionActive}
      />
    </div>
  )
}

/* ── Helpers ────────────────────────────────────────────────────────────── */



const QUICK_PROMPTS = [
  "What's today's news?",
  "Tell me a joke",
  "What's the weather like?",
  "Open YouTube",
  "Generate image of a sunset",
  "What time is it?",
]
