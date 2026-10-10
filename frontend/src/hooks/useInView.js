import { useEffect, useRef, useState } from 'react'

/*
  CUSTOM HOOK: tells you when an element scrolls into view.
  Used to start animations only when the user can actually see them.

  const [ref, inView] = useInView()
  <div ref={ref}>...</div>   // inView becomes true once it appears on screen
*/
export function useInView(threshold = 0.35) {
  const ref = useRef(null)
  const [inView, setInView] = useState(false)

  useEffect(() => {
    const element = ref.current
    if (!element) return
    // IntersectionObserver: a browser feature that watches when elements enter the screen
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setInView(true)
          observer.disconnect() // only animate the first time
        }
      },
      { threshold }
    )
    observer.observe(element)
    return () => observer.disconnect()
  }, [threshold])

  return [ref, inView]
}
