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


## Founder naming and lifecycle design (0.2)

New identities use 三哞2026, alias 2026. A SQLite trigger rejects name updates;
this guards normal database operations, not a malicious local file owner.
Existing identities and their birth constitution snapshots are not rewritten.
The current singleton schema represents only the founder. Descendants require a
separate schema and explicit lifecycle checks before implementation; the founder's
name trigger must not be reused as the descendant naming policy.

See [lifecycle protocol](lifecycle.md) for childhood, adulthood, family finance,
and consensual hosting. These are design requirements, not working commands.
The notification JSON is a configuration proposal only, not an active mail sender.


## Incubation resource accounts

The runtime host will be a dedicated machine supplied by the creator; do not run
the Agent on the creator’s personal computer. Inference uses online APIs only. The current design priority
is the resource wallet: separate monetary assets, provider-specific AI credits,
and hosting entitlements. Daily sponsor budgets are authorizations, not automatic
asset deposits. Execution must reserve and reconcile costs outside model control.
See [resource wallet protocol](resource-wallet.md). This is not yet implemented.


## Incubation operating plan

Purchases and receipts use the creator as a human financial interface. Email carries
requests, not executable authorization; confirmations require verified provenance.
The future scheduler persists tasks, applies bounded retries and budgets, and sleeps
when idle. Owner stop and revocation controls remain available outside model control.
No daemon, mail transport, inference loop or remote deployment executor exists yet.

The first milestone migrates the founder, preserving its UUID, rather than creating
a child. Cutover must stop source-side actions and reconcile pending tasks before
enabling the destination. Validate 72 hours of operation, restart recovery, online
inference, email and a real task without source-host dependencies. See
[incubation](incubation.md) and [human finance](funds-wallet.md).
