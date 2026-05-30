import { motion, AnimatePresence } from 'framer-motion'
import AIOrb from './AIOrb.jsx'
import StatusBadge from './StatusBadge.jsx'

/**
 * HomeScreen — Continuous voice assistant screen.
 *
 * Replaces the Jarvis GIF with an animated AIOrb.
 * Voice input stays on THIS page — no auto-navigation to Chat.
 * Image generation requests navigate to Chat automatically (handled by App.jsx).
 *
 * Props:
 *   status           — string (backend status)
 *   isConnected      — boolean
 *   config           — { assistantname, username, ... }
 *   voiceSession     — { voiceState, isSessionActive, transcript, interimText,
 *                        lastResponse, isSupported, errorMsg,
 *                        startSession, stopSession }
 */
export default function HomeScreen({ status, isConnected, config, voiceSession }) {
  const assistantname = config?.assistantname ?? 'Nexon'

  const {
    voiceState,
    isSessionActive,
    transcript,
    interimText,
    lastResponse,
    isSupported,
    errorMsg,
    startSession,
    stopSession,
  } = voiceSession

  const isProcessing = status !== 'Available...' && status !== 'Connecting...'

  // Derive orb state
  let orbState = 'idle'
  if (isSessionActive) {
    if (voiceState === 'speaking')   orbState = 'speaking'
    else if (voiceState === 'processing' || isProcessing) orbState = 'processing'
    else orbState = 'listening'
  }

  return (
    <div className="h-full flex flex-col relative overflow-hidden select-none px-4">

      {/* ── Background ambient glow changes with state ───────────────────── */}
      <motion.div
        className="absolute pointer-events-none"
        animate={{
          background: orbState === 'idle'       ? 'radial-gradient(circle at center, rgba(124,58,237,0.10) 0%, transparent 65%)' :
                      orbState === 'listening'  ? 'radial-gradient(circle at center, rgba(34,211,238,0.15) 0%, transparent 65%)' :
                      orbState === 'processing' ? 'radial-gradient(circle at center, rgba(167,139,250,0.14) 0%, transparent 65%)' :
                                                  'radial-gradient(circle at center, rgba(192,38,211,0.16) 0%, transparent 65%)',
        }}
        transition={{ duration: 0.8 }}
        style={{ width: '700px', height: '700px', top: '50%', left: '50%', transform: 'translate(-50%, -55%)' }}
      />

      {/* ── AI Orb Section (Centers itself in available space) ───────────── */}
      <div className="flex-1 flex flex-col items-center justify-center relative z-10 mt-6">
        <motion.div
          initial={{ opacity: 0, scale: 0.88, y: 20 }}
          animate={{ opacity: 1, scale: 1,    y: 0 }}
          transition={{ duration: 0.9, ease: [0.25, 0.46, 0.45, 0.94] }}
        >
          <AIOrb state={orbState} size={160} />
        </motion.div>

        {/* ── Assistant name ──────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-center mt-6"
        >
          <h1 className="text-3xl font-bold tracking-widest uppercase gradient-text">
            {assistantname}
          </h1>
          <p className="text-xs text-slate-500 tracking-[0.3em] uppercase mt-1 font-medium">
            AI Voice Assistant
          </p>
        </motion.div>

        {/* ── Status badge ────────────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.4 }}
          className="mt-4"
        >
          <StatusBadge status={isSessionActive ? getVoiceStatus(voiceState, status) : status} />
        </motion.div>
      </div>

      {/* ── Transcript and Controls (Anchored to bottom) ────────────────── */}
      <div className="shrink-0 flex flex-col items-center justify-end pb-8 relative z-10 w-full max-w-lg mx-auto min-h-[220px]">
        
        {/* ── Voice transcript area ────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.4 }}
          className="w-full min-h-[80px] flex flex-col items-center justify-end gap-2"
        >
          {/* Interim / transcript text */}
          <AnimatePresence mode="wait">
            {interimText ? (
              <motion.div
                key="interim"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="voice-card text-slate-300 text-sm text-center italic"
              >
                <span className="text-cyan-400 text-xs font-semibold uppercase tracking-widest block mb-1">Hearing…</span>
                "{interimText}"
              </motion.div>
            ) : transcript && voiceState !== 'idle' ? (
              <motion.div
                key="transcript"
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="voice-card text-slate-300 text-sm text-center"
              >
                <span className="text-violet-400 text-xs font-semibold uppercase tracking-widest block mb-1">You said</span>
                "{transcript}"
              </motion.div>
            ) : null}
          </AnimatePresence>

          {/* AI response text */}
          <AnimatePresence>
            {lastResponse && voiceState !== 'idle' && (
              <motion.div
                key="response"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className="voice-card text-slate-200 text-sm text-center max-h-28 overflow-y-auto"
              >
                <span className="text-fuchsia-400 text-xs font-semibold uppercase tracking-widest block mb-1">
                  {assistantname}
                </span>
                {lastResponse}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Idle hint */}
          {!isSessionActive && !transcript && (
            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-xs text-slate-600 text-center"
            >
              Start a voice session to talk with {assistantname}
            </motion.p>
          )}
        </motion.div>

        {/* ── Voice session controls ───────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.4 }}
          className="mt-5 flex flex-col items-center gap-3"
        >
          {!isSupported ? (
            <p className="text-xs text-amber-400 text-center max-w-xs">
              Voice mode requires Chrome or Edge browser with microphone permissions.
            </p>
          ) : (
            <>
              {/* Main voice session button */}
              <div className="relative flex items-center justify-center">
                {/* Ripple rings when listening */}
                <AnimatePresence>
                  {isSessionActive && orbState === 'listening' && (
                    <>
                      {[0, 1].map(i => (
                        <motion.span
                          key={i}
                          className="absolute rounded-full border border-cyan-500/40"
                          style={{ width: '68px', height: '68px' }}
                          initial={{ scale: 1, opacity: 0.6 }}
                          animate={{ scale: 2.8 + i * 0.5, opacity: 0 }}
                          exit={{ opacity: 0 }}
                          transition={{ duration: 1.8, repeat: Infinity, delay: i * 0.5, ease: 'easeOut' }}
                        />
                      ))}
                    </>
                  )}
                </AnimatePresence>

                <motion.button
                  id="voice-session-btn"
                  onClick={isSessionActive ? stopSession : startSession}
                  disabled={isProcessing && !isSessionActive}
                  aria-label={isSessionActive ? 'Stop voice session' : 'Start voice session'}
                  className={`relative z-10 w-16 h-16 rounded-full flex items-center justify-center text-2xl
                    focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500
                    transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed
                    ${isSessionActive
                      ? orbState === 'listening'
                        ? 'bg-gradient-to-br from-cyan-500 to-blue-600 shadow-2xl shadow-cyan-500/50'
                        : orbState === 'speaking'
                          ? 'bg-gradient-to-br from-fuchsia-500 to-purple-700 shadow-2xl shadow-fuchsia-500/50'
                          : 'bg-gradient-to-br from-violet-500 to-indigo-600 shadow-2xl shadow-violet-500/50'
                      : 'glass border-white/10 hover:border-violet-500/50 hover:shadow-xl hover:shadow-violet-500/20'
                    }`}
                  whileHover={{ scale: 1.07 }}
                  whileTap={{ scale: 0.93 }}
                  animate={isSessionActive && orbState === 'listening'
                    ? { boxShadow: ['0 0 20px rgba(34,211,238,0.3)', '0 0 50px rgba(34,211,238,0.7)', '0 0 20px rgba(34,211,238,0.3)'] }
                    : {}
                  }
                  transition={{ duration: 1.8, repeat: Infinity }}
                >
                  {isSessionActive
                    ? orbState === 'speaking'   ? '🔊'
                    : orbState === 'processing' ? '⏳'
                    : '🎙'
                    : '🎙'}
                </motion.button>
              </div>

              {/* Session label */}
              <AnimatePresence mode="wait">
                <motion.p
                  key={isSessionActive ? 'active' : 'inactive'}
                  initial={{ opacity: 0, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="text-xs font-medium text-center"
                  style={{ color: isSessionActive ? '#22d3ee' : '#64748b' }}
                >
                  {isSessionActive
                    ? orbState === 'listening'  ? 'Listening — tap to stop'
                    : orbState === 'processing' ? `${status}`
                    : orbState === 'speaking'   ? `${assistantname} is speaking…`
                    : 'Session active'
                    : 'Tap to start voice session'}
                </motion.p>
              </AnimatePresence>
            </>
          )}

          {/* Error */}
          {errorMsg && (
            <p className="text-xs text-red-400 max-w-xs text-center">{errorMsg}</p>
          )}
        </motion.div>
      </div>

      {/* ── Offline notice ───────────────────────────────────────────────── */}
      {!isConnected && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="absolute bottom-6 text-xs text-red-400/70 text-center z-10"
        >
          Connecting to backend… ensure FastAPI is running on port 8000
        </motion.p>
      )}

      {/* ── Grid overlay ─────────────────────────────────────────────────── */}
      <div
        className="absolute inset-0 pointer-events-none opacity-[0.02]"
        style={{
          backgroundImage:
            'linear-gradient(rgba(255,255,255,0.4) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.4) 1px, transparent 1px)',
          backgroundSize: '60px 60px',
        }}
      />
    </div>
  )
}

/* ── Helpers ─────────────────────────────────────────────────────────────── */

function getVoiceStatus(voiceState, backendStatus) {
  if (voiceState === 'listening')  return 'Listening...'
  if (voiceState === 'speaking')   return 'Speaking...'
  if (voiceState === 'processing') return backendStatus
  return 'Voice Mode Active'
}
