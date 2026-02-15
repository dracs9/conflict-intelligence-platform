import '../styles/globals.css'
import type { AppProps } from 'next/app'
import { useEffect, useState } from 'react'

export default function App({ Component, pageProps }: AppProps) {
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    if (typeof window === 'undefined') return 'dark'
    return (localStorage.getItem('theme') as 'dark' | 'light') || 'dark'
  })

  useEffect(() => {
    document.documentElement.classList.toggle('theme-light', theme === 'light')
    localStorage.setItem('theme', theme)
  }, [theme])

  return (
    <>
      {/* floating theme toggle (available on every page) */}
      <div className="theme-toggle fixed top-4 right-4 z-50">
        <button
          aria-label="Toggle theme"
          className="w-10 h-10 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center shadow-sm hover:scale-105 transition-transform"
          onClick={() => setTheme(t => (t === 'dark' ? 'light' : 'dark'))}
        >
          {theme === 'dark' ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 3v1m0 16v1m8.66-9H21M3 12H4.34M18.36 5.64l-.7.7M6.34 17.66l-.7.7M18.36 18.36l-.7-.7M6.34 6.34l-.7-.7M12 5a7 7 0 1 0 7 7" />
            </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          )}
        </button>
      </div>

      {/* global animated background (moved here so all pages share it) */}
      <div className="global-bg">
        <div className="stars" />
        <div className="cosmic-bg" />
      </div>

      <Component {...pageProps} />
    </>
  )
}
