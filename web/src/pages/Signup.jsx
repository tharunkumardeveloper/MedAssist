import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, errorMessage } from '../lib/api'

export default function Signup() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [role, setRole] = useState('patient')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)
  const [loading, setLoading] = useState(false)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await api.post('/signup', { email, password, role })
      setSuccess(true)
      setTimeout(() => navigate('/login'), 1200)
    } catch (err) {
      setError(errorMessage(err, 'Signup failed'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-950 via-brand-800 to-brand-600 px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 text-center text-white">
          <p className="text-4xl">🩺</p>
          <h1 className="mt-2 text-2xl font-semibold">MedAssist AI</h1>
        </div>

        <div className="card p-8">
          <h2 className="text-lg font-semibold text-slate-900">Create your account</h2>
          <p className="mt-1 text-sm text-slate-500">Get started in seconds</p>

          <form onSubmit={handleSubmit} className="mt-6 space-y-4">
            <div>
              <label className="label">Email</label>
              <input
                type="email" required className="input" value={email}
                onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com"
              />
            </div>
            <div>
              <label className="label">Password</label>
              <input
                type="password" required minLength={8} className="input" value={password}
                onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters"
              />
            </div>
            <div>
              <label className="label">I am a</label>
              <div className="grid grid-cols-3 gap-3">
                {['patient', 'nurse', 'provider'].map((r) => (
                  <button
                    type="button" key={r} onClick={() => setRole(r)}
                    className={`rounded-lg border px-3 py-2 text-sm font-medium capitalize transition ${
                      role === r
                        ? 'border-brand-600 bg-brand-50 text-brand-700'
                        : 'border-slate-300 text-slate-600 hover:bg-slate-50'
                    }`}
                  >
                    {r}
                  </button>
                ))}
              </div>
              <p className="mt-1 text-xs text-slate-400">
                Nurses and providers get access to the analytics dashboard and triage queue.
                Clinic admin and admin accounts are provisioned by an existing admin.
              </p>
            </div>

            {error && <div className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}
            {success && (
              <div className="rounded-lg bg-emerald-50 px-3 py-2 text-sm text-emerald-700">
                Account created! Redirecting to login…
              </div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Creating account…' : 'Create account'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-brand-700 hover:underline">Log in</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
