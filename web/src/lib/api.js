import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const api = axios.create({ baseURL: API_URL })

console.info(`[MedAssist] API base URL: ${API_URL}`)

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const { config, response, code, message } = err
    if (response) {
      console.error(
        `[MedAssist] ${config?.method?.toUpperCase()} ${config?.url} -> ${response.status}`,
        response.data
      )
    } else {
      console.error(
        `[MedAssist] ${config?.method?.toUpperCase()} ${config?.url} failed before a response was received ` +
          `(code=${code}, message=${message}). Common causes: backend not running, wrong VITE_API_URL, or a CORS ` +
          `origin mismatch (check the backend's CORS_ORIGINS env var includes ${window.location.origin}).`
      )
    }
    return Promise.reject(err)
  }
)

export function setAuthToken(token) {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`
  } else {
    delete api.defaults.headers.common.Authorization
  }
}

export function errorMessage(err, fallback = 'Something went wrong') {
  if (err?.response?.data?.detail) return err.response.data.detail
  if (err?.code === 'ERR_NETWORK') return `Could not reach the MedAssist API at ${API_URL}. Is the backend running?`
  return err?.message || fallback
}
