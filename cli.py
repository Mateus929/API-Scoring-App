import click
from typing import Optional
from main import main as run_main
from reports.export import export_report

@click.command()
@click.argument('input_path', type=click.Path(exists=False))
@click.option(
    '--export', '-e',
    type=click.Choice(['json', 'markdown', 'html']),
    help="Export report format"
)
@click.option(
    '--output', '-o',
    type=click.Path(),
    help="Output file path for exported report"
)
def cli(input_path: str, export: Optional[str], output: Optional[str]) -> None:
    """
    Score an OpenAPI 3.x specification from INPUT_PATH (file or URL).

    Args:
        input_path (str): Path or URL to the OpenAPI spec file.
        export (Optional[str]): Format to export the report ('json', 'markdown', 'html').
        output (Optional[str]): Output file path to save the exported report.
    """
    try:
        report = run_main(input_path)
        if export:
            if not output:
                ext_map = {'json': 'json', 'markdown': 'md', 'html': 'html'}
                output = f'report.{ext_map[export]}'
            export_report(report, export, output)
            click.echo(f"Report exported to: {output}")
        else:
            click.echo(f"Score: {report.get('score', 'N/A')}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

if __name__ == '__main__':
    cli()
