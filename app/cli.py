import click
from pathlib import Path

from app.core.parser import parse_gpt_file, parse_gpt_directory
from app.core.converter import convert_gpt
from app.core.targets import ALL_TARGET_NAMES
from app.audit.logger import log_migration


@click.group()
def cli():
    """JSON Wandler - Migriere ChatGPT Custom GPTs zu anderen Plattformen."""
    pass


@cli.command()
def targets():
    """Zeige alle verfügbaren Zielplattformen."""
    click.echo("Verfügbare Ziele:")
    for name in ALL_TARGET_NAMES:
        click.echo(f"  - {name}")
    click.echo(f"  - all (alle auf einmal)")


@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.option(
    "--target", "-t",
    multiple=True,
    default=["all"],
    help="Zielplattform(en): claude, gemini, grok, perplexity, all",
)
@click.option(
    "--mode", "-m",
    type=click.Choice(["quick", "optimized"]),
    default="quick",
    help="Modus: quick (1:1) oder optimized (KI-optimiert)",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="output",
    help="Ausgabeverzeichnis",
)
@click.option(
    "--provider", "-p",
    type=click.Choice(["anthropic", "openai"]),
    default="anthropic",
    help="LLM-Provider für optimierten Modus",
)
def migrate(source: str, target: tuple[str], mode: str, output: str, provider: str):
    """Migriere eine GPT-JSON oder einen ganzen Ordner."""
    source_path = Path(source)
    output_dir = Path(output)
    output_dir.mkdir(parents=True, exist_ok=True)

    target_list = list(target)

    # Einzelne Datei oder Ordner?
    if source_path.is_file():
        gpts = []
        gpt = parse_gpt_file(source_path)
        if gpt:
            gpts.append(gpt)
        else:
            click.echo(f"Fehler: Konnte {source_path.name} nicht parsen.", err=True)
            return
    elif source_path.is_dir():
        gpts = parse_gpt_directory(source_path)
        if not gpts:
            click.echo(f"Keine gültigen GPT-JSONs in {source_path} gefunden.", err=True)
            return
        click.echo(f"{len(gpts)} GPT(s) gefunden.")
    else:
        click.echo(f"Fehler: {source} ist weder Datei noch Ordner.", err=True)
        return

    # Migration durchführen
    total_success = 0
    total_error = 0

    for gpt in gpts:
        click.echo(f"\nMigriere: {gpt.name}")
        results = convert_gpt(gpt, target_list, mode, output_dir)

        for r in results:
            # Loggen
            log_migration(
                source_name=r.source_name,
                target=r.target,
                mode=r.mode,
                status=r.status,
                output_path=r.output_path,
                error_message=r.error_message,
                tokens_input=r.tokens_input,
                tokens_output=r.tokens_output,
                duration_ms=r.duration_ms,
                original_prompt=gpt.system_prompt[:500],
            )

            if r.status == "success":
                total_success += 1
                click.echo(f"  {r.target}: {r.output_path}")
            else:
                total_error += 1
                click.echo(f"  {r.target}: FEHLER - {r.error_message}", err=True)

    click.echo(f"\nFertig! {total_success} erfolgreich, {total_error} Fehler.")


if __name__ == "__main__":
    cli()
