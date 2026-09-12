# Architecture and data ownership

## The deployed personal system

The project uses Hermes as a general agent runtime. Telegram provides the conversation interface, while an OpenRouter model interprets the user's reports and invokes available tools. The runtime persists conversation history in SQLite and provides full-text session search.

Coaching state is primarily file based. A policy document defines schedule, progression and persistence rules. Separate files contain exercise structure, stable preferences, current results and temporary overrides. A longer dated journal retains details beyond the bounded working history.

This division avoids repeatedly loading the entire journal into the model context. The current state answers ordinary questions; older material is consulted selectively. Instructions define source precedence so recent explicit information can override a stale plan.

The language model remains responsible for much of the workflow and interpretation. A prompt instruction is not a programmatic guarantee. No standalone transactional workout engine is part of the deployed architecture described here.

## The daily data boundary

The deployed daily coordinator invokes a nutrition parser, obtains same-date activity and calls a numerical helper. It passes structured JSON back to the agent. The date belongs to the diary being evaluated, not automatically to the upload time or the next day's plan.

The extracted parser recognizes encodings, headers and a day-total row. It also exposes a macro-calorie cross-check. Explicit totals avoid a common double-counting problem when exports contain both individual rows and subtotal rows.

The original arithmetic helper contains personal parameters. It is deliberately not copied into this edition. The public demo supplies invented coefficients through a visible fixture, so no personal metabolic estimate or nutritional target is revealed.

## Public demonstration boundaries

The public runner uses the extracted parser's local-file interface. Activity is supplied by a synthetic fixture. There is no credential lookup, network client or model request in the runner. Its response is a deterministic rendering of validated fields; the `model` object records zero calls and `deterministic_mock` mode.

The output contains observed fixture totals, provenance, the calculation chain and a synthetic marker. Stale/missing activity removes the estimate rather than reporting invented certainty. An available zero-step value remains a valid observation.

A fixed demonstration clock makes the test repeatable. A mismatched or future date is rejected. This clock is test input, not a production clock policy.

## Persistence semantics

The original journal helper uses a lock and atomic file replacement to update a dated Markdown section. Other working files are updated separately by agent tools. There is no single transaction across all those files.

The demo uses a smaller JSON journal with date-keyed replacement. Replaying a date does not add another key; a corrected fixture replaces that date's value. It does not retain immutable correction lineage, support concurrent writers or reproduce a database event store. Atomic replacement applies to the journal file only; JSON and Markdown report outputs are separate writes.

## What would require separate validation

Live deployment would require an independently configured Hermes installation, credentials, a reviewed policy and explicit authorization for data access. Provider/model behavior, credential refresh, Telegram delivery and real data quality must be tested separately. The synthetic fixture does not prove those integrations work in a new environment.

The broader coaching decisions, exercise progression and personal history are described conceptually but not reproduced as public data. No real context file was renamed and included as a demo.
