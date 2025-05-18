from __future__ import annotations

from typing import Dict, Any, Tuple, List

from src.scoring.rules_base import Rule


def is_valid_schema(schema: Dict[str, Any]) -> Tuple[bool, str, str]:
    if not isinstance(schema, dict):
        return (
            False,
            "Schema is not a dictionary.",
            "Ensure the schema is a valid object.",
        )

    if "$ref" in schema:
        return True, "", ""

    schema_type = schema.get("type")
    valid_types = {"string", "number", "integer", "boolean", "array", "object"}

    if not schema_type:
        return (
            False,
            "Missing 'type' in schema.",
            "Add a 'type' field, such as 'object', to the schema.",
        )

    if schema_type not in valid_types:
        return (
            False,
            f"Invalid schema type: {schema_type}.",
            "Use a valid type like 'object', 'array', etc.",
        )

    if schema_type == "object":
        has_props = isinstance(schema.get("properties"), dict)
        has_structural = any(k in schema for k in ("allOf", "anyOf", "oneOf"))
        if has_props or has_structural:
            return True, "", ""
        ap = schema.get("additionalProperties")
        if ap is False:
            return True, "", ""
        if isinstance(ap, dict):
            return is_valid_schema(ap)
        return (
            False,
            "Free-form object without defined structure.",
            "Define 'properties' or use a valid structure.",
        )

    if schema_type == "array":
        items = schema.get("items")
        if not isinstance(items, dict):
            return (
                False,
                "Missing or invalid 'items' in array schema.",
                "Add an 'items' field with a valid schema.",
            )
        return is_valid_schema(items)

    return True, "", ""


def collect_schemas(spec: Dict[str, Any]) -> List[Tuple[Dict[str, Any], str, str, str]]:
    found: List[Tuple[Dict[str, Any], str, str, str]] = []

    def walk(obj: Any, context: str, path: str, operation: str):
        if isinstance(obj, dict):
            if "schema" in obj:
                found.append((obj["schema"], f"{context}.schema", path, operation))
            for k, v in obj.items():
                walk(v, f"{context}.{k}", path, operation)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{context}[{i}]", path, operation)

    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if not isinstance(op, dict):
                continue
            walk(op, f"paths.{path}.{method}", path, method)

    for name, schema in spec.get("components", {}).get("schemas", {}).items():
        found.append((schema, f"components.schemas.{name}", "N/A", "N/A"))

    return found


class SchemaTypesRule(Rule):
    name = "Schema & Types"
    weight = 20

    def apply(self, spec: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
        issues = []
        total = 0
        valid = 0
        schemas = collect_schemas(spec)

        for schema, context, path, method in schemas:
            total += 1
            ok, description, suggestion = is_valid_schema(schema)
            if ok:
                valid += 1
            else:
                issues.append(
                    {
                        "path": path,
                        "operation": method,
                        "location": context,
                        "description": description,
                        "severity": "high",
                        "suggestion": suggestion,
                    }
                )

        score = round(100 * valid / total) if total else 100

        return score, issues
