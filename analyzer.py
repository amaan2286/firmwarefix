"""Rule-based, explainable checks for embedded C/C++ debugging."""
from dataclasses import dataclass, asdict
import re
from typing import Iterable

@dataclass
class Finding:
    rule_id: str
    severity: str
    title: str
    evidence: str
    explanation: str
    suggestion: str
    line: int | None = None

    def to_dict(self):
        return asdict(self)

def _line_number(source: str, match_start: int) -> int:
    return source.count("\n", 0, match_start) + 1

def analyze_source(source: str) -> list[Finding]:
    findings: list[Finding] = []
    rules = [
        ("FF001", "high", "Unbounded string copy",
         r"\bstrcpy\s*\(",
         "`strcpy` copies until a NUL terminator without knowing the destination capacity.",
         "Prefer a bounded operation and validate lengths; ensure the destination is large enough."),
        ("FF002", "high", "Potentially unbounded formatted output",
         r"\bsprintf\s*\(",
         "`sprintf` does not know the destination buffer size and can overflow it.",
         "Prefer `snprintf(buffer, sizeof buffer, ...)` and check its return value."),
        ("FF003", "medium", "Arduino String allocation",
         r"\bString\s+\w+",
         "Repeated dynamic `String` allocation on small MCUs can contribute to heap fragmentation.",
         "For long-running firmware, consider fixed-size buffers or carefully bounded allocation."),
        ("FF004", "medium", "Blocking delay in firmware",
         r"\bdelay\s*\(",
         "A blocking delay may prevent timely processing of sensors, communication, or control tasks.",
         "Consider a non-blocking timer/state-machine approach when responsiveness matters."),
        ("FF005", "medium", "ISR-shared variable review",
         r"\battachInterrupt\s*\(",
         "An interrupt handler is registered here; shared state needs careful synchronization.",
         "Review variables shared with the ISR. `volatile` can prevent some compiler optimizations but does not make compound operations atomic."),
    ]
    for rule_id, severity, title, pattern, explanation, suggestion in rules:
        for match in re.finditer(pattern, source):
            start = match.start()
            line = _line_number(source, start)
            evidence = source.splitlines()[line - 1].strip() if source.splitlines() else match.group(0)
            findings.append(Finding(rule_id, severity, title, evidence[:180], explanation, suggestion, line))

    # A narrow heuristic: an infinite loop without any obvious wait/yield mechanism.
    for match in re.finditer(r"\bwhile\s*\(\s*1\s*\)\s*\{", source):
        block_start = match.end()
        # Only inspect a bounded region; this is intentionally a heuristic.
        region = source[block_start:block_start + 700]
        if not re.search(r"\b(delay|vTaskDelay|yield|sleep|ulTaskNotifyTake|xQueueReceive)\s*\(", region):
            line = _line_number(source, match.start())
            findings.append(Finding(
                "FF006", "medium", "Busy-wait loop may starve other work",
                source.splitlines()[line - 1].strip(),
                "This `while(1)` region has no obvious delay/yield call in the inspected window.",
                "If using an RTOS, block on a queue/semaphore or yield appropriately. For bare metal, ensure the loop is intentionally bounded by timing and workload needs.",
                line
            ))
    return findings

def analyze_diagnostics(diagnostics: str) -> list[Finding]:
    findings: list[Finding] = []
    checks = [
        ("FF101", "high", "Undeclared identifier", r"\b(?:undeclared|not declared in this scope)\b",
         "The compiler cannot resolve a name at the reported location.",
         "Check spelling, declaration order, scope, and required headers."),
        ("FF102", "medium", "Missing header or include path", r"\b(?:No such file or directory|fatal error:.*\.h)",
         "A referenced header could not be found.",
         "Verify the include spelling and configure the correct SDK/toolchain include paths."),
        ("FF103", "high", "Possible type mismatch", r"\b(?:invalid conversion|cannot convert|incompatible types)\b",
         "The compiler reports incompatible types or a conversion it cannot perform.",
         "Inspect the reported expression and use an explicit, semantically correct type conversion only if appropriate."),
        ("FF104", "medium", "Undefined reference / link failure", r"\bundefined reference to\b",
         "Compilation reached the linker, but a referenced symbol was not resolved.",
         "Check that the implementation is compiled and linked, and that declarations and definitions match."),
        ("FF105", "medium", "Warning treated as error", r"\bwarning:.*\[-Werror",
         "A compiler warning is being promoted to an error.",
         "Fix the underlying warning rather than disabling `-Werror` by default."),
    ]
    for line_no, line in enumerate(diagnostics.splitlines(), 1):
        for rule_id, severity, title, pattern, explanation, suggestion in checks:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(Finding(rule_id, severity, title, line.strip()[:180], explanation, suggestion, line_no))
    return findings

def analyze_logs(logs: str) -> list[Finding]:
    findings: list[Finding] = []
    checks = [
        ("FF201", "high", "Watchdog reset", r"watchdog|wdt reset",
         "The watchdog may have reset the device because a task or loop did not service it in time.",
         "Inspect blocking calls, deadlocks, long critical sections, and task priorities."),
        ("FF202", "high", "Stack overflow signal", r"stack overflow|stack canary",
         "The runtime log suggests a stack limit or stack corruption issue.",
         "Check recursive/deep calls and large local arrays; measure task stack high-water marks if available."),
        ("FF203", "medium", "Brownout / supply instability", r"brownout|brown out|undervoltage",
         "The device reports a supply-voltage event.",
         "Check regulator capacity, transient current draw, wiring, and decoupling before changing firmware."),
        ("FF204", "medium", "I2C communication timeout", r"i2c.*timeout|timeout.*i2c|nack",
         "The log suggests an I2C transaction failed or timed out.",
         "Check address, pull-ups, bus voltage, wiring, clock rate, and whether the target is powered."),
        ("FF205", "medium", "UART framing or receive issue", r"uart.*(?:framing|overrun|overflow)|serial.*overflow",
         "The log suggests serial data may be corrupted or arriving faster than it is consumed.",
         "Check baud rate, framing settings, buffer sizing, and receive handling latency."),
    ]
    for line_no, line in enumerate(logs.splitlines(), 1):
        for rule_id, severity, title, pattern, explanation, suggestion in checks:
            if re.search(pattern, line, re.IGNORECASE):
                findings.append(Finding(rule_id, severity, title, line.strip()[:180], explanation, suggestion, line_no))
    return findings

def analyze(source: str = "", diagnostics: str = "", logs: str = "") -> list[Finding]:
    return analyze_source(source) + analyze_diagnostics(diagnostics) + analyze_logs(logs)
