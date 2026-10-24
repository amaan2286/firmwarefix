import unittest
from firmwarefix.analyzer import analyze_source, analyze_diagnostics, analyze_logs

class AnalyzerTests(unittest.TestCase):
    def test_unsafe_string_copy(self):
        findings = analyze_source('char x[4]; strcpy(x, "too long");')
        self.assertTrue(any(f.rule_id == "FF001" for f in findings))

    def test_compiler_identifier(self):
        findings = analyze_diagnostics("error: 'x' was not declared in this scope")
        self.assertTrue(any(f.rule_id == "FF101" for f in findings))

    def test_watchdog_log(self):
        findings = analyze_logs("Task watchdog got triggered")
        self.assertTrue(any(f.rule_id == "FF201" for f in findings))

if __name__ == "__main__":
    unittest.main()
