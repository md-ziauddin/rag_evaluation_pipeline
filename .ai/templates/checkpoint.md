<!--
Template for .ai/checkpoints/<milestone-or-tag>-<date>.md

Checkpoints are heavier than STATE.md: a full snapshot taken at a milestone boundary (or before
a risky change), useful for rollback context or for an agent that needs the complete picture at
a specific point in time rather than just "now." Not created every session — only at milestone
completion, or before a change significant enough that "what did the project look like right
before this" is worth preserving on its own.
-->

# Checkpoint: <milestone or tag> — YYYY-MM-DD

**Trigger:** <why this checkpoint exists — milestone completion, pre-risky-change snapshot, etc.>

## Project state at this point

<Copy the relevant parts of STATE.md's milestone table and TASKS.md's epic table as they stood
at this moment — this is a snapshot, so it should read correctly even after STATE.md and
TASKS.md have both moved on.>

## What existed

<A condensed FILE_INDEX.md view — what was implemented, what was still scaffold, as of this
checkpoint.>

## What was verified working

<Concretely: what commands were run, what tests passed, what was manually confirmed.>

## Known issues / deferred work at this point

<Anything left open, so a future rollback to this checkpoint knows what it's rolling back to.>

## Git reference

**Commit:** <SHA, if committed at this point>
