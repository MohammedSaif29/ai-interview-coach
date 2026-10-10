// An error message box. role="alert" makes screen readers read it out immediately.
// Use `dark` inside dark sections so the text stays readable.
export function Alert({ children, dark = false, className = '' }) {
  const colors = dark ? 'bg-mark-light/10 text-mark-light' : 'bg-mark/10 text-mark'
  return (
    <div role="alert" className={`rounded-lg px-4 py-3 text-sm ${colors} ${className}`}>
      {children}
    </div>
  )
}
