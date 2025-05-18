import pytest

from src.scoring.schema_type_rule import SchemaTypesRule


@pytest.fixture
def rule():
    return SchemaTypesRule()


def make_path_response_with_inline_schema():
    return {
        "get": {
            "responses": {
                "200": {
                    "description": "desc",
                    "content": {"application/json": {"schema": {"type": "object"}}},
                }
            }
        }
    }


def make_path_response_with_ref_schema():
    return {
        "get": {
            "responses": {
                "200": {
                    "description": "desc",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/ValidSchema"}
                        }
                    },
                }
            }
        }
    }


def make_components_with_invalid_schema():
    return {"schemas": {"InvalidSchema": {"type": "object"}}}


def make_components_with_valid_schema():
    return {
        "schemas": {
            "ValidSchema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "value": {"type": "integer"},
                },
            }
        }
    }


def make_components_with_mixed_schemas():
    return {
        "schemas": {
            "ValidSchema": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                },
            },
            "InvalidSchema": {"type": "object"},
        }
    }


def make_path_response_with_inline_properties():
    return {
        "get": {
            "responses": {
                "200": {
                    "description": "desc",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {"name": {"type": "string"}},
                            }
                        }
                    },
                }
            }
        }
    }


def test_apply_zero_score(rule):
    spec = {
        "paths": {"/test": make_path_response_with_inline_schema()},
        "components": make_components_with_invalid_schema(),
    }
    score, issues = rule.apply(spec)
    assert score == 0
    assert len(issues) == 2


def test_apply_full_score(rule):
    spec = {
        "paths": {"/test": make_path_response_with_ref_schema()},
        "components": make_components_with_valid_schema(),
    }
    score, issues = rule.apply(spec)
    assert score == 100
    assert len(issues) == 0


def test_apply_partial_score(rule):
    spec = {
        "paths": {"/test": make_path_response_with_inline_properties()},
        "components": make_components_with_mixed_schemas(),
    }
    score, issues = rule.apply(spec)
    assert 0 < score < 100
    assert len(issues) == 1
