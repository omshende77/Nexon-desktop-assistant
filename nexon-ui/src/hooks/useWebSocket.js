import { useState, useEffect, useRef, useCallback } from 'react'

/**
 * useWebSocket — manages real-time connection to the FastAPI backend.
 *
 * UPDATED:
 *   - Handles streaming token events (type: "token") for live text rendering
 *   - Thread-aware: passes thread_id in every query message
 *   - Syncs thread history to backend on thread switch
 *   - New message types: token, thread_synced, delete_thread
 *
 * Message protocol (Server → Client):
 *   { type: 'init',           username, assistantname, deployment_mode, automation_available, ai_provider }
 *   { type: 'status',         value: string }
 *   { type: 'token',          content: string, thread_id: string }   ← streaming
 *   { type: 'message',        role: 'assistant', content: string, thread_id: string }
 *   { type: 'tts_ready',      url: string }
 *   { type: 'images_ready',   images: string[], prompt: string, navigate?: 'chat' }
 *   { type: 'automation_result', success: bool, commands?, error? }
 *   { type: 'automation_disabled', message: string }
 *   { type: 'thread_synced',  thread_id: string, count: number }
 *   { type: 'error',          message: string }
 *   { type: 'exit' }
 *   { type: 'pong' }
 *
 * Message protocol (Client → Server):
 *   { type: 'query',         text: string, thread_id: string }
 *   { type: 'sync_thread',   thread_id: string, messages: Message[] }
 *   { type: 'delete_thread', thread_id: string }
 *   { type: 'ping' }
 */
