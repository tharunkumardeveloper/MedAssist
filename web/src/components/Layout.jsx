import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const ORG_ADMIN_NAV = [
  { to: '/analytics', label: 'Analytics', icon: '📊' },
  { to: '/triage', label: 'Triage Queue', icon: '🚨' },
  { to: '/users', label: 'User Management', icon: '🗂️' },
]

const NAV_BY_ROLE = {
  patient: [
    { to: '/dashboard', label: 'Dashboard', icon: '🏠' },
    { to: '/checker', label: 'Symptom Checker', icon: '🩺' },
    { to: '/history', label: 'History', icon: '📖' },
    { to: '/profile', label: 'My Profile', icon: '👤' },
  ],
  nurse: [
    { to: '/triage', label: 'Triage Queue', icon: '🚨' },
    { to: '/analytics', label: 'Analytics', icon: '📊' },
  ],
  provider: [
    { to: '/analytics', label: 'Analytics', icon: '📊' },
    { to: '/triage', label: 'Triage Queue', icon: '🚨' },
  ],
  clinic_admin: ORG_ADMIN_NAV,
  hospital_admin: ORG_ADMIN_NAV,
  telemedicine_admin: ORG_ADMIN_NAV,
  org_admin: ORG_ADMIN_NAV,
  admin: ORG_ADMIN_NAV,
}

const ROLE_LABEL = {
  patient: 'Patient',
  nurse: 'Nurse',
  provider: 'Provider',
  clinic_admin: 'Clinic Admin',
  hospital_admin: 'Hospital Admin',
  telemedicine_admin: 'Telemedicine Admin',
  org_admin: 'Org Admin',
  admin: 'Admin',
}

const ROLE_BADGE = {
  patient: 'bg-emerald-100 text-emerald-700',
  nurse: 'bg-teal-100 text-teal-700',
  provider: 'bg-blue-100 text-blue-700',
  clinic_admin: 'bg-indigo-100 text-indigo-700',
  hospital_admin: 'bg-cyan-100 text-cyan-700',
  telemedicine_admin: 'bg-fuchsia-100 text-fuchsia-700',
  org_admin: 'bg-orange-100 text-orange-700',
  admin: 'bg-purple-100 text-purple-700',
}

export default function Layout() {
  const { role, email, logout } = useAuth()
  const navigate = useNavigate()
  const items = NAV_BY_ROLE[role] || []

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex min-h-screen bg-slate-50">
      <aside className="flex w-64 shrink-0 flex-col border-r border-slate-200 bg-white">
        <div className="flex items-center gap-2 border-b border-slate-200 px-6 py-5">
          <span className="text-2xl">🩺</span>
          <div>
            <p className="text-base font-semibold leading-tight text-slate-900">MedAssist AI</p>
            <p className="text-xs text-slate-500">Health intelligence platform</p>
          </div>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
                  isActive
                    ? 'bg-brand-50 text-brand-700'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                }`
              }
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-slate-200 p-4">
          <div className="mb-3 flex items-center gap-2">
            <span className={`badge ${ROLE_BADGE[role] || 'bg-slate-100 text-slate-700'}`}>{ROLE_LABEL[role] || role}</span>
          </div>
          <p className="truncate text-sm text-slate-600" title={email}>{email}</p>
          <button onClick={handleLogout} className="btn-secondary mt-3 w-full">
            Log out
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="mx-auto max-w-6xl px-6 py-8 lg:px-10">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
