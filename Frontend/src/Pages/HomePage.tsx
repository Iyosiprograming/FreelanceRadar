// Frontend/src/Pages/HomePage.tsx
import { Show, SignInButton, SignUpButton } from '@clerk/react'
import { Link } from 'react-router-dom'

export const HomePage = () => {
  return (
    <div className="min-h-screen bg-[#0b0f17] text-slate-100 flex flex-col justify-between selection:bg-emerald-500/20 selection:text-emerald-300">
      {/* Navigation */}
      <header className="border-b border-slate-800/80 bg-[#0e1626]/70 backdrop-blur-md sticky top-0 z-10 px-6 py-4">
        <div className="max-w-5xl mx-auto flex justify-between items-center">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2.5">
            <img src="/favicon.svg" alt="FreelanceRadar" className="w-7 h-7" />
            <span className="text-base font-bold text-white tracking-tight">
              FreelanceRadar
            </span>
          </Link>

          {/* Auth Actions (UserButton removed as requested) */}
          <nav className="flex items-center gap-3">
            <Show when="signed-out">
              <SignInButton mode="modal" forceRedirectUrl="/dashboard">
                <button className="px-4 py-2 text-xs sm:text-sm font-medium text-slate-300 hover:text-white transition cursor-pointer">
                  Sign In
                </button>
              </SignInButton>
              <SignUpButton mode="modal" forceRedirectUrl="/dashboard">
                <button className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs sm:text-sm transition shadow-lg shadow-emerald-500/15 cursor-pointer">
                  Sign Up Free
                </button>
              </SignUpButton>
            </Show>

            <Show when="signed-in">
              <Link
                to="/dashboard"
                className="inline-flex items-center gap-1.5 px-5 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-xs sm:text-sm transition shadow-lg shadow-emerald-500/15 cursor-pointer"
              >
                <span>Go to Dashboard</span>
                <span aria-hidden="true">&rarr;</span>
              </Link>
            </Show>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="max-w-5xl mx-auto px-4 sm:px-6 py-16 sm:py-24 flex flex-col items-center text-center">
        {/* Status Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold tracking-wide uppercase mb-6">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Real-Time Job Radar</span>
        </div>

        {/* Main Heading */}
        <h1 className="text-3xl sm:text-5xl font-extrabold text-white tracking-tight leading-tight max-w-3xl mb-6">
          Never Miss a Freelance Job Again.{' '}
          <span className="text-emerald-400">Be First to Bid.</span>
        </h1>

        {/* Subtitle */}
        <p className="text-sm sm:text-lg text-slate-400 max-w-2xl leading-relaxed mb-8">
          FreelanceRadar monitors jobs 24/7 matching your exact skills and budget. The moment a client posts a matched project, you get an instant alert on Telegram so you can win the contract.
        </p>

        {/* Main CTA */}
        <div className="flex flex-col sm:flex-row gap-3 items-center justify-center mb-16">
          <Show when="signed-out">
            <SignUpButton mode="modal" forceRedirectUrl="/dashboard">
              <button className="px-7 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm sm:text-base transition shadow-xl shadow-emerald-500/20 cursor-pointer">
                🚀 Start Tracking Jobs for Free
              </button>
            </SignUpButton>
            <SignInButton mode="modal" forceRedirectUrl="/dashboard">
              <button className="px-6 py-3.5 rounded-xl bg-slate-800/80 hover:bg-slate-800 border border-slate-700 text-slate-200 font-semibold text-sm sm:text-base transition cursor-pointer">
                Sign In
              </button>
            </SignInButton>
          </Show>

          <Show when="signed-in">
            <Link
              to="/dashboard"
              className="px-8 py-3.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-sm sm:text-base transition shadow-xl shadow-emerald-500/20 cursor-pointer inline-flex items-center gap-2"
            >
              <span>Open Your Radar Dashboard</span>
              <span aria-hidden="true">&rarr;</span>
            </Link>
          </Show>
        </div>

        {/* Monitored Provider Section */}
        <div className="w-full max-w-md p-4 rounded-2xl bg-[#0e1626] border border-slate-800/80 mb-20 shadow-lg">
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-500 block mb-2">
            Currently Monitored Platform
          </span>
          <div className="flex items-center justify-between p-3 rounded-xl bg-[#090d16] border border-slate-800">
            <div className="flex items-center gap-3">
              {/* Freelancer.com Origami Bird SVG Icon */}
              <div className="w-9 h-9 rounded-lg bg-[#0089e0]/10 border border-[#0089e0]/30 flex items-center justify-center shrink-0">
                <svg
                  className="w-5 h-5 text-[#29b2fe] fill-current"
                  viewBox="0 0 32 32"
                >
                  <path d="M15.5 3.5l11.5 8.5-10 3.7-1.5-12.2zm-2.2 1.5l1.5 10.7-8.8-3.5 7.3-7.2zm2.6 13.1l8.9-3.4-6.8 11.2-2.1-7.8zm-2.3 1.4l1.7 6.4-9.3-3.1 7.6-3.3z" />
                </svg>
              </div>
              <div className="text-left">
                <span className="text-sm font-bold text-white block leading-tight">
                  Freelancer.com
                </span>
                <span className="text-[11px] text-slate-400">
                  Live REST API feed & WebSocket sync
                </span>
              </div>
            </div>

            <span className="inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              Active
            </span>
          </div>
        </div>

        {/* How It Works: 3 Simple Steps */}
        <div className="w-full">
          <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mb-3">
            How It Works in 3 Simple Steps
          </h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-lg mx-auto mb-10">
            Set it up once in 60 seconds and let the radar scan client posts automatically.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
            {/* Step 1 */}
            <div className="p-6 rounded-2xl bg-[#0e1626] border border-slate-800/80 shadow-md">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-lg mb-4">
                🎯
              </div>
              <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider block mb-1">
                Step 1
              </span>
              <h3 className="text-base font-bold text-white mb-2">Set Your Filters</h3>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                Choose your target skills (React, Python, FastAPI, etc.), preferred contract type, and minimum budget thresholds.
              </p>
            </div>

            {/* Step 2 */}
            <div className="p-6 rounded-2xl bg-[#0e1626] border border-slate-800/80 shadow-md">
              <div className="w-10 h-10 rounded-xl bg-sky-500/10 border border-sky-500/20 flex items-center justify-center text-lg mb-4">
                ✈️
              </div>
              <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider block mb-1">
                Step 2
              </span>
              <h3 className="text-base font-bold text-white mb-2">Link Telegram Bot</h3>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                Tap "Connect Telegram" to start our bot. No tedious API configurations or complicated webhooks required.
              </p>
            </div>

            {/* Step 3 */}
            <div className="p-6 rounded-2xl bg-[#0e1626] border border-slate-800/80 shadow-md">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-lg mb-4">
                ⚡
              </div>
              <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider block mb-1">
                Step 3
              </span>
              <h3 className="text-base font-bold text-white mb-2">Bid Before Competitors</h3>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                Get push notifications the moment a client posts. Tap the link, submit your proposal first, and close more deals.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/60 py-8 px-6 text-center text-xs text-slate-500">
        <p>FreelanceRadar &bull; Real-time job alerts for modern freelancers.</p>
      </footer>
    </div>
  )
}