export function useWebSocket(url, token, {
  onAppendMessage,     // (message) => void
  onStreamToken,       // (token, thread_id) => void  ← NEW
  onStreamComplete,    // (thread_id) => void          ← NEW
  onNavigate,          // (page) => void
  onVoiceTtsReady,     // () => void
  onVoiceResponse,     // (text) => void
} = {}) {
  const [rawMessages, setRawMessages]   = useState([])
  const [status, setStatus]             = useState('Connecting...')
  const [isConnected, setConnected]     = useState(false)
  const [ttsReady, setTtsReady]         = useState(0)
  const [config, setConfig]             = useState(null)

  const wsRef           = useRef(null)
  const reconnectRef    = useRef(null)
  const pingIntervalRef = useRef(null)
  const isUnmounted     = useRef(false)

  // Keep callback refs current without resubscribing
  const onAppendRef       = useRef(onAppendMessage)
  const onStreamTokenRef  = useRef(onStreamToken)
  const onStreamCompleteRef = useRef(onStreamComplete)
  const onNavigateRef     = useRef(onNavigate)
  const onVoiceTtsRef     = useRef(onVoiceTtsReady)
  const onVoiceRespRef    = useRef(onVoiceResponse)

  useEffect(() => { onAppendRef.current         = onAppendMessage   }, [onAppendMessage])
  useEffect(() => { onStreamTokenRef.current    = onStreamToken     }, [onStreamToken])
  useEffect(() => { onStreamCompleteRef.current = onStreamComplete  }, [onStreamComplete])
  useEffect(() => { onNavigateRef.current       = onNavigate        }, [onNavigate])
  useEffect(() => { onVoiceTtsRef.current       = onVoiceTtsReady  }, [onVoiceTtsReady])
  useEffect(() => { onVoiceRespRef.current      = onVoiceResponse   }, [onVoiceResponse])

  // ── Message handler ────────────────────────────────────────────────────────
  const handleMessage = useCallback((data) => {
    switch (data.type) {

      case 'init': {
        setConfig({
          username:             data.username,
          assistantname:        data.assistantname,
          deployment_mode:      data.deployment_mode,
          automation_available: data.automation_available,
          ai_provider:          data.ai_provider ?? 'Google Gemini',
        })
        setStatus('Available...')
        break
      }

      case 'status':
        setStatus(data.value ?? 'Available...')
        break

      // ── Streaming token (live typing effect) ─────────────────────────────
      case 'token': {
        // Notify App.jsx to append token to the streaming message in the thread
        onStreamTokenRef.current?.(data.content, data.thread_id)
        break
      }

      // ── Full message (streaming complete) ────────────────────────────────
      case 'message': {
        const msg = {
          id:          `msg-${Date.now()}-${Math.random()}`,
          role:        data.role,
          content:     data.content,
          type:        'text',
          timestamp:   Date.now(),
          thread_id:   data.thread_id,
          ai_provider: data.ai_provider, // <-- NEW
        }
        setRawMessages(prev => [...prev, msg])
        onAppendRef.current?.(msg)
        onStreamCompleteRef.current?.(data.thread_id)
        // Notify voice session of new assistant text
        if (data.role === 'assistant') {
          onVoiceRespRef.current?.(data.content)
        }
        break
      }

      case 'tts_ready':
        setTtsReady(n => n + 1)
        onVoiceTtsRef.current?.()
        break

      case 'images_ready': {
        const msg = {
          id:        `img-${Date.now()}`,
          role:      'assistant',
          type:      'images',
          images:    data.images,
          prompt:    data.prompt,
          content:   `Generated 4 images for: "${data.prompt}"`,
          timestamp: Date.now(),
        }
        setRawMessages(prev => [...prev, msg])
        onAppendRef.current?.(msg)
        if (data.navigate) {
          onNavigateRef.current?.(data.navigate)
        }
        break
      }

      case 'automation_disabled': {
        const msg = {
          id:        `auto-${Date.now()}`,
          role:      'assistant',
          type:      'info',
          content:   `⚠️ ${data.message}`,
          timestamp: Date.now(),
        }
        setRawMessages(prev => [...prev, msg])
        onAppendRef.current?.(msg)
        break
      }

      case 'automation_result':
        if (!data.success && data.error) {
          const msg = {
            id:        `err-${Date.now()}`,
            role:      'assistant',
            type:      'info',
            content:   `❌ Automation error: ${data.error}`,
            timestamp: Date.now(),
          }
          setRawMessages(prev => [...prev, msg])
          onAppendRef.current?.(msg)
        }
        break

      case 'error': {
        const msg = {
          id:        `err-${Date.now()}`,
          role:      'assistant',
          type:      'error',
          content:   `⚠️ ${data.message}`,
          timestamp: Date.now(),
        }
        setRawMessages(prev => [...prev, msg])
        onAppendRef.current?.(msg)
        setStatus('Available...')
        break
      }

      case 'thread_synced':
        console.log(`[WS] Thread synced: ${data.thread_id} (${data.count} messages)`)
        break

      case 'info':
        console.info('[Nexon]', data.message)
        break

      case 'exit':
        console.log('[Nexon] Session ended.')
        break

      case 'pong':
        break

      default:
        console.warn('[WS] Unknown message type:', data.type)
    }
  }, [])

  // ── Connection ─────────────────────────────────────────────────────────────
  const connect = useCallback(() => {
    if (isUnmounted.current) return
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    try {
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        if (isUnmounted.current) { ws.close(); return }
        setConnected(true)
        clearTimeout(reconnectRef.current)

        if (token) {
          ws.send(JSON.stringify({ type: 'auth', token }))
        }

        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }))
          }
        }, 30_000)
      }

      ws.onclose = () => {
        setConnected(false)
        clearInterval(pingIntervalRef.current)
        if (!isUnmounted.current) {
          setStatus('Reconnecting...')
          reconnectRef.current = setTimeout(connect, 3000)
        }
      }

      ws.onerror = () => { ws.close() }

      ws.onmessage = (event) => {
        if (isUnmounted.current) return
        try {
          const data = JSON.parse(event.data)
          handleMessage(data)
        } catch (e) {
          console.error('[WS] Parse error:', e)
        }
      }
    } catch (e) {
      console.error('[WS] Connection error:', e)
      if (!isUnmounted.current) {
        reconnectRef.current = setTimeout(connect, 3000)
      }
    }
  }, [url, token, handleMessage])

  useEffect(() => {
    isUnmounted.current = false
    connect()
    return () => {
      isUnmounted.current = true
      clearTimeout(reconnectRef.current)
      clearInterval(pingIntervalRef.current)
      wsRef.current?.close()
    }
  }, [connect])

  // ── Send helpers ───────────────────────────────────────────────────────────
  const sendRaw = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  /**
   * sendQuery — optimistically adds user message to UI,
   * then sends to backend with thread context.
   */
  const sendQuery = useCallback((text, threadId = 'default', isVoice = false) => {
    if (!text?.trim()) return null
    const msg = {
      id:        `user-${Date.now()}`,
      role:      'user',
      content:   text.trim(),
      type:      'text',
      timestamp: Date.now(),
    }
    setRawMessages(prev => [...prev, msg])
    onAppendRef.current?.(msg)
    sendRaw({ type: 'query', text: text.trim(), thread_id: threadId, is_voice: isVoice })
    return msg
  }, [sendRaw])

  /**
   * syncThread — send a thread's message history to backend
   * so Gemini has full conversation context when switching threads.
   */
  const syncThread = useCallback((threadId, messages) => {
    if (!threadId) return
    // Only send user/assistant text messages (not images, info, errors)
    const filtered = messages
      .filter(m => m.type === 'text' && m.content)
      .map(m => ({ role: m.role, content: m.content }))
    sendRaw({ type: 'sync_thread', thread_id: threadId, messages: filtered })
  }, [sendRaw])

  /**
   * notifyThreadDelete — tell backend to clear Gemini history for a thread.
   */
  const notifyThreadDelete = useCallback((threadId) => {
    sendRaw({ type: 'delete_thread', thread_id: threadId })
  }, [sendRaw])

  return {
    rawMessages,
    status,
    isConnected,
    ttsReady,
    config,
    sendQuery,
    sendRaw,
    syncThread,
    notifyThreadDelete,
  }
}
