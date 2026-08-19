from app.services.rbac import allowed_departments, department_filter


def test_general_role_sees_only_general():
    assert allowed_departments("general") == ["general"]


def test_hr_role_sees_hr_and_general():
    assert set(allowed_departments("hr")) == {"hr", "general"}


def test_c_level_sees_every_department():
    assert set(allowed_departments("c-level")) == {"engineering", "finance", "general", "hr", "marketing"}


def test_unknown_role_gets_nothing():
    assert allowed_departments("not-a-real-role") == []


def test_department_filter_matches_allowed_departments_for_role():
    condition = department_filter("marketing").must[0]
    assert condition.key == "metadata.department"
    assert set(condition.match.any) == {"marketing", "general"}
