from typing import Dict, Any, Tuple, List
from src.scoring.rules_base import Rule
import re


class ResponseCodesRule(Rule):
    name = "Response Codes"
    weight = 15
    HTTP_STATUS_CODE_PATTERN = re.compile(r"^[1-5]\d{2}$")
    SUCCESS_CODES = {str(code) for code in range(200, 300)}
    ERROR_CODES = {str(code) for code in range(400, 600)}

    def apply(self, spec: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
        issues: List[Dict[str, str]] = []
        total_ops = 0
        passed_ops = 0

        paths = spec.get("paths", {})
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            for method, operation in path_item.items():
                if method.lower() not in {
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "head",
                    "options",
                }:
                    continue

                total_ops += 1

                responses = operation.get("responses", {})
                if not responses:
                    issues.append(
                        {
                            "path": path,
                            "operation": method,
                            "location": f"paths.{path}.{method}.responses",
                            "description": "Operation missing 'responses' definition.",
                            "severity": "high",
                            "suggestion": "Add at least one success and one error response.",
                        }
                    )
                    continue

                valid_codes = set()
                has_success = False
                has_error = False
                invalid_codes = []

                for code in responses.keys():
                    if not self.HTTP_STATUS_CODE_PATTERN.match(code):
                        invalid_codes.append(code)
                        continue
                    valid_codes.add(code)
                    if code in self.SUCCESS_CODES:
                        has_success = True
                    if code in self.ERROR_CODES:
                        has_error = True

                if invalid_codes:
                    issues.append(
                        {
                            "path": path,
                            "operation": method,
                            "location": f"paths.{path}.{method}.responses",
                            "description": f"Invalid HTTP response code(s): {', '.join(invalid_codes)}.",
                            "severity": "medium",
                            "suggestion": "Use standard 3-digit HTTP status codes.",
                        }
                    )

                if not has_success:
                    issues.append(
                        {
                            "path": path,
                            "operation": method,
                            "location": f"paths.{path}.{method}.responses",
                            "description": "No success (2xx) response code defined.",
                            "severity": "high",
                            "suggestion": "Add at least one 2xx status code to indicate success.",
                        }
                    )

                if not has_error:
                    issues.append(
                        {
                            "path": path,
                            "operation": method,
                            "location": f"paths.{path}.{method}.responses",
                            "description": "No error (4xx or 5xx) response code defined.",
                            "severity": "medium",
                            "suggestion": "Add at least one 4xx or 5xx status code to indicate errors.",
                        }
                    )

                if has_success and has_error and not invalid_codes:
                    passed_ops += 1

        score = 0 if total_ops == 0 else round(100 * passed_ops / total_ops)
        return score, issues
