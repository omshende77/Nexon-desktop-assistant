import { useState, useCallback, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useSpeechRecognition } from '../hooks/useSpeechRecognition.js'

/**
 * ChatInput — text + voice input bar, pinned to the bottom of the chat screen.
 *
 * When isVoiceSessionActive is true, shows a session indicator but still allows
 * text input and single-shot mic use for supplementary queries.
 */
export default function ChatInput({ onSend, isProcessing, config, isVoiceSessionActive }) {
  const [text, setText]             = useState('')
  const [isListening, setListening] = useState(false)
  const textareaRef = useRef(null)

  const { startListening, stopListening, isSupported, errorMsg, interimText } =
    useSpeechRecognition()

  const assistantname = config?.assistantname ?? 'Nexon'
  const lang          = 'en-US'

  /* ── Send ─────────────────────────────────────────────────────────────── */
  const handleSend = useCallback(() => {
    const trimmed = text.trim()
    if (!trimmed || isProcessing) return
    onSend(trimmed)
    setText('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
    textareaRef.current?.focus()
  }, [text, isProcessing, onSend])

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  /* ── Auto-resize textarea ─────────────────────────────────────────────── */
  const handleChange = (e) => {
    setText(e.target.value)
    e.target.style.height = 'auto'
    e.target.style.height = Math.min(e.target.scrollHeight, 160) + 'px'
  }

  /* ── Single-shot mic toggle ───────────────────────────────────────────── */
  const handleMicToggle = useCallback(() => {
    if (isListening) {
      stopListening()
      setListening(false)
    } else {
      setText('')
      if (textareaRef.current) textareaRef.current.style.height = 'auto'
      startListening(lang, (transcript) => {
        setListening(false)
        if (transcript) onSend(transcript, true)
      })
      setListening(true)
    }
  }, [isListening, startListening, stopListening, onSend, lang])

  const placeholder = isListening
    ? (interimText || 'Listening…')
    : `Message ${assistantname}… (Enter to send)`

  const displayValue = isListening && interimText ? interimText : text

  return (
    <div className="border-t border-white/5 bg-[#080810]/80 backdrop-blur-sm px-4 pb-4 pt-3">

      {/* Voice session active notice */}
      {isVoiceSessionActive && (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center justify-center gap-2 mb-2"
        >
          <motion.div
            className="w-1.5 h-1.5 rounded-full bg-cyan-400"
            animate={{ scale: [1, 1.5, 1] }}
            transition={{ duration: 1.2, repeat: Infinity }}
          />
          <p className="text-[11px] text-cyan-400/80 font-medium">
            Voice session active — speak or type below
          </p>
        </motion.div>
      )}

      {/* Automation notice */}
      {config?.automation_available === false && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-[10px] text-slate-600 text-center mb-2"
        >
          Running in web mode — desktop automation is disabled
        </motion.p>
      )}

      {/* Input row */}
      <div className="flex items-end gap-3">
        {/* Textarea */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            id="chat-input"
            value={displayValue}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={isProcessing || isListening}
            rows={1}
            className={`w-full glass border rounded-2xl px-4 py-3 text-sm text-slate-100
              placeholder-slate-600 focus:outline-none focus:border-violet-500/50
              focus:ring-1 focus:ring-violet-500/20 resize-none transition-all
              leading-relaxed min-h-[48px]
              disabled:opacity-60 disabled:cursor-not-allowed
              ${isListening ? 'border-violet-500/40 bg-violet-500/5' : 'border-white/8'}`}
            style={{ maxHeight: '160px' }}
          />
          {text.length > 200 && (
            <span className="absolute bottom-2 right-3 text-[10px] text-slate-600">
              {text.length}
            </span>
          )}
        </div>

        {/* Mic button */}
        {isSupported && (
          <motion.button
            type="button"
            id="mic-button"
            onClick={handleMicToggle}
            disabled={isProcessing}
            aria-label={isListening ? 'Stop voice input' : 'Start voice input'}
            className={`shrink-0 w-11 h-11 rounded-2xl flex items-center justify-center text-lg
              transition-all duration-200 focus:outline-none
              disabled:opacity-40 disabled:cursor-not-allowed
              ${isListening
                ? 'bg-red-500/80 border border-red-500/30 shadow-lg shadow-red-500/20'
                : 'glass border-white/8 hover:border-violet-500/40 hover:bg-violet-500/8'
              }`}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.93 }}
          >
            <AnimatePresence mode="wait">
              {isListening
                ? <motion.span key="stop"  initial={{ scale: 0.6 }} animate={{ scale: 1 }} exit={{ scale: 0.6 }}>⏹</motion.span>
                : <motion.span key="mic"   initial={{ scale: 0.6 }} animate={{ scale: 1 }} exit={{ scale: 0.6 }}>🎙</motion.span>
              }
            </AnimatePresence>
          </motion.button>
        )}

        {/* Send button */}
        <motion.button
          type="button"
          id="send-button"
          onClick={handleSend}
          disabled={!text.trim() || isProcessing || isListening}
          aria-label="Send message"
          className="shrink-0 w-11 h-11 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-700
            flex items-center justify-center text-white shadow-lg shadow-violet-500/20
            transition-all duration-200 focus:outline-none
            disabled:opacity-40 disabled:cursor-not-allowed
            hover:from-violet-500 hover:to-indigo-600 hover:shadow-violet-500/30"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.93 }}
        >
          <AnimatePresence mode="wait">
            {isProcessing ? (
              <motion.div
                key="spin"
                className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                animate={{ rotate: 360 }}
                transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
              />
            ) : (
              <motion.svg
                key="send"
                initial={{ scale: 0.7, x: -4 }}
                animate={{ scale: 1, x: 0 }}
                width="16" height="16" viewBox="0 0 24 24"
                fill="none" stroke="currentColor" strokeWidth="2.5"
                strokeLinecap="round" strokeLinejoin="round"
              >
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </motion.svg>
            )}
          </AnimatePresence>
        </motion.button>
      </div>

      {/* Speech error */}
      {errorMsg && (
        <p className="text-[11px] text-red-400/80 mt-2 text-center">{errorMsg}</p>
      )}
    </div>
  )
}
