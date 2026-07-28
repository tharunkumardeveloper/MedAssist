import { useEffect, useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { api, errorMessage } from '../lib/api'

const ORG_ADMIN_ROLES = ['clinic_admin', 'hospital_admin', 'telemedicine_admin', 'org_admin']
const ALL_ROLES = ['patient', 'nurse', 'provider', ...ORG_ADMIN_ROLES, 'admin']
const ORG_ADMIN_MANAGEABLE_ROLES = ['patient', 'nurse', 'provider']

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

export default function AdminUsers() {
  const [users, setUsers] = useState(null)
  const [error, setError] = useState('')
  const [busyId, setBusyId] = useState(null)
  const { email: myEmail, role: myRole } = useAuth()

  const load = () => {
    api.get('/admin/users')
      .then((res) => setUsers(res.data))
      .catch((err) => setError(errorMessage(err, 'Could not load users')))
  }

  useEffect(load, [])

  const updateUser = async (id, payload) => {
    setError('')
    setBusyId(id)
    try {
      await api.patch(`/admin/users/${id}`, payload)
      load()
    } catch (err) {
      setError(errorMessage(err, 'Update failed'))
    } finally {
      setBusyId(null)
    }
  }

  const canManage = (targetRole) => {
    if (myRole === 'admin') return true
    return ORG_ADMIN_MANAGEABLE_ROLES.includes(targetRole)
  }

  const roleOptionsFor = (targetRole) => {
    if (myRole === 'admin') return ALL_ROLES
    // clinic_admin: can only assign the roles it's allowed to manage, and only
    // for users currently in that same manageable set (enforced server-side too).
    return ORG_ADMIN_MANAGEABLE_ROLES.includes(targetRole) ? ORG_ADMIN_MANAGEABLE_ROLES : [targetRole]
  }

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">User Management</h1>
        <p className="mt-1 text-sm text-slate-500">
          Manage roles and access across all MedAssist accounts.
          {ORG_ADMIN_ROLES.includes(myRole) && ' As an organization admin, you can manage patients, nurses, and providers — admin and other organization-admin accounts are read-only to you.'}
        </p>
      </header>

      {error && <div className="mb-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}

      <div className="card overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="border-b border-slate-200 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th className="px-4 py-3">Email</th>
              <th className="px-4 py-3">Role</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Assessments</th>
              <th className="px-4 py-3">Joined</th>
              <th className="px-4 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users === null && !error && (
              <tr><td colSpan={6} className="px-4 py-6 text-center text-slate-400">Loading…</td></tr>
            )}
            {users && users.map((u) => {
              const isSelf = u.email === myEmail
              const isBusy = busyId === u.id
              const locked = isSelf || isBusy || !canManage(u.role)
              return (
                <tr key={u.id} className="border-b border-slate-100 last:border-0">
                  <td className="px-4 py-3 font-medium text-slate-800">
                    {u.email} {isSelf && <span className="text-xs text-slate-400">(you)</span>}
                  </td>
                  <td className="px-4 py-3">
                    <select
                      className={`badge border-0 ${ROLE_BADGE[u.role]}`}
                      value={u.role}
                      disabled={locked}
                      onChange={(e) => updateUser(u.id, { role: e.target.value })}
                    >
                      {roleOptionsFor(u.role).map((r) => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`badge ${u.is_active ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-200 text-slate-600'}`}>
                      {u.is_active ? 'Active' : 'Deactivated'}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-slate-600">{u.assessment_count}</td>
                  <td className="px-4 py-3 text-slate-500">{new Date(u.created_at).toLocaleDateString()}</td>
                  <td className="px-4 py-3 text-right">
                    <button
                      disabled={locked}
                      onClick={() => updateUser(u.id, { is_active: !u.is_active })}
                      className="btn-secondary px-3 py-1 text-xs"
                    >
                      {u.is_active ? 'Deactivate' : 'Activate'}
                    </button>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
