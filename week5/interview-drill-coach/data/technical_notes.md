# REST
REST is an architectural style rather than a synonym for HTTP verbs. Useful constraints include client-server separation, statelessness, cacheability, a uniform interface and layered systems. HTTP methods are one implementation detail of the uniform interface.

# WebSockets
WebSockets provide a persistent, full-duplex connection after the initial HTTP upgrade. Unlike repeated request-response polling, the server can push updates to connected clients. Implementations must manage connection lifecycle, authentication, concurrent clients, broadcasting and disconnect handling.

# Async SQLAlchemy
Repositories encapsulate data-access operations and should not own the transaction boundary. A Unit of Work manages the session and coordinates commit or rollback across operations. Async sessions must be scoped carefully and closed reliably.

# Testing
Unit tests isolate a component, while integration tests exercise multiple components and their boundaries. FastAPI TestClient can test HTTP routes; WebSocket tests verify connection, authentication, message shape and disconnect behaviour.

# Behavioural answers
STAR answers should clearly distinguish Situation, Task, Action and Result. The Result should explain the outcome, evidence of impact and what was learned rather than ending after implementation details.
