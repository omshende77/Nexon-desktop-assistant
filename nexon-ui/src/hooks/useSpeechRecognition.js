import { useRef, useCallback, useState, useEffect } from 'react'

/**
 * useSpeechRecognition — wraps the browser's native Web Speech API.
 *
 * Modified for robust state transitions and safe restarts.
 */
export function useSpeechRecognition() {
  const recognitionRef  = useRef(null)
  const onFinalRef      = useRef(null)
  const onInterimRef    = useRef(null)
  const continuousModeRef = useRef(false)
  const shouldRestartRef  = useRef(false)
  const langRef           = useRef('en-US')

  const [isListening, setListening]   = useState(false)
  const [interimText, setInterimText] = useState('')
  const [errorMsg, setErrorMsg]       = useState('')

  const isSupported =
    typeof window !== 'undefined' &&
    ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)

  // ── Internal builder ──────────────────────────────────────────────────────
  const buildRecognition = useCallback((lang) => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition
    const rec = new SR()
    rec.lang            = lang
    rec.continuous      = continuousModeRef.current
    rec.interimResults  = true
    rec.maxAlternatives = 1

    rec.onstart = () => {
      setListening(true)
      setInterimText('')
      setErrorMsg('')
    }

    rec.onresult = (event) => {
      let interim = ''
      let final   = ''
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript
        if (event.results[i].isFinal) final += t
        else interim += t
      }

      if (interim) {
        setInterimText(interim)
        onInterimRef.current?.(interim)
      }

      if (final) {
        setInterimText('')
        onInterimRef.current?.('')
        onFinalRef.current?.(final.trim())
      }
    }

    rec.onerror = (event) => {
      setListening(false)
      setInterimText('')
      if (event.error === 'aborted' || event.error === 'no-speech') return
      
      const messages = {
        'not-allowed':         'Microphone access was denied. Please allow microphone permissions.',
        'audio-capture':       'No microphone found.',
        'network':             'Network error during speech recognition.',
        'service-not-allowed': 'Speech recognition service is not allowed.',
      }
      setErrorMsg(messages[event.error] || `Speech error: ${event.error}`)
    }

    rec.onend = () => {
      setInterimText('')
      // Important: Only restart if we are in continuous mode AND explicitly requested to restart.
      // This prevents the silent crashes and duplicate instances.
      if (shouldRestartRef.current && continuousModeRef.current) {
        try {
          recognitionRef.current = buildRecognition(langRef.current)
          recognitionRef.current.start()
        } catch (_) {
          setListening(false)
        }
      } else {
        setListening(false)
      }
    }

    return rec
  }, [])

  // ── Single-shot mode ──────────────────────────────────────────────────────
  const startListening = useCallback((lang = 'en-US', onFinal, onInterim) => {
    if (!isSupported) {
      setErrorMsg('Speech recognition is not supported in this browser. Please use Chrome or Edge.')
      return
    }
    
    // Explicitly abort any running instance before starting
    if (recognitionRef.current) {
      shouldRestartRef.current = false
      try { recognitionRef.current.abort() } catch (e) {}
    }

    continuousModeRef.current = false
    shouldRestartRef.current  = false
    langRef.current           = lang
    onFinalRef.current        = onFinal
    onInterimRef.current      = onInterim ?? null

    const rec = buildRecognition(lang)
    recognitionRef.current = rec
    try { rec.start() } catch (e) { console.warn("Failed to start SR", e) }
  }, [isSupported, buildRecognition])

  // ── Continuous mode (for Voice Session) ───────────────────────────────────
  const startContinuousListening = useCallback((lang = 'en-US', onFinal, onInterim) => {
    if (!isSupported) {
      setErrorMsg('Speech recognition is not supported in this browser. Please use Chrome or Edge.')
      return
    }
    
    if (recognitionRef.current) {
      shouldRestartRef.current = false
      try { recognitionRef.current.abort() } catch (e) {}
    }

    continuousModeRef.current = true
    shouldRestartRef.current  = true
    langRef.current           = lang
    onFinalRef.current        = onFinal
    onInterimRef.current      = onInterim ?? null

    const rec = buildRecognition(lang)
    recognitionRef.current = rec
    try { rec.start() } catch (e) { console.warn("Failed to start continuous SR", e) }
  }, [isSupported, buildRecognition])

  // ── Pause listening (without fully stopping session) ─────────────────────
  const pauseListening = useCallback(() => {
    shouldRestartRef.current = false
    try {
      // Use abort() instead of stop() for immediate shutdown to prevent lingering onend events
      recognitionRef.current?.abort()
    } catch (e) {}
    setListening(false)
  }, [])

  // ── Resume listening (after TTS finishes) ─────────────────────────────────
  const resumeListening = useCallback((lang = 'en-US') => {
    if (!isSupported || !continuousModeRef.current) return
    
    // Safety check: if already listening, don't spin up another instance
    if (isListening) return

    shouldRestartRef.current = true
    langRef.current          = lang
    
    // Abort any zombie instances before recreating
    if (recognitionRef.current) {
      try { recognitionRef.current.abort() } catch (e) {}
    }
    
    try {
      const rec = buildRecognition(lang)
      recognitionRef.current = rec
      rec.start()
    } catch (e) {
      console.warn("Failed to resume listening", e)
      setListening(false)
    }
  }, [isSupported, isListening, buildRecognition])

  // ── Stop completely ────────────────────────────────────────────────────────
  const stopListening = useCallback(() => {
    continuousModeRef.current = false
    shouldRestartRef.current  = false
    try {
      recognitionRef.current?.abort()
    } catch (e) {}
    recognitionRef.current = null
    setListening(false)
    setInterimText('')
  }, [])

  // ── Cleanup ────────────────────────────────────────────────────────────────
  useEffect(() => {
    return () => stopListening()
  }, [stopListening])

  return {
    startListening,
    startContinuousListening,
    pauseListening,
    resumeListening,
    stopListening,
    isListening,
    interimText,
    isSupported,
    errorMsg,
  }
}
