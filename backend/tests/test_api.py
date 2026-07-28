def signup_and_login(client, email="patient@example.com", password="supersecret1", role="patient"):
    resp = client.post("/signup", json={"email": email, "password": password, "role": role})
    assert resp.status_code == 200, resp.text
    resp = client.post("/login", data={"username": email, "password": password})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_reference_data_shape(client):
    resp = client.get("/reference-data")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["symptoms"]) > 100
    assert any(c["key"] == "diabetes" for c in data["risk_conditions"])
    assert len(data["smoker_status_options"]) == 4


def test_assess_with_lifestyle_screening(client):
    token = signup_and_login(client, "patient15@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/assess", json={
        "symptoms": ["fatigue"],
        "age": 45, "gender": "male", "blood_pressure": "high", "cholesterol_level": "high",
        "lifestyle": {
            "age": 45, "sex": "male", "bmi": 31, "smoker_status": 4,
            "exercise": False, "high_cholesterol": True, "high_blood_pressure": True,
            "alcohol_days_per_month": 8,
        },
        "risk_conditions": ["diabetes", "heart_attack"],
    }, headers=headers)
    assert resp.status_code == 200, resp.text
    result = resp.json()
    screening = result["lifestyle_risk_screening"]
    assert screening is not None
    assert {c["condition"] for c in screening} == {"diabetes", "heart_attack"}
    assert all(0 <= c["risk_probability"] <= 1 for c in screening)


def test_signup_rejects_short_password(client):
    resp = client.post("/signup", json={"email": "weak@example.com", "password": "short", "role": "patient"})
    assert resp.status_code == 400


def test_signup_rejects_invalid_role(client):
    resp = client.post("/signup", json={"email": "bad@example.com", "password": "supersecret1", "role": "admin"})
    assert resp.status_code == 400


def test_login_wrong_password(client):
    client.post("/signup", json={"email": "u1@example.com", "password": "supersecret1", "role": "patient"})
    resp = client.post("/login", data={"username": "u1@example.com", "password": "wrongpass"})
    assert resp.status_code == 401


def test_assess_requires_auth(client):
    resp = client.post("/assess", json={
        "symptoms": ["fever", "fatigue"],
        "age": 30, "gender": "male", "blood_pressure": "normal", "cholesterol_level": "normal",
    })
    assert resp.status_code == 401


def test_assess_and_history_flow(client):
    token = signup_and_login(client, "patient2@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post("/assess", json={
        "symptoms": ["fever", "cough", "fatigue", "difficulty breathing"],
        "age": 40, "gender": "female", "blood_pressure": "high", "cholesterol_level": "high",
    }, headers=headers)
    assert resp.status_code == 200, resp.text
    result = resp.json()
    assert "disease_prediction" in result
    assert "risk_assessment" in result
    assert result["disease_prediction"]["prediction_confidence"] in ("Low", "Moderate", "High")

    resp = client.get("/history", headers=headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_analytics_blocked_for_patient(client):
    token = signup_and_login(client, "patient3@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/analytics", headers=headers)
    assert resp.status_code == 403


def test_analytics_allowed_for_provider(client):
    token = signup_and_login(client, "provider1@example.com", role="provider")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/analytics", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total_assessments"] == 0


