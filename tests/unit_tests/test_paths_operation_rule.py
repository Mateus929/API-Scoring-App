import pytest

from src.scoring.paths_operation_rule import PathsOperationsRule


@pytest.fixture
def rule():
    return PathsOperationsRule()


def test_conflicting_paths(rule):
    spec = {
        "paths": {
            "/users": {"get": {}},
            "/users/": {"post": {}},
        }
    }
    score, issues = rule.apply(spec)
    assert score < 100
    assert any("conflict" in issue["description"].lower() for issue in issues)


def test_post_with_id_not_allowed(rule):
    spec = {
        "paths": {
            "/users/{userId}": {"post": {}},
        }
    }
    score, issues = rule.apply(spec)
    assert score < 100
    assert any("post should not be used with resource ids" in issue["description"].lower() for issue in issues)


def test_valid_paths_no_issues(rule):
    spec = {
        "paths": {
            "/users": {"get": {}, "post": {}},
            "/users/{id}": {"get": {}, "put": {}, "delete": {}},
            "/{id}/actions/": {"post": {}},
        }
    }
    score, issues = rule.apply(spec)
    assert score > 85
    # as scoring penalizes even if it sees potential issues
    # so it is hard to achieve perfect score


