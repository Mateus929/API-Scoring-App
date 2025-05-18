from __future__ import annotations

from typing import List

from src.scoring.descriptions_documentation_rule import DescriptionsDocumentationRule
from src.scoring.examples_samples_rule import ExamplesSamplesRule
from src.scoring.miscellaneous_rule import MiscellaneousBestPracticesRule
from src.scoring.paths_operation_rule import PathsOperationsRule
from src.scoring.response_code_rule import ResponseCodesRule
from src.scoring.rules_base import Rule
from src.scoring.schema_type_rule import SchemaTypesRule
from src.scoring.security_rule import SecurityRule


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
