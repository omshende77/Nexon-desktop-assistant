import { useState, useRef, useCallback, useEffect } from 'react'
import { useSpeechRecognition } from './useSpeechRecognition.js'

/**
 * useVoiceSession — Continuous ChatGPT-style voice session orchestrator.
 *
 * State machine:
 *   idle → listening → processing → speaking → listening → …
 *
 * The session stays active until the user explicitly calls stopSession().
 * Microphone is paused while AI is processing and speaking, then automatically
 * resumed when TTS audio finishes.
 *
 * Usage:
 *   const {
 *     voiceState,       // 'idle' | 'listening' | 'processing' | 'speaking'
 *     isSessionActive,  // boolean
 *     transcript,       // last spoken user text
 *     interimText,      // live interim STT text
 *     lastResponse,     // last AI response text
 *     startSession,     // () => void
 *     stopSession,      // () => void
 *     notifyProcessing, // () => void  — called when query is sent
 *     notifyResponse,   // (text, ttsUrl) => void — called when AI responds
 *     notifyTtsReady,   // () => void  — called when TTS audio is ready
 *   } = useVoiceSession({ onQuery, onNavigate })
 *
 * Props:
 *   onQuery(text)     — called when user speech is finalised; send to backend
 *   onNavigate(page)  — called to switch pages (e.g. 'chat' for image gen)
 */
export function useVoiceSession({ onQuery, onNavigate }) {
  const [voiceState, setVoiceState]       = useState('idle')
  const [isSessionActive, setSession]     = useState(false)
  const [transcript, setTranscript]       = useState('')
  const [lastResponse, setLastResponse]   = useState('')

  const sessionRef      = useRef(false)
  const processingRef   = useRef(false)

  // Initialize a persistent Audio object for playback to bypass Autoplay restrictions
  const audioRef = useRef(null)
  if (!audioRef.current && typeof Audio !== 'undefined') {
    audioRef.current = new Audio()
  }

  const {
    startContinuousListening,
    pauseListening,
    resumeListening,
    stopListening,
    isListening,
    interimText,
    isSupported,
    errorMsg,
  } = useSpeechRecognition()

  // ── Play TTS audio, then resume mic ───────────────────────────────────────
  const playTtsAudio = useCallback((url) => {
    if (!sessionRef.current) return

    setVoiceState('speaking')
    pauseListening()

    const audio = audioRef.current
    if (!audio) return

    // Stop previous audio if any
    audio.pause()
    audio.src = url
    audio.currentTime = 0

    audio.onended = () => {
      if (sessionRef.current) {
        setVoiceState('listening')
        resumeListening('en-US')
      } else {
        setVoiceState('idle')
      }
    }

    audio.onerror = () => {
      console.warn('[VoiceSession] TTS play error')
      if (sessionRef.current) {
        setVoiceState('listening')
        resumeListening('en-US')
      }
    }

    audio.play().catch(e => {
      console.warn('[VoiceSession] TTS play exception:', e)
      if (sessionRef.current) {
        setVoiceState('listening')
        resumeListening('en-US')
      }
    })
  }, [pauseListening, resumeListening])

  // ── Called by useWebSocket when tts_ready fires ────────────────────────────
  const notifyTtsReady = useCallback(() => {
    if (!sessionRef.current) return
    const url = `/api/tts/audio?t=${Date.now()}`
    playTtsAudio(url)
  }, [playTtsAudio])

  // ── Called when user query is sent to backend ─────────────────────────────
  const notifyProcessing = useCallback(() => {
    if (!sessionRef.current) return
    processingRef.current = true
    setVoiceState('processing')
    pauseListening()
  }, [pauseListening])

  // ── Called when AI text response arrives ──────────────────────────────────
  const notifyResponse = useCallback((text) => {
    setLastResponse(text)
  }, [])

  // ── Start session ─────────────────────────────────────────────────────────
  const startSession = useCallback(() => {
    if (!isSupported) return
    sessionRef.current = true
    setSession(true)
    setVoiceState('listening')
    setTranscript('')
    setLastResponse('')

    // Unlock audio context for Autoplay by playing a silent data URI
    if (audioRef.current) {
      audioRef.current.src = 'data:audio/wav;base64,UklGRigAAABXQVZFZm10IBIAAAABAAEARKwAAIhYAQACABAAAABkYXRhAgAAAAEA'
      audioRef.current.play().catch(e => console.warn('[VoiceSession] Audio unlock failed:', e))
    }

    startContinuousListening(
      'en-US',
      // onFinal
      (text) => {
        if (!sessionRef.current || !text.trim()) return
        setTranscript(text)
        processingRef.current = true
        setVoiceState('processing')
        pauseListening()
        onQuery?.(text)
      },
      // onInterim — handled via hook state
      null
    )
  }, [isSupported, startContinuousListening, pauseListening, onQuery])

  // ── Stop session ──────────────────────────────────────────────────────────
  const stopSession = useCallback(() => {
    sessionRef.current = false
    setSession(false)
    setVoiceState('idle')
    processingRef.current = false
    stopListening()

    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.src = ''
    }
  }, [stopListening])

  // ── Cleanup on unmount ────────────────────────────────────────────────────
  useEffect(() => {
    return () => {
      sessionRef.current = false
      stopListening()
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current.src = ''
      }
    }
  }, [stopListening])

  return {
    voiceState,
    isSessionActive,
    transcript,
    interimText,
    lastResponse,
    isSupported,
    errorMsg,
    startSession,
    stopSession,
    notifyProcessing,
    notifyResponse,
    notifyTtsReady,
  }
}