def test_profile_upsert_and_get(client):
    token = signup_and_login(client, "patient4@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/profile", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["full_name"] is None

    resp = client.put("/profile", json={
        "full_name": "Jane Doe",
        "date_of_birth": "1990-01-01",
        "gender": "Female",
        "allergies": "Penicillin",
        "medical_history": "None",
    }, headers=headers)
    assert resp.status_code == 200
    assert resp.json()["full_name"] == "Jane Doe"

    resp = client.get("/profile", headers=headers)
    assert resp.json()["full_name"] == "Jane Doe"


def admin_token(client):
    resp = client.post("/login", data={"username": "admin@example.com", "password": "adminpass123"})
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_admin_bootstrap_login(client):
    token = admin_token(client)
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/analytics", headers=headers)
    assert resp.status_code == 200


def test_admin_users_forbidden_for_patient(client):
    token = signup_and_login(client, "patient5@example.com")
    resp = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_admin_can_list_and_promote_user(client):
    signup_and_login(client, "patient6@example.com")
    a_token = admin_token(client)
    a_headers = {"Authorization": f"Bearer {a_token}"}

    resp = client.get("/admin/users", headers=a_headers)
    assert resp.status_code == 200
    users = resp.json()
    target = next(u for u in users if u["email"] == "patient6@example.com")
    assert target["role"] == "patient"
    assert target["is_active"] is True

    resp = client.patch(f"/admin/users/{target['id']}", json={"role": "provider"}, headers=a_headers)
    assert resp.status_code == 200
    assert resp.json()["role"] == "provider"


def test_admin_cannot_deactivate_self(client):
    a_token = admin_token(client)
    a_headers = {"Authorization": f"Bearer {a_token}"}
    resp = client.get("/admin/users", headers=a_headers)
    me = next(u for u in resp.json() if u["email"] == "admin@example.com")

    resp = client.patch(f"/admin/users/{me['id']}", json={"is_active": False}, headers=a_headers)
    assert resp.status_code == 400


def test_deactivated_user_cannot_login(client):
    token = signup_and_login(client, "patient7@example.com")
    a_token = admin_token(client)
    a_headers = {"Authorization": f"Bearer {a_token}"}

    resp = client.get("/admin/users", headers=a_headers)
    target = next(u for u in resp.json() if u["email"] == "patient7@example.com")
    resp = client.patch(f"/admin/users/{target['id']}", json={"is_active": False}, headers=a_headers)
    assert resp.status_code == 200

    resp = client.post("/login", data={"username": "patient7@example.com", "password": "supersecret1"})
    assert resp.status_code == 403


def test_analytics_shape_has_new_fields(client):
    token = signup_and_login(client, "patient8@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    client.post("/assess", json={
        "symptoms": ["fever"],
        "age": 22, "gender": "female", "blood_pressure": "normal", "cholesterol_level": "normal",
    }, headers=headers)

    a_token = admin_token(client)
    resp = client.get("/analytics", headers={"Authorization": f"Bearer {a_token}"})
    data = resp.json()
    assert len(data["assessments_per_day"]) == 14
    assert "19-35" in data["age_distribution"]
    assert data["gender_distribution"].get("female", 0) >= 1


def test_signup_allows_nurse_role(client):
    resp = client.post("/signup", json={"email": "nurse1@example.com", "password": "supersecret1", "role": "nurse"})
    assert resp.status_code == 200
    assert resp.json()["role"] == "nurse"


def test_signup_rejects_clinic_admin_role(client):
    resp = client.post("/signup", json={"email": "ca1@example.com", "password": "supersecret1", "role": "clinic_admin"})
    assert resp.status_code == 400


