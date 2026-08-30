# DV Knowledge Schema

## Knowledge Object

Required fields:

- id
- type
- title
- status
- content
- sources
- owner
- created_at
- updated_at

Knowledge status:

```text
confirmed
contested
superseded
obsolete
```

## Candidate

Required concepts:

- id
- type
- title
- status
- proposed_knowledge
- evidence
- reasoning
- conflicts, when applicable
- created_at

Candidate status:

```text
candidate
contested
needs-review
```

## Types

```text
behavior
corner-case
limitation
known-issue
designer-qa
debug
dv-knowledge
```

## Evidence

Each evidence entry contains:

```yaml
type: spec
ref: SPEC-v3.2
```

Supported evidence types:

```text
spec
designer-qa
jira
debug
dv-experience
session
```

Optional evidence metadata:

```text
version
date
author
location
```

Evidence is not the same thing as interpretation or Knowledge.
