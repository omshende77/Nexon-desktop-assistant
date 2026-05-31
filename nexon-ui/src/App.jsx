import { useState, useCallback, useEffect, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import TopBar from "./components/TopBar.jsx";
import HomeScreen from "./components/HomeScreen.jsx";
import ChatScreen from "./components/ChatScreen.jsx";
import ThreadSidebar from "./components/ThreadSidebar.jsx";
import { useWebSocket } from "./hooks/useWebSocket.js";
import { useThreads } from "./hooks/useThreads.js";
import { useVoiceSession } from "./hooks/useVoiceSession.js";
import { useAuth } from "./hooks/useAuth.js";
import LoginScreen from "./components/LoginScreen.jsx";
import SignupScreen from "./components/SignupScreen.jsx";
/**
 * Derive the correct WebSocket URL regardless of deployment environment.
 * - Dev (Vite proxy): ws://localhost:5173/ws → proxied to ws://localhost:8000/ws
 * - Production:       wss://your-domain.com/ws (served directly by FastAPI)
 */
function getWsUrl() {
  const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${protocol}//${window.location.host}/ws`;
}

const WS_URL = getWsUrl();

const PAGE_VARIANTS = {
  home: {
    initial: { opacity: 0, x: -30 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -30 },
  },
  chat: {
    initial: { opacity: 0, x: 30 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 30 },
  },
};

export default function App() {
  const { user, token, loading, login, register, logout } = useAuth();
  useEffect(() => {
    if (user) {
      setActiveScreen("home");
    }
  }, [user?.id]);

  const [activeScreen, setActiveScreen] = useState("home");

  // Sidebar: open by default on desktop (≥1024px), closed on mobile
  const [sidebarOpen, setSidebarOpen] = useState(
    () => window.innerWidth >= 1024,
  );

  // ── Thread management ────────────────────────────────────────────────────
  const {
    threads,
    activeThreadId,
    activeMessages,
    createThread,
    selectThread,
    appendMessage,
    deleteThread,
    renameThread,
  } = useThreads(token, user);

  // Use refs to expose latest versions to callbacks defined before they exist
  const activeThreadIdRef = useRef(activeThreadId);
  const appendMessageRef = useRef(appendMessage);
  const sendQueryRef = useRef(null); // filled after useWebSocket

  useEffect(() => {
    activeThreadIdRef.current = activeThreadId;
  }, [activeThreadId]);
  useEffect(() => {
    appendMessageRef.current = appendMessage;
  }, [appendMessage]);

  // ── Ensure we always have an active thread (stable, via refs) ────────────
  const ensureThread = useCallback(() => {
    if (activeThreadIdRef.current) return activeThreadIdRef.current;
    return createThread();
  }, [createThread]);

  // ── New chat handler ─────────────────────────────────────────────────────
  const handleNewChat = useCallback(() => {
    createThread();
    setActiveScreen("chat");
  }, [createThread]);

  // ── Voice Session (Continuous mode handling) ───────────────────────────────
  const handleVoiceQuery = useCallback(
    async (text) => {
      const threadId = await ensureThread();
      sendQueryRef.current?.(text, threadId, true);
    },
    [ensureThread],
  );

  // onNavigate for voice session (image gen → chat)
  const handleVoiceNavigate = useCallback((page) => {
    setActiveScreen(page);
  }, []);

  const voiceSession = useVoiceSession({
    onQuery: handleVoiceQuery,
    onNavigate: handleVoiceNavigate,
  });

  // Keep voice session notifiers in refs so WebSocket callbacks can call them
  const voiceSessionRef = useRef(voiceSession);
  useEffect(() => {
    voiceSessionRef.current = voiceSession;
  }, [voiceSession]);

  // ── WebSocket ────────────────────────────────────────────────────────────
  const {
    rawMessages,
    status,
    isConnected,
    ttsReady,
    config,
    sendQuery,
    sendRaw,
    syncThread,
  } = useWebSocket(WS_URL, token, {
    onAppendMessage: useCallback((msg) => {
      const tid = activeThreadIdRef.current;
      if (tid) appendMessageRef.current?.(tid, msg);
    }, []),

    onNavigate: useCallback((page) => {
      setActiveScreen(page);
    }, []),

    onVoiceTtsReady: useCallback(() => {
      voiceSessionRef.current?.notifyTtsReady();
    }, []),

    onVoiceResponse: useCallback((text) => {
      voiceSessionRef.current?.notifyResponse(text);
    }, []),
  });

  // Resume listening if backend finished processing without TTS
  useEffect(() => {
    if (status === "Available...") {
      voiceSessionRef.current?.notifyProcessingComplete?.();
    }
  }, [status]);

  // Expose sendQuery to voice session via ref (avoids circular hook dependency)
  sendQueryRef.current = sendQuery;

  // ── Send from chat (text input or quick prompts) ─────────────────────────
  const handleChatSend = useCallback(
    async (text) => {
      if (!text?.trim()) return;
      const threadId = await ensureThread();
      sendQuery(text, threadId);
    },
    [ensureThread, sendQuery],
  );

  // ── Handle thread selection ──────────────────────────────────────────────
  const handleSelectThread = useCallback(
    async (threadId) => {
      const msgs = await selectThread(threadId);
      if (msgs && msgs.length > 0) {
        syncThread(threadId, msgs);
      }
      setActiveScreen("chat");
    },
    [selectThread, syncThread],
  );

  // ── Sidebar toggle ────────────────────────────────────────────────────────
  const handleSidebarToggle = useCallback(() => setSidebarOpen((v) => !v), []);
  const handleSidebarClose = useCallback(() => setSidebarOpen(false), []);

  // ── Responsive sidebar: close on mobile resize ────────────────────────────
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 1024) setSidebarOpen(false);
    };
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  // ── Derived state ─────────────────────────────────────────────────────────
  const activeThread = threads.find((t) => t.id === activeThreadId);
  const threadTitle = activeThread?.title ?? "New Chat";

  // Messages for ChatScreen: prefer active thread, otherwise if a thread is selected show empty, else fallback to raw WebSocket
  const chatMessages = activeThreadId ? activeMessages : rawMessages;

  // Is sidebar actually pushing content on desktop?
  const [isDesktop, setIsDesktop] = useState(() => window.innerWidth >= 1024);
  useEffect(() => {
    const check = () => setIsDesktop(window.innerWidth >= 1024);
    window.addEventListener("resize", check);
    return () => window.removeEventListener("resize", check);
  }, []);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-[#080810] text-white">
        Loading...
      </div>
    );
  }

  if (!user && activeScreen !== "signup") {
    return (
      <div className="h-screen flex overflow-hidden bg-[#080810] relative">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <LoginScreen
          onLogin={login}
          onNavigateToSignup={() => setActiveScreen("signup")}
        />
      </div>
    );
  }

  if (!user && activeScreen === "signup") {
    return (
      <div className="h-screen flex overflow-hidden bg-[#080810] relative">
        <div className="orb orb-1" />
        <div className="orb orb-2" />
        <SignupScreen
          onSignup={register}
          onNavigateToLogin={() => setActiveScreen("login")}
        />
      </div>
    );
  }

  return (
    <div className="h-screen flex overflow-hidden bg-[#080810] relative">
      {/* Background ambient orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />

      {/* ── Thread Sidebar (Left) ─────────────────────────────────────────── */}
      <ThreadSidebar
        threads={threads}
        activeThreadId={activeThreadId}
        onSelect={handleSelectThread}
        onNew={handleNewChat}
        onDelete={deleteThread}
        onRename={renameThread}
        isOpen={sidebarOpen}
        onClose={handleSidebarClose}
      />

      {/* ── Main Content Area (Right) ─────────────────────────────────────── */}
      <div className="flex-1 flex flex-col min-w-0 relative z-10 h-full">
        {/* Chat Header (formerly TopBar) */}
        <TopBar
          activeScreen={activeScreen}
          onNavigate={setActiveScreen}
          isConnected={isConnected}
          config={config}
          onSidebarToggle={handleSidebarToggle}
          onNewChat={handleNewChat}
          isSidebarOpen={sidebarOpen}
          user={user}
          onLogout={logout}
        />

        {/* Dynamic Screen Content */}
        <div className="flex-1 relative overflow-hidden">
          <AnimatePresence mode="wait">
            {activeScreen === "home" ? (
              <motion.div
                key="home"
                variants={PAGE_VARIANTS.home}
                initial="initial"
                animate="animate"
                exit="exit"
                transition={{ duration: 0.25, ease: "easeInOut" }}
                className="absolute inset-0"
              >
                <HomeScreen
                  status={status}
                  isConnected={isConnected}
                  config={config}
                  voiceSession={voiceSession}
                />
              </motion.div>
            ) : (
              <motion.div
                key="chat"
                variants={PAGE_VARIANTS.chat}
                initial="initial"
                animate="animate"
                exit="exit"
                transition={{ duration: 0.25, ease: "easeInOut" }}
                className="absolute inset-0"
              >
                <ChatScreen
                  messages={chatMessages}
                  status={status}
                  onSend={handleChatSend}
                  ttsReady={ttsReady}
                  config={config}
                  isVoiceSessionActive={voiceSession.isSessionActive}
                  threadTitle={threadTitle}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
