import os

import streamlit as st
import requests

API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000")
REQUEST_TIMEOUT = 10

st.set_page_config(page_title="MedAssist AI", page_icon="🩺", layout="centered")

# ---- Session state ----
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "email" not in st.session_state:
    st.session_state.email = None


def auth_headers():
    return {"Authorization": f"Bearer {st.session_state.token}"}


def safe_request(method, path, **kwargs):
    """Wrap requests calls so a down/unreachable backend shows a clear message instead of a stack trace."""
    try:
        return requests.request(method, f"{API_URL}{path}", timeout=REQUEST_TIMEOUT, **kwargs)
    except requests.exceptions.ConnectionError:
        st.error(f"Could not reach the MedAssist API at {API_URL}. Is the backend running?")
    except requests.exceptions.Timeout:
        st.error("The request timed out. Please try again.")
    except requests.exceptions.RequestException as e:
        st.error(f"Unexpected error contacting the API: {e}")
    return None


def error_detail(resp, fallback="Something went wrong"):
    try:
        return resp.json().get("detail", fallback)
    except ValueError:
        return fallback


# ---- Sidebar: auth status + nav ----
st.sidebar.title("🩺 MedAssist AI")

if st.session_state.token:
    st.sidebar.success(f"Logged in as {st.session_state.email} ({st.session_state.role})")
    nav_options = ["Symptom Checker", "History", "My Profile"]
    if st.session_state.role == "provider":
        nav_options.append("Analytics Dashboard")
    page = st.sidebar.radio("Navigate", nav_options)
    if st.sidebar.button("Logout"):
        st.session_state.token = None
        st.session_state.role = None
        st.session_state.email = None
        st.rerun()
else:
    page = st.sidebar.radio("Navigate", ["Login", "Signup"])