def test_patient_cannot_view_triage(client):
    token = signup_and_login(client, "patient9@example.com")
    resp = client.get("/triage", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_nurse_can_view_analytics_and_triage(client):
    token = signup_and_login(client, "nurse2@example.com", role="nurse")
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/analytics", headers=headers).status_code == 200
    assert client.get("/triage", headers=headers).status_code == 200


def test_triage_lists_high_priority_assessment(client):
    token = signup_and_login(client, "patient10@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/assess", json={
        "symptoms": ["chest pain", "difficulty breathing", "sweating"],
        "age": 50, "gender": "male", "blood_pressure": "high", "cholesterol_level": "high",
    }, headers=headers)
    assert resp.status_code == 200

    a_token = admin_token(client)
    resp = client.get("/triage", headers={"Authorization": f"Bearer {a_token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] >= 1
    assert any(item["patient_email"] == "patient10@example.com" for item in data["items"])


def test_assess_includes_care_plan_and_health_score(client):
    token = signup_and_login(client, "patient11@example.com")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post("/assess", json={
        "symptoms": ["runny nose"],
        "age": 25, "gender": "female", "blood_pressure": "normal", "cholesterol_level": "normal",
    }, headers=headers)
    result = resp.json()
    assert "care_plan" in result
    assert "follow_up_guidance" in result["care_plan"]
    assert 0 <= result["health_score"] <= 100
    assert "severity_level" in result["risk_assessment"]
    assert "emergency_case" in result["risk_assessment"]


def test_me_summary_shape(client):
    token = signup_and_login(client, "patient12@example.com")
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.get("/me/summary", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total_assessments"] == 0

    client.post("/assess", json={
        "symptoms": ["fever"],
        "age": 40, "gender": "male", "blood_pressure": "normal", "cholesterol_level": "normal",
    }, headers=headers)

    resp = client.get("/me/summary", headers=headers)
    data = resp.json()
    assert data["total_assessments"] == 1
    assert data["latest_health_score"] is not None
    assert len(data["recent_assessments"]) == 1


def test_clinic_admin_cannot_manage_admin_accounts(client):
    signup_and_login(client, "patient13@example.com")
    a_token = admin_token(client)
    a_headers = {"Authorization": f"Bearer {a_token}"}

    # Promote patient13 to clinic_admin
    resp = client.get("/admin/users", headers=a_headers)
    target = next(u for u in resp.json() if u["email"] == "patient13@example.com")
    resp = client.patch(f"/admin/users/{target['id']}", json={"role": "clinic_admin"}, headers=a_headers)
    assert resp.status_code == 200

    ca_token_resp = client.post("/login", data={"username": "patient13@example.com", "password": "supersecret1"})
    ca_headers = {"Authorization": f"Bearer {ca_token_resp.json()['access_token']}"}

    # clinic_admin can list users
    resp = client.get("/admin/users", headers=ca_headers)
    assert resp.status_code == 200

    # clinic_admin cannot touch the bootstrap admin account
    admin_user = next(u for u in resp.json() if u["email"] == "admin@example.com")
    resp = client.patch(f"/admin/users/{admin_user['id']}", json={"is_active": False}, headers=ca_headers)
    assert resp.status_code == 403

    # clinic_admin cannot grant admin/clinic_admin roles
    signup_and_login(client, "patient14@example.com")
    resp = client.get("/admin/users", headers=ca_headers)
    other = next(u for u in resp.json() if u["email"] == "patient14@example.com")
    resp = client.patch(f"/admin/users/{other['id']}", json={"role": "admin"}, headers=ca_headers)
    assert resp.status_code == 403

    # but clinic_admin CAN promote a patient to provider
    resp = client.patch(f"/admin/users/{other['id']}", json={"role": "provider"}, headers=ca_headers)
    assert resp.status_code == 200


def test_org_admin_roles_have_scoped_admin_access(client):
    """hospital_admin / telemedicine_admin / org_admin behave like clinic_admin:
    can manage patient/nurse/provider accounts and view analytics/triage, but
    cannot touch admin or other org-admin accounts."""
    a_token = admin_token(client)
    a_headers = {"Authorization": f"Bearer {a_token}"}

    for i, org_role in enumerate(["hospital_admin", "telemedicine_admin", "org_admin"]):
        patient_email = f"orgpatient{i}@example.com"
        signup_and_login(client, patient_email)
        resp = client.get("/admin/users", headers=a_headers)
        target = next(u for u in resp.json() if u["email"] == patient_email)
        resp = client.patch(f"/admin/users/{target['id']}", json={"role": org_role}, headers=a_headers)
        assert resp.status_code == 200, resp.text
        assert resp.json()["role"] == org_role

        login_resp = client.post("/login", data={"username": patient_email, "password": "supersecret1"})
        org_headers = {"Authorization": f"Bearer {login_resp.json()['access_token']}"}

        assert client.get("/analytics", headers=org_headers).status_code == 200
        assert client.get("/triage", headers=org_headers).status_code == 200
        assert client.get("/admin/users", headers=org_headers).status_code == 200

        admin_row = next(u for u in client.get("/admin/users", headers=org_headers).json() if u["email"] == "admin@example.com")
        resp = client.patch(f"/admin/users/{admin_row['id']}", json={"is_active": False}, headers=org_headers)
        assert resp.status_code == 403
