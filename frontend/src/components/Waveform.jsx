// Animated voice waveform. Bars bounce while `active`, and settle when it's not.
const HEIGHTS = [45, 70, 55, 90, 65, 100, 50, 80, 60, 95, 40, 75, 85, 55, 70, 45]

export default function Waveform({ active = true, bars = 28, className = '' }) {
  return (
    <div className={`flex h-7 items-center gap-[3px] ${className}`} aria-hidden="true">
      {Array.from({ length: bars }, (_, i) => (
        <span
          key={i}
          className="w-[3px] rounded-full bg-glow transition-transform duration-700"
          style={{
            height: `${HEIGHTS[i % HEIGHTS.length]}%`,
            animation: active ? `wave 0.9s ease-in-out ${(i * 97) % 800}ms infinite alternate` : 'none',
            transform: active ? undefined : 'scaleY(0.18)',
          }}
        />
      ))}
    </div>
  )
}
