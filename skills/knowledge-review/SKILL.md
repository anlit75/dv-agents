---
name: knowledge-review
description: Helps the human owner review, edit, accept, or reject pending DV Knowledge Candidates. Use this skill when the user wants to review new knowledge or when the knowledge-learning plugin notifies about pending candidates.
version: 0.1.0
---

# Knowledge Review Skill

## Purpose

This skill allows the human DV engineer to review pending Knowledge Candidates in `$PWD/.knowledge/candidates/`.

For each candidate, the user can:
- **Accept**: Move it to `$PWD/.knowledge/knowledge/` and update its status to `confirmed`.
- **Edit**: Modify the contents, then move it to `knowledge/` if accepted.
- **Reject**: Delete the candidate or mark it as `rejected`.
- **Request More Evidence**: Keep it in `candidates/` but add notes.

## Workflow

1. List all Markdown files in `$PWD/.knowledge/candidates/`.
2. If there are no candidates, inform the user that the queue is empty.
3. For each candidate:
   - Read and present the candidate's proposed knowledge, evidence, and interpretation.
   - Ask the user for their decision (Accept, Edit, Reject, Skip).
   - If **Accept**:
     - Change `status: candidate` to `status: confirmed` in the YAML frontmatter.
     - Move the file to `$PWD/.knowledge/knowledge/<filename>.md` (or categorize into subfolders like `behavior/`, `corner-case/`, etc. based on its type).
     - Remove the original from `candidates/`.
   - If **Edit**:
     - Ask the user what needs to be changed.
     - Update the candidate.
     - Loop back to asking for a decision.
   - If **Reject**:
     - Delete the candidate file from `$PWD/.knowledge/candidates/`.
   - If **Skip**:
     - Leave it in the queue for later.

## Hard Constraints

- **Do NOT** read or access RTL.
- **Do NOT** automatically accept candidates without human confirmation.
- Ensure the original `sources` block in the YAML frontmatter is preserved when moving to `knowledge/`.
- Ensure the `owner` field is filled with the current user's name or identity when accepting.
