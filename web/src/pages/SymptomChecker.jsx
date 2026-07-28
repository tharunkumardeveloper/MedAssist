import { useEffect, useMemo, useRef, useState } from 'react'
import { api, errorMessage } from '../lib/api'

const FLAG_STYLES = {
  'HIGH PRIORITY': { badge: 'bg-rose-100 text-rose-700', banner: 'bg-rose-50 border-rose-200 text-rose-800', icon: '⚠️' },
  REVIEW: { badge: 'bg-amber-100 text-amber-700', banner: 'bg-amber-50 border-amber-200 text-amber-800', icon: '🟡' },
  LOW: { badge: 'bg-emerald-100 text-emerald-700', banner: 'bg-emerald-50 border-emerald-200 text-emerald-800', icon: '🟢' },
}

const QUICK_SYMPTOMS = [
  'fever', 'cough', 'fatigue', 'difficulty breathing', 'headache', 'nausea',
  'vomiting', 'sore throat', 'chest pain', 'abdominal pain', 'rash', 'dizziness',
]

const EMERGENCY_FLAGS = new Set([
  'chest pain', 'difficulty breathing', 'shortness of breath',
  'sudden weakness', 'slurred speech', 'loss of consciousness',
  'severe bleeding', 'confusion',
])

const STEPS = ['Symptoms', 'Lifestyle Screening', 'Review', 'Results']

