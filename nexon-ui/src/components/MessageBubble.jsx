import { motion, AnimatePresence } from 'framer-motion'

/**
 * MessageBubble — renders a single chat message.
 *
 * Supports three types:
 *   'text'   — regular chat message
 *   'images' — grid of AI-generated images
 *   'info'   — system/automation notice
 *   'error'  — error notice
 */
export default function MessageBubble({ message, config }) {
  const isUser = message.role === 'user'
  const username      = config?.assistantname ? config.username      : 'You'
  const assistantname = config?.assistantname ? config.assistantname : 'Nexon'
  const label = isUser ? username : assistantname

  if (message.type === 'images') {
    return <ImageGrid message={message} assistantname={assistantname} />
  }

  if (message.type === 'info' || message.type === 'error') {
    return <InfoBubble message={message} />
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 16, scale: 0.97 }}
      animate={{ opacity: 1, y: 0,  scale: 1 }}
      transition={{ duration: 0.28, ease: 'easeOut' }}
      className={`flex gap-3 w-full ${isUser ? 'flex-row-reverse' : 'flex-row'}`}
    >
      {/* Avatar */}
      <div className="shrink-0 mt-0.5">
        <div
          className={`w-8 h-8 rounded-2xl flex items-center justify-center text-xs font-bold shadow-md
            ${isUser
              ? 'bg-gradient-to-br from-indigo-500 to-violet-600'
              : 'bg-gradient-to-br from-violet-600 to-fuchsia-600'
            }`}
        >
          {label[0]?.toUpperCase()}
        </div>
      </div>

      {/* Bubble */}
      <div className={`flex flex-col gap-1 max-w-[76%] ${isUser ? 'items-end' : 'items-start'}`}>
        <span className="text-[11px] font-semibold text-slate-500 px-1">
          {label}
        </span>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap break-words
            ${isUser
              ? 'bg-gradient-to-br from-indigo-600 to-violet-700 text-white rounded-tr-sm shadow-lg shadow-indigo-500/15'
              : 'glass text-slate-100 rounded-tl-sm'
            }`}
        >
          {message.content}
        </div>
      </div>
    </motion.div>
  )
}

/* ── Image Grid ─────────────────────────────────────────────────────────── */

function ImageGrid({ message, assistantname }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="flex flex-col gap-2 max-w-[80%]"
    >
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-2xl bg-gradient-to-br from-violet-600 to-fuchsia-600 flex items-center justify-center text-xs font-bold">
          {assistantname[0]?.toUpperCase()}
        </div>
        <span className="text-[11px] font-semibold text-slate-500">{assistantname}</span>
      </div>

      <div className="glass rounded-2xl rounded-tl-sm p-3">
        <p className="text-xs text-slate-400 mb-3 italic">
          🎨 Generated 4 images for: "{message.prompt}"
        </p>
        <div className="grid grid-cols-2 gap-2">
          {message.images.map((src, i) => (
            <motion.a
              key={i}
              href={src}
              target="_blank"
              rel="noopener noreferrer"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1 }}
              className="block rounded-xl overflow-hidden border border-white/10 hover:border-violet-500/50 transition-colors"
            >
              <img
                src={`${src}?t=${Date.now()}`}
                alt={`Generated ${i + 1}`}
                className="w-full aspect-square object-cover hover:scale-105 transition-transform duration-300"
                onError={(e) => {
                  e.target.style.display = 'none'
                  e.target.parentElement.style.display = 'none'
                }}
              />
            </motion.a>
          ))}
        </div>
      </div>
    </motion.div>
  )
}

/* ── Info / Error Bubble ────────────────────────────────────────────────── */

function InfoBubble({ message }) {
  const isError = message.type === 'error'
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`self-center inline-flex items-start gap-2 px-4 py-2.5 rounded-xl text-xs border max-w-[85%]
        ${isError
          ? 'bg-red-500/10 border-red-500/20 text-red-300'
          : 'bg-amber-500/8 border-amber-500/15 text-amber-300/80'
        }`}
    >
      <span className="shrink-0 mt-0.5">{isError ? '⚠️' : 'ℹ️'}</span>
      <span className="leading-relaxed">{message.content}</span>
    </motion.div>
  )
}
