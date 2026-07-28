import { useEffect, useMemo, useState } from 'react'
import { api, errorMessage } from '../lib/api'

const FLAG_BADGE = {
  'HIGH PRIORITY': 'bg-rose-100 text-rose-700',
  REVIEW: 'bg-amber-100 text-amber-700',
}

export default function TriageQueue() {
  const [items, setItems] = useState(null)
  const [error, setError] = useState('')
  const [filter, setFilter] = useState('ALL')

  useEffect(() => {
    api.get('/triage')
      .then((res) => setItems(res.data.items))
      .catch((err) => setError(errorMessage(err, 'Could not load the triage queue')))
  }, [])

  const filtered = useMemo(() => {
    if (!items) return []
    if (filter === 'ALL') return items
    return items.filter((i) => i.risk_flag === filter)
  }, [items, filter])

  return (
    <div>
      <header className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-slate-900">Triage Queue</h1>
          <p className="mt-1 text-sm text-slate-500">
            Patients flagged for follow-up, most recent first — emergency case identification at a glance.
          </p>
        </div>
        <div className="flex gap-2">
          {['ALL', 'HIGH PRIORITY', 'REVIEW'].map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-lg border px-3 py-1.5 text-sm font-medium transition ${
                filter === f ? 'border-brand-600 bg-brand-50 text-brand-700' : 'border-slate-300 text-slate-600 hover:bg-slate-50'
              }`}
            >
              {f === 'ALL' ? 'All' : f}
            </button>
          ))}
        </div>
      </header>

      {error && <div className="mb-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}

      {items === null && !error && <p className="text-sm text-slate-400">Loading…</p>}

      {items && filtered.length === 0 && (
        <div className="card p-8 text-center text-sm text-slate-400">
          No flagged assessments right now — the queue is clear.
        </div>
      )}

      <div className="card overflow-x-auto">
        {items && filtered.length > 0 && (
          <table className="w-full text-left text-sm">
            <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Patient</th>
                <th className="px-4 py-3">Flag</th>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Likely Condition</th>
                <th className="px-4 py-3">Symptoms</th>
                <th className="px-4 py-3">When</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((item) => (
                <tr key={item.id} className="border-b border-slate-100 last:border-0">
                  <td className="px-4 py-3 font-medium text-slate-800">{item.patient_email}</td>
                  <td className="px-4 py-3">
                    <span className={`badge ${FLAG_BADGE[item.risk_flag] || 'bg-slate-100 text-slate-700'}`}>{item.risk_flag}</span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{(item.priority_score * 100).toFixed(0)}%</td>
                  <td className="px-4 py-3 text-slate-700">{item.top_disease || '—'}</td>
                  <td className="px-4 py-3 text-slate-500">{item.reported_symptoms.join(', ') || 'None'}</td>
                  <td className="px-4 py-3 text-slate-400">{new Date(item.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
