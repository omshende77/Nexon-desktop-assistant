import { motion, AnimatePresence } from 'framer-motion'

/**
 * AIOrb — Minimalist Animated AI Assistant Visual
 *
 * States:
 *   idle       — Small soft-glowing purple sphere.
 *   listening  — Subtle pulsing cyan glow, expanding gentle ripples.
 *   processing — Smooth rotating indigo ring indicating loading state.
 *   speaking   — Audio-reactive pulsing animations with bright fuchsia glow.
 */
export default function AIOrb({ state = 'idle', size = 120 }) {
  // Base sphere colors per state
  const sphereColors = {
    idle:       'bg-violet-500 shadow-violet-500/50',
    listening:  'bg-cyan-400 shadow-cyan-400/60',
    processing: 'bg-indigo-500 shadow-indigo-500/50',
    speaking:   'bg-fuchsia-500 shadow-fuchsia-500/60',
  }

  return (
    <div
      className="relative flex items-center justify-center select-none"
      style={{ width: size, height: size }}
    >
      {/* ── Background Glow ──────────────────────────────────────────────── */}
      <motion.div
        className="absolute inset-0 rounded-full blur-xl opacity-60"
        animate={{
          backgroundColor:
            state === 'idle'       ? '#8b5cf6' :
            state === 'listening'  ? '#22d3ee' :
            state === 'processing' ? '#6366f1' :
                                     '#d946ef'
        }}
        transition={{ duration: 1.5 }}
      />

      {/* ── Listening Ripples ────────────────────────────────────────────── */}
      <AnimatePresence>
        {state === 'listening' && (
          <>
            {[0, 1].map(i => (
              <motion.div
                key={`ripple-${i}`}
                className="absolute inset-0 rounded-full border-2 border-cyan-400/40"
                initial={{ scale: 1, opacity: 1 }}
                animate={{ scale: 2.2 + i * 0.5, opacity: 0 }}
                exit={{ opacity: 0, transition: { duration: 0.5 } }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  delay: i * 1,
                  ease: 'easeOut',
                }}
              />
            ))}
          </>
        )}
      </AnimatePresence>

      {/* ── Processing Ring ──────────────────────────────────────────────── */}
      <AnimatePresence>
        {state === 'processing' && (
          <motion.div
            className="absolute rounded-full border-t-2 border-r-2 border-indigo-400"
            style={{ width: size * 1.3, height: size * 1.3 }}
            initial={{ opacity: 0, rotate: 0 }}
            animate={{ opacity: 1, rotate: 360 }}
            exit={{ opacity: 0, scale: 0.8, transition: { duration: 0.5 } }}
            transition={{
              opacity: { duration: 0.5 },
              rotate: { duration: 1.2, repeat: Infinity, ease: 'linear' }
            }}
          />
        )}
      </AnimatePresence>

      {/* ── Speaking Waveforms (Audio Reactive Illusion) ─────────────────── */}
      <AnimatePresence>
        {state === 'speaking' && (
          <motion.div
            className="absolute flex items-center justify-center gap-1.5"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0, transition: { duration: 0.3 } }}
          >
            {[1, 2, 3, 4, 5].map((i) => (
              <motion.div
                key={`bar-${i}`}
                className="w-1.5 rounded-full bg-white/80 z-20"
                animate={{
                  height: [
                    size * 0.2,
                    size * (0.4 + Math.random() * 0.4),
                    size * 0.2
                  ]
                }}
                transition={{
                  duration: 0.5 + Math.random() * 0.5,
                  repeat: Infinity,
                  ease: 'easeInOut',
                  delay: i * 0.1
                }}
              />
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Core Sphere ──────────────────────────────────────────────────── */}
      <motion.div
        className={`relative z-10 rounded-full shadow-2xl transition-colors duration-1000 ${sphereColors[state]}`}
        style={{ width: size * 0.6, height: size * 0.6 }}
        animate={{
          scale: state === 'speaking' ? [1, 1.15, 1] :
                 state === 'listening' ? [1, 1.05, 1] : 1
        }}
        transition={{
          duration: state === 'speaking' ? 0.8 : 2,
          repeat: Infinity,
          ease: 'easeInOut'
        }}
      >
        {/* Subtle inner gradient to make it look spherical */}
        <div className="absolute inset-0 rounded-full bg-gradient-to-br from-white/30 to-transparent mix-blend-overlay" />
      </motion.div>

    </div>
  )
}
