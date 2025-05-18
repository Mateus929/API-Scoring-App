import pytest

from src.scoring.descriptions_documentation_rule import DescriptionsDocumentationRule


@pytest.fixture
def rule():
    return DescriptionsDocumentationRule(min_desc_length=10)


def make_path_with_short_desc():
    return {
        "description": "TODO",
        "get": {"description": "desc", "responses": {"200": {"description": "ok"}}},
    }


def make_path_with_good_desc():
    return {
        "description": "This path handles the test resource properly.",
        "post": {
            "description": "Creates a new test resource with valid data.",
            "responses": {"201": {"description": "Created successfully"}},
        },
    }


def make_spec_all_fail():
    return {"paths": {"/test": make_path_with_short_desc()}}


def make_spec_all_pass():
    return {"paths": {"/test": make_path_with_good_desc()}}


def make_spec_partial():
    return {
        "paths": {
            "/good": make_path_with_good_desc(),
            "/bad": make_path_with_short_desc(),
        }
    }


def test_apply_zero_score(rule):
    spec = make_spec_all_fail()
    score, issues = rule.apply(spec)
    assert score == 0
    assert len(issues) == 2
    for issue in issues:
        assert "Missing" in issue["description"]


def test_apply_full_score(rule):
    spec = make_spec_all_pass()
    score, issues = rule.apply(spec)
    assert score == 100
    assert issues == []


def test_apply_partial_score(rule):
    spec = make_spec_partial()
    score, issues = rule.apply(spec)
    assert score != 0 and score != 100
    assert len(issues) == 2
    paths_with_issues = {issue["path"] for issue in issues}
    assert "/bad" in paths_with_issues
