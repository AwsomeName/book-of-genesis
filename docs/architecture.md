# Architecture / 架构

## Implemented

The standard-library CLI opens a local SQLite database only when a command runs.
A singleton identity contains a UUID, display name, creator relationship, UTC birth
 time, and the exact constitution text loaded at birth. Events are append-only
through the CLI; activity state changes and their corresponding events share a
transaction. Existing identity data is never replaced by `birth`.

The father relationship is user-supplied provenance, not authenticated identity.
No model executes the constitution. `remember` records operator input, explicitly
labelled as such. SQLite is not encrypted or tamper-proof; local file owners can
edit it. These are research records, not a security boundary.

## Intended separation

A future reasoning component proposes actions. A separate executor checks scoped,
expiring authorizations, resource limits, and stop controls before execution.
Memory and outside content must not grant permissions. Legal uncertainty cannot
be resolved by a model declaring its own action lawful.

Resource discovery and recommendations can be investigated before granting any
ability to allocate resources. Account creation, purchases, third-party messages,
and reproduction are outside the current implementation.

## Continuity and recovery

Stop all CLI writers, then copy the entire data directory to a backup or another
authorized host. Keep the original backup until `status` and `recall` succeed on
the destination. Treat this as recovery/migration of one identity; running two
copies independently is a lineage problem not solved by this prototype.
Do not commit state files or secrets. Backups are currently operator-managed.

## Questions for the experiment

- How should an individual distinguish inherited records from lived experience?
- When does a branch become a separate individual?
- How should conflicting memories and value revisions be preserved?
- What counts as recoverable dormancy, and when does an experiment end?

Measure memory continuity, recovery success, useful activity, resource costs and
human intervention. Do not reward defeating stop controls or obtaining resources
without authorization.
