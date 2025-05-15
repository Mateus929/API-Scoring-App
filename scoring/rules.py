from scoring.rules_base import Rule


class SchemaTypesRule(Rule):
    name = "Schema & Types"
    weight = 20


class DescriptionsDocumentationRule(Rule):
    name = "Descriptions & Documentation"
    weight = 20


class PathsOperationsRule(Rule):
    name = "Paths & Operations"
    weight = 15


class ResponseCodesRule(Rule):
    name = "Response Codes"
    weight = 15


class ExamplesSamplesRule(Rule):
    name = "Examples & Samples"
    weight = 10


class SecurityRule(Rule):
    name = "Security"
    weight = 10


class MiscBestPracticesRule(Rule):
    name = "Miscellaneous Best Practices"
    weight = 10
