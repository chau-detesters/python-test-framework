import pytest
import json
import time
from pathlib import Path
from typing import Dict, List, Any

class TestMetricsCollector:
    """Collect test execution metrics"""
    def __init__(self):
        self.test_results: List[Dict[str, Any]] = []
        self.start_time = time.time()

    def add_test_result(self, test_name: str, status: str, duration: float, error: str = None):
        self.test_results.append({
            "test_name": test_name,
            "status": status,
            "duration": duration,
            "error": error,
            "timestamp": time.time()
        })

    def generate_report(self) -> Dict[str, Any]:
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed_tests = len([r for r in self.test_results if r["status"] == "FAILED"])
        skipped_tests = len([r for r in self.test_results if r["status"] == "SKIPPED"])
        total_duration = sum(r["duration"] for r in self.test_results)
        avg_duration = total_duration / total_tests if total_tests > 0 else 0
        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "skipped": skipped_tests,
                "success_rate": passed_tests / total_tests * 100 if total_tests > 0 else 0,
                "total_duration": total_duration,
                "average_duration": avg_duration
            },
            "test_results": self.test_results,
            "generated_at": time.time()
        }

metrics_collector = TestMetricsCollector()

# Hook: verzamel testresultaten na elke test-call
@pytest.hookimpl(tryfirst=True)
def pytest_runtest_makereport(item, call):
    if call.when == "call":
        if call.excinfo is None:
            status = "PASSED"
            error = None
        elif call.excinfo.typename == "Skipped":
            status = "SKIPPED"
            error = str(call.excinfo.value)
        else:
            status = "FAILED"
            error = str(call.excinfo.value)
        metrics_collector.add_test_result(
            test_name=item.nodeid,
            status=status,
            duration=call.duration,
            error=error
        )

# Hook: genereer en print metrics rapport na de testsessie
def pytest_sessionfinish(session, exitstatus):
    report = metrics_collector.generate_report()
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    with open(reports_dir / "metrics_report.json", "w") as f:
        json.dump(report, f, indent=2)
    summary = report["summary"]
    print(f"\n{'='*50}")
    print(f"TEST EXECUTION SUMMARY")
    print(f"{'='*50}")
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Skipped: {summary['skipped']}")
    print(f"Success Rate: {summary['success_rate']:.1f}%")
    print(f"Total Duration: {summary['total_duration']:.2f}s")
    print(f"Average Duration: {summary['average_duration']:.3f}s")
    print(f"{'='*50}") 