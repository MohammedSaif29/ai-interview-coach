import { Link } from 'react-router'

// Reusable button styles. Every button on the site uses these,
// so the design stays consistent.
const base =
  'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg font-semibold transition-all duration-200 ' +
  'active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-60 disabled:active:scale-100'

const variants = {
  // hover: a soft glow appears under the button
  primary: 'bg-brand text-white hover:bg-brand-dark hover:shadow-[0_8px_24px_-8px_var(--color-brand)]',
  secondary: 'border border-line bg-white text-ink hover:border-ink/30',
  inverse: 'bg-white text-brand hover:shadow-[0_8px_28px_-6px_rgba(255,255,255,0.6)]',
  // for dark sections: a bright button that glows
  glow:
    'bg-glow text-night shadow-[0_0_24px_-6px_var(--color-glow)] ' +
    'hover:shadow-[0_0_36px_-4px_var(--color-glow)] hover:brightness-105',
  outlineLight: 'border border-white/20 text-white hover:border-white/50 hover:bg-white/5',
}

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2.5 text-[15px]',
  lg: 'px-5 py-3 text-base',
}

function classes(variant, size, className) {
  return `${base} ${variants[variant]} ${sizes[size]} ${className}`
}

export function Button({ variant = 'primary', size = 'md', className = '', ...props }) {
  return <button className={classes(variant, size, className)} {...props} />
}

// Looks like a button, but navigates to another page
export function ButtonLink({ to, variant = 'primary', size = 'md', className = '', ...props }) {
  return <Link to={to} className={classes(variant, size, className)} {...props} />
}

// Plain text-style link button, e.g. "Show another tip"
export function TextButton({ className = '', ...props }) {
  return (
    <button
      className={`text-sm font-semibold text-brand underline-offset-4 hover:underline disabled:opacity-60 ${className}`}
      {...props}
    />
  )
}
