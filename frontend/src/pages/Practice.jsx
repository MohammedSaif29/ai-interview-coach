import QuestionCard from '../components/QuestionCard.jsx'
import TipCard from '../components/TipCard.jsx'

export default function Practice() {
  return (
    <div className="mx-auto max-w-3xl">
      <h1 className="font-serif text-4xl tracking-tight sm:text-5xl">Practice</h1>
      <p className="mt-2 text-muted">
        Read the question, take a breath, then answer out loud. Aim for one to two minutes.
      </p>
      <div className="mt-8 rounded-2xl border border-line bg-white p-6 sm:p-10">
        <QuestionCard />
      </div>
      <TipCard className="mt-6" />
    </div>
  )
}
