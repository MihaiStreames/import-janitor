from __future__ import annotations

from pathlib import Path

from janitor.graph import build_graph
from janitor.graph import find_cycles
from rich.console import Console
import typer


app = typer.Typer(
    name="janitor",
    help="Best-effort Python import fixer",
    no_args_is_help=True,
)
console = Console()
err_console = Console(stderr=True)


@app.command()
def check(
    path: Path = typer.Argument(..., help="Project root to analyze"),
    show_errors: bool = typer.Option(False, "--show-errors", "-e"),
):
    """Report import issues without modifying files"""
    if not path.is_dir():
        err_console.print(f"[red]Not a directory: {path}[/red]")
        raise typer.Exit(1)

    graph, errors = build_graph(path)
    cycles = find_cycles(graph)

    if show_errors and errors:
        for e in errors:
            err_console.print(f"[yellow]Parse error:[/yellow] {e}")

    if not cycles:
        console.print("[green]✓ No import cycles found[/green]")
        raise typer.Exit(0)

    console.print(f"[red]Found {len(cycles)} cycle(s):[/red]\n")
    for cycle in cycles:
        console.print(f"  [bold]{cycle}[/bold]")

    raise typer.Exit(1)


@app.command()
def diff(
    path: Path = typer.Argument(..., help="Project root to analyze"),
):
    """Show what changes would be made without modifying files"""
    # stub: implement after check is solid
    console.print("[dim]diff not yet implemented[/dim]")
    raise typer.Exit(0)


if __name__ == "__main__":
    app()
