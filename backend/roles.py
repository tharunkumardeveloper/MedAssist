# Scoped, non-superuser admin roles — one per kind of organization the
# platform serves (spec: "patients, healthcare providers, clinics, hospitals,
# telemedicine platforms, and healthcare organizations"). All four behave
# identically in terms of permissions; they exist as distinct roles so a
# deployment can label its administrators by organization type.
ORG_ADMIN_ROLES = ("clinic_admin", "hospital_admin", "telemedicine_admin", "org_admin")

ALL_ROLES = ("patient", "nurse", "provider", *ORG_ADMIN_ROLES, "admin")

# Roles a user can pick for themselves at signup. Elevated roles are
# provisioned only by an existing admin/org-admin via /admin/users.
SELF_SIGNUP_ROLES = ("patient", "nurse", "provider")

# Roles that can see cross-patient clinical views (analytics, triage queue).
CLINICAL_STAFF_ROLES = ("nurse", "provider", *ORG_ADMIN_ROLES, "admin")

# Roles that can manage other users' accounts.
USER_MANAGER_ROLES = (*ORG_ADMIN_ROLES, "admin")

# Roles an org-admin (a scoped, non-superuser admin) is allowed to touch.
ORG_ADMIN_MANAGEABLE_ROLES = ("patient", "nurse", "provider")


def can_manage_target(actor_role: str, target_role: str, desired_role: str | None = None) -> bool:
    """Whether `actor_role` may modify a user currently holding `target_role`,
    optionally changing their role to `desired_role`.

    admin: unrestricted.
    org-admin (clinic_admin/hospital_admin/telemedicine_admin/org_admin): can
    only touch patient/nurse/provider accounts, and can only assign them to
    patient/nurse/provider — never admin or another org-admin role. This
    keeps organization-level staff from escalating themselves or peers to
    platform-wide control.
    """
    if actor_role == "admin":
        return True
    if actor_role in ORG_ADMIN_ROLES:
        if target_role not in ORG_ADMIN_MANAGEABLE_ROLES:
            return False
        if desired_role is not None and desired_role not in ORG_ADMIN_MANAGEABLE_ROLES:
            return False
        return True
    return False
