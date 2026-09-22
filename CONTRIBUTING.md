# Contributing

Start with an issue describing the experimental question and intended behavior.
Use Python 3.10+ and the standard library for the initial prototype.

Run `python3 -m unittest discover -s tests -v` before submitting changes.
Include tests for identity continuity and state transitions when changing storage.
Keep real identities, credentials, personal memories and runtime databases out of commits.

Changes introducing external actions need explicit authorization and budget semantics,
and must preserve the owner's ability to stop execution. Document limitations honestly;
do not represent simulated behavior as consciousness or autonomous execution.
