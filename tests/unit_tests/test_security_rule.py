import pytest

from src.scoring.security_rule import SecurityRule


@pytest.fixture
def rule():
    return SecurityRule()


def make_spec_all_fail():
    return {"paths": {"/users": {"get": {}}}, "components": {}}


def make_spec_all_pass():
    return {
        "paths": {"/users": {"get": {"security": [{"ApiKeyAuth": []}]}}},
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"}
            }
        },
    }


def make_spec_partial():
    return {
        "paths": {
            "/users": {"get": {"security": [{"ApiKeyAuth": []}]}},
            "/admin": {"post": {}},
        },
        "components": {
            "securitySchemes": {
                "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"}
            }
        },
    }


def test_apply_zero_score(rule):
    spec = make_spec_all_fail()
    score, issues = rule.apply(spec)
    assert score == 0
    locations = {issue["location"] for issue in issues}
    assert "components.securitySchemes" in locations


def test_apply_full_score(rule):
    spec = make_spec_all_pass()
    score, issues = rule.apply(spec)
    assert score == 100
    assert issues == []


def test_apply_partial_score(rule):
    spec = make_spec_partial()
    score, issues = rule.apply(spec)
    assert score != 100 and score != 0
    assert len(issues) == 1
    issue = issues[0]
    assert issue["location"] == "paths./admin.post.security"
