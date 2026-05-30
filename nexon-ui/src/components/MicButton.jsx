import { useState, useCallback } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition.js'

/**
 * MicButton — standalone large microphone button (single-shot mode).
 *
 * Used in contexts that need a simple tap-to-speak button.
 * For continuous voice sessions, use useVoiceSession + HomeScreen instead.
 *
 * Props:
 *   onSend    — (text: string) => void
 *   status    — string (backend status to detect busy state)
 *   lang      — string (BCP 47 language tag, default 'en-US')
 */
export default function MicButton({ onSend, status, lang = 'en-US' }) {
  const [isListening, setListening] = useState(false)
  const [preview, setPreview]       = useState('')

  const { startListening, stopListening, isSupported, errorMsg, interimText } =
    useSpeechRecognition()

  const isProcessing = status !== 'Available...' && status !== 'Connecting...'

  const handleToggle = useCallback(() => {
    if (isProcessing) return

    if (isListening) {
      stopListening()
      setListening(false)
      setPreview('')
    } else {
      setPreview('')
      startListening(lang, (text) => {
        setListening(false)
        setPreview('')
        if (text && typeof onSend === 'function') {
          onSend(text, true)
        }
      })
      setListening(true)
    }
  }, [isListening, isProcessing, startListening, stopListening, lang, onSend])

  const displayText = interimText || preview

  return (
    <div className="flex flex-col items-center gap-4 mt-6">
      <div className="relative flex items-center justify-center">
        {/* Ripple rings */}
        <AnimatePresence>
          {isListening && (
            <>
              {[0, 1, 2].map(i => (
                <motion.span
                  key={i}
                  className="absolute rounded-full border border-violet-500/40"
                  style={{ width: '80px', height: '80px' }}
                  initial={{ scale: 1, opacity: 0.7 }}
                  animate={{ scale: 3.2 + i * 0.5, opacity: 0 }}
                  transition={{ duration: 2, repeat: Infinity, delay: i * 0.5, ease: 'easeOut' }}
                />
              ))}
            </>
          )}
        </AnimatePresence>

        <motion.button
          onClick={handleToggle}
          disabled={!isSupported || isProcessing}
          aria-label={isListening ? 'Stop listening' : 'Start listening'}
          className={`relative z-10 w-20 h-20 rounded-full flex items-center justify-center text-3xl
            transition-colors duration-300 focus:outline-none focus-visible:ring-2 focus-visible:ring-violet-500
            disabled:opacity-40 disabled:cursor-not-allowed
            ${isListening
              ? 'bg-gradient-to-br from-violet-500 to-indigo-600 shadow-2xl shadow-violet-500/50'
              : 'glass border-white/10 hover:border-violet-500/40 hover:shadow-xl hover:shadow-violet-500/20'
            }`}
          whileHover={{ scale: isProcessing ? 1 : 1.06 }}
          whileTap={{ scale: 0.94 }}
          animate={isListening ? {
            boxShadow: ['0 0 30px rgba(124,58,237,0.4)', '0 0 60px rgba(124,58,237,0.8)', '0 0 30px rgba(124,58,237,0.4)']
          } : {}}
          transition={{ duration: 2, repeat: Infinity }}
        >
          {isListening ? '⏹' : '🎙'}
        </motion.button>
      </div>

      {/* Hint / interim text */}
      <AnimatePresence mode="wait">
        {displayText ? (
          <motion.p
            key="interim"
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="text-sm text-slate-300 max-w-xs text-center italic"
          >
            "{displayText}"
          </motion.p>
        ) : (
          <motion.p
            key="hint"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="text-sm text-slate-500"
          >
            {!isSupported
              ? 'Voice input not supported in this browser'
              : isProcessing
                ? status
                : isListening
                  ? 'Listening — tap to stop'
                  : 'Tap to speak'}
          </motion.p>
        )}
      </AnimatePresence>

      {errorMsg && (
        <p className="text-xs text-red-400 max-w-xs text-center">{errorMsg}</p>
      )}
    </div>
  )
}
