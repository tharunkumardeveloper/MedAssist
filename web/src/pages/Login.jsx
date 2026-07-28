import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { api, errorMessage } from '../lib/api'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const form = new URLSearchParams()
      form.set('username', email)
      form.set('password', password)
      const res = await api.post('/login', form)
      login(res.data.access_token, res.data.role, email)
      navigate('/')
    } catch (err) {
      setError(errorMessage(err, 'Login failed'))
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
          <p className="text-sm text-brand-100">AI-powered symptom analysis & health insights</p>
        </div>

        <div className="card p-8">
          <h2 className="text-lg font-semibold text-slate-900">Welcome back</h2>
          <p className="mt-1 text-sm text-slate-500">Log in to continue</p>

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
                type="password" required className="input" value={password}
                onChange={(e) => setPassword(e.target.value)} placeholder="••••••••"
              />
            </div>

            {error && (
              <div className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>
            )}

            <button type="submit" disabled={loading} className="btn-primary w-full">
              {loading ? 'Logging in…' : 'Log in'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500">
            Don&apos;t have an account?{' '}
            <Link to="/signup" className="font-medium text-brand-700 hover:underline">Sign up</Link>
          </p>
        </div>

        <p className="mt-6 text-center text-xs text-brand-100">
          Preliminary AI-generated assessments are not a substitute for professional medical advice.
        </p>
      </div>
    </div>
  )
}
