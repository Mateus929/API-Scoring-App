from __future__ import annotations

from typing import Dict, Any, Tuple, List
from src.scoring.rules_base import Rule


class MiscellaneousBestPracticesRule(Rule):
    name = "Miscellaneous Best Practices"
    weight = 10

    def apply(self, spec: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
        issues: List[Dict[str, str]] = []
        passed = 0
        total = 4
        version = spec.get("info", {}).get("version")
        # TODO: in future this check may be improved
        if version and isinstance(version, str) and version.strip():
            passed += 1
        else:
            issues.append(
                {
                    "path": "info.version",
                    "operation": "GLOBAL",
                    "location": "info.version",
                    "description": "API version is missing or empty.",
                    "severity": "medium",
                    "suggestion": "Set the version in 'info.version' (e.g., '1.0.0').",
                }
            )
        servers = spec.get("servers", [])
        if isinstance(servers, list) and len(servers) > 0:
            passed += 1
        else:
            issues.append(
                {
                    "path": "servers",
                    "operation": "GLOBAL",
                    "location": "servers",
                    "description": "No servers defined.",
                    "severity": "medium",
                    "suggestion": "Include at least one server in the 'servers' array.",
                }
            )
        tags_used = False
        for path_item in spec.get("paths", {}).values():
            if isinstance(path_item, dict):
                for op in path_item.values():
                    if isinstance(op, dict) and "tags" in op:
                        tags_used = True
                        break
            if tags_used:
                break

        if tags_used:
            passed += 1
        else:
            issues.append(
                {
                    "path": "paths",
                    "operation": "GLOBAL",
                    "location": "paths",
                    "description": "No tags used in operations.",
                    "severity": "low",
                    "suggestion": "Add tags to operations to help group and organize endpoints.",
                }
            )

        components = spec.get("components", {})
        reused = any(
            components.get(key)
            for key in [
                "schemas",
                "responses",
                "parameters",
                "examples",
                "headers",
                "requestBodies",
            ]
        )
        if reused:
            passed += 1
        else:
            issues.append(
                {
                    "path": "components",
                    "operation": "GLOBAL",
                    "location": "components",
                    "description": "No reusable components found.",
                    "severity": "low",
                    "suggestion": "Define common schemas, responses, or parameters under 'components' for reuse.",
                }
            )

        score = round(100 * passed / total) if total > 0 else 100
        return score, issues
