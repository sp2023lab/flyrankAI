# FL-07 Build Log — Interview Drill Coach

This log was started before the MVP was considered complete. Entries describe the actual implementation and test sequence rather than a polished retrospective.

## Entry 1 — Scope and first implementation

**Date:** 1 August 2026  
**Goal:** Implement the narrowest FL-06 workflow as a two-question command-line session.  
**Attempted:** Created Pydantic models, local Markdown note retrieval, JSON progress persistence, a provider interface and a CLI loop.  
**Decision/cut:** Chose keyword retrieval instead of embeddings and JSON instead of SQLite. The corpus is small, and these choices reduce installation and debugging time while preserving the four tool responsibilities from FL-06.  
**Result:** Initial code and tests were created. The live provider was isolated behind an interface so the workflow could be tested without API calls.

## Entry 2 — Progress-file failure discovered by test

**Date:** 1 August 2026  
**Goal:** Make local persistence safe enough for repeated demonstrations.  
**What broke:** A test using a malformed `progress.json` failed because `_read()` called `json.loads()` directly and raised `JSONDecodeError`. This could prevent the agent from starting after an interrupted or manually damaged file.  
**Change:** Pending after the first test run: add recovery that backs up the corrupt file and reinitialises a valid empty store.  
**Reason:** The agent should fail safely and preserve the broken file for inspection rather than silently destroying it.

## Entry 3 — To be completed after test rerun

Record the exact test result, any prompt/provider issue, and the final end-to-end mock run here after running the project.

## Entry 3 — Retrieval chunking failure discovered and fixed

**Date:** 1 August 2026  
**Goal:** Verify that the live file tool can retrieve project evidence from ordinary Markdown formatting.  
**What broke:** The first test run returned no match when a heading and its body were separated by a single newline rather than a blank line. The original chunker treated the entire block as a heading and discarded the body.  
**Change:** Replaced block-only parsing with a line-aware Markdown chunker that carries the nearest heading into each paragraph.  
**Result sought:** The WebSocket query should now retrieve the corresponding project excerpt regardless of whether the Markdown author inserted a blank line after the heading.

## Entry 4 — Corrupt progress recovery implemented

**Date:** 1 August 2026  
**Goal:** Resolve the persistence failure from Entry 2.  
**Change:** Added guarded JSON/Pydantic loading. A malformed progress file is renamed with a `.corrupt` suffix and a new empty store is written atomically.  
**Trade-off:** Recovery prevents startup failure, but the agent does not automatically reconstruct an interrupted session from the backup.

## Entry 5 — Tests and end-to-end run

**Date:** 1 August 2026  
**Test result after fixes:** `5 passed`. The retrieval, read-only file boundary, progress lifecycle, corrupt-file recovery and complete two-question agent loop all passed.  
**End-to-end run:** Ran the CLI with the deterministic setup provider and a temporary progress file. The terminal showed progress retrieval, local note search, two questions, immediate result saving, correct termination and a final report.  
**Observed limitation:** The first retrieval query returned the highest lexical matches rather than a semantic match. This is acceptable for the MVP corpus but remains documented as a known limitation.  
**Live-run dependency:** The OpenAI provider follows the Responses API structured-output pattern and requires the user's `OPENAI_API_KEY`; it could not be called in the build environment because no user API credential was supplied.  
**Final cut:** Kept FastAPI, a graphical interface, vector embeddings, voice and multi-agent orchestration out of FL-07. They do not improve the checkpoint's core evidence: one complete loop with a live file/data connection.

## Entry 5 — Optional dependency blocked the setup run

**Date:** 1 August 2026  
**Goal:** Run the complete CLI with the deterministic provider before using a paid API.  
**What broke:** `app.main` imported the OpenAI provider at module load time. The setup environment did not have the `openai` package installed, so even `--provider mock` failed before the provider could be selected.  
**Change:** Moved the OpenAI-provider import into the live-provider branch. The local/mock workflow can now run with only Pydantic and dotenv, while `requirements.txt` still installs OpenAI for the final live run.  
**Reason:** Optional integrations should not prevent testing the core loop.

## Entry 6 — Passing checkpoint and final MVP state

**Date:** 1 August 2026  
**Automated result:** `5 passed`.  
**End-to-end result:** The two-question CLI completed without mid-run editing. It read progress, searched local files, generated grounded questions, evaluated both answers, saved both results, generated the final report and terminated cleanly. A transcript is stored in `sample_run.txt`.  
**Observed limitation:** Keyword retrieval is transparent and reliable for the small corpus but can miss semantic matches with no shared vocabulary. This remains a documented post-MVP improvement.  
**Live-run dependency:** The OpenAI structured-output provider requires the user's API key and a model available to that API project. The final raw capture must therefore be recorded locally after `.env` is configured.  
**Final scope:** The FL-06 single-agent design is preserved. FastAPI/UI, embeddings, voice, analytics and multiple agents remain deliberately deferred.
