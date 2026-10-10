import { Link } from 'react-router'
import { useAuth } from '../context/AuthContext.jsx'
import { useInView } from '../hooks/useInView.js'
import { ButtonLink } from '../components/ui/Button.jsx'
import Wordmark from '../components/Wordmark.jsx'
import TranscriptDemo from '../components/TranscriptDemo.jsx'
import QuestionCard from '../components/QuestionCard.jsx'
import GlowBackdrop from '../components/GlowBackdrop.jsx'

const STEPS = [
  {
    title: 'Get a question',
    text: 'Questions from HR and technical rounds, one at a time, so you can focus.',
  },
  {
    title: 'Answer out loud',
    text: 'Speak the way you would in the room. Your answer is recorded and transcribed.',
  },
  {
    title: 'Read your feedback',
    text: 'See your filler words, pace and pauses, with tips to make the next answer stronger.',
  },
]

export default function Landing() {
  const { user } = useAuth()

  return (
    <div className="min-h-screen animate-fade-up">
      {/* Dark "recording booth" hero with the glow */}
      <div className="relative isolate overflow-hidden bg-night">
        <GlowBackdrop />

        <header className="relative mx-auto flex max-w-6xl items-center px-4 py-5 sm:px-6">
          <Wordmark to="/" light compact />
          <nav className="ml-auto flex items-center gap-1 sm:gap-2" aria-label="Account">
            {user ? (
              <ButtonLink to="/dashboard" variant="glow">Go to dashboard</ButtonLink>
            ) : (
              <>
                <Link to="/login" className="whitespace-nowrap rounded-md px-3 py-2 text-[15px] font-medium text-white/80 hover:text-white">
                  Log in
                </Link>
                <ButtonLink to="/signup" variant="glow">Create account</ButtonLink>
              </>
            )}
          </nav>
        </header>

        <section className="relative mx-auto grid max-w-6xl items-center gap-14 px-4 pb-24 pt-10 sm:px-6 lg:grid-cols-[1fr_1.15fr] lg:gap-16 lg:pb-32 lg:pt-20">
          <div>
            <h1 className="font-serif text-5xl leading-[1.04] tracking-tight text-balance text-white sm:text-[4.25rem]">
              Practise interviews out loud.
            </h1>
            <p className="mt-6 max-w-[34rem] text-lg leading-relaxed text-white/65">
              Answer real interview questions by speaking. Interview Bot listens, then shows you
              what to work on: filler words, speaking pace, long pauses, and the answer itself.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <ButtonLink to={user ? '/practice' : '/signup'} variant="glow" size="lg">
                {user ? 'Start practice' : 'Create free account'}
              </ButtonLink>
              <a
                href="#try"
                className="inline-flex items-center rounded-lg border border-white/20 px-5 py-3 font-semibold text-white transition-colors hover:border-white/50 hover:bg-white/5"
              >
                Try a question
              </a>
            </div>
          </div>
          <TranscriptDemo />
        </section>
      </div>

      <main>
        <HowItWorks />

        {/* Live demo using the real API */}
        <section id="try" className="mx-auto max-w-3xl scroll-mt-8 px-4 py-20 sm:px-6">
          <h2 className="font-serif text-3xl tracking-tight">Try a question now</h2>
          <p className="mt-2 text-muted">
            No account needed. Read the question, answer it out loud, then get another.
          </p>
          <div className="mt-8 rounded-2xl border border-line bg-white p-6 sm:p-10">
            <QuestionCard />
          </div>
          {!user && (
            <p className="mt-6 text-muted">
              Want feedback on your answers?{' '}
              <Link to="/signup" className="font-semibold text-brand underline-offset-4 hover:underline">
                Create a free account
              </Link>
            </p>
          )}
        </section>
      </main>

      <footer className="border-t border-line">
        <div className="mx-auto flex max-w-6xl flex-wrap gap-x-6 gap-y-2 px-4 py-8 text-sm text-muted sm:px-6">
          <p>Interview Bot is a final-year project.</p>
          <a
            href="https://github.com/MohammedSaif29/interview-bot"
            className="font-medium text-ink underline-offset-4 hover:underline"
          >
            Source code on GitHub
          </a>
        </div>
      </footer>
    </div>
  )
}

// The steps are a real sequence, so they're numbered, and a line "flows"
// from one to the next when the section scrolls into view.
function HowItWorks() {
  const [ref, inView] = useInView()

  return (
    <section className="border-b border-line bg-white">
      <div className="mx-auto max-w-6xl px-4 py-20 sm:px-6">
        <h2 className="font-serif text-3xl tracking-tight sm:text-4xl">How a practice session works</h2>
        <ol ref={ref} className="relative mt-12 grid gap-10 sm:grid-cols-3 sm:gap-8">
          {/* The connecting line: grey track + teal line that draws left to right */}
          <div aria-hidden="true" className="absolute left-5 right-[calc((100%-4rem)/3-1.25rem)] top-5 hidden h-0.5 bg-line sm:block">
            <div
              className={`h-full origin-left bg-brand transition-transform duration-[1600ms] ease-out ${
                inView ? 'scale-x-100' : 'scale-x-0'
              }`}
            />
          </div>

          {STEPS.map((step, i) => (
            <li
              key={step.title}
              className={`relative transition-all duration-700 ${inView ? 'translate-y-0 opacity-100' : 'translate-y-3 opacity-0'}`}
              style={{ transitionDelay: `${i * 450}ms` }}
            >
              <span
                className={`grid size-10 place-items-center rounded-full font-serif text-lg transition-all duration-700 ${
                  inView
                    ? 'bg-brand text-white shadow-[0_0_0_6px_var(--color-brand-soft),0_0_28px_-2px_var(--color-brand)]'
                    : 'border-2 border-line bg-white text-muted'
                }`}
                style={{ transitionDelay: `${i * 450 + 200}ms` }}
              >
                {i + 1}
              </span>
              <h3 className="mt-5 text-lg font-semibold">{step.title}</h3>
              <p className="mt-2 leading-relaxed text-muted">{step.text}</p>
            </li>
          ))}
        </ol>
      </div>
    </section>
  )
}
