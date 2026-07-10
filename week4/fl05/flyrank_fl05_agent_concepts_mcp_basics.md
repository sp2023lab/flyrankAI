# FL-05: Agent Concepts and MCP Basics

## Explainer

An AI workflow is a system where the route through the task is mostly decided in advance by the developer. The model may still generate text, classify something, or call a tool, but the surrounding code controls the sequence. For example, a pipeline might take an input, clean it, send it to an LLM, validate the output, save the result, and return a response. The important point is that the model is not deciding the overall process. It is one component inside a designed path.

An agent is different because the model has more control over how the task is completed. Instead of only filling in one step, it can decide what to do next, which tool to use, whether it needs more information, whether the result is good enough, and when to stop. That does not mean an agent is magic or fully independent. A useful agent still needs boundaries, tools, logging, permissions, and evaluation. The difference is that the control loop is more model-directed than code-directed.

My FL-04 pipeline is currently a workflow, not a full agent. The pipeline has a clear build path: API request, backend logic, optional model/tool step, validation, and response. Even if an LLM is involved, the steps are predetermined. The system does not independently inspect the task, choose between multiple tools, plan a route, recover from failure, or ask for more context. It behaves more like a reliable backend pipeline than an autonomous assistant. That is a good thing for the current stage because predictable workflows are easier to test, debug, and explain.

MCP stands for Model Context Protocol. I understand it as a standard way for an AI application to connect to external systems. Without MCP, every AI app and every external service needs its own custom integration. With MCP, a client such as Claude can connect to an MCP server that exposes useful capabilities in a predictable format. This is why MCP is often described like a USB-C port for AI applications: it gives AI systems a common connection pattern for data, tools, and workflows.

The three MCP primitives are tools, resources, and prompts. Tools are actions the model can invoke, such as reading a file, querying a database, searching a service, or calling an API. Resources are data or content exposed by the server, such as local files, logs, documents, database rows, images, or API responses. Prompts are reusable prompt templates or guided workflows that a server can surface to the user or client. In simple terms: tools let the AI do things, resources let it read context, and prompts give it reusable instructions.

For my MCP setup, I used a filesystem connector/server pointed at my `flyrankAI` project folder. This lets Claude inspect local project files rather than relying only on what I paste into chat. The three tasks I would use as evidence are: first, asking Claude to list the files inside `week3/general2` and identify the generated SVG/Markdown assets; second, asking Claude to read the image curation Markdown file and summarise the final image set; third, asking Claude to create or update an evidence note inside the Week 4 folder. Plain chat could not do those tasks alone because it cannot access my local filesystem or write files without a connector.

To turn my FL-04 workflow into an agent, I would add a model-directed planning and recovery loop. Instead of always following one fixed path, the system would inspect the user request, choose between available tools, run the selected step, validate the result, and decide whether to retry, ask for clarification, or finish. For example, an agentic version of my pipeline could choose between reading project files, checking API output, running tests, or generating a summary depending on the task. A validation step would still be required so that the model cannot silently return malformed or low-quality output.

The concrete upgrade I would make is an evaluator-optimizer loop. The first model call would produce the output, then a second evaluation step would check it against criteria such as schema validity, relevance, completeness, and evidence quality. If the output failed, the system would feed the failure reason back into another attempt. This would make the pipeline more agent-like because the system would not just run once and stop; it would use feedback to decide whether another action is needed. However, I would still keep strong guardrails: limited tools, clear permissions, structured outputs, and logs. The goal is not to make the system look impressive, but to make it more reliable on tasks where a fixed workflow is too rigid.

## Evidence plan for screenshots

1. Screenshot 1: Claude/your MCP client listing files from `C:\Users\samsung\flyrankAI\week3\general2`.
2. Screenshot 2: Claude/your MCP client reading `flyrank_week3_curate_images.md` and summarising the image set.
3. Screenshot 3: Claude/your MCP client creating or updating `week4\fl05\mcp_evidence_notes.md`.

## Suggested MCP task prompts

### Task 1

List the files in my local project folder `week3/general2`. Identify which files are SVG assets and which file is the Markdown submission.

### Task 2

Read `week3/general2/flyrank_week3_curate_images.md` from my local project. Summarise the final image set and explain where I chose real captures over AI-generated images.

### Task 3

Create a new file at `week4/fl05/mcp_evidence_notes.md` summarising the three MCP tasks I ran and why plain chat could not have done them.