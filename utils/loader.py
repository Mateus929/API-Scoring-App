import json
import requests
import yaml
from openapi_spec_validator import validate


class SpecLoadError(Exception):
    """Custom error when spec loading fails."""


def load_spec(input_path: str) -> dict:
    """
    Loads and validates an OpenAPI 3.x spec from a local file or URL.

    Args:
        input_path (str): Path to local file or URL.

    Returns:
        dict: Parsed OpenAPI spec.

    Raises:
        SpecLoadError: If the spec is invalid or cannot be loaded.
    """
    spec_content = None
    try:
        if input_path.startswith("http://") or input_path.startswith("https://"):
            response = requests.get(input_path)
            response.raise_for_status()
            spec_content = response.text
        else:
            with open(input_path, "r", encoding="utf-8") as f:
                spec_content = f.read()

        if not spec_content.strip():
            raise SpecLoadError("Spec content is empty.")

        try:
            spec = yaml.safe_load(spec_content)
        except yaml.YAMLError:
            try:
                spec = json.loads(spec_content)
            except json.JSONDecodeError:
                raise SpecLoadError("Invalid YAML/JSON format.")

        if not isinstance(spec, dict):
            raise SpecLoadError("Loaded spec is not a valid object.")

        try:
            validate(spec)
        except Exception as e:
            raise SpecLoadError(f"OpenAPI validation failed: {e}")

        return spec

    except (OSError, requests.RequestException) as e:
        raise SpecLoadError(f"Failed to load spec: {e}")

if __name__ == "__main__":
    test_files = [
        "../valid_openapi.yaml"
    ]

    for path in test_files:
        print(f"\nTesting: {path}")
        try:
            spec = load_spec(path)
            print(f"Success! Loaded spec keys: {list(spec.keys())}")
        except Exception as e:
            print(f"Error: {e}")
