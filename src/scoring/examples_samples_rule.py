from typing import Dict, Any, Tuple, List
from src.scoring.rules_base import Rule


class ExamplesSamplesRule(Rule):
    name = "Examples & Samples"
    weight = 10
    HTTP_METHODS = {"get", "post", "put", "delete", "patch"}

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
                has_request_example = False
                has_response_example = False

                request_body = operation.get("requestBody", {})
                content = request_body.get("content", {})
                for media_obj in content.values():
                    if self._has_examples(media_obj):
                        has_request_example = True
                        break

                responses = operation.get("responses", {})
                for response_obj in responses.values():
                    content = response_obj.get("content", {})
                    for media_obj in content.values():
                        if self._has_examples(media_obj):
                            has_response_example = True
                            break
                    if has_response_example:
                        break

                if has_request_example and has_response_example:
                    passed_ops += 1
                else:
                    if not has_request_example and request_body:
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

        score = 0 if total_ops == 0 else round(100 * passed_ops / total_ops)
        return score, issues
