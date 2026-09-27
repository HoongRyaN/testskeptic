# TestSkeptic

Passing tests can still miss broken behavior.

TestSkeptic is a small Python prototype that exposes test blind spots through controlled code mutations, with IBM Bob-assisted analysis of missing test cases.

## Problem

A test suite may pass while missing an important business-rule boundary. Developers need evidence that their assertions can detect meaningful behavior changes.

## Target users

Developers and reviewers who want to investigate gaps in tests for small business rules.

## Workflow

1. Run the original tests and require a passing baseline.
2. Create a temporary copy with one predefined mutation.
3. Run the same test suite against that copy.
4. Classify the result as KILLED, SURVIVED, or INVALID.
5. Inspect surviving mutations with IBM Bob.
6. Add a requirement-based test and rerun the experiment.

Each mutation is tested independently. The runner does not edit the original business code.

## Demo business rule

For non-negative integer subtotals:

- Subtotal >= 100: shipping fee is 0.
- Subtotal < 100: shipping fee is 10.

## Requirements

- Python 3.14; tested with Python 3.14.7 on Windows.
- Git to clone the repository.
- No third-party Python packages.

## Setup on Windows

Clone the repository:

```powershell
git clone https://github.com/HoongRyaN/testskeptic.git
cd testskeptic
```

Create a virtual environment:

```powershell
python -m venv .venv
```

If Python is available through the Windows launcher instead:

```powershell
py -3.14 -m venv .venv
```

Use whichever command is available on your machine. You only need to create the environment once.

## Run the demonstration

Before adding the missing test:

```powershell
.\.venv\Scripts\python.exe skeptic.py --suite before
```

After adding the missing test:

```powershell
.\.venv\Scripts\python.exe skeptic.py --suite after
```

Open the generated reports:

```powershell
Start-Process .\report-before.html
Start-Process .\report-after.html
```

The before suite is an intentionally incomplete demonstration fixture. The after suite is the current test suite.

## Observed results

| Metric | Before | After |
|---|---:|---:|
| Original tests passing | 3 | 4 |
| Predefined mutations checked | 3 | 3 |
| KILLED | 2 | 3 |
| SURVIVED | 1 | 0 |
| INVALID | 0 | 0 |

The added test checks that a subtotal of 99 still incurs a shipping fee of 10.

It detects M02, which incorrectly changes the free-shipping threshold from 100 to 99.

These results describe the included example and three selected mutations. They are not a general test-coverage or software-correctness score.

## Result definitions

- KILLED: the mutated run produced assertion failures under this prototype's classification rules.
- SURVIVED: the mutated run passed the selected tests.
- INVALID: the mutation target was unavailable or the run did not produce a supported valid test result.

Syntax errors and import failures are not credited as successful detections.

## Additional validation

In a separate validation copy, M03 was changed to insert `return (`.

The original tests passed, while the malformed mutation produced INVALID.

Observed totals: 2 KILLED, 0 SURVIVED, 1 INVALID.

Saved reports are in `docs/demo/`:

- `before.html`
- `after.html`
- `invalid.html`

These are saved run artifacts. Use the commands above to generate fresh before and after reports.

## IBM Bob contribution

IBM Bob was used to analyze the repository's test gaps, explain surviving mutations, and propose tests grounded in the business rule.

The participant manually entered the code and tests.

See `docs/bob-usage.md` for details and `bob_sessions/` for session evidence.

## Current limitations

- Supports the included shipping example and three predefined text replacements.
- Does not automatically discover arbitrary mutation locations.
- Parses standard unittest text output rather than a structured result protocol.
- Tests run locally; temporary directories are not security sandboxes.
- The runner does not call an IBM Bob API.
- No general productivity benchmark has been measured.

## Project files

- `shipping.py`: example business rule.
- `test_shipping.py`: improved test suite.
- `demo_before.py`: intentionally incomplete demo suite.
- `skeptic.py`: mutation runner and HTML report generator.
- `docs/demo/`: saved demonstration reports.
- `bob_sessions/`: IBM Bob task evidence.