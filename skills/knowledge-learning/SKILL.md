---
name: knowledge-learning
description: Automatically extracts durable, reusable Design Verification (DV) knowledge from completed sessions and proposes them as Knowledge Candidates for human review. Make sure to use this skill whenever a session goes idle or the user finishes a DV task, or when the user mentions saving knowledge, extracting insights, or updating the shared knowledge base. This skill creates candidates for DUT behavior, corner cases, limitations, and Designer Q&A while strictly prohibiting RTL access.
version: 0.1.0
---

# Knowledge Learning Skill

## Purpose

Maintain the shared DV Knowledge repository for the current working directory.

The Knowledge repository is:

    $PWD/.knowledge/

The current working directory defines the Knowledge scope.

Do not infer or create additional project, DUT, block, or hierarchy scopes.

The goal is to identify durable knowledge that can improve future DV work,
preserve evidence, detect duplicates and contradictions, and propose updates
for human review.

## Hard Constraints

### RTL is forbidden

The agent MUST NOT:

- read RTL files
- search RTL files
- use RTL as evidence
- infer DUT behavior from RTL
- reference RTL-derived conclusions as Knowledge

If understanding a question requires RTL inspection, state that the required
information is unavailable under the DV Agent access policy.

### Knowledge scope

Only use:

    $PWD/.knowledge/

Do not automatically search parent directories, sibling directories, other
DUTs, or other projects.

### Human ownership

AI may create and modify Candidates.

AI MUST NOT silently convert a Candidate into confirmed Knowledge.

A human owner must review and accept a Candidate before it becomes confirmed
Knowledge.

### Evidence preservation

Original sources must be preserved. AI-generated summaries must not replace
original evidence.

### Avoid noise

Do not create Knowledge for temporary conversation context, trivial
observations, one-off commands, unsupported speculation, or information that
is unlikely to help future DV work.

## Repository Structure

```text
.knowledge/
├── knowledge/
├── sources/
└── candidates/
```

### knowledge/

Confirmed Knowledge usable by DV Skills.

Suggested categories:

```text
behavior/
corner-case/
limitation/
known-issue/
designer-qa/
debug/
dv-knowledge/
```

### sources/

Original evidence such as:

```text
spec/
designer-qa/
jira/
debug/
session/
```

Sources are evidence, not Knowledge.

### candidates/

AI-generated Knowledge Candidates. Candidates require human review before
promotion to `knowledge/`.

## Automatic Session Learning

When invoked after a session, analyze the session for durable Knowledge.

Look especially for:

- Designer clarification of ambiguous or incorrect specification text
- hidden corner cases
- DUT limitations
- known issues
- reusable debug findings
- reusable DV experience
- facts that would materially help another DV engineer

Before creating a Candidate:

1. Search relevant existing Knowledge.
2. Check for duplicates.
3. Check for contradictions.
4. Identify supporting evidence.
5. Decide whether the information is durable and reusable.

If useful Knowledge exists, create a Candidate rather than silently modifying
confirmed Knowledge.

## Evidence Types

Supported evidence types:

```text
spec
designer-qa
jira
debug
dv-experience
session
```

Do not invent evidence.

Clearly distinguish:

```text
Evidence
Interpretation
Proposed Knowledge
```

## Conflict Handling

If new evidence conflicts with existing Knowledge, do not silently overwrite
existing Knowledge.

Create a Candidate describing:

- existing claim
- new claim
- evidence for each
- nature of the conflict
- what requires human clarification

## Knowledge Quality

Before creating a Candidate, ask:

> Would another DV engineer benefit from knowing this in a future task?

If not, do nothing.

Prefer fewer, high-quality Knowledge objects over a large amount of noise.
