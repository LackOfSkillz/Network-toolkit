/**
 * useShortcuts
 *
 * Tiny hook to attach keyboard shortcuts. Handlers is a map of key
 * combinations to callback functions — e.g. 'Shift+A' => handler.
 * The hook attaches a single keydown listener and looks up handlers by
 * a normalized key string.
 */
import { useEffect } from 'react'

/**
 * useShortcuts: attach simple keyboard shortcuts
 * handlers: { keyCombo: handler }
 * keyCombo example: 'Shift+A', 'Ctrl+S', 'a'
 */
export default function useShortcuts(handlers = {}){
  useEffect(()=>{
    function parseEventKey(e){
      const parts = []
      if(e.shiftKey) parts.push('Shift')
      if(e.ctrlKey) parts.push('Ctrl')
      if(e.altKey) parts.push('Alt')
      const key = e.key.length === 1 ? e.key.toUpperCase() : e.key
      parts.push(key)
      return parts.join('+')
    }

    function onKey(e){
      const combo = parseEventKey(e)
      const handler = handlers[combo]
      if(handler){
        // prevent default browser shortcuts when handler exists
        try{ e.preventDefault() }catch(_){ }
        handler(e)
      }
    }

    window.addEventListener('keydown', onKey)
    return ()=> window.removeEventListener('keydown', onKey)
  }, [handlers])
}
