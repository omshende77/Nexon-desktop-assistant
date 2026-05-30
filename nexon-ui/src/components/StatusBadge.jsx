import { motion, AnimatePresence } from 'framer-motion'

const STATUS_MAP = {
  'Available...':          { color: 'text-emerald-400', bg: 'bg-emerald-400/10 border-emerald-500/25', dot: 'bg-emerald-400', pulse: false },
  'Connecting...':         { color: 'text-slate-400',   bg: 'bg-slate-400/10  border-slate-500/25',   dot: 'bg-slate-400',   pulse: true  },
  'Reconnecting...':       { color: 'text-amber-400',   bg: 'bg-amber-400/10  border-amber-500/25',   dot: 'bg-amber-400',   pulse: true  },
  'Thinking...':           { color: 'text-amber-400',   bg: 'bg-amber-400/10  border-amber-500/25',   dot: 'bg-amber-400',   pulse: true  },
  'Generating response...':{ color: 'text-violet-400',  bg: 'bg-violet-400/10 border-violet-500/25',  dot: 'bg-violet-400',  pulse: true  },
  'Searching the web...':  { color: 'text-cyan-400',    bg: 'bg-cyan-400/10   border-cyan-500/25',    dot: 'bg-cyan-400',    pulse: true  },
  'Speaking...':           { color: 'text-purple-400',  bg: 'bg-purple-400/10 border-purple-500/25',  dot: 'bg-purple-400',  pulse: true  },
  'Executing task...':     { color: 'text-orange-400',  bg: 'bg-orange-400/10 border-orange-500/25',  dot: 'bg-orange-400',  pulse: true  },
  'Generating image...':   { color: 'text-pink-400',    bg: 'bg-pink-400/10   border-pink-500/25',    dot: 'bg-pink-400',    pulse: true  },
  'Translating...':        { color: 'text-blue-400',    bg: 'bg-blue-400/10   border-blue-500/25',    dot: 'bg-blue-400',    pulse: true  },
}

function getStyle(status) {
  return STATUS_MAP[status] ?? {
    color: 'text-slate-400',
    bg:    'bg-slate-400/10 border-slate-500/25',
    dot:   'bg-slate-400',
    pulse: true,
  }
}

export default function StatusBadge({ status, className = '' }) {
  const style = getStyle(status)

  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={status}
        initial={{ opacity: 0, y: -6, scale: 0.92 }}
        animate={{ opacity: 1, y: 0,  scale: 1 }}
        exit={{    opacity: 0, y:  6, scale: 0.92 }}
        transition={{ duration: 0.18, ease: 'easeOut' }}
        className={`inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border text-xs font-semibold tracking-wide
          ${style.bg} ${style.color} ${className}`}
      >
        <motion.span
          className={`w-2 h-2 rounded-full shrink-0 ${style.dot}`}
          animate={style.pulse ? { scale: [1, 1.6, 1], opacity: [1, 0.4, 1] } : {}}
          transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
        />
        {status}
      </motion.div>
    </AnimatePresence>
  )
}
