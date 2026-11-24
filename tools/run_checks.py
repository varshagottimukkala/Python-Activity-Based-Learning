import ast
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
FORBIDDEN = (
    ast.Import,
    ast.ImportFrom,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Lambda,
    ast.Dict,
    ast.Set,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
    ast.Try,
    ast.With,
    ast.AsyncWith,
    ast.Await,
    ast.Yield,
    ast.YieldFrom,
)
ALLOWED_CALLS = {"print", "input", "int", "str", "len", "range"}


def run_checks():
    report = []
    issues = []
    directories = sorted(ROOT.glob("[0-9][0-9]_*"))
    for directory in directories:
        program = directory / "program.py"
        tree = ast.parse(program.read_text(encoding="utf-8"), filename=str(program))
        for node in ast.walk(tree):
            if isinstance(node, FORBIDDEN):
                issues.append(f"{directory.name}: out-of-syllabus construct {type(node).__name__}")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id not in ALLOWED_CALLS:
                issues.append(f"{directory.name}: unexpected built-in call {node.func.id}")
        cases = json.loads((directory / "tests.json").read_text(encoding="utf-8"))
        output_directory = directory / "test_outputs"
        output_directory.mkdir(exist_ok=True)
        for case in cases:
            failures = []
            try:
                result = subprocess.run(
                    [sys.executable, "-B", str(program)],
                    input=case["input"],
                    text=True,
                    encoding="utf-8",
                    capture_output=True,
                    timeout=5,
                    cwd=ROOT,
                )
                stdout = result.stdout.replace("\r\n", "\n")
                if result.returncode != 0:
                    failures.append(f"exit status {result.returncode}: {result.stderr.strip()}")
                if result.stderr:
                    failures.append(f"unexpected stderr: {result.stderr.strip()}")
                for expected in case["contains"]:
                    if expected not in stdout:
                        failures.append(f"missing expected output: {expected!r}")
                for unwanted in case.get("absent", []):
                    if unwanted in stdout:
                        failures.append(f"unexpected output: {unwanted!r}")
            except subprocess.TimeoutExpired:
                stdout = ""
                failures.append("program exceeded the five-second test limit")
            (output_directory / f"{case['id']}.txt").write_text(stdout, encoding="utf-8")
            status = "PASS" if not failures else "FAIL"
            report.append({
                "study": directory.name,
                "test": case["id"],
                "status": status,
                "failures": failures,
            })
            if failures:
                print(f"FAIL {directory.name}/{case['id']}")
                for failure in failures:
                    print(f"  {failure}")
        passed = sum(item["status"] == "PASS" for item in report if item["study"] == directory.name)
        print(f"{directory.name}: {passed}/{len(cases)} checks passed")
    passed = sum(item["status"] == "PASS" for item in report)
    summary = {
        "python_version": sys.version.split()[0],
        "studies": len(directories),
        "passed": passed,
        "total": len(report),
        "syllabus_issues": issues,
        "results": report,
    }
    (ROOT / "verification.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(f"\nTOTAL: {passed}/{len(report)} checks passed across {len(directories)} studies")
    print(f"Syllabus checks: {'PASS' if not issues else 'FAIL'}")
    for issue in issues:
        print(f"  {issue}")
    return 0 if passed == len(report) and not issues else 1


if __name__ == "__main__":
    raise SystemExit(run_checks())
