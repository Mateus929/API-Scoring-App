from typing import Dict, Any, Tuple, List

from scoring.rules_base import Rule


def is_valid_schema(schema: Dict[str, Any]) -> bool:
    if not isinstance(schema, dict):
        return False

    if "$ref" in schema:
        return True

    schema_type = schema.get("type")
    valid_types = {"string", "number", "integer", "boolean", "array", "object"}

    if not schema_type:
        return False

    if schema_type and schema_type not in valid_types:
        return False

    if schema_type == "object":
        has_props = isinstance(schema.get("properties"), dict)
        has_structural = any(k in schema for k in ("allOf", "anyOf", "oneOf"))
        if has_props or has_structural:
            return True
        ap = schema.get("additionalProperties")
        if ap is False:
            return True
        if isinstance(ap, dict):
            return is_valid_schema(ap)
        return False

    if schema_type == "array":
        items = schema.get("items")
        if isinstance(items, dict):
            return is_valid_schema(items)
        return False

    return True


def collect_schemas(spec: Dict[str, Any]) -> List[Tuple[Dict[str, Any], str]]:
    found = []

    def walk(obj: Any, context: str):
        if isinstance(obj, dict):
            if "schema" in obj:
                found.append((obj["schema"], f"{context}.schema"))
            for k, v in obj.items():
                walk(v, f"{context}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(item, f"{context}[{i}]")

    for name, schema in spec.get("components", {}).get("schemas", {}).items():
        found.append((schema, f"components.schemas.{name}"))

    for path, methods in spec.get("paths", {}).items():
        for method, op in methods.items():
            if not isinstance(op, dict):
                continue
            ctx = f"paths.{path}.{method}"
            walk(op, ctx)
    return found


class SchemaTypesRule(Rule):
    name = "Schema & Types"
    def apply(self, spec: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
        issues: List[Dict[str, str]] = []
        total = 0
        valid = 0
        schemas = collect_schemas(spec)
        for schema, context in schemas:
            total += 1
            if is_valid_schema(schema):
                valid += 1
            else:
                issues.append({"message": "Free-form or undefined schema", "location": context})
        if total > 5:
            score = round(100 * valid / total)
        else:
            score = 20 + round(80 * valid / total) if total else 100
        return score, issues