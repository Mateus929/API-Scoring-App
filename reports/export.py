import json
from typing import Dict
from markdown2 import markdown  # optional: convert markdown to html easily

def export_report(report: Dict, fmt: str, output_path: str) -> None:
    """
    Export the report dictionary to the given format and write to output_path.
    Supported formats: json, markdown, html.
    """
    if fmt == "json":
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
    elif fmt == "markdown":
        md = report_to_markdown(report)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)
    elif fmt == "html":
        md = report_to_markdown(report)
        html = markdown(md)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
    else:
        raise ValueError(f"Unsupported export format: {fmt}")

def report_to_markdown(report: Dict) -> str:
    """
    Convert the report dict to a human-readable Markdown string.
    """
    lines = []
    lines.append(f"# API Scoring Report\n")
    lines.append(f"**Score:** {report.get('score', 'N/A')}  ")
    lines.append(f"**Grade:** {report.get('grade', 'N/A')}\n")

    lines.append("## Criteria Scores")
    criteria = report.get("criteria", {})
    for crit, info in criteria.items():
        lines.append(f"- **{crit}**: {info.get('score', 0)} / {info.get('weight', 0)}")

    lines.append("\n## Issues")
    issues = report.get("issues", [])
    if not issues:
        lines.append("No issues found. Great job!")
    else:
        for i, issue in enumerate(issues, 1):
            lines.append(f"### Issue {i}")
            lines.append(f"- **Path:** {issue.get('path', 'N/A')}")
            lines.append(f"- **Operation:** {issue.get('operation', 'N/A')}")
            lines.append(f"- **Location:** {issue.get('location', 'N/A')}")
            lines.append(f"- **Description:** {issue.get('description', 'N/A')}")
            lines.append(f"- **Severity:** {issue.get('severity', 'N/A')}")
            lines.append(f"- **Suggestion:** {issue.get('suggestion', 'N/A')}\n")

    return "\n".join(lines)
