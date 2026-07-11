# FastAPI Interview Study Notes

## Definition

FastAPI is a modern, high-performance Python web framework used to build APIs. It is based on standard Python type hints and uses **Starlette** for its underlying web functionality and **Pydantic** for data validation and schema generation.

## Why It Is Used

FastAPI is designed to help developers build robust, standards-based APIs efficiently. It reduces repetitive development work by using Python type hints to provide request validation, response serialization, editor support, and automatically generated API documentation.

## How It Works

- Developers associate Python functions with URL paths and HTTP methods using **path operation decorators** (e.g. `@app.get()`, `@app.post()`).
- Parameters and request models are declared using standard Python type hints.
- **Pydantic** validates incoming data and converts it into the expected Python types.
- FastAPI generates an **OpenAPI** schema from the application structure.
- **Swagger UI** and **ReDoc** use the OpenAPI schema to provide interactive API documentation.
- Functions declared with `async def` can use `await` for asynchronous I/O operations.
- Normal `def` path operation functions are executed in an external **thread pool** so that blocking code does not directly block the main event loop.

> ⚠️ **Human review flag:** The exact behaviour of synchronous `def` routes, thread pools, and asynchronous dependencies should be verified against current FastAPI documentation before being presented as a fully detailed technical explanation.

**Key components:**

| Component | Role |
|---|---|
| Starlette | Routing, WebSockets, middleware, background tasks, application lifecycle events |
| Pydantic | Validation, serialization, schema generation from type annotations |
| Dependency injection | Resolves dependencies/sub-dependencies (auth, DB sessions, shared logic) |
| OpenAPI | Describes API structure, parameters, response schemas, security requirements |
| Path operation functions | Python functions tied to a URL path and HTTP method |
| Swagger UI / ReDoc | Auto-generated interactive documentation |

## Practical Example

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float


@app.post("/items")
async def create_item(item: Item):
    return item
