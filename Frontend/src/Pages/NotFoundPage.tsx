// Frontend/src/Pages/NotFoundPage.tsx
import { Link, useNavigate } from 'react-router-dom'

export const NotFoundPage = () => {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-[#0b0f17] text-slate-100 flex flex-col justify-between selection:bg-emerald-500/20 selection:text-emerald-300">
      {/* Header */}
      <header className="border-b border-slate-800/80 bg-[#0e1626]/70 backdrop-blur-md px-6 py-4">
        <div className="max-w-5xl mx-auto flex items-center gap-2.5">
          <Link to="/" className="flex items-center gap-2.5">
            <img src="/favicon.svg" alt="FreelanceRadar" className="w-7 h-7" />
            <span className="text-base font-bold text-white tracking-tight">
              FreelanceRadar
            </span>
          </Link>
        </div>
      </header>

      {/* Main 404 Hero */}
      <main className="max-w-md mx-auto px-6 py-16 flex flex-col items-center text-center">
        {/* Status Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs font-semibold uppercase tracking-wider mb-6">
          <span className="w-2 h-2 rounded-full bg-rose-400" />
          <span>404 &bull; Signal Lost</span>
        </div>

        {/* Big Glitch / Number */}
        <h1 className="text-6xl sm:text-7xl font-extrabold text-white tracking-tighter mb-4">
          4<span className="text-emerald-400">0</span>4
        </h1>

        {/* Message */}
        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mb-2">
          Page Off Our Radar
        </h2>
        <p className="text-sm text-slate-400 leading-relaxed mb-8">
          The page or project you are searching for has moved, expired, or doesn’t exist in this coordinate.
        </p>

        {/* Navigation CTAs */}
        <div className="flex flex-col sm:flex-row items-center gap-3 w-full justify-center">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm transition shadow-lg shadow-emerald-500/15 cursor-pointer"
          >
            &larr; Back to Home
          </button>
          <Link
            to="/dashboard"
            className="w-full sm:w-auto px-6 py-3 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold text-sm transition cursor-pointer"
          >
            Go to Dashboard &rarr;
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 py-6 px-6 text-center text-xs text-slate-500">
        <p>FreelanceRadar &bull; Real-time job alerts for modern freelancers.</p>
      </footer>
    </div>
  )
}
