from pathlib import Path
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
        return "ERROR"
    output = result.stdout + result.stderr
    print(output)

    count = re.search(r"Ran (\d+) tests?", output)
    if count is None or int(count.group(1)) == 0:
        return "ERROR"

    if result.returncode == 0:
        return "PASS"

    if result.returncode == 1 and re.search(r"FAILED \(failures=\d+\)", output):
        return "FAIL"

    return "ERROR"


print("Checking the original tests...")
baseline =  run_tests(ROOT)
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

    status = run_tests(folder)

if status == "PASS":
    print("SURVIVED: tests missed the changed behavior.")
elif status == "FAIL":
    print("KILLED: tests detected the changed behavior.")
else:
    print("INVALID: execution failed; do not count this as detection.")