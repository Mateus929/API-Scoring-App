from typing import Protocol, Any, Dict, List, Tuple

from scoring.rules import SchemaTypesRule, DescriptionsDocumentationRule, PathsOperationsRule, ResponseCodesRule, \
    ExamplesSamplesRule, SecurityRule, MiscBestPracticesRule


class Rule(Protocol):
    """
    Protocol for a scoring rule.
    """
    name: str
    weight: float

    def apply(self, spec: Dict[str, Any]) -> Tuple[float, List[Dict[str, Any]]]:
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


def get_all_rules() -> List[Rule]:
    """
    Return instances of all rules to be applied.
    """
    return [
        SchemaTypesRule(),
        DescriptionsDocumentationRule(),
        PathsOperationsRule(),
        ResponseCodesRule(),
        ExamplesSamplesRule(),
        SecurityRule(),
        MiscBestPracticesRule(),
    ]