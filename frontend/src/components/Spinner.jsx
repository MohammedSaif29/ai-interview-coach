export default function Spinner({ label = 'Loading' }) {
  return (
    <div className="grid min-h-screen place-items-center" role="status">
      <span className="size-6 animate-spin rounded-full border-2 border-line border-t-brand motion-reduce:animate-none" />
      <span className="sr-only">{label}</span>
    </div>
  )
}
