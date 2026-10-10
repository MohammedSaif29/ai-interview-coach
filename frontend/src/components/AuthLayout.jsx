import Wordmark from './Wordmark.jsx'
import GlowBackdrop from './GlowBackdrop.jsx'
import Waveform from './Waveform.jsx'

// Shared frame for the login and signup pages:
// form on the left, an example interview question on the right (large screens only).
export default function AuthLayout({ title, subtitle, question, children }) {
  return (
    <div className="grid min-h-screen animate-fade-up lg:grid-cols-2">
      <div className="flex flex-col px-4 py-6 sm:px-10">
        <Wordmark to="/" />
        <main className="mx-auto flex w-full max-w-sm flex-1 flex-col justify-center py-12">
          <h1 className="font-serif text-4xl tracking-tight">{title}</h1>
          <p className="mt-2 text-muted">{subtitle}</p>
          <div className="mt-8">{children}</div>
        </main>
      </div>

      <aside className="relative isolate hidden flex-col justify-end overflow-hidden bg-night p-14 text-white lg:flex" aria-hidden="true">
        <GlowBackdrop />
        <div className="relative">
          <Waveform bars={36} className="mb-10 h-10" />
          <p className="max-w-lg font-serif text-[2.6rem] leading-[1.15] tracking-tight text-balance">
            &ldquo;{question}&rdquo;
          </p>
          <p className="mt-6 text-white/60">A question you might hear in your next interview.</p>
        </div>
      </aside>
    </div>
  )
}
