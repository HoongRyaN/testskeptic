# How IBM Bob Was Used

## Development approach

TestSkeptic was developed by a solo participant who manually typed the code.

External AI tutoring supported step-by-step implementation and debugging. IBM Bob was used in the project workspace for repository-aware analysis of test gaps and proposed improvements.

## Boundary analysis at 100

Bob analyzed why tests using subtotals of 50 and 150 could not distinguish `subtotal >= 100` from `subtotal > 100`.

It identified 100 as the distinguishing input and proposed asserting that the shipping fee is 0.

The participant entered the test and verified that the mutation changed from SURVIVED to KILLED.

## Analysis of surviving mutation M02

After the prototype supported three mutations, M02 still survived.

Bob explained why changing the threshold from 100 to 99 was invisible to tests using 50, 100, and 150.

It proposed a test asserting that `shipping_fee(99)` equals 10, based on the business rule.

The participant entered that test and reran all three mutations.

## Discussion of evidence and limitations

Bob explained that detecting the selected mutations does not prove the application is bug-free.

Its analysis helped distinguish mutation sensitivity from overall correctness.

## Observed outcome

Before the final test was added:
- 3 original tests passed.
- 2 mutations were detected.
- 1 mutation survived.

After the final test was added:
- 4 original tests passed.
- All 3 predefined mutations were detected.

## Role separation

Bob's demonstrated role was analysis and test-design assistance in the IDE.

The participant manually implemented changes and executed validation commands.

The Python runner performs the experiments and generates reports without calling a Bob API.

## Evidence

Task-session summary screenshots and supporting conversation screenshots are stored in `bob_sessions/`.