export default function SymptomChecker() {
  const [step, setStep] = useState(0)
  const [reference, setReference] = useState(null)
  const [refError, setRefError] = useState('')

  // Step 1 — symptoms + basic vitals
  const [selectedSymptoms, setSelectedSymptoms] = useState([])
  const [query, setQuery] = useState('')
  const [showSuggestions, setShowSuggestions] = useState(false)
  const [age, setAge] = useState(30)
  const [gender, setGender] = useState('male')
  const [bloodPressure, setBloodPressure] = useState('normal')
  const [cholesterolLevel, setCholesterolLevel] = useState('normal')

  // Step 2 — optional lifestyle/chronic-risk screening
  const [includeLifestyle, setIncludeLifestyle] = useState(false)
  const [heightCm, setHeightCm] = useState(170)
  const [weightKg, setWeightKg] = useState(70)
  const [smokerStatus, setSmokerStatus] = useState(4)
  const [exercise, setExercise] = useState(true)
  const [highCholesterol, setHighCholesterol] = useState(false)
  const [highBloodPressure, setHighBloodPressure] = useState(false)
  const [alcoholDays, setAlcoholDays] = useState(0)
  const [selectedConditions, setSelectedConditions] = useState([])

  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const searchRef = useRef(null)

  useEffect(() => {
    api.get('/reference-data')
      .then((res) => setReference(res.data))
      .catch((err) => setRefError(errorMessage(err, 'Could not load symptom reference data')))
  }, [])

  useEffect(() => {
    function onClickOutside(e) {
      if (searchRef.current && !searchRef.current.contains(e.target)) setShowSuggestions(false)
    }
    document.addEventListener('mousedown', onClickOutside)
    return () => document.removeEventListener('mousedown', onClickOutside)
  }, [])

  const bmi = useMemo(() => {
    const m = heightCm / 100
    if (!m) return 0
    return +(weightKg / (m * m)).toFixed(1)
  }, [heightCm, weightKg])

  const suggestions = useMemo(() => {
    if (!reference || !query.trim()) return []
    const q = query.toLowerCase()
    return reference.symptoms
      .filter((s) => s.toLowerCase().includes(q) && !selectedSymptoms.includes(s))
      .slice(0, 8)
  }, [reference, query, selectedSymptoms])

  const emergencyPreview = useMemo(() => {
    const matched = selectedSymptoms.filter((s) => EMERGENCY_FLAGS.has(s.toLowerCase()))
    return { matched, isPossibleEmergency: matched.length >= 2 }
  }, [selectedSymptoms])

  const addSymptom = (s) => {
    if (!s) return
    const normalized = s.trim().toLowerCase()
    if (!normalized || selectedSymptoms.includes(normalized)) return
    setSelectedSymptoms((list) => [...list, normalized])
    setQuery('')
    setShowSuggestions(false)
  }

  const removeSymptom = (s) => setSelectedSymptoms((list) => list.filter((x) => x !== s))

  const toggleCondition = (key) => {
    setSelectedConditions((list) => (list.includes(key) ? list.filter((k) => k !== key) : [...list, key]))
  }

  const canProceedFromSymptoms = selectedSymptoms.length > 0 && age > 0

  const handleSubmit = async () => {
    setError('')
    setLoading(true)
    setResult(null)
    try {
      const payload = {
        symptoms: selectedSymptoms,
        age: Number(age),
        gender,
        blood_pressure: bloodPressure,
        cholesterol_level: cholesterolLevel,
        lifestyle: includeLifestyle ? {
          age: Number(age),
          sex: gender,
          bmi,
          smoker_status: Number(smokerStatus),
          exercise,
          high_cholesterol: highCholesterol,
          high_blood_pressure: highBloodPressure,
          alcohol_days_per_month: Number(alcoholDays),
        } : null,
        risk_conditions: includeLifestyle && selectedConditions.length ? selectedConditions : null,
      }
      const res = await api.post('/assess', payload)
      setResult(res.data)
      setStep(3)
    } catch (err) {
      setError(errorMessage(err, 'Assessment failed'))
    } finally {
      setLoading(false)
    }
  }

  const startOver = () => {
    setResult(null)
    setSelectedSymptoms([])
    setSelectedConditions([])
    setIncludeLifestyle(false)
    setStep(0)
  }

  const flagStyle = result ? FLAG_STYLES[result.risk_assessment.flag] || FLAG_STYLES.LOW : null

  return (
    <div>
      <header className="mb-6">
        <h1 className="text-2xl font-semibold text-slate-900">Symptom Checker</h1>
        <p className="mt-1 text-sm text-slate-500">
          This is a preliminary AI-generated assessment, not a medical diagnosis.
        </p>
      </header>

      <Stepper step={step} />

      {refError && <div className="mb-4 rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{refError}</div>}

      {step === 0 && (
        <div className="card space-y-6 p-6">
          <div ref={searchRef} className="relative">
            <label className="label">Search &amp; add your symptoms</label>
            <input
              className="input"
              placeholder="Start typing e.g. &ldquo;breathing&rdquo;, &ldquo;fever&rdquo;, &ldquo;pain&rdquo;…"
              value={query}
              onChange={(e) => { setQuery(e.target.value); setShowSuggestions(true) }}
              onFocus={() => setShowSuggestions(true)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') { e.preventDefault(); addSymptom(suggestions[0] || query) }
              }}
              disabled={!reference}
            />
            {showSuggestions && suggestions.length > 0 && (
              <ul className="absolute z-10 mt-1 max-h-56 w-full overflow-auto rounded-lg border border-slate-200 bg-white shadow-lg">
                {suggestions.map((s) => (
                  <li key={s}>
                    <button
                      type="button"
                      className="block w-full px-3 py-2 text-left text-sm capitalize hover:bg-brand-50"
                      onClick={() => addSymptom(s)}
                    >
                      {s}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div>
            <p className="label mb-2">Or pick a common symptom</p>
            <div className="flex flex-wrap gap-2">
              {QUICK_SYMPTOMS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => addSymptom(s)}
                  disabled={selectedSymptoms.includes(s)}
                  className="rounded-full border border-slate-300 px-3 py-1 text-xs font-medium capitalize text-slate-600 transition hover:border-brand-500 hover:text-brand-700 disabled:cursor-not-allowed disabled:border-slate-200 disabled:text-slate-300"
                >
                  + {s}
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="label mb-2">Your selected symptoms ({selectedSymptoms.length})</p>
            {selectedSymptoms.length === 0 ? (
              <p className="text-sm text-slate-400">No symptoms added yet — search above or use a quick pick.</p>
            ) : (
              <div className="flex flex-wrap gap-2">
                {selectedSymptoms.map((s) => (
                  <span key={s} className="badge gap-2 bg-brand-50 pr-1.5 text-brand-700">
                    <span className="capitalize">{s}</span>
                    <button
                      type="button"
                      onClick={() => removeSymptom(s)}
                      className="rounded-full px-1.5 leading-none text-brand-500 hover:bg-brand-100 hover:text-brand-800"
                      aria-label={`Remove ${s}`}
                    >
                      ×
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {emergencyPreview.isPossibleEmergency && (
            <div className="rounded-lg border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">
              ⚠️ You&apos;ve reported multiple emergency-pattern symptoms ({emergencyPreview.matched.join(', ')}).
              If this is a medical emergency, call your local emergency number now — don&apos;t wait for this assessment.
            </div>
          )}

          <div className="grid grid-cols-2 gap-4 border-t border-slate-100 pt-5 sm:grid-cols-4">
            <div>
              <label className="label">Age</label>
              <input type="number" min={0} max={120} className="input" value={age} onChange={(e) => setAge(e.target.value)} />
            </div>
            <Select label="Gender" value={gender} onChange={setGender} options={[['male', 'Male'], ['female', 'Female']]} />
            <Select label="Blood Pressure" value={bloodPressure} onChange={setBloodPressure} options={[['normal', 'Normal'], ['low', 'Low'], ['high', 'High']]} />
            <Select label="Cholesterol" value={cholesterolLevel} onChange={setCholesterolLevel} options={[['normal', 'Normal'], ['high', 'High']]} />
          </div>

          <div className="flex justify-end gap-3 border-t border-slate-100 pt-5">
            <button type="button" className="btn-primary" disabled={!canProceedFromSymptoms} onClick={() => setStep(1)}>
              Continue →
            </button>
          </div>
        </div>
      )}

      {step === 1 && (
        <div className="card space-y-6 p-6">
          <div className="flex items-start justify-between gap-4 rounded-lg bg-slate-50 p-4">
            <div>
              <p className="font-medium text-slate-800">Optional: Chronic-condition risk screening</p>
              <p className="mt-1 text-sm text-slate-500">
                Answer a few lifestyle questions to screen for diabetes, heart disease, stroke, and 7 other
                chronic conditions, using a population-scale CDC survey model — independent of the symptom
                check above.
              </p>
            </div>
            <label className="flex shrink-0 items-center gap-2 text-sm font-medium text-slate-700">
              <input type="checkbox" checked={includeLifestyle} onChange={(e) => setIncludeLifestyle(e.target.checked)} />
              Include this
            </label>
          </div>

          {includeLifestyle && (
            <>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
                <div>
                  <label className="label">Height (cm)</label>
                  <input type="number" className="input" value={heightCm} onChange={(e) => setHeightCm(e.target.value)} />
                </div>
                <div>
                  <label className="label">Weight (kg)</label>
                  <input type="number" className="input" value={weightKg} onChange={(e) => setWeightKg(e.target.value)} />
                </div>
                <div>
                  <label className="label">Calculated BMI</label>
                  <div className="input flex items-center bg-slate-50 font-medium text-slate-700">{bmi || '—'}</div>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <Select
                  label="Smoking status"
                  value={smokerStatus}
                  onChange={(v) => setSmokerStatus(v)}
                  options={(reference?.smoker_status_options || []).map((o) => [o.value, o.label])}
                />
                <div>
                  <label className="label">Alcohol — days per month</label>
                  <input type="number" min={0} max={30} className="input" value={alcoholDays} onChange={(e) => setAlcoholDays(e.target.value)} />
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-3">
                <ToggleField label="Exercise in last 30 days?" value={exercise} onChange={setExercise} />
                <ToggleField label="Told you have high cholesterol?" value={highCholesterol} onChange={setHighCholesterol} />
                <ToggleField label="Told you have high blood pressure?" value={highBloodPressure} onChange={setHighBloodPressure} />
              </div>

              <div>
                <p className="label mb-2">Conditions to screen (leave empty to screen all 10)</p>
                <div className="flex flex-wrap gap-2">
                  {(reference?.risk_conditions || []).map((c) => (
                    <button
                      key={c.key}
                      type="button"
                      onClick={() => toggleCondition(c.key)}
                      className={`rounded-full border px-3 py-1 text-xs font-medium transition ${
                        selectedConditions.includes(c.key)
                          ? 'border-brand-600 bg-brand-50 text-brand-700'
                          : 'border-slate-300 text-slate-600 hover:bg-slate-50'
                      }`}
                    >
                      {c.label}
                    </button>
                  ))}
                </div>
              </div>
            </>
          )}

          <div className="flex justify-between border-t border-slate-100 pt-5">
            <button type="button" className="btn-secondary" onClick={() => setStep(0)}>← Back</button>
            <button type="button" className="btn-primary" onClick={() => setStep(2)}>Continue →</button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="card space-y-6 p-6">
          <h3 className="font-semibold text-slate-900">Review your assessment</h3>

          <div className="grid gap-4 sm:grid-cols-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Symptoms</p>
              <p className="mt-1 text-sm capitalize text-slate-700">{selectedSymptoms.join(', ')}</p>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Profile</p>
              <p className="mt-1 text-sm text-slate-700">
                {age} yrs &middot; {gender} &middot; BP {bloodPressure} &middot; Cholesterol {cholesterolLevel}
              </p>
            </div>
            {includeLifestyle && (
              <div className="sm:col-span-2">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">Lifestyle screening</p>
                <p className="mt-1 text-sm text-slate-700">
                  BMI {bmi} &middot; {exercise ? 'exercises regularly' : 'no regular exercise'} &middot;{' '}
                  {alcoholDays} alcohol day(s)/month &middot;{' '}
                  {selectedConditions.length ? `screening: ${selectedConditions.join(', ')}` : 'screening all 10 conditions'}
                </p>
              </div>
            )}
          </div>

          {error && <div className="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</div>}

          <div className="flex justify-between border-t border-slate-100 pt-5">
            <button type="button" className="btn-secondary" onClick={() => setStep(1)}>← Back</button>
            <button type="button" disabled={loading} onClick={handleSubmit} className="btn-primary">
              {loading ? 'Assessing…' : 'Run Assessment'}
            </button>
          </div>
        </div>
      )}

      {step === 3 && result && (
        <ResultsView result={result} flagStyle={flagStyle} onStartOver={startOver} />
      )}
    </div>
  )
}

function Stepper({ step }) {
  return (
    <ol className="mb-6 flex items-center gap-2 text-xs font-medium text-slate-400">
      {STEPS.map((label, i) => (
        <li key={label} className="flex items-center gap-2">
          <span
            className={`flex h-6 w-6 items-center justify-center rounded-full ${
              i === step ? 'bg-brand-600 text-white' : i < step ? 'bg-brand-100 text-brand-700' : 'bg-slate-100 text-slate-400'
            }`}
          >
            {i < step ? '✓' : i + 1}
          </span>
          <span className={i === step ? 'text-slate-700' : ''}>{label}</span>
          {i < STEPS.length - 1 && <span className="mx-1 h-px w-6 bg-slate-200" />}
        </li>
      ))}
    </ol>
  )
}

function Select({ label, value, onChange, options }) {
  return (
    <div>
      <label className="label">{label}</label>
      <select className="input" value={value} onChange={(e) => onChange(e.target.value)}>
        {options.map(([val, text]) => (
          <option key={val} value={val}>{text}</option>
        ))}
      </select>
    </div>
  )
}

function ToggleField({ label, value, onChange }) {
  return (
    <label className="flex items-center justify-between rounded-lg border border-slate-200 px-3 py-2.5 text-sm text-slate-700">
      {label}
      <input type="checkbox" checked={value} onChange={(e) => onChange(e.target.checked)} />
    </label>
  )
}

function ResultsView({ result, flagStyle, onStartOver }) {
  const normalizedPriority = Math.min(result.risk_assessment.priority_score / 3, 1)

  return (
    <div className="space-y-4">
      <div className={`card border p-5 ${flagStyle.banner}`}>
        <div className="flex items-center justify-between">
          <p className="flex items-center gap-2 text-base font-semibold">
            <span>{flagStyle.icon}</span>
            {result.risk_assessment.flag}
          </p>
          <button onClick={onStartOver} className="btn-secondary bg-white/70">Start a new check</button>
        </div>
        <p className="mt-1 text-sm">
          Severity: <b>{result.risk_assessment.severity_level}</b> &middot; Priority: <b>{(normalizedPriority * 100).toFixed(0)}%</b>
          {' '}&middot; Outcome probability: <b>{(result.disease_prediction.outcome_probability_positive * 100).toFixed(1)}%</b>
          {' '}&middot; Confidence: <b>{result.disease_prediction.prediction_confidence}</b>
        </p>
        {result.risk_assessment.emergency_case && (
          <p className="mt-2 rounded-md bg-rose-600/10 px-3 py-2 text-sm font-medium">
            🚨 {result.risk_assessment.emergency_reason} — seek immediate medical attention.
          </p>
        )}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-5">
          <h3 className="font-semibold text-slate-900">Possible Conditions</h3>
          <p className="mt-1 text-xs text-slate-400">
            Ranked by symptom-similarity match against a 155-condition reference table.
          </p>
          <ul className="mt-3 space-y-2">
            {result.disease_prediction.top_possible_diseases.map((d) => (
              <li key={d.disease_canonical} className="rounded-lg bg-slate-50 px-3 py-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium capitalize text-slate-800">{d.disease_canonical}</span>
                  <span className="text-slate-500">{d.confidence_pct}% confidence</span>
                </div>
                <div className="mt-1.5 h-1.5 rounded-full bg-slate-200">
                  <div className="h-1.5 rounded-full bg-brand-500" style={{ width: `${d.confidence_pct}%` }} />
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="card p-5">
          <h3 className="font-semibold text-slate-900">Recommendations</h3>
          <p className="mt-2 text-sm text-slate-600">
            <span className="font-medium text-slate-800">Suggested care: </span>
            {result.recommendations.suggested_cures || 'No specific recommendation available.'}
          </p>
          <p className="mt-1 text-sm text-slate-600">
            <span className="font-medium text-slate-800">See a: </span>
            {result.recommendations.suggested_doctor || 'General physician'}
          </p>

          {result.recommendations.real_world_treatment_examples?.length > 0 && (
            <div className="mt-4 border-t border-slate-100 pt-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                Reference: similar real-world cases
              </p>
              <p className="mt-1 text-xs text-slate-400">
                From de-identified hospital discharge notes (MIMIC-IV) — illustrative only.
              </p>
              <ul className="mt-2 space-y-2">
                {result.recommendations.real_world_treatment_examples.map((ex, i) => (
                  <li key={i} className="rounded-lg border border-slate-100 px-3 py-2 text-xs text-slate-600">
                    <p className="font-medium text-slate-700">{ex.diagnosis_clean}</p>
                    <p className="mt-1 line-clamp-3 text-slate-500">{ex.medications_clean}</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {result.lifestyle_risk_screening && (
        <div className="card p-5">
          <h3 className="font-semibold text-slate-900">Chronic Condition Risk Screening</h3>
          <p className="mt-1 text-xs text-slate-400">
            Based on a population-scale CDC BRFSS survey model — independent of the symptom-based prediction above.
          </p>
          <div className="mt-3 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {result.lifestyle_risk_screening.map((c) => (
              <div
                key={c.condition}
                className={`rounded-lg border p-3 ${c.flagged_at_risk ? 'border-amber-200 bg-amber-50' : 'border-slate-200 bg-slate-50'}`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-slate-800">{c.label}</span>
                  {c.flagged_at_risk && <span className="badge bg-amber-100 text-amber-700">At risk</span>}
                </div>
                <p className="mt-1 text-lg font-semibold text-slate-900">{(c.risk_probability * 100).toFixed(0)}%</p>
                <p className="text-xs text-slate-400">model AUC {c.model_auc}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="card p-5">
        <h3 className="font-semibold text-slate-900">Care Plan</h3>
        <ul className="mt-2 space-y-1.5 text-sm text-slate-600">
          <li><span className="font-medium text-slate-800">Preventive care: </span>{result.care_plan.preventive_care}</li>
          <li><span className="font-medium text-slate-800">Follow-up: </span>{result.care_plan.follow_up_guidance}</li>
          <li><span className="font-medium text-slate-800">Lifestyle advice: </span>{result.care_plan.lifestyle_advice}</li>
        </ul>
      </div>

      <p className="text-xs text-slate-400">{result.disclaimer}</p>
    </div>
  )
}
