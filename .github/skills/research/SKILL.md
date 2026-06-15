---
name: research
description: "Investigate a focused question about this codebase or its libraries and return a cited, structured brief. Read-only. Good as a one-off or as the research step of a workflow."
argument-hint: "the question + desired depth (quick | medium | thorough)"
context: fork
user-invocable: true
disable-model-invocation: false
---

# Research a question

Forked: the investigation runs in its own context and returns only the brief, so
the caller's context stays clean.

1. Restate the question in one line; confirm depth (default medium).
2. Gather evidence: search and read the relevant files; use the web for library
   or framework docs. Stop once findings overlap across sources.
3. Return this structure:
   - **Question** - one line.
   - **Findings** - each a fact with a citation: a workspace path (with line
     numbers) or a URL.
   - **Recommendation** - 1-3 sentences, marked as a recommendation, not a
     decision.
   - **Open questions** - anything unresolved.

Cite every non-trivial claim. Say "the codebase doesn't show this" rather than
guess. Do not edit anything.
