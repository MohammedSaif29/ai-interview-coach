// An error message box. role="alert" makes screen readers read it out immediately.
export function Alert({ children, className = '' }) {
  return (
    <div role="alert" className={`rounded-lg bg-mark/10 px-4 py-3 text-sm text-mark ${className}`}>
      {children}
    </div>
  )
}
