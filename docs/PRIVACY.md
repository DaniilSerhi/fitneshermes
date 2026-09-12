# Public-copy preparation

This edition was built in a new directory from an explicit file selection. The working source and personal state were preserved, and no original Git metadata or history was copied. No repository was created on a hosting service and nothing was pushed.

## Included by selection

One existing standalone CSV parser and the upstream license notice were copied. A new offline runner, behavior tests, generic documentation, CI definition and synthetic inputs were authored for this edition. [PUBLIC_FILES.txt](../PUBLIC_FILES.txt) lists the exact files intended for the first commit.

## Excluded categories

- Credentials, private keys, tokens, cookies, OAuth files and real environment files.
- Conversation histories, profiles, coaching prompts containing personal context and session databases.
- Real health, nutrition, workout, wearable and progress records.
- Personal notes, educational records, financial/client documents and internal audits.
- Server addresses, machine-specific home paths and account identifiers.
- Working screenshots, office documents, PDFs, media and archives.
- Runtime copies, environments, caches, dependency folders and build artifacts.

The empty `.env.example` documents possible integration credential names only. The offline demo does not read it.

## Synthetic provenance

Every input under `examples/synthetic/` was invented for this edition: three fictional food rows, one fictional date, an activity count and toy arithmetic coefficients. They were not produced by replacing a name in a real record. The CSV preamble and JSON markers declare their status. The expected report and JSON were generated only from these inputs.

## Verification scope

Checks run locally. No private project content was uploaded to an external scanner. The publication checker validates the explicit inventory, internal file links, empty environment values and focused patterns for private keys, credential-like values, personal home paths and IP addresses. A separate local comparison checked the selected public files against available private credential values without printing those values.

Pattern checks are not a guarantee that every possible secret format is recognized. The primary control is the small allowlist plus content review, not `.gitignore`. No images or binary documents are included, so there are no hidden image/document metadata fields to carry over.

No new Git repository was initialized during preparation. There is no copied index or history to clean. Publication and any new commit remain owner-controlled.
