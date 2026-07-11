# FL-04 Workflow Prompts

## Prompt 1 — Gather Source-Grounded Research

```text
Using only the sources in this notebook, gather the most important information
about FastAPI for a graduate software engineering interview.

Extract:

- A precise definition
- The main purpose
- How it works
- Important components
- Advantages
- Limitations and trade-offs
- Common mistakes
- One practical example
- Important terminology
- Statements that require extra caution or human verification

Keep the output source-grounded and include citations to the notebook sources.
Do not add information that is not supported by the supplied sources.
```

## Prompt 2 — Synthesise into an Evidence Pack

```text
Turn the FastAPI research above into a structured evidence pack for another AI
tool.

Use this exact format:

Topic:
Definition:
Purpose:
How it works:
Key components:
Advantages:
Limitations:
Practical example:
Common misconceptions:
Important terminology:
Claims requiring human review:
Source references:

Remove repetition, but preserve important technical detail.

Use only information supported by the selected NotebookLM sources. Keep the
source citations in the response.
```

## Prompt 3 — Create the First Draft

```text
Create graduate software engineering interview study notes using the evidence
pack below.

Use only claims supported by the evidence pack. Clearly flag anything that
still requires human verification.

Include:

- Definition
- Why it is used
- How it works
- Practical example
- Advantages
- Limitations and trade-offs
- Common mistakes or misconceptions
- A 30-to-60-second spoken interview answer
- Three likely interview questions with model answers
- A human-review checklist

Relate examples to my experience only when the evidence supports doing so.

Evidence pack:

[PASTE THE FASTAPI SYNTHESISED EVIDENCE PACK HERE]
```

## Prompt 4 — Critique the First Draft

```text
Critique the FastAPI study notes as if you were a technical interviewer.

Use the original evidence pack as the factual boundary.

Check for:

- Unsupported technical claims
- Incorrect or vague terminology
- Claims that are too absolute
- Missing limitations or trade-offs
- Explanations that sound memorised rather than understood
- Examples that exaggerate my experience
- Material that is too advanced or too basic for a graduate interview
- Statements requiring human verification
- Interview answers that would be difficult to say naturally

Return a numbered list containing:

1. The issue
2. Why it is a problem
3. The recommended correction

Do not rewrite the study notes yet.
```