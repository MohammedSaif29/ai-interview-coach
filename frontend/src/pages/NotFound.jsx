import { ButtonLink } from '../components/ui/Button.jsx'
import Wordmark from '../components/Wordmark.jsx'

export default function NotFound() {
  return (
    <div className="flex min-h-screen animate-fade-up flex-col px-4 py-6 sm:px-10">
      <Wordmark to="/" />
      <main className="mx-auto flex max-w-md flex-1 flex-col justify-center text-center">
        <h1 className="font-serif text-4xl tracking-tight">This page doesn't exist</h1>
        <p className="mt-3 text-muted">Check the address, or go back to the home page.</p>
        <ButtonLink to="/" className="mx-auto mt-8">Go to home page</ButtonLink>
      </main>
    </div>
  )
}
