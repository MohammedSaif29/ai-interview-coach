// The transcript with filler words underlined and pauses marked where they happened.
// Designed for the dark panels.
export default function AnnotatedTranscript({ tokens }) {
  return (
    <p className="mt-2 text-[17px] leading-[1.8] text-white/90 [--filler:var(--color-mark-light)]">
      {tokens.map((token, i) => (
        <span key={i}>
          {token.filler ? <span className="filler">{token.text}</span> : token.text}{' '}
          {token.pause_kind && (
            <>
              <span
                className={`mx-0.5 inline-block rounded px-1.5 align-[1px] text-xs font-medium ${
                  token.pause_kind === 'long' ? 'bg-mark-light/15 text-mark-light' : 'bg-white/10 text-white/60'
                }`}
                title={token.pause_kind === 'long' ? 'Long pause' : 'Hesitation'}
              >
                pause {token.pause_seconds}s
              </span>{' '}
            </>
          )}
        </span>
      ))}
    </p>
  )
}
