ROLE_DEPARTMENT_ACCESS = {
    "hr":          ["hr", "general"],
    "finance":     ["finance", "general"],
    "marketing":   ["marketing", "general"],
    "engineering": ["engineering", "general"],
    "c_level":     ["hr", "finance", "marketing", "engineering", "general"]
}


def get_allowed_departments(role: str) -> list[str]:
    departments = ROLE_DEPARTMENT_ACCESS.get(role)
    if not departments:
        raise ValueError(f"Unknown role: {role}")
    return departments


def is_valid_role(role: str) -> bool:
    return role in ROLE_DEPARTMENT_ACCESS
