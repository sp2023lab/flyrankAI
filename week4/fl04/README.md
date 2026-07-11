# FL-04: Source-Grounded Technical Interview Notes Workflow

## Purpose

This workflow turns official technical documentation into structured,
source-grounded study notes for graduate software engineering interviews.

The workflow is designed to reduce the time required to research, draft,
review and format technical notes while keeping human review in the process.

## Tools Used

- NotebookLM for source-grounded research and synthesis
- Claude Project for drafting, critique and revision
- Markdown files for recording each run and its outputs
- GitHub for storing the workflow evidence

## Workflow Diagram

```text
Technical topic
      |
      v
1. Gather official sources in NotebookLM
      |
      | Handoff: source-grounded research notes
      v
2. Synthesise the research in NotebookLM
      |
      | Handoff: structured evidence pack
      v
3. Draft interview notes in Claude Project
      |
      | Handoff: first draft
      v
4. Critique the draft in Claude Project
      |
      | Handoff: numbered issues and corrections
      v
5. Revise and format the final notes
      |
      | Handoff: final Markdown document
      v
6. Human review and approval

## Timing Summary

| Run | Topic | Recorded execution time |
|---|---|---:|
| Run 1 | FastAPI | Not calculable |
| Run 2 | Redis | 45 minutes |
| Run 3 | Docker Compose | Not calculable |
| Run 4 | RESTful APIs | Not calculable |
| Run 5 | WebSockets | Not calculable |

Initial workflow setup cost: approximately 45 minutes.

Only Run 2 was timed completely. Other runs are marked as not calculable
because exact stage timings were not recorded. No timings were reconstructed
retrospectively.