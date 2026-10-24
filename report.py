"""Human-readable report formatting."""
from .analyzer import Finding

def render_text(findings: list[Finding]) -> str:
    if not findings:
        return "FirmwareFix report\n\nNo findings matched the current rules. This does not prove the code is bug-free.\n"
    lines = ["FirmwareFix report", "=" * 18, f"\nFindings: {len(findings)}\n"]
    for i, f in enumerate(findings, 1):
        where = f" (line {f.line})" if f.line else ""
        lines.extend([
            f"{i}. [{f.severity.upper()}] {f.title}{where} — {f.rule_id}",
            f"   Evidence: {f.evidence}",
            f"   Why it matters: {f.explanation}",
            f"   Suggested next step: {f.suggestion}",
            ""
        ])
    lines.append("Note: Findings are heuristic. Verify recommendations against your board, SDK, and application.")
    return "\n".join(lines)

def render_markdown(findings: list[Finding]) -> str:
    if not findings:
        return "# FirmwareFix report\n\nNo findings matched the current rules. This does not prove the code is bug-free.\n"
    lines = ["# FirmwareFix report", f"**Findings:** {len(findings)}", ""]
    for i, f in enumerate(findings, 1):
        where = f" — line {f.line}" if f.line else ""
        lines.extend([
            f"## {i}. [{f.severity.upper()}] {f.title}{where}",
            f"- **Rule:** `{f.rule_id}`",
            f"- **Evidence:** `{f.evidence}`",
            f"- **Why it matters:** {f.explanation}",
            f"- **Suggested next step:** {f.suggestion}",
            ""
        ])
    lines.append("> Findings are heuristic. Verify recommendations against your board, SDK, and application.")
    return "\n".join(lines) + "\n"