# ---- Login page ----
if page == "Login":
    st.title("Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        resp = safe_request("post", "/login", data={"username": email, "password": password})
        if resp is None:
            pass
        elif resp.status_code == 200:
            data = resp.json()
            st.session_state.token = data["access_token"]
            st.session_state.role = data["role"]
            st.session_state.email = email
            st.success("Logged in!")
            st.rerun()
        else:
            st.error(error_detail(resp, "Login failed"))

# ---- Signup page ----
elif page == "Signup":
    st.title("Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password", help="At least 8 characters")
    role = st.selectbox("Role", ["patient", "provider"])
    if st.button("Create Account"):
        resp = safe_request("post", "/signup", json={"email": email, "password": password, "role": role})
        if resp is None:
            pass
        elif resp.status_code == 200:
            st.success("Account created! Go to Login.")
        else:
            st.error(error_detail(resp, "Signup failed"))

# ---- Symptom Checker page ----
elif page == "Symptom Checker":
    st.title("Symptom Checker")
    st.caption("This is a preliminary AI-generated assessment, not a medical diagnosis.")

    col1, col2 = st.columns(2)
    with col1:
        fever = st.selectbox("Fever", ["Yes", "No"])
        cough = st.selectbox("Cough", ["Yes", "No"])
        fatigue = st.selectbox("Fatigue", ["Yes", "No"])
        breathing = st.selectbox("Difficulty Breathing", ["Yes", "No"])
    with col2:
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Male", "Female"])
        bp = st.selectbox("Blood Pressure", ["Normal", "Low", "High"])
        chol = st.selectbox("Cholesterol Level", ["Normal", "High"])

    if st.button("Assess Symptoms", type="primary"):
        payload = {
            "Fever": fever, "Cough": cough, "Fatigue": fatigue,
            "Difficulty_Breathing": breathing, "Age": age, "Gender": gender,
            "Blood_Pressure": bp, "Cholesterol_Level": chol
        }
        resp = safe_request("post", "/assess", json=payload, headers=auth_headers())

        if resp is None:
            pass
        elif resp.status_code == 200:
            result = resp.json()

            flag = result["risk_assessment"]["flag"]
            proba = result["disease_prediction"]["outcome_probability_positive"]
            confidence = result["disease_prediction"].get("prediction_confidence", "N/A")

            if flag == "HIGH PRIORITY":
                st.error(f"⚠️ {flag} — probability of positive condition: {proba:.1%} (confidence: {confidence})")
            elif flag == "REVIEW":
                st.warning(f"🟡 {flag} — probability of positive condition: {proba:.1%} (confidence: {confidence})")
            else:
                st.success(f"🟢 {flag} — probability of positive condition: {proba:.1%} (confidence: {confidence})")

            st.subheader("Possible Conditions")
            for d in result["disease_prediction"]["top_possible_diseases"]:
                ratio = d.get("match_ratio")
                ratio_str = f", {ratio:.0%} of your reported symptoms" if ratio is not None else ""
                st.write(f"- **{d['Disease']}** (symptom overlap: {d['match_count']}{ratio_str})")

            st.subheader("Recommendations")
            st.write(f"**Suggested care:** {result['recommendations']['suggested_cures']}")
            st.write(f"**See a:** {result['recommendations']['suggested_doctor']}")

            st.caption(result["disclaimer"])
        elif resp.status_code == 401:
            st.error("Session expired. Please log in again.")
            st.session_state.token = None
        elif resp.status_code == 429:
            st.error("Too many requests. Please wait a moment and try again.")
        else:
            st.error(error_detail(resp, f"Error {resp.status_code}"))

# ---- History page ----
elif page == "History":
    st.title("Assessment History")
    resp = safe_request("get", "/history", headers=auth_headers())

    if resp is not None and resp.status_code == 200:
        records = resp.json()
        if not records:
            st.info("No assessments yet. Run one from the Symptom Checker page.")
        for r in reversed(records):
            with st.expander(f"Assessment #{r['id']} — {r['risk_flag']} — {r['created_at'][:19]}"):
                st.write("**Symptoms:**", r["input"])
                st.write("**Top possible diseases:**")
                for d in r["result"]["disease_prediction"]["top_possible_diseases"]:
                    st.write(f"- {d['Disease']} (match: {d['match_count']})")
                st.write("**Recommendation:**", r["result"]["recommendations"]["suggested_cures"])

                report_resp = safe_request("get", f"/report/{r['id']}", headers=auth_headers())
                if report_resp is not None and report_resp.status_code == 200:
                    st.download_button(
                        "📄 Download PDF Report",
                        data=report_resp.content,
                        file_name=f"MedAssist_Report_{r['id']}.pdf",
                        mime="application/pdf",
                        key=f"pdf_{r['id']}"
                    )
    elif resp is not None:
        st.error("Could not load history.")

# ---- My Profile page ----
elif page == "My Profile":
    st.title("My Profile")
    st.caption("Keep your medical history up to date for more context in future assessments.")

    resp = safe_request("get", "/profile", headers=auth_headers())
    profile = resp.json() if (resp is not None and resp.status_code == 200) else {}

    full_name = st.text_input("Full name", value=profile.get("full_name") or "")
    date_of_birth = st.text_input("Date of birth (YYYY-MM-DD)", value=profile.get("date_of_birth") or "")
    gender = st.selectbox(
        "Gender", ["", "Male", "Female", "Other"],
        index=["", "Male", "Female", "Other"].index(profile.get("gender")) if profile.get("gender") in ["Male", "Female", "Other"] else 0,
    )
    allergies = st.text_area("Known allergies", value=profile.get("allergies") or "")
    medical_history = st.text_area("Medical history", value=profile.get("medical_history") or "")

    if st.button("Save Profile", type="primary"):
        payload = {
            "full_name": full_name or None,
            "date_of_birth": date_of_birth or None,
            "gender": gender or None,
            "allergies": allergies or None,
            "medical_history": medical_history or None,
        }
        put_resp = safe_request("put", "/profile", json=payload, headers=auth_headers())
        if put_resp is not None and put_resp.status_code == 200:
            st.success("Profile saved.")
        elif put_resp is not None:
            st.error(error_detail(put_resp, "Could not save profile"))

# ---- Analytics Dashboard page (providers only) ----
elif page == "Analytics Dashboard":
    st.title("📊 Analytics Dashboard")
    resp = safe_request("get", "/analytics", headers=auth_headers())

    if resp is not None and resp.status_code == 200:
        data = resp.json()

        col1, col2 = st.columns(2)
        col1.metric("Total Assessments", data["total_assessments"])
        col2.metric("Total Patients", data["total_patients"])

        if data["total_assessments"] > 0:
            st.subheader("Risk Flag Distribution")
            st.bar_chart(data["risk_flag_distribution"])

            st.subheader("Top Predicted Diseases")
            disease_df = {d["disease"]: d["count"] for d in data["top_predicted_diseases"]}
            st.bar_chart(disease_df)
        else:
            st.info("No assessments yet.")
    elif resp is not None and resp.status_code == 403:
        st.error("Only providers can view analytics.")
    elif resp is not None:
        st.error("Could not load analytics.")
