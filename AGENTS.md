# Agent entry point

This repository is worked on by multiple AI coding agents that don't share memory with each
other. Before writing any code, read and follow **[`.ai/BOOTSTRAP.md`](.ai/BOOTSTRAP.md)** in
full.

That procedure will have you read `.ai/PROJECT.md`, `.ai/STATE.md`, `.ai/TASKS.md`, and
`.ai/ARCHITECTURE.md`, check `.ai/FILE_INDEX.md` before creating anything, and produce a short
plan before you start. It also tells you when to stop and ask instead of guessing.

Before ending your session, run **[`.ai/SHUTDOWN.md`](.ai/SHUTDOWN.md)** in full — it updates
task status, the file index, the changelog, and writes a session record so the next agent (in
any tool) can pick up exactly where you left off.

Hard constraints that apply regardless of task: **[`.ai/RULES.md`](.ai/RULES.md)**.

Everything else — task board, architecture decisions, API/schema registries, decision log,
prompt history, session log — lives under [`.ai/`](.ai/README.md).
