// Waveform driven by real microphone levels (numbers from 0 to 1).
export default function LiveWaveform({ levels, className = '' }) {
  return (
    <div className={`flex h-16 items-center justify-center gap-[3px] ${className}`} aria-hidden="true">
      {levels.map((level, i) => (
        <span
          key={i}
          className="h-full w-1 rounded-full bg-glow shadow-[0_0_10px_-2px_var(--color-glow)] transition-transform duration-75"
          style={{ transform: `scaleY(${Math.max(0.08, level)})` }}
        />
      ))}
    </div>
  )
}
