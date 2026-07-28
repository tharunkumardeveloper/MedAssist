export default function StatCard({ label, value, hint, accent = 'brand' }) {
  const accentClasses = {
    brand: 'text-brand-700 bg-brand-50',
    emerald: 'text-emerald-700 bg-emerald-50',
    amber: 'text-amber-700 bg-amber-50',
    rose: 'text-rose-700 bg-rose-50',
  }
  return (
    <div className="card p-5">
      <p className="text-sm font-medium text-slate-500">{label}</p>
      <p className={`mt-2 inline-block rounded-md px-2 py-1 text-2xl font-semibold ${accentClasses[accent] || accentClasses.brand}`}>
        {value}
      </p>
      {hint && <p className="mt-2 text-xs text-slate-400">{hint}</p>}
    </div>
  )
}
