import { Navigate, Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import { useAuth } from './context/AuthContext'
import AdminUsers from './pages/AdminUsers'
import Dashboard from './pages/Dashboard'
import History from './pages/History'
import Login from './pages/Login'
import PatientDashboard from './pages/PatientDashboard'
import Profile from './pages/Profile'
import Signup from './pages/Signup'
import SymptomChecker from './pages/SymptomChecker'
import TriageQueue from './pages/TriageQueue'

const ORG_ADMIN_ROLES = ['clinic_admin', 'hospital_admin', 'telemedicine_admin', 'org_admin']
const CLINICAL_STAFF_ROLES = ['nurse', 'provider', ...ORG_ADMIN_ROLES, 'admin']
const USER_MANAGER_ROLES = [...ORG_ADMIN_ROLES, 'admin']

function RequireAuth({ children }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function RequireRole({ roles, children }) {
  const { role } = useAuth()
  if (!roles.includes(role)) return <Navigate to="/" replace />
  return children
}

function HomeRedirect() {
  const { role } = useAuth()
  if (role === 'patient') return <Navigate to="/dashboard" replace />
  if (CLINICAL_STAFF_ROLES.includes(role)) return <Navigate to="/analytics" replace />
  return <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      <Route
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route path="/" element={<HomeRedirect />} />

        <Route
          path="/dashboard"
          element={
            <RequireRole roles={['patient']}>
              <PatientDashboard />
            </RequireRole>
          }
        />
        <Route
          path="/checker"
          element={
            <RequireRole roles={['patient']}>
              <SymptomChecker />
            </RequireRole>
          }
        />
        <Route
          path="/history"
          element={
            <RequireRole roles={['patient']}>
              <History />
            </RequireRole>
          }
        />
        <Route
          path="/profile"
          element={
            <RequireRole roles={['patient']}>
              <Profile />
            </RequireRole>
          }
        />

        <Route
          path="/analytics"
          element={
            <RequireRole roles={CLINICAL_STAFF_ROLES}>
              <Dashboard />
            </RequireRole>
          }
        />
        <Route
          path="/triage"
          element={
            <RequireRole roles={CLINICAL_STAFF_ROLES}>
              <TriageQueue />
            </RequireRole>
          }
        />
        <Route
          path="/users"
          element={
            <RequireRole roles={USER_MANAGER_ROLES}>
              <AdminUsers />
            </RequireRole>
          }
        />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
