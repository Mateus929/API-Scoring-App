from typing import Protocol, Any, Dict, List, Tuple

from src.scoring.descriptions_documentation_rule import DescriptionsDocumentationRule
from src.scoring.examples_samples_rule import ExamplesSamplesRule
from src.scoring.miscellaneous_rule import MiscellaneousBestPracticesRule
from src.scoring.paths_operation_rule import PathsOperationsRule
from src.scoring.response_code_rule import ResponseCodesRule
from src.scoring.schema_type_rule import SchemaTypesRule
from src.scoring.security_rule import SecurityRule


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
        MiscellaneousBestPracticesRule(),
    ]
