# Generic demonstration policy

This is a newly written explanation of the agent boundary, not a copied personal prompt. It is not executed by the offline runner.

An example agent consuming a daily data packet should distinguish supplied observations, unavailable values and estimates. It should use the packet's report date, quote numerical results consistently and avoid interpreting incomplete records as a complete day.

Calculations belong in deterministic code. Personal targets and exercise prescriptions require a separately configured policy and appropriate evidence; they are not supplied in this public edition. Missing information should remain missing rather than being inferred from an unrelated day.

A model may explain a validated packet, but a model response alone is not proof that state was saved. The system should only claim a successful write after the persistence operation succeeds.

The public renderer demonstrates this boundary with fixed text and no tools or LLM calls. It does not evaluate whether a hosted model follows these instructions.
