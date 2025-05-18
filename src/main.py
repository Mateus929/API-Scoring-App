from typing import Dict, Any

from src.core.scoring_engine import ScoringEngine


def main(input_path: str) -> Dict[str, Any]:
    """
    Main function to produce a report for the given OpenAPI spec.

    Args:
        input_path (str): File path or URL to the OpenAPI spec.

    Returns:
        dict: Report including score, grade, subscores, and issues.
    """
    engine = ScoringEngine(input_path)
    return engine.run()
