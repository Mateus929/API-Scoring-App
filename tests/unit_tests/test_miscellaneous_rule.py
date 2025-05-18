import pytest

from src.scoring.miscellaneous_rule import MiscellaneousBestPracticesRule


@pytest.fixture
def rule():
    return MiscellaneousBestPracticesRule()


def make_spec_all_fail():
    return {
        "info": {},
        "servers": [],
        "paths": {"/path": {"get": {}}},
        "components": {},
    }


def make_spec_all_pass():
    return {
        "info": {"version": "1.0.0"},
        "servers": [{"url": "https://api.example.com"}],
        "paths": {"/path": {"get": {"tags": ["example"]}}},
        "components": {"schemas": {"MySchema": {"type": "object"}}},
    }


def make_spec_partial():
    return {
        "info": {"version": "  "},
        "servers": [{"url": "https://api.example.com"}],
        "paths": {"/path": {"get": {}}},
        "components": {},
    }


def test_apply_zero_score(rule):
    spec = make_spec_all_fail()
    score, issues = rule.apply(spec)
    assert score == 0
    assert len(issues) == 4
    paths = {issue["path"] for issue in issues}
    assert "info.version" in paths
    assert "servers" in paths
    assert "paths" in paths
    assert "components" in paths


def test_apply_full_score(rule):
    spec = make_spec_all_pass()
    score, issues = rule.apply(spec)
    assert score == 100
    assert issues == []


def test_apply_partial_score(rule):
    spec = make_spec_partial()
    score, issues = rule.apply(spec)
    assert score == 25
    assert len(issues) == 3
    paths = {issue["path"] for issue in issues}
    assert "info.version" in paths
    assert "paths" in paths
    assert "components" in paths
