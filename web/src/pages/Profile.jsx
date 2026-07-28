import { useEffect, useState } from 'react'
import { api, errorMessage } from '../lib/api'

const EMPTY = { full_name: '', date_of_birth: '', gender: '', allergies: '', medical_history: '' }

export default function Profile() {
  const [form, setForm] = useState(EMPTY)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [saving, setSaving] = useState(false)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    api.get('/profile')
      .then((res) => setForm({ ...EMPTY, ...res.data }))
      .catch((err) => setError(errorMessage(err, 'Could not load profile')))
      .finally(() => setLoaded(true))
  }, [])

  const set = (key) => (e) => setForm((f) => ({ ...f, [key]: e.target.value }))

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess(false)
    setSaving(true)
    try {
      const payload = Object.fromEntries(
        Object.entries(form).map(([k, v]) => [k, v === '' ? null : v])
      )
      const res = await api.put('/profile', payload)
      setForm({ ...EMPTY, ...res.data })
      setSuccess(true)
      setTimeout(() => setSuccess(false), 2500)
    } catch (err) {
      setError(errorMessage(err, 'Could not save profile'))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">My Profile</h1>
        <p className="mt-1 text-sm text-slate-500">
          Keep your medical history up to date for more context in future assessments.
        </p>
      </header>

      {!loaded && <p className="text-sm text-slate-400">Loading…</p>}

      {loaded && (
        <form onSubmit={handleSubmit} className="card max-w-2xl space-y-5 p-6">
          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <label className="label">Full name</label>
              <input className="input" value={form.full_name || ''} onChange={set('full_name')} />
            </div>
            <div>
              <label className="label">Date of birth</label>
              <input type="date" className="input" value={form.date_of_birth || ''} onChange={set('date_of_birth')} />
            </div>
            <div>
              <label className="label">Gender</label>
              <select className="input" value={form.gender || ''} onChange={set('gender')}>
                <option value="">Prefer not to say</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div>
            <label className="label">Known allergies</label>
            <textarea rows={2} className="input" value={form.allergies || ''} onChange={set('allergies')} />
          </div>

          <div>
            <label className="label">Medical history</label>
            <textarea rows={4} className="input" value={form.medical_history || ''} onChange={set('medical_history')} />
          </div>

          {error && <div className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}
          {success && <div className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">Profile saved.</div>}

          <button type="submit" disabled={saving} className="btn-primary">
            {saving ? 'Saving…' : 'Save Profile'}
          </button>
        </form>
      )}
    </div>
  )
}
