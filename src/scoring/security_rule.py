from __future__ import annotations

from typing import Dict, Any, Tuple, List, Set
from src.scoring.rules_base import Rule


class SecurityRule(Rule):
    name = "Security"
    weight = 10
    description = "Defined and referenced security schemes where needed"

    def apply(self, spec: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
        issues: List[Dict[str, str]] = []
        total_ops = 0
        secured_ops = 0

        security_schemes = spec.get("components", {}).get("securitySchemes", {})
        defined_schemes: Set[str] = set(security_schemes.keys())

        if not defined_schemes:
            issues.append(
                {
                    "path": "components.securitySchemes",
                    "operation": "GLOBAL",
                    "location": "components.securitySchemes",
                    "description": "No security schemes defined",
                    "severity": "high",
                    "suggestion": "Define security schemes (e.g., API key, OAuth2) under components.securitySchemes",
                }
            )

        paths = spec.get("paths", {})
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            for method, operation in path_item.items():
                method_lower = method.lower()
                if method_lower not in {"get", "post", "put", "delete", "patch"}:
                    continue

                total_ops += 1
                op_security = operation.get("security", spec.get("security", []))

                referenced_schemes: Set[str] = set()
                for sec_req in op_security or []:
                    if isinstance(sec_req, dict):
                        referenced_schemes.update(k for k in sec_req.keys() if k)

                if referenced_schemes & defined_schemes:
                    secured_ops += 1
                elif defined_schemes:
                    issues.append(
                        {
                            "path": path,
                            "operation": method.upper(),
                            "location": f"paths.{path}.{method}.security",
                            "description": "No valid security scheme referenced",
                            "severity": "high",
                            "suggestion": "Reference at least one defined security scheme",
                        }
                    )

        # TODO: this case (no operation case) should be handled in separate class
        # We only handle this case in this class, so in similar classes (etc response
        # code rule) we just return empty list with score = 0
        if total_ops == 0:
            score = 0
            issues.append(
                {
                    "path": "paths",
                    "operation": "GLOBAL",
                    "location": "paths",
                    "description": "No operations defined in the OpenAPI specification to evaluate security",
                    "severity": "high",
                    "suggestion": "Define at least one path and operation (e.g., GET, POST) to apply security rules",
                }
            )
        else:
            score = round(100 * secured_ops / total_ops)

        return score, issues
