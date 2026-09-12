# Contribution and provenance

Project owner: Daniil Serhieiev.

FitnesHermes is a personal application assembled on an existing AI agent framework. Its project-specific scope is the coaching workflow, organization of context and history, specialized data handling, and operation of the personal assistant. These are descriptions of the project scope, not a claim of unaided authorship of every component.

## What this edition includes

| File or group | Origin | Public preparation |
|---|---|---|
| `scripts/fatsecret_parse.py` | Existing nutrition parser in the working deployment | Copied by explicit selection; one explanatory comment translated; no private data copied |
| `scripts/run_demo.py` | New AI-assisted public demonstration | Reimplements selected coordination, calculation and journal concepts for invented inputs; not the production orchestrator |
| `tests/` and `scripts/check_public.py` | New AI-assisted public verification | Exercises the public artifacts; does not claim coverage of the private agent |
| `examples/` | Created from scratch for this edition | No transformation or renaming of personal records |
| Documentation | Written from source inspection and previously checked runtime facts | Personal details, historical audits and operational identifiers excluded |
| `licenses/HERMES-MIT.txt` | Existing upstream license | Preserved verbatim with Nous Research attribution |

The standalone deployment parser has no embedded author or license header. Its presence in the working project is established; a line-by-line manual authorship claim is not. This edition does not attach an inferred third-party license to it.

## Third-party work

Nous Research Hermes supplies the agent runtime, gateway, tool infrastructure and session system. Hosted model providers supply the models. Garmin and FatSecret supply the external data systems used by the personal deployment. Their products and integrations are not represented as original creations of this project owner.

## How AI assistance is represented

AI assistants supported implementation and documentation, including preparation of this public edition. The runnable demo and tests are AI-assisted engineering artifacts. They are not evidence that the owner personally typed all code or trained a model.

The portfolio evidence a reader can inspect is the working data flow, explicit boundaries, reproducible outputs and failure cases. Statements about personal decision-making or unaided coding should be made by the owner in their own words, supported by examples they can explain.
