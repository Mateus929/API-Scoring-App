from __future__ import annotations

from typing import Dict, Any, Tuple, List
from src.scoring.rules_base import Rule


class ExamplesSamplesRule(Rule):
    name = "Examples & Samples"
    weight = 10
    HTTP_METHODS = {"get", "post", "put", "delete", "patch"}
    REQUIRE_REQUEST_EXAMPLES = {"post", "put", "patch"}

    def _has_examples(self, content_dict: Dict[str, Any]) -> bool:
        return isinstance(content_dict, dict) and (
            "example" in content_dict or "examples" in content_dict
        )

    def apply(self, spec: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
        issues: List[Dict[str, str]] = []
        total_ops = 0
        passed_ops = 0

        paths = spec.get("paths", {})
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            for method, operation in path_item.items():
                method_lower = method.lower()
                if method_lower not in self.HTTP_METHODS:
                    continue

                total_ops += 1
                needs_request_check = (
                    method_lower in self.REQUIRE_REQUEST_EXAMPLES
                )  # New logic
                has_request_example = (
                    not needs_request_check
                )  # Assume true if not needed
                has_response_example = False

                if needs_request_check:
                    request_body = operation.get("requestBody", {})
                    content = request_body.get("content", {})
                    has_request_example = any(
                        self._has_examples(media_obj) for media_obj in content.values()
                    )
                    if (
                        not has_request_example and content
                    ):  # Only report if content exists
                        issues.append(
                            {
                                "path": path,
                                "operation": method.upper(),
                                "location": f"paths.{path}.{method}.requestBody",
                                "description": "Missing request example",
                                "severity": "medium",
                                "suggestion": "Add an 'example' or 'examples' field to requestBody content",
                            }
                        )

                responses = operation.get("responses", {})
                for code, response_obj in responses.items():
                    if not isinstance(response_obj, dict):  # Added safety check
                        continue
                    content = response_obj.get("content", {})
                    if any(
                        self._has_examples(media_obj) for media_obj in content.values()
                    ):
                        has_response_example = True
                        break

                if not has_response_example and responses:
                    issues.append(
                        {
                            "path": path,
                            "operation": method.upper(),
                            "location": f"paths.{path}.{method}.responses",
                            "description": "Missing response example",
                            "severity": "medium",
                            "suggestion": "Add an 'example' or 'examples' field to response content",
                        }
                    )

                if has_request_example and has_response_example:
                    passed_ops += 1

        score = 0 if total_ops == 0 else round(100 * passed_ops / total_ops)
        return score, issues