# FirmwareFix 🛠️

**A local-first, rule-based debugging assistant for embedded C/C++ firmware.** It checks source code, compiler diagnostics, and serial/runtime logs for a small set of common patterns, then explains the evidence and suggests next steps.

> **Scope:** this is an MVP heuristic analyzer, not a compiler, static-analysis proof, or validated AI system. It can miss bugs and produce false positives. Verify every finding on your toolchain and target hardware. It does not automatically patch code.

## Features
- Browser workbench for source code, compiler output, and serial logs
- Python rule engine with stable finding IDs and evidence
- Local HTTP API connecting the browser UI to the Python analyzer
- Command-line reports in text or Markdown
- Example inputs and unit tests; no third-party Python dependencies

## Requirements
- Python 3.10 or newer
- A modern browser

## Run the web app
From the repository root:
```bash
python server.py
```
Open **http://127.0.0.1:8000**. Paste source code, compiler diagnostics, and/or logs, then select **Run Diagnostics**. The server binds to loopback (`127.0.0.1`) and is intended for local development only. Do not expose this basic development server to the public internet as-is.

## Run the CLI
```bash
python -m firmwarefix.cli examples/buggy_firmware.c
python -m firmwarefix.cli examples/buggy_firmware.c --diagnostics examples/compiler_errors.txt --logs examples/serial_log.txt --format markdown --output report.md
```

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Current rule coverage
| IDs | Input | Example patterns |
|---|---|---|
| FF001–FF006 | Source code | `strcpy`, `sprintf`, Arduino `String`, `delay`, ISR review reminder, busy-wait loop heuristic |
| FF101–FF105 | Compiler diagnostics | undeclared identifiers, missing headers, type mismatches, undefined references, `-Werror` |
| FF201–FF205 | Runtime/serial logs | watchdog, stack overflow, brownout, I2C timeout/NACK, UART receive problems |

These are pattern-based checks; the rule list is not exhaustive and does not parse a full C/C++ abstract syntax tree.

## Repository layout
```text
index.html                 Browser workbench
server.py                  Local HTTP server and /api/analyze endpoint
firmwarefix/analyzer.py    Rule-based checks
firmwarefix/cli.py         CLI entry point
firmwarefix/report.py      Text/Markdown report formatting
examples/                  Sample firmware, compiler output, and logs
tests/                     Unit tests
```

## Next steps
Potential improvements: parser-backed analysis, more target-specific rules, regression tests per rule, compiler/toolchain integration, and a measured false-positive/false-negative evaluation on a documented dataset.
