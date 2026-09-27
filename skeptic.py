from pathlib import Path
from datetime import datetime
from html import escape
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent


def run_tests(folder):
    command = [
        sys.executable,
        "-X",
        "utf8",
        "-B",
        "-m",
        "unittest",
        "-v",
        "test_shipping",
    ]

    try:
        result = subprocess.run(
            command,
            cwd=folder,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=10,
        )
    except subprocess.TimeoutExpired:
        print("ERROR: test run timed out.")
        return "ERROR", "Test run exceeded the 10-second limit."
    output = result.stdout + result.stderr
    print(output)

    count = re.search(r"Ran (\d+) tests?", output)
    if count is None or int(count.group(1)) == 0:
        return "ERROR", output

    if result.returncode == 0:
        return "PASS", output

    if result.returncode == 1 and re.search(r"FAILED \(failures=\d+\)", output):
        return "FAIL", output

    return "ERROR", output


print("Checking the original tests...")
baseline, baseline_output = run_tests(ROOT)
print("Baseline result:", baseline)

if baseline != "PASS":
    raise SystemExit("STOP: original tests must pass before mutation.")

source_path = ROOT / "shipping.py"
source = source_path.read_text(encoding="utf-8")

original = "subtotal >= 100"
replacement = "subtotal > 100"

if source.count(original) != 1:
    raise SystemExit("STOP: expected exactly one mutation target.")

print("Testing a mutated copy...")

with tempfile.TemporaryDirectory(prefix="testskeptic-") as temprary:
    folder = Path(temprary)
    shutil.copy2(ROOT / "test_shipping.py", folder / "test_shipping.py")

    mutated = source.replace(original, replacement, 1)
    (folder / "shipping.py").write_text(mutated, encoding="utf-8")

    status, mutation_output = run_tests(folder)

if status == "PASS":
    verdict = "SURVIVED"
    summary = "Tests missed the changed behavior."
elif status == "FAIL":
    verdict = "KILLED"
    summary = "Tests detected the changed behavior."
else:
    verdict = "INVALID"
    summary = "Execution failed; do not count this as detection."

print(f"{verdict}: {summary}")

generated_at = datetime.now().astimezone().isoformat(timespec="seconds")

report = f"""<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>TestSkeptic Report</title>
    <style>
        body {{ font-family: sans-serif; }}
        pre {{ white-space: pre-wrap; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
        .error {{ color: orange; }}
    </style>
</head>
<body style="font-family: sans-serif; max-width: 960px; margin: 40px auto; padding: 0 20px; line-height: 1.6;">
    <h1>TestSkeptic</h1>
    <p>Single-mutation test report</p>
    <p>Generated: {escape(generated_at)}</p>

    <h2>Result: {escape(verdict)}</h2>
    <p>{escape(summary)}</p>
    <p>Original test status: <strong>{escape(baseline)}</strong></p>

    <h2>Controlled mutation</h2>
    <p>Original: <code>{escape(original)}</code></p>
    <p>Mutated: <code>{escape(replacement)}</code></p>

    <h2>Original test run</h2>
    <pre style="background: #f3f4f6; padding: 16px; overflow-x: auto;">{escape(baseline_output)}</pre>

    <h2>Mutated test run</h2>
    <pre style="background: #f3f4f6; padding: 16px; overflow-x: auto;">{escape(mutation_output)}</pre>

    <hr>
    <p>Scope: the included shipping example and one predifined mutation.</p>
    <p>This result is not an overall software correctness score.</p>
</body>
</html>
"""

report_path = ROOT / "report.html"
report_path.write_text(report, encoding="utf-8")
print("Report saved to:", report_path)
