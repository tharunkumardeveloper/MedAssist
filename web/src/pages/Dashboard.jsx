import { useEffect, useState } from 'react'
import {
  Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart,
  ResponsiveContainer, Tooltip, XAxis, YAxis,
} from 'recharts'
import StatCard from '../components/StatCard'
import { api, errorMessage } from '../lib/api'

const RISK_COLORS = {
  'HIGH PRIORITY': '#e11d48',
  REVIEW: '#d97706',
  LOW: '#059669',
}
const BAR_COLOR = '#1d70f0'
const PIE_FALLBACK = ['#1d70f0', '#059669', '#d97706', '#e11d48', '#7c3aed']

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    api.get('/analytics')
      .then((res) => setData(res.data))
      .catch((err) => setError(errorMessage(err, 'Could not load analytics')))
  }, [])

  if (error) return <div className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>
  if (!data) return <p className="text-sm text-slate-400">Loading…</p>

  const riskData = Object.entries(data.risk_flag_distribution).map(([name, value]) => ({ name, value }))
  const diseaseData = data.top_predicted_diseases
  const trendData = data.assessments_per_day.map((d) => ({
    date: d.date.slice(5),
    count: d.count,
  }))
  const genderData = Object.entries(data.gender_distribution).map(([name, value]) => ({ name, value }))
  const ageData = Object.entries(data.age_distribution).map(([name, value]) => ({ name, value }))

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold text-slate-900">Analytics Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">Aggregate insights across all patient assessments.</p>
      </header>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Total Assessments" value={data.total_assessments} accent="brand" />
        <StatCard label="Total Patients" value={data.total_patients} accent="emerald" />
        <StatCard label="High Priority Cases" value={data.risk_flag_distribution['HIGH PRIORITY'] || 0} accent="rose" />
        <StatCard label="Needs Review" value={data.risk_flag_distribution['REVIEW'] || 0} accent="amber" />
      </div>

      {data.total_assessments === 0 ? (
        <div className="card p-8 text-center text-sm text-slate-400">
          No assessments recorded yet — charts will populate as patients use the Symptom Checker.
        </div>
      ) : (
        <>
          <div className="card p-5">
            <h3 className="mb-4 font-semibold text-slate-900">Assessments (last 14 days)</h3>
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <YAxis allowDecimals={false} tick={{ fontSize: 12 }} stroke="#94a3b8" />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke={BAR_COLOR} strokeWidth={2} dot={{ r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="card p-5">
              <h3 className="mb-4 font-semibold text-slate-900">Risk Flag Distribution</h3>
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                    {riskData.map((entry) => (
                      <Cell key={entry.name} fill={RISK_COLORS[entry.name] || '#94a3b8'} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="card p-5">
              <h3 className="mb-4 font-semibold text-slate-900">Top Predicted Diseases</h3>
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={diseaseData} layout="vertical" margin={{ left: 24 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <YAxis type="category" dataKey="disease" width={110} tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <Tooltip />
                  <Bar dataKey="count" fill={BAR_COLOR} radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="card p-5">
              <h3 className="mb-4 font-semibold text-slate-900">Gender Distribution</h3>
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie data={genderData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {genderData.map((entry, i) => (
                      <Cell key={entry.name} fill={PIE_FALLBACK[i % PIE_FALLBACK.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="card p-5">
              <h3 className="mb-4 font-semibold text-slate-900">Age Distribution</h3>
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={ageData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <YAxis allowDecimals={false} tick={{ fontSize: 12 }} stroke="#94a3b8" />
                  <Tooltip />
                  <Bar dataKey="value" fill="#7c3aed" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