```

Here, the `Item` Pydantic model defines and validates the expected request body shape, and the `@app.post("/items")` decorator registers the path operation. FastAPI uses this to validate incoming JSON, convert it into an `Item` instance, and generate OpenAPI documentation automatically.

> ⚠️ **Human review flag:** This example is illustrative only, drawn from the evidence pack. It should not be presented as personal project experience in an interview unless independently confirmed as work you have actually done.

## Advantages

- Standard Python type hints are reused for validation, documentation, and editor support.
- Automatic interactive API documentation reduces the need to manually maintain separate docs.
- Supports asynchronous I/O using `async`/`await`.
- Pydantic provides structured request validation and clear validation errors.
- Dependency injection supports modular, reusable application architecture.
- Strong autocompletion and type-checking support in development environments.
- Suitable for building standards-based REST APIs and other HTTP services.

## Limitations and Trade-offs

- Asynchronous programming does **not** automatically improve CPU-bound workloads.
- CPU-intensive work may require multiprocessing, task queues, or separate worker services.
- Blocking libraries used inside async routes reduce the benefits of asynchronous execution.
- Developers must understand when to use `def`, `async def`, and `await` correctly.
- Incorrectly calling blocking operations inside an async route can block the event loop.
- Performance comparisons with other languages or frameworks depend on workload, implementation, and deployment environment — specific benchmark claims should be treated with caution and verified independently.
- FastAPI's abstractions can hide lower-level behaviour; diagnosing complex issues may still require understanding Starlette, Pydantic, and asynchronous Python internals.

## Important Terminology

- **API:** An interface that allows different software systems to communicate.
- **Path operation:** A combination of a URL path, an HTTP method, and the Python function that handles the request.
- **Path operation decorator:** A decorator such as `@app.get()` or `@app.post()` that connects a function to a route and HTTP method.
- **Type hint:** A Python annotation describing the expected type of a variable, parameter, or return value.
- **Pydantic model:** A Python class used to define, validate, and serialize structured data.
- **Coroutine:** An asynchronous operation that can be paused while waiting and resumed later.
- **Event loop:** The mechanism that schedules and manages asynchronous tasks.
- **I/O-bound task:** Work that spends much of its time waiting for databases, networks, files, or external services.
- **CPU-bound task:** Work dominated by calculations or intensive processor usage.
- **Thread pool:** A group of worker threads that can execute synchronous blocking functions without directly blocking the main event loop.
- **Dependency injection:** A system that provides functions with required dependencies, such as authentication logic, services, or database sessions.
- **OpenAPI:** A standard specification used to describe the structure and behaviour of an HTTP API.

## Common Mistakes and Misconceptions

| Misconception | Reality |
|---|---|
| `async def` automatically makes an endpoint faster | Async is mainly beneficial when the app is waiting on I/O (database, network, files) |
| FastAPI makes blocking libraries non-blocking | FastAPI cannot convert blocking calls into non-blocking ones; blocking code inside an async route can still block the event loop |
| Every route should use `async def` | Plain `def` is appropriate for synchronous/blocking libraries; FastAPI runs these in a thread pool |
| Type hints alone perform validation | Type hints describe expected types; Pydantic performs the actual runtime validation, conversion, and schema generation |
| Auto-generated docs remove the need for manual documentation | Swagger UI and ReDoc describe routes and schemas, but business rules, authentication requirements, and expected behaviour still need to be documented manually — this reduces manual documentation effort, it does not eliminate it |
| FastAPI guarantees high performance for every app | Performance also depends on database access, external services, architecture, deployment configuration, and code quality |
| Async improves CPU-bound tasks | CPU-bound work typically needs multiprocessing, background workers, task queues, or separate services instead |

## 30-to-60-Second Interview Answer

> ⚠️ **Note:** The following is a template explanation of the technology, not a claim about personal project experience, unless independently confirmed.

"FastAPI is a Python framework for building APIs. It's built on Starlette for the web layer and Pydantic for data validation. You define endpoints with decorators like `@app.post()`, and use standard Python type hints to describe the request and response data — Pydantic handles the validation and conversion automatically. It also generates an OpenAPI schema from your code, which powers interactive docs through Swagger UI and ReDoc. FastAPI supports async routes for I/O-bound work, like waiting on a database or network call, while regular `def` routes run in a thread pool instead. One thing worth knowing is that async doesn't help with CPU-bound work — that usually needs a different approach, like background workers."

## Likely Interview Questions

**Q1: What's the difference between using `def` and `async def` for a path operation in FastAPI?**
A: A plain `def` function is run by FastAPI in a thread pool, so blocking code doesn't tie up the main event loop. An `async def` function runs directly on the event loop and is useful when you can `await` I/O-bound work, such as a database query or a network call. The right choice depends on whether the code you're calling supports asynchronous execution.

**Q2: How does FastAPI generate its interactive API documentation?**
A: FastAPI builds an OpenAPI schema from the application's path operations, type-hinted parameters, and Pydantic models. Swagger UI and ReDoc then read that schema to render interactive documentation. This reduces how much documentation you need to write by hand, though things like business rules and authentication behaviour still need to be documented separately.

**Q3: Does using `async def` in FastAPI automatically make an application faster?**
A: Not on its own. Async mainly helps with I/O-bound work, where the app spends time waiting on something external, like a database or API call. For CPU-bound work, async provides no inherent benefit, and that kind of workload typically needs a different approach, such as multiprocessing or background task queues. Separately, it's worth noting that a blocking call placed inside an async route can still block the event loop, which is a related but distinct risk.

## Human Review Checklist

- [ ] Any claim that FastAPI performs at the same level as Node.js or Go is appropriately qualified — benchmarks depend on workload, server, configuration, and implementation.
- [ ] Any specific test-coverage percentage claim is checked against the current official repository or documentation (none is asserted in these notes).
- [ ] Supported Python, FastAPI, and Pydantic versions are confirmed against current release documentation.
- [ ] The exact behaviour of synchronous `def` routes, thread pools, and async dependencies is verified before giving a detailed technical explanation.
- [ ] The code example has been tested and is not described as "production-ready" without verification.
- [ ] Security, authentication, database, and deployment claims are separately verified — they are not covered by the underlying evidence pack.
- [ ] Any personal or project example used in the interview reflects features you have genuinely implemented — do not overstate personal experience.
- [ ] The spoken interview answer and model answers have been rehearsed aloud so they sound natural rather than memorised.
- [ ] Timing of the spoken answer has been checked aloud against a clock to confirm it fits the 30–60 second target.
