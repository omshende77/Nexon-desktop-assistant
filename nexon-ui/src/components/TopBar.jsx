import { motion } from 'framer-motion'

const NAV_ITEMS = [
  { id: 'home', label: 'Home', icon: '⬡' },
  { id: 'chat', label: 'Chat', icon: '◈' },
]

/**
 * TopBar — top navigation bar.
 *
 * Added:
 *   - Hamburger/sidebar toggle button (left of logo)
 *   - "New Chat" quick button (right side)
 */
export default function TopBar({
  activeScreen,
  onNavigate,
  isConnected,
  config,
  onSidebarToggle,
  onNewChat,
}) {
  const assistantname = config?.assistantname ?? 'Nexon'
  const username      = config?.username      ?? 'User'

  return (
    <header className="relative z-20 flex items-center justify-between px-4 py-3 glass border-b border-white/5 shrink-0">

      {/* ── Left: sidebar toggle + logo ─────────────────────────────────── */}
      <div className="flex items-center gap-2 min-w-[160px]">
        {/* Sidebar toggle */}
        <motion.button
          id="sidebar-toggle"
          onClick={onSidebarToggle}
          className="w-9 h-9 rounded-xl glass border-white/8 flex items-center justify-center
                     text-slate-400 hover:text-white hover:border-violet-500/40
                     transition-all duration-200 focus:outline-none shrink-0"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.94 }}
          aria-label="Toggle conversation sidebar"
        >
          <SidebarIcon />
        </motion.button>

        {/* Logo */}
        <div className="relative">
          <motion.div
            className="w-9 h-9 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-700 flex items-center justify-center font-bold text-white text-sm shadow-lg shadow-violet-500/30"
            animate={{ rotate: [0, 3, -3, 0] }}
            transition={{ duration: 6, repeat: Infinity, ease: 'easeInOut' }}
          >
            N
          </motion.div>
          <span
            className={`absolute -top-0.5 -right-0.5 w-2.5 h-2.5 rounded-full border-2 border-[#080810]
              ${isConnected ? 'bg-emerald-400' : 'bg-red-500'}`}
          />
        </div>

        <div className="leading-tight hidden sm:block">
          <span className="font-bold text-white text-sm tracking-wide">
            {assistantname.toUpperCase()}
          </span>
          <span className="text-violet-400 font-bold text-sm"> AI</span>
          <p className="text-[10px] text-slate-500 font-medium tracking-widest uppercase">
            {isConnected ? 'Online' : 'Offline'}
          </p>
        </div>
      </div>

      {/* ── Centre: navigation pills ─────────────────────────────────────── */}
      <nav className="flex items-center glass rounded-2xl p-1 gap-1">
        {NAV_ITEMS.map(item => {
          const isActive = activeScreen === item.id
          return (
            <motion.button
              key={item.id}
              id={`nav-${item.id}`}
              onClick={() => onNavigate(item.id)}
              className={`relative px-5 py-2 rounded-xl text-sm font-medium transition-colors duration-200
                ${isActive ? 'text-white' : 'text-slate-400 hover:text-slate-200'}`}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.97 }}
            >
              {isActive && (
                <motion.div
                  layoutId="active-pill"
                  className="absolute inset-0 rounded-xl bg-gradient-to-br from-violet-600 to-indigo-700 shadow-lg shadow-violet-500/20"
                  transition={{ type: 'spring', bounce: 0.2, duration: 0.4 }}
                />
              )}
              <span className="relative z-10 flex items-center gap-2">
                <span className="text-base">{item.icon}</span>
                {item.label}
              </span>
            </motion.button>
          )
        })}
      </nav>

      {/* ── Right: New Chat + user badge ─────────────────────────────────── */}
      <div className="flex items-center gap-2 min-w-[160px] justify-end">


        <span className="text-sm text-slate-400 hidden lg:block">{username}</span>
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center font-bold text-white text-sm shadow-lg">
          {username[0]?.toUpperCase() ?? 'U'}
        </div>
      </div>
    </header>
  )
}

/* ── Sidebar icon (hamburger) ────────────────────────────────────────────── */

function SidebarIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
      <rect y="3"  width="16" height="1.5" rx="0.75" fill="currentColor" />
      <rect y="7.25" width="11" height="1.5" rx="0.75" fill="currentColor" />
      <rect y="11.5" width="16" height="1.5" rx="0.75" fill="currentColor" />
    </svg>
  )
}
