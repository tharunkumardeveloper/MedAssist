import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import StatCard from '../components/StatCard'
import { api, errorMessage } from '../lib/api'

const FLAG_BADGE = {
  'HIGH PRIORITY': 'bg-rose-100 text-rose-700',
  REVIEW: 'bg-amber-100 text-amber-700',
  LOW: 'bg-emerald-100 text-emerald-700',
}

function scoreAccent(score) {
  if (score === null || score === undefined) return 'brand'
  if (score >= 70) return 'emerald'
  if (score >= 40) return 'amber'
  return 'rose'
}

export default function PatientDashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/me/summary')
      .then((res) => setData(res.data))
      .catch((err) => setError(errorMessage(err, 'Could not load your dashboard')))
  }, [])

  if (error) return <div className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>
  if (!data) return <p className="text-sm text-slate-400">Loading…</p>

  const trend = data.health_score_trend.map((t) => ({ date: t.date.slice(5), score: t.health_score }))

  return (
    <div className="space-y-6">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">My Health Dashboard</h1>
          <p className="mt-1 text-sm text-slate-500">A quick overview of your recent health assessments.</p>
        </div>
        <Link to="/checker" className="btn-primary">+ New Symptom Check</Link>
      </header>

      {data.total_assessments === 0 ? (
        <div className="card p-10 text-center">
          <p className="text-sm text-slate-500">
            You haven&apos;t run a symptom assessment yet.
          </p>
          <Link to="/checker" className="btn-primary mt-4 inline-flex">Run your first check</Link>
        </div>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-3">
            <StatCard
              label="Latest Health Score"
              value={`${data.latest_health_score}/100`}
              accent={scoreAccent(data.latest_health_score)}
            />
            <StatCard
              label="Latest Risk Flag"
              value={data.latest_risk_flag}
              accent={data.latest_risk_flag === 'HIGH PRIORITY' ? 'rose' : data.latest_risk_flag === 'REVIEW' ? 'amber' : 'emerald'}
            />
            <StatCard label="Total Assessments" value={data.total_assessments} accent="brand" />
          </div>

          {trend.length > 1 && (
            <div className="card p-5">
              <h3 className="mb-4 font-semibold text-slate-900">Health Score Trend</h3>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={trend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <Tooltip />
                  <Line type="monotone" dataKey="score" stroke="#1d70f0" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          )}

          <div className="card p-5">
            <h3 className="mb-4 font-semibold text-slate-900">Recent Assessments</h3>
            <ul className="divide-y divide-slate-100">
              {data.recent_assessments.map((a) => (
                <li key={a.id} className="flex items-center justify-between py-3 text-sm">
                  <div className="flex items-center gap-3">
                    <span className={`badge ${FLAG_BADGE[a.risk_flag] || 'bg-slate-100 text-slate-700'}`}>{a.risk_flag}</span>
                    <span className="text-slate-700">{a.top_disease || 'No condition matched'}</span>
                  </div>
                  <span className="text-xs text-slate-400">{new Date(a.created_at).toLocaleDateString()}</span>
                </li>
              ))}
            </ul>
            <Link to="/history" className="mt-3 inline-block text-sm font-medium text-brand-700 hover:underline">
              View full history →
            </Link>
          </div>
        </>
      )}
    </div>
  )
}
