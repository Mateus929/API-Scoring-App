from __future__ import annotations

from typing import Protocol, Any, Dict, List, Tuple


class Rule(Protocol):
    """
    Protocol for a scoring rule.
    """

    name: str
    weight: float

    def apply(self, spec: Dict[str, Any]) -> Tuple[float, List[Dict[str, str]]]:
        """
        Apply the rule to the OpenAPI spec.

        Args:
            spec (Dict[str, Any]): The parsed OpenAPI spec.

        Returns:
            Tuple[float, List[Dict[str, Any]]]: A tuple containing:
                - score (float): Score from 0 to 100 for this rule.
                - issues (List[Dict]): List of issues found, each as dict with keys:
                  path, operation, location, description, severity, suggestion.
        """
        ...
