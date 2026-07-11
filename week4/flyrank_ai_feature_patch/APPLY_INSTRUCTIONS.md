# Apply the FlyRank AI feature

This patch is designed for:

`flyrankAI\week4\flyrank_pdf_report_generator`

It adds:

- `POST /api/v1/summarize`
- Groq behind a provider-neutral `AIProvider.complete(...)` interface
- strict JSON Schema output and Pydantic validation
- one retry for malformed model output
- timeouts and retry/backoff for 429, 5xx, network errors and timeouts
- no retry for 400/non-transient 4xx
- token and estimated-cost logging
- mocked reliability tests
- updated README and `.env.example`
- a fix for the existing invalid `httpx2` dependency

## Apply on Windows PowerShell

Extract this ZIP. Then run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\apply_changes.ps1 -ProjectRoot "C:\Users\samsung\flyrankAI\week4\flyrank_pdf_report_generator"
```

The script overwrites only the listed implementation files. It does not modify your real `.env`.

## Add your key

Inside your project `.env`, add:

```dotenv
AI_PROVIDER=groq
GROQ_API_KEY=your_real_groq_key
GROQ_MODEL=openai/gpt-oss-20b
AI_TIMEOUT_SECONDS=20
AI_MAX_RETRIES=1
AI_RETRY_BACKOFF_SECONDS=0.5
GROQ_INPUT_COST_PER_MILLION=0.075
GROQ_OUTPUT_COST_PER_MILLION=0.30
```

Never commit `.env`.

## Rebuild and test

```powershell
cd C:\Users\samsung\flyrankAI\week4\flyrank_pdf_report_generator
docker compose down
docker compose up --build
```

In another terminal:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
pytest
```

Test the endpoint:

```powershell
$body = @{
    text = "Revenue increased by 18 percent. Refunds fell by 7 percent. Mobile orders now account for 61 percent of sales."
} | ConvertTo-Json

Invoke-RestMethod `
    -Method Post `
    -Uri "http://localhost:8000/api/v1/summarize" `
    -ContentType "application/json" `
    -Body $body
```

Expected shape:

```json
{
  "bullets": [
    "First summary point",
    "Second summary point",
    "Third summary point"
  ]
}
```
