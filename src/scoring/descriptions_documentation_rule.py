from __future__ import annotations

from typing import Dict, Any, List, Tuple

from src.scoring.rules_base import Rule


def has_meaningful_description(obj: Dict[str, Any], min_length: int = 10) -> bool:
    desc = obj.get("description")
    if not isinstance(desc, str):
        return False

    clean_desc = desc.strip()
    words = clean_desc.split()

    return (
        len(clean_desc) >= min_length
        and not clean_desc.startswith("TODO")
        and len(set(words)) > 3
        and not all(word == words[0] for word in words)
    )


class DescriptionsDocumentationRule(Rule):
    name = "Descriptions & Documentation"
    weight = 20

    def __init__(self, min_desc_length: int = 10):
        super().__init__()
        self.min_desc_length = min_desc_length

    def _check_path_item(
        self, path: str, path_item: Dict[str, Any], issues: List[Dict[str, str]]
    ) -> Tuple[int, int]:
        total = 0
        valid = 0
        if "description" in path_item:
            total += 1
            if has_meaningful_description(path_item, self.min_desc_length):
                valid += 1
            else:
                issues.append(
                    {
                        "path": path,
                        "operation": "N/A",
                        "location": f"paths.{path}.description",
                        "description": "Missing or insufficient path-level description.",
                        "severity": "low",
                        "suggestion": "Add a helpful description to this path group.",
                    }
                )
        return total, valid

    def _check_operation(
        self, path: str, method: str, op: Dict[str, Any], issues: List[Dict[str, str]]
    ) -> Tuple[int, int]:
        total = 1
        if has_meaningful_description(op, self.min_desc_length):
            valid = 1
        else:
            valid = 0
            issues.append(
                {
                    "path": path,
                    "operation": method,
                    "location": f"paths.{path}.{method}.description",
                    "description": "Missing or unhelpful operation description.",
                    "severity": "high",
                    "suggestion": "Add a meaningful description to this operation.",
                }
            )
        return total, valid

    def apply(self, spec: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
        issues: List[Dict[str, str]] = []
        total = 0
        valid = 0

        for path, path_item in spec.get("paths", {}).items():
            if isinstance(path_item, dict):
                path_total, path_valid = self._check_path_item(path, path_item, issues)
                total += path_total
                valid += path_valid

                for method, op in path_item.items():
                    if method.lower() in {
                        "get",
                        "post",
                        "put",
                        "delete",
                        "patch",
                    } and isinstance(op, dict):
                        op_total, op_valid = self._check_operation(
                            path, method, op, issues
                        )
                        total += op_total
                        valid += op_valid

        if total == 0:
            return 100, []

        score = round(100 * valid / total)
        return score, issues
