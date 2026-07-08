# Copyright (c) 2024-2026 Antonio Trento — https://antoniotrento.net
# All rights reserved. Use subject to the terms in the LICENSE file.

import logging
import shutil
import tempfile
from enum import Enum
from pathlib import Path

import typer
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table

from qwibo import __version__
from qwibo.config import DEFAULT_MODEL, SummaryLength, TranscribeConfig
from qwibo.export import export_all, export_summary_text
from qwibo.languages import language_label, normalize_language
from qwibo.jobs import (
    STATUS_COMPLETED,
    STATUS_FAILED,
    enqueue_job,
    get_job,
    jobs_root,
    load_index,
    requeue_failed,
)
from qwibo.pipeline import run_pipeline
from qwibo.summarize import summarize
from qwibo.transcribe import transcribe as run_transcribe
from qwibo.transcribe import unload_model
from qwibo.ui.launch import launch_ui
from qwibo.worker import run_worker_forever

app = typer.Typer(
    name="qwibo",
    help="Sbobina audio e video in testo (italiano) con NVIDIA NeMo Parakeet.",
)
console = Console()
jobs_app = typer.Typer(help="Gestione lavori e coda.")
app.add_typer(jobs_app, name="jobs")


class OutputFormat(str, Enum):
    txt = "txt"
    srt = "srt"


def _setup_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(console=console, rich_tracebacks=True, show_path=False)],
    )


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Senza sottocomando avvia l'interfaccia web."""
    if ctx.invoked_subcommand is None:
        console.print("[bold cyan]Avvio interfaccia web...[/bold cyan]")
        console.print("Apri il browser su [link=http://localhost:8501]http://localhost:8501[/link]")
        launch_ui()


@app.command()
def ui(
    port: int = typer.Option(8501, "--port", "-p", help="Porta del server web"),
) -> None:
    """Avvia l'interfaccia web (FastAPI)."""
    console.print(f"[bold cyan]Interfaccia web su http://localhost:{port}[/bold cyan]")
    launch_ui(port=port)


@app.command("docker-ui")
def docker_ui(
    port: int = typer.Option(8501, "--port", "-p", help="Porta del server web"),
) -> None:
    """Avvio container Docker: verifica RAM, scarica Qwen se possibile, poi UI."""
    from qwibo.local_llm_download import ensure_local_summary_llm_auto

    ensure_local_summary_llm_auto()
    console.print(f"[bold cyan]Interfaccia web su http://localhost:{port}[/bold cyan]")
    launch_ui(port=port)


@app.command()
def worker(
    poll_interval: float = typer.Option(1.0, "--interval", help="Secondi tra un poll e l'altro"),
) -> None:
    """Avvia il worker che elabora la coda job (per Docker o server headless)."""
    _setup_logging(verbose=False)
    console.print("[bold cyan]Worker coda avviato[/bold cyan]")
    console.print(f"Cartella lavori: [cyan]{jobs_root()}[/cyan]")
    console.print("Ctrl+C per fermare.\n")
    run_worker_forever(poll_interval=poll_interval)


