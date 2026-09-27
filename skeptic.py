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

mutations = [
    {
        "id": "M01",
        "original": "subtotal >= 100",
        "replacement": "subtotal > 100",
    },
    {
        "id": "M02",
        "original": "subtotal >= 100",
        "replacement": "subtotal >= 99",
    },
    {
        "id": "M03",
        "original": "return 10",
        "replacement": "return 0",
    },
]

results = []

for mutation in mutations:
    original = mutation["original"]
    replacement = mutation["replacement"]

    print("Testing mutation:", mutation["id"])

    if source.count(original) != 1:
        status = "ERROR"
        mutation_output = "Expected exactly one mutation target."
    else:
        with tempfile.TemporaryDirectory(prefix="testskeptic-") as temporary:
            folder = Path(temporary)
            shutil.copy2(ROOT / "test_shipping.py", folder / "test_shipping.py")

            mutated = source.replace(original, replacement, 1)
            (folder / "shipping.py").write_text(mutated, encoding="utf-8")

            status, mutation_output = run_tests(folder)

    verdict = {
        "PASS": "SURVIVED",
        "FAIL": "KILLED",
        "ERROR": "INVALID",
    }[status]

    print(mutation["id"], verdict)

    results.append({
        "id": mutation["id"],
        "original": original,
        "replacement": replacement,
        "verdict": verdict,
        "output": mutation_output,
    })

sections = ""
verdicts = []

for result in results:
    verdicts.append(result["verdict"])

    sections += f"""
    <section>
        <h2>{escape(result["id"])}: {escape(result["verdict"])}</h2>
        <p>Original: <code>{escape(result["original"])}</code></p>
        <p>Mutated: <code>{escape(result["replacement"])}</code></p>
        <details>
            <summary>View test output</summary>
            <pre style="background: #f3f4f6; padding: 16px; overflow-x: auto;">{escape(result["output"])}</pre>
        </details>
    </section>
    """

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
    <p>Controlled mutation test report</p>
    <p>Generated: {escape(generated_at)}</p>

    <h2>Summary</h2>
    <p>Original test status: <strong>{escape(baseline)}</strong></p>
    <ul>
        <li>Total mutations: {len(results)}</li>
        <li>KILLED: {verdicts.count("KILLED")}</li>
        <li>SURVIVED: {verdicts.count("SURVIVED")}</li>
        <li>INVALID: {verdicts.count("INVALID")}</li>
    </ul>

    <h2>Original test run</h2>
    <pre style="background: #f3f4f6; padding: 16px; overflow-x: auto;">{escape(baseline_output)}</pre>

    {sections}

    <hr>
    <p>Each mutation was tested independently against the same test suite.</p>
    <p>Scope: the included shipping example and three predefined mutations.</p>
    <p>These results are not an overall software correctness score.</p>
</body>
</html>
"""

report_path = ROOT / "report.html"
report_path.write_text(report, encoding="utf-8")
print("Report saved to:", report_path)
