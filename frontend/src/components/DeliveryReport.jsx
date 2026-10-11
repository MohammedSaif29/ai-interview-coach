import { formatTime } from '../lib/format.js'
import AnnotatedTranscript from './AnnotatedTranscript.jsx'

/*
  How the answer was spoken: marked-up transcript, pace/fillers/pauses,
  delivery score and tips. Used right after recording and on a saved session's page.
  Designed for the dark panels.
*/
export default function DeliveryReport({ analysis }) {
  const pauses = analysis.hesitation_count + analysis.long_pause_count

  return (
    <div>
      <p className="text-sm text-white/50">Your answer, transcribed</p>
      {analysis.tokens.length > 0 ? (
        <>
          <AnnotatedTranscript tokens={analysis.tokens} />
          {(analysis.filler_count > 0 || pauses > 0) && (
            <p className="mt-2 text-xs text-white/40">
              Filler words are underlined. Pauses are marked where they happened.
            </p>
          )}
        </>
      ) : (
        <p className="mt-2 text-white/60">
          No speech was detected. Record again, a little closer to your microphone.
        </p>
      )}

      <div className="mt-5 flex flex-wrap gap-x-6 gap-y-2 border-t border-white/10 pt-5">
        <Stat value={formatTime(analysis.speaking_seconds)} label="speaking time" />
        <Stat value={analysis.words_per_minute} label={`words per minute, ${analysis.pace}`} />
        <Stat
          value={analysis.filler_count}
          label={analysis.filler_count === 1 ? 'filler word' : 'filler words'}
          highlight={analysis.filler_count > 0}
        />
        <Stat value={pauses} label={pauses === 1 ? 'pause' : 'pauses'} />
      </div>

      <div className="mt-5 border-t border-white/10 pt-5">
        <div className="flex items-baseline gap-3">
          <p className="text-4xl font-semibold leading-none tracking-tight" aria-label={`Delivery score ${analysis.delivery_score} out of 10`}>
            {analysis.delivery_score}
            <span className="ml-1 text-base font-normal text-white/50">/10</span>
          </p>
          <p className="text-sm text-white/60">Delivery score</p>
        </div>
        <ul className="mt-4 space-y-2">
          {analysis.tips.map((tip) => (
            <li key={tip} className="flex gap-3 text-[15px] leading-relaxed text-white/80">
              <span className="mt-2.5 size-1.5 shrink-0 rounded-full bg-glow" aria-hidden="true" />
              {tip}
            </li>
          ))}
        </ul>
      </div>
    </div>
  )
}

function Stat({ value, label, highlight = false }) {
  return (
    <p className="text-sm text-white/60">
      <span className={`mr-1 text-lg font-semibold ${highlight ? 'text-mark-light' : 'text-white'}`}>{value}</span>
      {label}
    </p>
  )
}
