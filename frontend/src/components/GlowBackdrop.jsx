// Soft, slowly drifting light behind a dark section. Purely decorative.
export default function GlowBackdrop({ className = '' }) {
  return (
    <div className={`pointer-events-none absolute inset-0 overflow-hidden ${className}`} aria-hidden="true">
      <div className="absolute -left-32 -top-40 size-[34rem] animate-drift rounded-full bg-brand/40 blur-3xl" />
      <div
        className="absolute -bottom-48 right-[-10rem] size-[30rem] animate-drift rounded-full bg-glow/15 blur-3xl"
        style={{ animationDelay: '-11s' }}
      />
      {/* faint dot grid that fades out towards the edges */}
      <div className="absolute inset-0 bg-[radial-gradient(rgba(255,255,255,0.06)_1px,transparent_1px)] [background-size:22px_22px] [mask-image:radial-gradient(ellipse_at_center,black_20%,transparent_75%)]" />
    </div>
  )
}
