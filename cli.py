"""Command-line entry point."""
import argparse
from pathlib import Path
from .analyzer import analyze
from .report import render_markdown, render_text

def main():
    parser = argparse.ArgumentParser(description="Explain common embedded C/C++ source, compiler, and serial-log issues.")
    parser.add_argument("source", nargs="?", help="Path to a C/C++ source file")
    parser.add_argument("--diagnostics", help="Path to compiler/build output")
    parser.add_argument("--logs", help="Path to serial/runtime logs")
    parser.add_argument("--format", choices=("text", "markdown"), default="text")
    parser.add_argument("--output", help="Write report to this path instead of stdout")
    args = parser.parse_args()

    def read_optional(path):
        return Path(path).read_text(encoding="utf-8", errors="replace") if path else ""

    if not any((args.source, args.diagnostics, args.logs)):
        parser.error("provide a source file, --diagnostics, or --logs")

    source = read_optional(args.source)
    diagnostics = read_optional(args.diagnostics)
    logs = read_optional(args.logs)
    findings = analyze(source, diagnostics, logs)
    report = render_markdown(findings) if args.format == "markdown" else render_text(findings)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)

if __name__ == "__main__":
    main()
