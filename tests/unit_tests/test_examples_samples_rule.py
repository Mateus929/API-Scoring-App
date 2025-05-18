import pytest

from src.scoring.examples_samples_rule import ExamplesSamplesRule


@pytest.fixture
def rule():
    return ExamplesSamplesRule()

def make_response_example():
    return {
        "content": {
            "application/json": {
                "example": {"key": "value"}
            }
        }
    }

def make_request_example():
    return {
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {"param": 42}
                }
            }
        },
        "responses": {
            "200": make_response_example()
        }
    }

def make_request_no_example():
    return {
        "requestBody": {
            "content": {
                "application/json": {
                }
            }
        },
        "responses": {
            "200": make_response_example()
        }
    }

def make_response_no_example():
    return {
        "responses": {
            "200": {
                "content": {
                    "application/json": {
                    }
                }
            }
        }
    }

def test_apply_zero_score(rule):
    spec = {
        "paths": {
            "/zero": {
                "post": make_request_no_example(),
                "get": make_response_no_example(),
            }
        }
    }
    score, issues = rule.apply(spec)
    assert score == 0
    assert len(issues) == 2
    assert all(issue["severity"] == "medium" for issue in issues)

def test_apply_full_score(rule):
    spec = {
        "paths": {
            "/full": {
                "post": make_request_example(),
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "example": {"result": "ok"}
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    score, issues = rule.apply(spec)
    assert score == 100
    assert issues == []

def test_apply_partial_score(rule):
    spec = {
        "paths": {
            "/partial": {
                "post": make_request_example(),
                "put": make_request_no_example(),
                "get": make_response_no_example(),
                "delete": {
                    "responses": {
                        "204": {}
                    }
                }
            }
        }
    }
    score, issues = rule.apply(spec)
    assert score != 0 and score != 100
    paths_with_issues = {issue["path"] for issue in issues}
    assert "/partial" in paths_with_issues
    operations_with_issues = {issue["operation"] for issue in issues}
    assert "PUT" in operations_with_issues
    assert "GET" in operations_with_issues
