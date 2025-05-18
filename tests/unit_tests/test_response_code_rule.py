import pytest
from src.scoring.response_code_rule import ResponseCodesRule


@pytest.fixture
def rule():
    return ResponseCodesRule()


def make_spec_all_fail():
    return {"paths": {"/users": {"get": {}}}}


def make_spec_all_pass():
    return {
        "paths": {
            "/users": {"get": {"responses": {"200": {}, "400": {}}}},
            "/users/{id}": {"put": {"responses": {"204": {}, "404": {}}}},
        }
    }


def make_spec_partial():
    return {
        "paths": {
            "/users": {"post": {"responses": {"201": {}}}},
            "/users/{id}": {"delete": {"responses": {"500": {}, "abc": {}}}},
            "/products": {"get": {"responses": {"200": {}, "404": {}}}},
        }
    }


def test_apply_zero_score(rule):
    spec = make_spec_all_fail()
    score, issues = rule.apply(spec)
    assert score == 0
    assert len(issues) == 1
    assert issues[0]["location"] == "paths./users.get.responses"
    assert "missing" in issues[0]["description"].lower()


def test_apply_full_score(rule):
    spec = make_spec_all_pass()
    score, issues = rule.apply(spec)
    assert score == 100
    assert issues == []


def test_apply_partial_score(rule):
    spec = make_spec_partial()
    score, issues = rule.apply(spec)
    assert score != 0 and score != 100
    locations = {issue["location"] for issue in issues}
    assert "paths./users.post.responses" in locations
    assert "paths./users/{id}.delete.responses" in locations
    descriptions = [issue["description"] for issue in issues]
    assert any("invalid http response code" in desc.lower() for desc in descriptions)
