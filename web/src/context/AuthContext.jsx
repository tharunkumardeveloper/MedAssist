import { createContext, useContext, useEffect, useMemo, useState } from 'react'
import { api, setAuthToken } from '../lib/api'

const AuthContext = createContext(null)

const STORAGE_KEY = 'medassist.auth'

function loadStored() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(loadStored)

  useEffect(() => {
    setAuthToken(auth?.token)
  }, [auth?.token])

  const login = (token, role, email) => {
    const next = { token, role, email }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
    setAuth(next)
  }

  const logout = () => {
    localStorage.removeItem(STORAGE_KEY)
    setAuth(null)
  }

  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      (res) => res,
      (err) => {
        if (err?.response?.status === 401) {
          logout()
        }
        return Promise.reject(err)
      }
    )
    return () => api.interceptors.response.eject(interceptor)
  }, [])

  const value = useMemo(
    () => ({
      token: auth?.token ?? null,
      role: auth?.role ?? null,
      email: auth?.email ?? null,
      isAuthenticated: Boolean(auth?.token),
      login,
      logout,
    }),
    [auth]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