@app.command()
def transcribe(
    input_path: Path = typer.Argument(..., help="File audio o video da trascrivere", exists=True),
    output_dir: Path = typer.Option(
        Path("data/output"),
        "--output",
        "-o",
        help="Cartella di output (solo con --legacy-output)",
    ),
    model: str = typer.Option(
        DEFAULT_MODEL,
        "--model",
        "-m",
        help="Modello NeMo pre-addestrato",
    ),
    device: str | None = typer.Option(
        None,
        "--device",
        "-d",
        help="cpu o cuda (default: auto)",
    ),
    formats: list[OutputFormat] = typer.Option(
        [OutputFormat.txt, OutputFormat.srt],
        "--format",
        "-f",
        help="Formati di export (solo con --legacy-output)",
    ),
    summarize_result: bool = typer.Option(
        False,
        "--summarize",
        "-s",
        help="Genera anche un riassunto del testo",
    ),
    summary_provider: str = typer.Option(
        "openai",
        "--summary-provider",
        help="Provider riassunto: local, openai, gemini, claude, deepseek, kimi",
    ),
    summary_length: SummaryLength = typer.Option(
        SummaryLength.auto,
        "--summary-length",
        help="auto, short, normal, detailed",
    ),
    language: str = typer.Option(
        "it",
        "--language",
        "-l",
        help="Lingua parlata nell'audio: it, en, fr, es, de",
    ),
    summary_language: str = typer.Option(
        "it",
        "--summary-language",
        help="Lingua output riassunto: it, en, fr, es, de",
    ),
    legacy_output: bool = typer.Option(
        False,
        "--legacy-output",
        help="Salva in data/output/{nome}.txt senza registro jobs/",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
) -> None:
    """Trascrive un file audio o video in testo."""
    _setup_logging(verbose)
    asr_lang = normalize_language(language)
    summary_lang = normalize_language(summary_language)
    config = TranscribeConfig(model_name=model, device=device, language=asr_lang)

    if legacy_output:
        fmt_names = [f.value for f in formats]
        console.print(f"[bold]Input:[/bold]  {input_path}")
        console.print(f"[bold]Output:[/bold]  {output_dir} ({', '.join(fmt_names)})")
        work_dir = Path(tempfile.mkdtemp(prefix="qwibo_"))
        try:
            with console.status("[bold green]Trascrizione in corso..."):
                result = run_transcribe(input_path, config=config, work_dir=work_dir)
            written = export_all(result, output_dir, input_path.stem, fmt_names)
            if summarize_result:
                unload_model()
                with console.status("[bold green]Riassunto in corso..."):
                    summary = summarize(
                        result.text,
                        provider=summary_provider,
                        length=summary_length,
                        language=summary_lang,
                        source_language=asr_lang,
                    )
                path = export_summary_text(
                    summary.text, output_dir / f"{input_path.stem}_riassunto.txt"
                )
                written.append(path)
            console.print("\n[bold green]Completato![/bold green]")
            for path in written:
                console.print(f"  → {path}")
        finally:
            shutil.rmtree(work_dir, ignore_errors=True)
        return

    console.print(f"[bold]Input:[/bold]  {input_path}")
    console.print(f"[bold]Modello:[/bold] {model}")
    console.print(f"[bold]Lingua audio:[/bold] {language_label(asr_lang)}")
    console.print(f"[bold]Device:[/bold]  {config.resolve_device()}")

    job = enqueue_job(
        input_path,
        input_path.name,
        input_path.stem,
        summary_requested=summarize_result,
        model_name=model,
        device=device,
        summary_provider=summary_provider if summarize_result else "",
        summary_length=summary_length.value,
        asr_language=asr_lang,
        summary_language=summary_lang if summarize_result else asr_lang,
    )
    console.print(f"[bold]Job ID:[/bold]  {job.id}")
    console.print(f"[bold]Cartella:[/bold] {job.path}")

    with console.status("[bold green]Elaborazione in corso..."):
        run_pipeline(job.id)

    job = get_job(job.id)
    if job and job.status == STATUS_COMPLETED:
        console.print("\n[bold green]Completato![/bold green]")
        console.print(f"  → {job.txt_path()}")
        console.print(f"  → {job.srt_path()}")
        if job.summary_path().exists():
            console.print(f"  → {job.summary_path()}")
    elif job and job.status == STATUS_FAILED:
        console.print(f"\n[bold red]Fallito:[/bold red] {job.error}")
        raise typer.Exit(code=1)


@jobs_app.command("list")
def jobs_list(
    status: str | None = typer.Option(None, "--status", help="Filtra per stato"),
    limit: int = typer.Option(20, "--limit", "-n"),
) -> None:
    """Elenca i lavori salvati."""
    jobs = load_index(status=status, limit=limit) if status else load_index(limit=limit)
    if not jobs:
        console.print("Nessun lavoro.")
        return
    table = Table(title="Lavori Qwibo")
    table.add_column("ID")
    table.add_column("File")
    table.add_column("Stato")
    table.add_column("Cartella")
    for job in jobs:
        table.add_row(job.id, job.source_name, job.status, str(job.path))
    console.print(table)


@jobs_app.command("show")
def jobs_show(job_id: str) -> None:
    """Mostra dettaglio di un lavoro."""
    job = get_job(job_id)
    if not job:
        console.print(f"[red]Job {job_id} non trovato[/red]")
        raise typer.Exit(code=1)
    console.print(f"[bold]ID:[/bold]      {job.id}")
    console.print(f"[bold]File:[/bold]    {job.source_name}")
    console.print(f"[bold]Stato:[/bold]   {job.status}")
    console.print(f"[bold]Cartella:[/bold] {job.path}")
    if job.txt_path().exists():
        console.print(f"[bold]TXT:[/bold]     {job.txt_path()}")
    if job.srt_path().exists():
        console.print(f"[bold]SRT:[/bold]     {job.srt_path()}")
    if job.summary_path().exists():
        console.print(f"[bold]Riassunto:[/bold] {job.summary_path()}")
    if job.error:
        console.print(f"[bold red]Errore:[/bold red] {job.error}")


@jobs_app.command("retry")
def jobs_retry(
    job_id: str | None = typer.Argument(None, help="ID job (se omesso, ritenta tutti i falliti)"),
) -> None:
    """Rimette in coda job falliti per rielaborarli."""
    if job_id:
        from qwibo.jobs import requeue_job

        if requeue_job(job_id):
            console.print(f"[green]Job {job_id} rimesso in coda.[/green]")
        else:
            console.print(f"[red]Impossibile rimettere in coda {job_id}[/red]")
            raise typer.Exit(code=1)
        return

    requeued = requeue_failed()
    if not requeued:
        console.print("Nessun job fallito da ritentare.")
        return
    console.print(f"[green]{len(requeued)} job rimessi in coda:[/green]")
    for jid in requeued:
        console.print(f"  • {jid}")


@app.command()
def info() -> None:
    """Mostra modello predefinito e requisiti."""
    config = TranscribeConfig()
    console.print(f"[bold]Qwibo[/bold] v{__version__}\n")
    console.print(f"Modello predefinito: [cyan]{DEFAULT_MODEL}[/cyan]")
    console.print("Lingue ASR: italiano, inglese, francese, spagnolo, tedesco (Parakeet v3)")
    console.print(f"Device rilevato:    [cyan]{config.resolve_device()}[/cyan]")
    console.print(f"Cartella lavori:    [cyan]{jobs_root()}[/cyan]")
    console.print("\nIl modello è [bold]pre-addestrato[/bold]: nessun training necessario.")
    console.print("Primo avvio: download ~2.5 GB del checkpoint NeMo.\n")
    console.print("Uso:")
    console.print("  qwibo              # avvia interfaccia web (coda automatica)")
    console.print("  qwibo worker       # worker headless per Docker")
    console.print("  qwibo transcribe video.mp4 -l en -s --summary-language it")
    console.print("  qwibo jobs list")


if __name__ == "__main__":
    app()
