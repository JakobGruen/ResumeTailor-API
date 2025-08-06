import os
import json
from pathlib import Path
from rich import print
import typer

from resumetailor.models import Resume
from resumetailor.services.utils import str_to_model, model_to_str


def convert_resume(input_file: Path, output_file: Path):
    """Convert resume from YAML to JSON format."""

    # Check if input file exists
    if not input_file.exists():
        typer.echo(f"Error: Input file '{input_file}' does not exist", err=True)
        raise typer.Exit(1)

    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Read and convert the resume
        with open(input_file, "r", encoding="utf-8") as f:
            resume_str = f.read()
        resume = str_to_model(resume_str, Resume, format="yaml")

        # Write to output file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(resume.model_dump(), f, indent=2)

        print(
            f"[green]Successfully converted '{input_file}' to '{output_file}'[/green]"
        )

    except Exception as e:
        typer.echo(f"Error converting file: {e}", err=True)
        raise typer.Exit(1)


app = typer.Typer(help="Convert resume from YAML to JSON format")


@app.command()
def main(
    input_file: Path = typer.Argument(..., help="Input YAML file path"),
    output_file: Path = typer.Argument(..., help="Output JSON file path"),
):
    convert_resume(input_file, output_file)


if __name__ == "__main__":
    app()
