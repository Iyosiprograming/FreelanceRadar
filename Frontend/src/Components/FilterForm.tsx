import React, { useState } from 'react'
import type { Filter, CreateFilterInput, UpdateFilterInput } from '../api/filter'

interface FilterFormProps {
  initialData?: Filter | null
  onSave: (data: CreateFilterInput | UpdateFilterInput) => Promise<void>
  onDelete?: () => Promise<void>
  onCancel?: () => void
  isLoading?: boolean
}

// Popular quick-add skill suggestions
const SUGGESTED_SKILLS = ['React', 'TypeScript', 'Python', 'FastAPI', 'Node.js', 'PostgreSQL', 'Tailwind']

export const FilterForm: React.FC<FilterFormProps> = ({
  initialData,
  onSave,
  onDelete,
  onCancel,
  isLoading = false,
}) => {
  // Form fields
  const [name, setName] = useState(initialData?.name || '')
  const [projectType, setProjectType] = useState<'any' | 'fixed' | 'hourly'>(
    initialData?.project_type || 'any'
  )
  const [skills, setSkills] = useState<string[]>(initialData?.skills || [])
  const [minBudget, setMinBudget] = useState<string>(
    initialData?.min_budget ? String(initialData.min_budget) : ''
  )
  const [minHourlyRate, setMinHourlyRate] = useState<string>(
    initialData?.min_hourly_rate ? String(initialData.min_hourly_rate) : ''
  )

  // Input helper for adding new skills
  const [skillInput, setSkillInput] = useState('')
  const [formError, setFormError] = useState<string | null>(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  // Add skill to the list
  const handleAddSkill = (skillToAdd: string) => {
    const trimmed = skillToAdd.trim()
    if (!trimmed) return

    // Prevent duplicates (case-insensitive)
    const exists = skills.some((s) => s.toLowerCase() === trimmed.toLowerCase())
    if (!exists) {
      setSkills([...skills, trimmed])
    }
    setSkillInput('')
  }

  // Remove skill by name
  const handleRemoveSkill = (skillToRemove: string) => {
    setSkills(skills.filter((s) => s !== skillToRemove))
  }

  // Handle Enter key inside the skill input box
  const handleSkillKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      handleAddSkill(skillInput)
    }
  }

  // Form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setFormError(null)

    if (!name.trim()) {
      setFormError('Please provide a name for this radar filter.')
      return
    }

    const payload: CreateFilterInput = {
      name: name.trim(),
      skills,
      project_type: projectType,
      min_budget: minBudget ? parseFloat(minBudget) : null,
      min_hourly_rate: minHourlyRate ? parseFloat(minHourlyRate) : null,
    }

    try {
      setIsSubmitting(true)
      await onSave(payload)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setFormError(err.message)
      } else {
        setFormError('An unexpected error occurred while saving.')
      }
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="bg-[#0e1626] border border-slate-800/80 rounded-2xl p-6 sm:p-8 shadow-xl max-w-2xl w-full text-slate-100">
      {/* Header with status badge */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-5 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-xs font-semibold tracking-wider uppercase text-emerald-400">
              Job Radar Preferences
            </span>
          </div>
          <h3 className="text-xl font-bold text-white tracking-tight">
            {initialData ? 'Configure Your Radar Filter' : 'Create Job Radar Filter'}
          </h3>
        </div>

        {initialData && (
          <span className="text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/30 px-2.5 py-1 rounded-full font-medium">
            Active Filter
          </span>
        )}
      </div>

      {formError && (
        <div className="mb-6 p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm">
          {formError}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Filter Name */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Filter Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Senior Full-Stack & Python Radar"
            className="w-full px-4 py-2.5 rounded-xl bg-[#090d16] border border-slate-700/70 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 text-sm transition"
            required
          />
          <p className="mt-1.5 text-xs text-slate-400">
            A friendly label to identify this search criteria.
          </p>
        </div>

        {/* Project Contract Type Toggle */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Contract Type
          </label>
          <div className="grid grid-cols-3 gap-2 p-1 bg-[#090d16] rounded-xl border border-slate-700/70">
            {(
              [
                { id: 'any', label: 'All Jobs' },
                { id: 'fixed', label: 'Fixed Price' },
                { id: 'hourly', label: 'Hourly Rate' },
              ] as const
            ).map((type) => {
              const active = projectType === type.id
              return (
                <button
                  key={type.id}
                  type="button"
                  onClick={() => setProjectType(type.id)}
                  className={`py-2 text-xs sm:text-sm font-medium rounded-lg transition-all ${
                    active
                      ? 'bg-emerald-500 text-slate-950 font-semibold shadow-sm'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
                  }`}
                >
                  {type.label}
                </button>
              )
            })}
          </div>
        </div>

        {/* Skills Tag Input */}
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-2">
            Target Skills & Keywords
          </label>
          <div className="flex gap-2 mb-3">
            <input
              type="text"
              value={skillInput}
              onChange={(e) => setSkillInput(e.target.value)}
              onKeyDown={handleSkillKeyDown}
              placeholder="Type a skill (e.g. Next.js, Django) and press Enter"
              className="flex-1 px-4 py-2 rounded-xl bg-[#090d16] border border-slate-700/70 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 text-sm transition"
            />
            <button
              type="button"
              onClick={() => handleAddSkill(skillInput)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-sm font-medium rounded-xl transition cursor-pointer"
            >
              Add
            </button>
          </div>

          {/* Active Skills Badges */}
          {skills.length > 0 ? (
            <div className="flex flex-wrap gap-2 mb-3">
              {skills.map((skill) => (
                <span
                  key={skill}
                  className="inline-flex items-center gap-1.5 px-3 py-1 rounded-lg text-xs font-medium bg-emerald-500/15 border border-emerald-500/30 text-emerald-300"
                >
                  {skill}
                  <button
                    type="button"
                    onClick={() => handleRemoveSkill(skill)}
                    className="hover:text-emerald-100 focus:outline-none cursor-pointer"
                    aria-label={`Remove ${skill}`}
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 mb-3 italic">
              No skills added yet. Any project will be considered.
            </p>
          )}

          {/* Quick-add suggestions */}
          <div className="flex items-center flex-wrap gap-1.5 pt-1">
            <span className="text-xs text-slate-400 mr-1">Suggestions:</span>
            {SUGGESTED_SKILLS.filter(
              (s) => !skills.some((added) => added.toLowerCase() === s.toLowerCase())
            )
              .slice(0, 5)
              .map((suggestion) => (
                <button
                  key={suggestion}
                  type="button"
                  onClick={() => handleAddSkill(suggestion)}
                  className="text-xs px-2.5 py-1 rounded-md bg-slate-800/60 hover:bg-slate-800 border border-slate-700/50 text-slate-300 hover:text-emerald-300 transition cursor-pointer"
                >
                  + {suggestion}
                </button>
              ))}
          </div>
        </div>

        {/* Budget & Rate Minimums */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
          {projectType !== 'hourly' && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Min. Fixed Budget ($)
              </label>
              <div className="relative">
                <span className="absolute left-3.5 top-2.5 text-slate-500 text-sm">$</span>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={minBudget}
                  onChange={(e) => setMinBudget(e.target.value)}
                  placeholder="e.g. 500"
                  className="w-full pl-8 pr-4 py-2.5 rounded-xl bg-[#090d16] border border-slate-700/70 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 text-sm transition"
                />
              </div>
            </div>
          )}

          {projectType !== 'fixed' && (
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Min. Hourly Rate ($/hr)
              </label>
              <div className="relative">
                <span className="absolute left-3.5 top-2.5 text-slate-500 text-sm">$</span>
                <input
                  type="number"
                  min="0"
                  step="any"
                  value={minHourlyRate}
                  onChange={(e) => setMinHourlyRate(e.target.value)}
                  placeholder="e.g. 35"
                  className="w-full pl-8 pr-4 py-2.5 rounded-xl bg-[#090d16] border border-slate-700/70 text-slate-100 placeholder-slate-500 focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 text-sm transition"
                />
              </div>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-between gap-4 pt-6 border-t border-slate-800">
          {initialData && onDelete ? (
            <button
              type="button"
              disabled={isSubmitting || isLoading}
              onClick={async () => {
                if (window.confirm('Are you sure you want to delete this filter?')) {
                  setIsSubmitting(true)
                  try {
                    await onDelete()
                  } finally {
                    setIsSubmitting(false)
                  }
                }
              }}
              className="px-4 py-2.5 text-sm font-medium text-rose-400 hover:text-rose-300 hover:bg-rose-500/10 border border-transparent hover:border-rose-500/20 rounded-xl transition cursor-pointer"
            >
              Delete Filter
            </button>
          ) : (
            <div />
          )}

          <div className="flex items-center gap-3">
            {onCancel && (
              <button
                type="button"
                disabled={isSubmitting || isLoading}
                onClick={onCancel}
                className="px-4 py-2.5 text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 rounded-xl transition cursor-pointer"
              >
                Cancel
              </button>
            )}
            <button
              type="submit"
              disabled={isSubmitting || isLoading}
              className="px-6 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold text-sm transition shadow-lg shadow-emerald-500/15 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? 'Saving...' : initialData ? 'Save Changes' : 'Activate Radar Filter'}
            </button>
          </div>
        </div>
      </form>
    </div>
  )
}
