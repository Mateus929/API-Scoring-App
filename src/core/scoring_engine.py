from typing import Any, Dict
from src.utils.loader import load_spec
from src.scoring.rules_base import get_all_rules


class ScoringEngine:
    """
    Encapsulates the scoring logic for OpenAPI specs.
    """

    def __init__(self, input_path: str) -> None:
        self.input_path = input_path
        self.spec = load_spec(input_path)
        self.rules = get_all_rules()

    def run(self) -> Dict[str, Any]:
        """
        Apply all rules and return the scoring report.

        Returns:
            dict: The report including overall score, grade, per-rule scores, and issues.
        """

        if not self.spec:
            return {
                "score": "0",
                "grade": "F",
                "issues": [{"description": "Empty OpenAPI specification provided."}],
            }

        total_score = 0.0
        criteria = []
        issues = []

        for rule in self.rules:
            rule_score, rule_issues = rule.apply(self.spec)
            weighted_score = rule.weight * (rule_score / 100)
            total_score += weighted_score

            criteria.append(
                {
                    "name": rule.name,
                    "score": rule_score,
                    "weight": rule.weight,
                }
            )
            issues.extend(rule_issues)

        rounded_score = round(total_score, 2)

        grade = self._grade_from_score(rounded_score)

        return {
            "score": rounded_score,
            "grade": grade,
            "criteria": criteria,
            "issues": issues,
        }

    @staticmethod
    def _grade_from_score(score: float) -> str:
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        elif score >= 50:
            return "E"
        else:
            return "F"
