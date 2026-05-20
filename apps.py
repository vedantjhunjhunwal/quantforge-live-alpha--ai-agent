from __future__ import annotations
import argparse
from rich.console import Console
from rich.table import Table
from quantforge.graph.state import AlphaSignalState
from quantforge.graph.workflow import QuantForgeWorkflow

console = Console()


def parse_args():
    parser = argparse.ArgumentParser(description="QuantForge Live L4 Alpha Discoverer")
    parser.add_argument("--goal", default="Find a mean reversion alpha")
    parser.add_argument("--provider", choices=["yahoo", "binance", "csv", "parquet"], default="yahoo")
    parser.add_argument("--symbols", nargs="+", default=["AAPL", "MSFT", "NVDA", "SPY"])
    parser.add_argument("--data-file", default=None)
    parser.add_argument("--period", default="6mo")
    parser.add_argument("--interval", default="1d")
    parser.add_argument("--timeframe", default="5m")
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--max-mutations", type=int, default=5)
    parser.add_argument("--llm-provider", choices=["auto", "openai", "gemini", "deterministic"], default="auto", help="auto = use available API key; if absent, fall back to deterministic partial-agent nodes.")
    parser.add_argument("--llm-model", default=None, help="Optional model override, e.g. gpt-4o-mini or gemini-1.5-flash")
    parser.add_argument("--llm-fallback", choices=["auto", "strict"], default="auto", help="auto = no API key falls back to deterministic nodes; strict = missing key fails.")
    return parser.parse_args()


def main():
    args = parse_args()
    state = AlphaSignalState(
        goal=args.goal,
        provider=args.provider,
        symbols=args.symbols,
        data_file=args.data_file,
        period=args.period,
        interval=args.interval,
        timeframe=args.timeframe,
        limit=args.limit,
        max_mutations=args.max_mutations,
        llm_provider=args.llm_provider,
        llm_model=args.llm_model,
        llm_fallback=args.llm_fallback,
    )

    console.rule("[bold]QuantForge Live L4[/bold]")
    console.print("[bold]Production mode:[/bold] no synthetic/duplicate market data fallback.")
    console.print(f"[bold]LLM mode:[/bold] {state.llm_provider}" + (f" / {state.llm_model}" if state.llm_model else "") + f" | fallback={state.llm_fallback}")
    console.print(f"Goal: {state.goal}")
    console.print(f"Provider: {state.provider} | Symbols: {', '.join(state.symbols)}")

    try:
        final_state = QuantForgeWorkflow().run(state)
    except Exception as exc:
        console.print("[bold red]Run failed[/bold red]")
        console.print(str(exc))
        console.print("This project intentionally fails instead of using fake data when live/vendor data cannot be fetched.")
        raise SystemExit(1)

    console.rule("[bold]Node Trace[/bold]")
    for item in final_state.node_trace:
        console.print(item)

    table = Table(title="Final Alpha Decision")
    table.add_column("Field")
    table.add_column("Value")
    table.add_row("Decision", final_state.decision)
    table.add_row("Expression", final_state.current_expression)
    table.add_row("Iterations", str(final_state.iteration))
    table.add_row("Market rows", str(final_state.market_rows))
    table.add_row("Latest market timestamp", str(final_state.latest_timestamp))
    for k, v in final_state.metrics.items():
        table.add_row(k, f"{v:.6f}" if isinstance(v, float) else str(v))
    console.print(table)

    if final_state.critique_history:
        console.rule("[bold]Critique History[/bold]")
        for i, c in enumerate(final_state.critique_history, 1):
            console.print(f"{i}. {c}")

    if final_state.is_signal_viable:
        console.print(f"[bold green]Validated alpha exported to:[/bold green] {final_state.provider_metadata.get('export_path')}")
    else:
        console.print("[bold yellow]No validated alpha found within max mutations.[/bold yellow]")


if __name__ == "__main__":
    main()
