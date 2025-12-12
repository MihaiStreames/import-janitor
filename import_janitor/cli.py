import click
from pathlib import Path
from .analyzer import analyze_file


@click.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--check", is_flag=True, help="Check only, no modifications")
def main(path: str, check: bool):
    """Optimize Python imports."""
    path = Path(path)

    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*.py"))

    for file in files:
        click.echo(f"Analyzing {file}")
        imports = analyze_file(file)
        for imp in imports:
            click.echo(f"  {imp.module} -> {imp.names}")


if __name__ == "__main__":
    main()
