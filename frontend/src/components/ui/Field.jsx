import { useState } from 'react'

const inputClasses =
  'block w-full rounded-lg border border-line bg-white px-3.5 py-2.5 text-[15px] text-ink ' +
  'placeholder:text-muted/60 focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/25 ' +
  'aria-[invalid=true]:border-mark'

// A labelled input with an optional hint or error message underneath.
// aria-invalid and aria-describedby let screen readers announce the error.
export function Field({ label, id, error, hint, type = 'text', ...inputProps }) {
  const [showPassword, setShowPassword] = useState(false)
  const isPassword = type === 'password'
  const messageId = `${id}-message`

  return (
    <div>
      <label htmlFor={id} className="block text-sm font-medium">
        {label}
      </label>
      <div className="relative mt-1.5">
        <input
          id={id}
          type={isPassword && showPassword ? 'text' : type}
          aria-invalid={error ? true : undefined}
          aria-describedby={error || hint ? messageId : undefined}
          className={`${inputClasses} ${isPassword ? 'pr-16' : ''}`}
          {...inputProps}
        />
        {isPassword && (
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute inset-y-0 right-0 px-3.5 text-sm font-medium text-muted hover:text-ink"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? 'Hide' : 'Show'}
          </button>
        )}
      </div>
      {error ? (
        <p id={messageId} className="mt-1.5 text-sm text-mark">{error}</p>
      ) : hint ? (
        <p id={messageId} className="mt-1.5 text-sm text-muted">{hint}</p>
      ) : null}
    </div>
  )
}
