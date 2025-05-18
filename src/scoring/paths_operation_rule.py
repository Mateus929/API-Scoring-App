import re
from typing import Dict, Any, Tuple, List, Optional, Set
from src.scoring.rules_base import Rule


class PathsOperationsRule(Rule):
    name = "Paths & Operations"
    weight = 15

    DEFAULT_HTTP_METHODS = {"get", "post", "put", "delete", "patch", "head", "options"}
    DEFAULT_VERBS = {
        "get",
        "create",
        "update",
        "delete",
        "set",
        "fetch",
        "retrieve",
        "post",
    }
    ALLOWED_POST_WITH_ID_PATTERNS = {
        "/{id}/actions/",
        "/{id}/activate",
        "/{id}/deactivate",
    }

    def __init__(
        self,
        http_methods: Optional[Set[str]] = None,
        verbs: Optional[Set[str]] = None,
        allowed_post_with_id_patterns: Optional[Set[str]] = None,
    ):
        self.http_methods = http_methods or self.DEFAULT_HTTP_METHODS
        self.verbs = verbs or self.DEFAULT_VERBS
        self.allowed_post_with_id_patterns = (
            allowed_post_with_id_patterns or self.ALLOWED_POST_WITH_ID_PATTERNS
        )

    @staticmethod
    def normalize_path(path: str) -> str:
        path = path.split("?")[0].lower().rstrip("/")
        return re.sub(r"\{[^}]+}", "{id}", path)

    def contains_verb(self, path: str) -> bool:
        parts = path.strip("/").split("/")
        return any(
            part.lower() in self.verbs for part in parts if not part.startswith("{")
        )

    def is_allowed_post_with_id(self, path: str) -> bool:
        normalized = self.normalize_path(path)
        return any(
            pattern in normalized for pattern in self.allowed_post_with_id_patterns
        )

    def detect_path_conflicts(
        self, path: str, seen_paths: Dict[str, str]
    ) -> Optional[str]:
        normalized = self.normalize_path(path)

        if normalized in seen_paths:
            return seen_paths[normalized]

        for existing_path in seen_paths:
            if existing_path.startswith(normalized + "/") or normalized.startswith(
                existing_path + "/"
            ):
                return seen_paths[existing_path]

        return None

    def validate_http_method_usage(
        self, path: str, method: str
    ) -> Optional[Dict[str, str]]:
        method = method.lower()
        has_id_param = re.search(r"\{[^}]+\}", path)

        if method == "post" and has_id_param and not self.is_allowed_post_with_id(path):
            return {
                "description": "POST should not be used with resource IDs (except for RPC actions).",
                "suggestion": "Use POST on collection resources (e.g., /users) or add to allowed RPC patterns.",
                "severity": "medium",
            }

        if method in {"put", "delete"} and not has_id_param:
            return {
                "description": f"{method.upper()} operations should target specific resources.",
                "suggestion": "Include an ID parameter (e.g., /users/{id}).",
                "severity": "medium",
            }

        return None

    def apply(self, spec: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
        issues: List[Dict[str, str]] = []
        seen_paths: Dict[str, str] = {}
        total_checks = 0
        passed_checks = 0

        for path, path_item in spec.get("paths", {}).items():
            normalized_path = self.normalize_path(path)

            total_checks += 1
            conflict_with = self.detect_path_conflicts(path, seen_paths)
            if conflict_with:
                issues.append(
                    {
                        "path": path,
                        "operation": "N/A",
                        "location": "paths",
                        "description": f"Potential path conflict with '{conflict_with}'.",
                        "severity": "medium",
                        "suggestion": "Ensure paths are distinct or consolidate similar endpoints.",
                    }
                )
            else:
                seen_paths[normalized_path] = path
                passed_checks += 1

            if self.contains_verb(normalized_path):
                issues.append(
                    {
                        "path": path,
                        "operation": "N/A",
                        "location": "paths",
                        "description": "Path contains a verb, which is discouraged in REST APIs.",
                        "severity": "low",
                        "suggestion": "Use nouns for resources (e.g., /users instead of /getUser).",
                    }
                )
            else:
                passed_checks += 1

            if not isinstance(path_item, dict):
                continue

            for method, _ in path_item.items():
                method_lower = method.lower()
                if method_lower not in self.http_methods:
                    continue

                total_checks += 1
                method_issue = self.validate_http_method_usage(path, method_lower)

                if method_issue:
                    issues.append(
                        {
                            "path": path,
                            "operation": method,
                            "location": f"paths.{path}.{method}",
                            **method_issue,
                        }
                    )
                else:
                    passed_checks += 1

        if total_checks == 0:
            issues.append(
                {
                    "path": "paths",
                    "operation": "GLOBAL",
                    "location": "paths",
                    "description": "No valid paths or operations found to evaluate path/method quality.",
                    "severity": "high",
                    "suggestion": "Define at least one path with standard HTTP methods (e.g., GET, POST).",
                }
            )
            score = 0
        else:
            score = round(100 * passed_checks / total_checks)
        return score, issues
