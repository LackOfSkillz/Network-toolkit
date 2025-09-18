/**
 * themeProvider
 *
 * A tiny theme provider exposing `useTheme()` to toggle light/dark
 * themes. The selection is persisted to localStorage. This header is
 * informational only.
 */
import React, { createContext, useState, useContext, useEffect } from 'react'

const ThemeContext = createContext()

export function ThemeProvider({ children }){
  const [theme, setTheme] = useState(()=> localStorage.getItem('theme') || 'light')

  useEffect(()=>{
    try{ localStorage.setItem('theme', theme) }catch(_){}
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  function toggleTheme(){ setTheme(t => t === 'light' ? 'dark' : 'light') }

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

export function useTheme(){ return useContext(ThemeContext) }

export default ThemeProvider
