import { useEffect, useState } from 'react'
import { api, errorMessage } from '../lib/api'

const FLAG_BADGE = {
  'HIGH PRIORITY': 'bg-rose-100 text-rose-700',
  REVIEW: 'bg-amber-100 text-amber-700',
  LOW: 'bg-emerald-100 text-emerald-700',
}

export default function History() {
  const [records, setRecords] = useState(null)
  const [error, setError] = useState('')
  const [downloadingId, setDownloadingId] = useState(null)

  useEffect(() => {
    api.get('/history')
      .then((res) => setRecords(res.data))
      .catch((err) => setError(errorMessage(err, 'Could not load history')))
  }, [])

  const downloadReport = async (id) => {
    setDownloadingId(id)
    try {
      const res = await api.get(`/report/${id}`, { responseType: 'blob' })
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = url
      link.download = `MedAssist_Report_${id}.pdf`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError(errorMessage(err, 'Could not download report'))
    } finally {
      setDownloadingId(null)
    }
  }

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Assessment History</h1>
        <p className="mt-1 text-sm text-slate-500">Your past symptom assessments, most recent first.</p>
      </header>

      {error && <div className="mb-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}

      {records === null && !error && <p className="text-sm text-slate-400">Loading…</p>}

      {records && records.length === 0 && (
        <div className="card p-8 text-center text-sm text-slate-400">
          No assessments yet. Run one from the Symptom Checker page.
        </div>
      )}

      <div className="space-y-3">
        {records && [...records].reverse().map((r) => (
          <details key={r.id} className="card group p-5">
            <summary className="flex cursor-pointer list-none items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`badge ${FLAG_BADGE[r.risk_flag] || 'bg-slate-100 text-slate-700'}`}>{r.risk_flag}</span>
                <span className="text-sm font-medium text-slate-800">Assessment #{r.id}</span>
                <span className="text-xs text-slate-400">{new Date(r.created_at).toLocaleString()}</span>
              </div>
              <span className="text-slate-400 transition group-open:rotate-180">⌄</span>
            </summary>

            <div className="mt-4 grid gap-4 border-t border-slate-100 pt-4 sm:grid-cols-2">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Reported symptoms</p>
                <p className="mt-1 text-sm text-slate-700">
                  {r.result.symptom_analysis.reported_symptoms.join(', ') || 'None'}
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Top possible conditions</p>
                <ul className="mt-1 space-y-1 text-sm capitalize text-slate-700">
                  {r.result.disease_prediction.top_possible_diseases.map((d) => (
                    <li key={d.disease_canonical}>
                      {d.disease_canonical} <span className="text-slate-400">(confidence: {d.confidence_pct}%)</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="sm:col-span-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Recommendation</p>
                <p className="mt-1 text-sm text-slate-700">{r.result.recommendations.suggested_cures || 'No specific recommendation on file.'}</p>
              </div>
              {r.result.lifestyle_risk_screening && (
                <div className="sm:col-span-2">
                  <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Chronic condition risk screening</p>
                  <div className="mt-1 flex flex-wrap gap-2">
                    {r.result.lifestyle_risk_screening.map((c) => (
                      <span
                        key={c.condition}
                        className={`badge ${c.flagged_at_risk ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'}`}
                      >
                        {c.label}: {(c.risk_probability * 100).toFixed(0)}%
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <button
              onClick={() => downloadReport(r.id)}
              disabled={downloadingId === r.id}
              className="btn-secondary mt-4"
            >
              {downloadingId === r.id ? 'Preparing…' : '📄 Download PDF Report'}
            </button>
          </details>
        ))}
      </div>
    </div>
  )
}
