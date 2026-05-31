import { useState, useCallback, useEffect, useRef } from 'react'

const STORAGE_KEY = 'nexon_threads'

export function useThreads(token) {
  const [threads, setThreads] = useState([])
  const [activeThreadId, setActiveThreadId] = useState(null)
  const [activeMessages, setActiveMessages] = useState([])
  
  // Try to load from API first, fallback to localStorage
  useEffect(() => {
    const init = async () => {
      if (!token) return;
      try {
        const res = await fetch('/api/conversations', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        if (res.ok) {
          const data = await res.json()
          if (data.status === 'persistent') {
            const apiThreads = data.conversations.map(c => ({
              id: String(c.id),
              title: c.title,
              updatedAt: new Date(c.updated_at).getTime(),
              createdAt: new Date(c.created_at).getTime(),
              messages: []
            }))
            setThreads(apiThreads)
            localStorage.setItem(STORAGE_KEY, JSON.stringify(apiThreads))
            return
          }
        }
      } catch (e) {
        console.warn('[Threads] API fetch failed, falling back to localStorage', e)
      }
      
      // Fallback
      try {
        const raw = localStorage.getItem(STORAGE_KEY)
        if (raw) setThreads(JSON.parse(raw))
      } catch (e) {}
    }
    init()
  }, [])

  const createThread = useCallback(async () => {
    try {
      const res = await fetch('/api/conversations', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ title: 'New Chat' })
      })
      if (res.ok) {
        const data = await res.json()
        if (data.status !== 'ephemeral') {
          const newThread = {
            id: String(data.id),
            title: data.title,
            updatedAt: Date.now(),
            createdAt: Date.now(),
            messages: []
          }
          setThreads(prev => [newThread, ...prev])
          setActiveThreadId(String(data.id))
          setActiveMessages([])
          return String(data.id)
        }
      }
    } catch (e) {
      console.warn('[Threads] Failed to create thread via API', e)
    }
    
    // Fallback
    const id = `thread_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`
    const newThread = { id, title: 'New Chat', createdAt: Date.now(), updatedAt: Date.now(), messages: [] }
    setThreads(prev => [newThread, ...prev])
    setActiveThreadId(id)
    setActiveMessages([])
    return id
  }, [])

  const selectThread = useCallback(async (threadId) => {
    setActiveThreadId(String(threadId))
    
    if (String(threadId).startsWith('thread_')) {
      // It's a local thread
      const t = threads.find(x => x.id === threadId)
      const msgs = t ? (t.messages || []) : []
      setActiveMessages(msgs)
      return msgs
    }

    try {
      const res = await fetch(`/api/conversations/${threadId}/messages`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      if (res.ok) {
        const data = await res.json()
        if (data.status === 'persistent') {
          setActiveMessages(data.messages)
          return data.messages
        }
      }
    } catch (e) {
      console.warn('[Threads] Failed to fetch messages', e)
    }
    
    // Fallback: look in local memory
    let msgs = []
    setThreads(prev => {
      const t = prev.find(x => x.id === threadId)
      if (t) msgs = t.messages || []
      setActiveMessages(msgs)
      return prev
    })
    return msgs
  }, [threads])

  const appendMessage = useCallback((threadId, message) => {
    if (!threadId) return
    
    if (threadId === activeThreadId) {
      setActiveMessages(prev => [...prev, message])
    }

    setThreads(prev => prev.map(t => {
      if (t.id !== threadId) return t
      
      let title = t.title
      if (title === 'New Chat' && message.role === 'user' && message.content) {
        title = message.content.slice(0, 42) + (message.content.length > 42 ? '…' : '')
      }
      const newMessages = t.messages ? [...t.messages, message] : [message]
      return { ...t, title, updatedAt: Date.now(), messages: newMessages }
    }))
  }, [activeThreadId])

  const deleteThread = useCallback(async (threadId) => {
    try {
      if (!String(threadId).startsWith('thread_')) {
        await fetch(`/api/conversations/${threadId}`, { 
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        })
      }
    } catch (e) {}

    setThreads(prev => prev.filter(t => t.id !== threadId))
    setActiveThreadId(prev => {
      if (prev === threadId) {
        setActiveMessages([])
        return null
      }
      return prev
    })
  }, [])

  const renameThread = useCallback(async (threadId, title) => {
    const newTitle = title.trim() || 'New Chat'
    try {
      if (!String(threadId).startsWith('thread_')) {
        await fetch(`/api/conversations/${threadId}`, {
          method: 'PUT',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ title: newTitle })
        })
      }
    } catch (e) {}

    setThreads(prev => prev.map(t =>
      t.id === threadId ? { ...t, title: newTitle, updatedAt: Date.now() } : t
    ))
  }, [])

  const clearAll = useCallback(() => {
    setThreads([])
    setActiveThreadId(null)
    setActiveMessages([])
    try { localStorage.removeItem(STORAGE_KEY) } catch (_) {}
  }, [])

  // Write through cache
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(threads))
    } catch (e) {}
  }, [threads])

  return {
    threads,
    activeThreadId,
    activeMessages,
    createThread,
    selectThread,
    appendMessage,
    deleteThread,
    renameThread,
    clearAll,
  }
}

export function groupThreadsByDate(threads) {
  const now = Date.now()
  const DAY = 86_400_000
  const groups = { Today: [], Yesterday: [], 'Last 7 days': [], Older: [] }

  for (const t of threads) {
    const age = now - t.updatedAt
    if (age < DAY) groups['Today'].push(t)
    else if (age < 2 * DAY) groups['Yesterday'].push(t)
    else if (age < 7 * DAY) groups['Last 7 days'].push(t)
    else groups['Older'].push(t)
  }

  return groups
}
