// Frontend/src/Pages/DashboardPage.tsx
import { useEffect, useState, useCallback } from 'react'
import { useAuth, useUser, SignOutButton } from '@clerk/react'
import { Link } from 'react-router-dom'
import {
  getFilter,
  createFilter,
  updateFilter,
  deleteFilter,
  type Filter,
  type CreateFilterInput,
  type UpdateFilterInput,
} from '../api/filter'
import { getUserMe, type UserProfile } from '../api/user'
import { FilterForm } from '../Components/FilterForm'

const BOT_USERNAME = import.meta.env.VITE_TELEGRAM_BOT_USERNAME || 'Job_nofticationsbot'

export const DashboardPage = () => {
  const { getToken } = useAuth()
  const { user: clerkUser } = useUser()

  const [user, setUser] = useState<UserProfile | null>(null)
  const [filter, setFilter] = useState<Filter | null>(null)
  const [loading, setLoading] = useState(true)
  const [isEditing, setIsEditing] = useState(false)
  const [notification, setNotification] = useState<{
    type: 'success' | 'error'
    text: string
  } | null>(null)

  // Fetch both user profile and existing filter
  const loadData = useCallback(async () => {
    try {
      const token = await getToken()
      const [userProfile, userFilter] = await Promise.all([
        getUserMe(token),
        getFilter(token),
      ])
      setUser(userProfile)
      setFilter(userFilter)
    } catch (err: unknown) {
      console.error('Error loading dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }, [getToken])

  useEffect(() => {
    loadData()

    // Automatically re-check when the user returns to this tab (e.g. after clicking Start in Telegram)
    const handleFocus = () => loadData()
    window.addEventListener('focus', handleFocus)
    return () => window.removeEventListener('focus', handleFocus)
  }, [loadData])

  // Telegram deep-link URL (includes user UUID token)
  const effectiveUserId = user?.id || filter?.user_id
  const telegramLink = effectiveUserId
    ? `https://t.me/${BOT_USERNAME}?start=${effectiveUserId}`
    : `https://t.me/${BOT_USERNAME}`

  // Handle create or update
  const handleSaveFilter = async (data: CreateFilterInput | UpdateFilterInput) => {
    const token = await getToken()
    let saved: Filter

    if (filter) {
      saved = await updateFilter(data as UpdateFilterInput, token)
      setNotification({ type: 'success', text: 'Filter updated successfully!' })
    } else {
      saved = await createFilter(data as CreateFilterInput, token)
      setNotification({ type: 'success', text: 'Filter activated successfully!' })
    }

    setFilter(saved)
    setIsEditing(false) // Close form and show summary
    setTimeout(() => setNotification(null), 4000)
  }

  // Handle delete
  const handleDeleteFilter = async () => {
    const token = await getToken()
    await deleteFilter(token)
    setFilter(null)
    setIsEditing(false)
    setNotification({ type: 'success', text: 'Filter removed successfully.' })
    setTimeout(() => setNotification(null), 4000)
  }

  const isTelegramConnected = Boolean(user?.telegram_id)

  return (
    <div className="min-h-screen bg-[#0b0f17] text-slate-100">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-[#0e1626]/70 backdrop-blur-md sticky top-0 z-10 px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-2.5">
          <img src="/favicon.svg" alt="FreelanceRadar" className="w-7 h-7" />
          <div>
            <h1 className="text-base font-bold text-white tracking-tight leading-none">
              FreelanceRadar
            </h1>
            <span className="text-[11px] text-slate-400 font-medium">Dashboard</span>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <a
            href="https://github.com/Iyosiprograming/FreelanceRadar"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold text-slate-200 bg-slate-800 hover:bg-slate-700 hover:text-white border border-slate-700 transition shadow-sm cursor-pointer"
            title="View FreelanceRadar on GitHub"
          >
            <svg className="w-4 h-4 fill-current text-white" viewBox="0 0 24 24" aria-hidden="true">
              <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" />
            </svg>
            <span className="hidden sm:inline">GitHub</span>
          </a>
          <Link
            to="/"
            className="text-xs sm:text-sm text-slate-400 hover:text-slate-200 transition"
          >
            &larr; Home
          </Link>
          <div className="h-4 w-px bg-slate-800" />
          
          {/* Profile pic & Sign Out button only (Clerk manage account modal removed) */}
          <div className="flex items-center gap-2.5">
            {clerkUser?.imageUrl ? (
              <img
                src={clerkUser.imageUrl}
                alt={clerkUser.fullName || 'User'}
                className="w-8 h-8 rounded-full border border-slate-700 object-cover"
              />
            ) : (
              <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-xs font-semibold text-slate-300">
                👤
              </div>
            )}
            <SignOutButton redirectUrl="/">
              <button className="px-3 py-1.5 text-xs font-semibold text-slate-300 hover:text-white bg-slate-800/80 hover:bg-slate-700 border border-slate-700 rounded-lg transition cursor-pointer">
                Sign Out
              </button>
            </SignOutButton>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-8 flex flex-col gap-6">
        {/* Toast / Notification Banner */}
        {notification && (
          <div
            className={`px-4 py-3 rounded-xl text-sm font-medium border transition ${
              notification.type === 'success'
                ? 'bg-emerald-500/15 border-emerald-500/30 text-emerald-300'
                : 'bg-rose-500/15 border-rose-500/30 text-rose-300'
            }`}
          >
            {notification.text}
          </div>
        )}

        {/* 1. Live Telegram Connection Banner */}
        <div
          className={`border rounded-2xl p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-lg transition ${
            isTelegramConnected
              ? 'bg-[#0e1c22] border-emerald-500/30'
              : 'bg-[#0e1626] border-slate-800/80'
          }`}
        >
          <div className="flex items-start sm:items-center gap-3.5">
            <div
              className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border ${
                isTelegramConnected
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
                  : 'bg-sky-500/10 border-sky-500/20 text-sky-400'
              }`}
            >
              {/* Telegram Paper Plane Icon */}
              <svg className="w-5 h-5 fill-current" viewBox="0 0 24 24">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69a.2.2 0 00-.05-.18c-.06-.05-.14-.03-.21-.02-.09.02-1.49.95-4.22 2.79-.4.27-.76.41-1.08.4-.36-.01-1.04-.2-1.55-.37-.63-.2-1.12-.31-1.08-.66.02-.18.27-.36.74-.55 2.92-1.27 4.86-2.11 5.83-2.51 2.78-1.16 3.35-1.36 3.73-1.36.08 0 .27.02.39.12.1.08.13.19.14.27-.01.06.01.24 0 .38z" />
              </svg>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-semibold text-white">Telegram Job Alerts</h2>
                {isTelegramConnected ? (
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                    Connected
                  </span>
                ) : (
                  <span className="text-[11px] font-medium px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
                    Not Connected
                  </span>
                )}
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                {isTelegramConnected
                  ? 'Your bot is active and ready to deliver real-time job matches.'
                  : 'Connect our Telegram bot to receive instant alerts when jobs match your filter.'}
              </p>
            </div>
          </div>

          <a
            href={telegramLink}
            target="_blank"
            rel="noopener noreferrer"
            className={`inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl text-xs sm:text-sm font-semibold transition shrink-0 ${
              isTelegramConnected
                ? 'bg-emerald-500/15 hover:bg-emerald-500/25 border border-emerald-500/30 text-emerald-300'
                : 'bg-sky-500/15 hover:bg-sky-500/25 border border-sky-500/30 text-sky-300 hover:text-sky-200'
            }`}
          >
            <span>{isTelegramConnected ? 'Open Telegram Bot' : 'Connect Telegram'}</span>
            <span aria-hidden="true">&rarr;</span>
          </a>
        </div>

        {/* 2. Loading State */}
        {loading && (
          <div className="bg-[#0e1626] border border-slate-800/80 rounded-2xl p-12 flex flex-col items-center justify-center gap-3 text-slate-400">
            <div className="w-6 h-6 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
            <span className="text-xs">Checking your radar settings...</span>
          </div>
        )}

        {/* 3. Editing Mode (Form visible) */}
        {!loading && isEditing && (
          <FilterForm
            initialData={filter}
            onSave={handleSaveFilter}
            onDelete={filter ? handleDeleteFilter : undefined}
            onCancel={() => setIsEditing(false)}
          />
        )}

        {/* 4. No Filter State (Empty state with "+ Create Filter" button) */}
        {!loading && !isEditing && !filter && (
          <div className="bg-[#0e1626] border border-slate-800/80 rounded-2xl p-8 sm:p-12 text-center flex flex-col items-center shadow-lg">
            <div className="w-12 h-12 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-4">
              <span className="w-3 h-3 rounded-full bg-emerald-400" />
            </div>

            <h3 className="text-lg font-bold text-white mb-1.5">No Radar Filter Configured</h3>
            <p className="text-xs sm:text-sm text-slate-400 max-w-md mb-6">
              You haven't set up your job alert filter yet. Configure your required skills and minimum budget to start scanning for jobs.
            </p>

            <button
              type="button"
              onClick={() => setIsEditing(true)}
              className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-sm transition shadow-lg shadow-emerald-500/15 cursor-pointer"
            >
              + Create Filter
            </button>
          </div>
        )}

        {/* 5. Active Filter Summary Card (With "Edit Filter" button) */}
        {!loading && !isEditing && filter && (
          <div className="bg-[#0e1626] border border-slate-800/80 rounded-2xl p-6 sm:p-8 shadow-xl">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-5 mb-6">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className="text-xs font-semibold uppercase tracking-wider text-emerald-400">
                    Active Radar
                  </span>
                </div>
                <h3 className="text-xl font-bold text-white tracking-tight">{filter.name}</h3>
              </div>

              <button
                type="button"
                onClick={() => setIsEditing(true)}
                className="self-start sm:self-auto px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs sm:text-sm font-medium rounded-xl transition cursor-pointer"
              >
                Edit Filter
              </button>
            </div>

            {/* Filter Summary Details */}
            <div className="space-y-5">
              {/* Skills */}
              <div>
                <span className="text-xs font-medium text-slate-400 block mb-2">
                  Target Skills:
                </span>
                {filter.skills && filter.skills.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {filter.skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-3 py-1 rounded-lg text-xs font-medium bg-emerald-500/15 border border-emerald-500/30 text-emerald-300"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                ) : (
                  <span className="text-xs text-slate-500 italic">All skills accepted</span>
                )}
              </div>

              {/* Preferences Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
                <div className="p-3.5 rounded-xl bg-[#090d16] border border-slate-800">
                  <span className="text-[11px] font-medium text-slate-400 block mb-1">
                    Contract Type
                  </span>
                  <span className="text-sm font-semibold text-slate-200 capitalize">
                    {filter.project_type === 'any' ? 'All Types' : `${filter.project_type} Price`}
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-[#090d16] border border-slate-800">
                  <span className="text-[11px] font-medium text-slate-400 block mb-1">
                    Min. Fixed Budget
                  </span>
                  <span className="text-sm font-semibold text-slate-200">
                    {filter.min_budget ? `$${filter.min_budget}` : 'No minimum'}
                  </span>
                </div>

                <div className="p-3.5 rounded-xl bg-[#090d16] border border-slate-800">
                  <span className="text-[11px] font-medium text-slate-400 block mb-1">
                    Min. Hourly Rate
                  </span>
                  <span className="text-sm font-semibold text-slate-200">
                    {filter.min_hourly_rate ? `$${filter.min_hourly_rate}/hr` : 'No minimum'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
