import typer
import click
from rich.console import Console, Group, Styled
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from pathlib import Path
import json, yaml
import os

from resumetailor.llm import extractor, resume_writer, cover_letter_writer
from resumetailor.models import Resume

app = typer.Typer()
console = Console()

# TODO: finish/update the cli app


@app.command()
def refine_resume(
    with_job: bool = typer.Option(
        False, "--with-job", help="Refine with job description"
    ),
    cover_letter: bool = typer.Option(
        False, "--cover-letter", help="Generate cover letter (only with --with-job)"
    ),
):
    resume_path = Path("data/full_resume.json")
    if not resume_path.exists():
        console.print(
            f"[bold red]Error:[/bold red] Resume file {resume_path} not found."
        )
        raise typer.Exit(1)
    with open(resume_path, "r") as f:
        resume_data = json.load(f)
    full_resume = Resume(**resume_data)
    # Temporarily remove personal information for processing
    personal_information = full_resume.personal_information
    setattr(full_resume, "personal_information", None)

    if cover_letter and not with_job:
        console.print(
            "[bold red]Error:[/bold red] --cover-letter can only be used with --with-job."
        )
        raise typer.Exit(1)

    if with_job:
        console.print(
            Panel(
                "Paste the job description. When finished, type a line with only END and press Enter.",
                title="Job Description",
            )
        )
        job_desc_lines = []
        while True:
            line = click.prompt("", prompt_suffix="")
            if line.strip() == "END":
                break
            job_desc_lines.append(line)
        job_desc = "\n".join(job_desc_lines)
        console.print("[yellow]Input accepted. Please wait...[/yellow]")
        job_profile = extractor.extract(job_desc, thread_id="cli")
        job_profile_dict = job_profile.model_dump()
        while True:
            console.print(
                Panel(
                    yaml.dump(job_profile_dict, sort_keys=False, allow_unicode=True),
                    title="Extracted Job Profile",
                    subtitle="Confirm or suggest edits (not editable here)",
                    style="green",
                )
            )
            suggestions = Prompt.ask(
                "Enter editing suggestions (or leave blank to confirm)"
            )
            if suggestions.strip():
                console.print("[yellow]Input accepted. Please wait...[/yellow]")
                job_profile = extractor.edit(
                    editing_suggestions=suggestions, thread_id="cli"
                )
                job_profile_dict = job_profile.model_dump()
            else:
                break
        # Resume refinement and confirmation/edit loop
        console.print("[yellow]Input accepted. Please wait...[/yellow]")

        resume = resume_writer.generate(
            thread_id="cli", resume=full_resume, job_profile=job_profile_dict
        )
        resume_dict = resume.model_dump()
        while True:
            # Print each section of the resume separately for better readability
            section_panels = []
            for section, value in resume_dict.items():
                if isinstance(value, list):
                    # For lists, create a sub-panel for each entry
                    sub_panels = []
                    for idx, entry in enumerate(value):
                        entry_yaml = yaml.dump(
                            entry, sort_keys=False, allow_unicode=True
                        )
                        sub_panels.append(Panel(entry_yaml, style="blue"))
                        console.print(entry_yaml)
                    section_panels.append(
                        Panel(
                            Group(*sub_panels),
                            title=f"{section.replace('_', ' ').capitalize()} (json_key: {section})",
                            style="green",
                        )
                    )
                else:
                    section_yaml = yaml.dump(value, sort_keys=False, allow_unicode=True)
                    section_panels.append(
                        Panel(
                            section_yaml,
                            title=f"{section.replace('_', ' ').capitalize()} (json_key: {section})",
                            style="green",
                        )
                    )
            for panel in section_panels:
                console.print(panel)
            confirmation = Confirm.ask("Are you satisfied with the resume?")
            if not confirmation:
                section_key = Prompt.ask(
                    "Which section would you like to edit? (enter the json key)"
                )
                suggestions = Prompt.ask("Enter editing suggestions")
                console.print("[yellow]Input accepted. Please wait...[/yellow]")
                section = resume_writer.edit_section(
                    thread_id="cli",
                    section_key=section_key,
                    editing_suggestions=suggestions,
                )
                setattr(resume, section_key, section)
                resume_dict = resume.model_dump()
            else:
                break
        # Cover letter loop
        if cover_letter:
            console.print("[yellow]Input accepted. Please wait...[/yellow]")
            cover = cover_letter_writer.generate(
                thread_id="cli",
                job_profile=job_profile_dict,
                candidate_resume=resume,
                job_description=job_desc,
            )
            while True:
                console.print(
                    Panel(
                        cover,
                        title="Generated Cover Letter",
                        subtitle="Confirm or suggest edits (not editable here)",
                        style="magenta",
                    )
                )
                suggestions = Prompt.ask(
                    "Enter editing suggestions (or leave blank to confirm)"
                )
                if suggestions.strip():
                    console.print("[yellow]Input accepted. Please wait...[/yellow]")
                    cover = cover_letter_writer.edit(
                        thread_id="cli", editing_suggestions=suggestions
                    )
                else:
                    break
        company = job_profile_dict.get("company", "unknown").replace(" ", "_")
        title = job_profile_dict.get("position", "unknown").replace(" ", "_")
    else:
        job_title = Prompt.ask("Enter job title(s) (optional)")
        focus = Prompt.ask("Enter focus aspect (optional)")
        console.print("[yellow]Input accepted. Please wait...[/yellow]")
        resume = resume_writer.generate(
            thread_id="cli", resume=full_resume, job_title=job_title, focus=focus
        )
        resume_dict = resume.model_dump()
        while True:
            console.print(
                Panel(
                    yaml.dump(resume_dict, sort_keys=False, allow_unicode=True),
                    title="Refined Resume",
                    subtitle="Confirm or suggest edits (not editable here)",
                    style="green",
                )
            )
            confirmed = Confirm.ask(
                "Is the refined resume correct? (suggest edits if not)"
            )
            if confirmed:
                break
            suggestions = Prompt.ask(
                "Enter editing suggestions (or leave blank to confirm)"
            )
            if suggestions.strip():
                console.print("[yellow]Input accepted. Please wait...[/yellow]")
                resume = resume_writer.edit(
                    resume, editing_suggestions=suggestions, thread_id="cli"
                )
                resume_dict = resume.model_dump()
            else:
                break
        company = "nojob"
        title = job_title.replace(" ", "_") if job_title else "general"
        cover = None
    # Set personal information back to resume
    setattr(resume, "personal_information", personal_information)
    resume_dict = resume.model_dump()
    # Save files
    out_dir = Path(f"data/{company}_{title}")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "resume.json", "w") as f:
        json.dump(resume_dict, f, indent=2)
    # Render HTML using Jinja2 template
    from services.jinja_render import render_resume

    html = render_resume(Resume(**resume_dict))
    html_path = out_dir / "resume.html"
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)
    # Generate PDF using Puppeteer
    try:
        from services.puppeteer_pdf import generate_pdf

        pdf_path = out_dir / "resume.pdf"
        generate_pdf(html_path=html_path, pdf_path=pdf_path)
    except Exception as e:
        console.print(f"[yellow]PDF generation failed: {e}[/yellow]")
    if with_job and cover_letter and cover:
        with open(out_dir / "cover_letter.txt", "w") as f:
            f.write(cover)
        # Optionally save cover letter as PDF/HTML if supported
    console.print(f"[bold green]Files saved to {out_dir}[/bold green]")


if __name__ == "__main__":
    app()
