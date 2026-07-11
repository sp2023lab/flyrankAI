# Docker Compose — Graduate Software Engineering Interview Study Notes

## 1. Definition

Docker Compose is a tool for defining and running multi-container applications. It implements the Compose Specification, which is the current recommended Compose file format.

## 2. Why Docker Compose Is Used

Docker Compose simplifies management of an application stack by describing services, networks, volumes, and related configuration in a single YAML Compose file. The same application model can support development, testing, staging, CI, and other environments, although environment-specific configuration and review may still be required.

## 3. How It Works

- Developers describe an application in a `compose.yaml` file.
- The Compose CLI reads the file and creates the required containers, networks, and volumes.
- `docker compose up` builds or obtains images, creates the required resources, and starts the selected services.
- Compose provides commands for starting, stopping, recreating, inspecting, and debugging the application.
- Compose can resolve environment-variable interpolation and combine configuration from multiple files.
- `docker compose config` can be used to inspect the resolved configuration before it is applied.

## 4. Compose File Structure

Main top-level elements:

- `services`
- `networks`
- `volumes`
- `configs`
- `secrets`

The Compose Specification also supports features such as `include` for modularising configuration. **Some features depend on the installed Docker Compose version and should be verified before use.**

## 5. Services, Networks, and Volumes

### Services

A service describes a containerised application component. A service can:

- Use an image from a registry
- Build an image from a local Dockerfile and build context
- Publish host-to-container ports
- Define environment variables
- Mount volumes
- Join networks
- Define health checks
- Express dependencies on other services

### Networks

Networks provide communication channels between services. By default, Compose creates a network for the application, and containers attached to it can normally discover one another using service names as hostnames (e.g., a web service reaching Redis via the hostname `redis` rather than `localhost`). Custom networks can be declared when an application needs more explicit network separation or configuration.

### Volumes

Volumes store data outside a container's temporary writable layer. Named volumes are managed by Docker and can remain available when containers are removed and recreated.

- A plain `docker compose down` removes containers and networks but **does not** remove named volumes by default.
- `docker compose down -v` **does** remove named volumes — this can cause permanent data loss.
- A named volume provides persistent storage, but persistence alone is **not** a complete backup strategy; backup and recovery requirements must be designed separately.

### Startup Order vs. Readiness (important distinction)

Compose can start services according to dependencies expressed through `depends_on`. **Starting a dependency first does not mean it is ready to accept connections.** A health check can test whether a service is actually operating correctly, and a dependency configured with `condition: service_healthy` can make a dependent service wait until the health check succeeds. The exact behaviour should be checked against the current Compose file reference and installed Compose version.

## 6. Common Commands

| Command | What it does |
|---|---|
| `docker compose up` | Builds or obtains images as needed, creates or recreates containers, and starts the application services. |
| `docker compose down` | Stops and removes service containers and networks. Named volumes are not removed by default. |
| `docker compose stop` | Stops existing containers without removing them. Not a long-term data-persistence strategy, since containers may later be removed or recreated. |
| `docker compose config` | Parses the configuration, resolves interpolation, and displays the resulting configuration — useful for checking configuration before starting the application. |
| `docker compose exec` | Runs a command inside an already-running service container. |
| `docker compose logs -f` | Follows and combines log output from the application's services. |

## 7. Common Use Cases

- Running a multi-container application during local development
- Starting an application together with databases, caches, or message services
- Creating consistent integration-test or CI environments
- Using Compose Watch to synchronise development changes
- Dividing a larger application model across multiple Compose files
- Reproducing an application stack with a shared, version-controlled configuration

## 8. Practical Multi-Container Example

*This is an illustrative example from the evidence pack, not a description of a completed personal implementation.*

A Flask web application and a Redis service can be defined in one `compose.yaml` file:

- The web service can be built from a local Dockerfile.
- The Redis service can use an image from a registry.
- Both services join the application's default network.
- The Flask application connects to Redis using `redis` as the hostname and Redis's container port.
- A Redis health check can run `redis-cli ping`.
- The web service can express a dependency on Redis using:

```yaml
depends_on:
  redis:
    condition: service_healthy
```

This reduces (but does not eliminate) the risk that the web service starts before Redis is ready. A named volume can be mounted if Redis data needs to survive container recreation — whether that's needed depends on the application's requirements.

This example is illustrative rather than a complete production deployment. Security, secrets, backups, resource limits, monitoring, and failure handling would still require review.

## 9. Advantages

- Replaces multiple separate `docker run` commands with a declarative application configuration.
- Defines services, networks, and volumes together.
- Makes the application's required components easier to reproduce.
- Supports service-name-based discovery on Compose networks.
- Provides lifecycle and debugging commands through one CLI.
- Supports interpolation and multiple-file configuration.
- Supports named volumes for data that must survive container recreation.
- Supports health checks and dependency conditions for improved startup handling.

## 10. Limitations and Trade-offs

- A valid Compose file does **not** guarantee that an application is secure or production-ready.
- Service startup order is different from application readiness.
- Incorrect dependency or health-check configuration can still produce startup failures.
- Container writable-layer data is lost when the container is removed.
- Named volumes require separate backup and recovery planning.
- `docker compose down -v` can delete named-volume data.
- Environment interpolation can produce unexpected values if variables are missing or resolved from an unintended source.
- `docker compose config` should be used to inspect the final configuration.
- `.env` files can contain sensitive information and must not automatically be assumed safe for version control.
- `.dockerignore` only excludes matching files from the build context when it is configured correctly — it does not by itself protect secrets.
- Build arguments and ordinary environment variables are not appropriate mechanisms for securely passing build secrets.
- Advanced features such as `include` may require a particular Compose version.
- Behaviour can differ between development and production environments.

## 11. Common Mistakes / Misconceptions

- **"Docker Compose is the same as a Dockerfile."** A Dockerfile describes how to build an image; a Compose file describes how multiple services, networks, volumes, and related resources should run together.
- **"`depends_on` means a dependency is fully ready."** `depends_on` controls dependency order, but readiness normally requires a health check and an appropriate dependency condition (`condition: service_healthy`).
- **"`docker compose stop` provides reliable permanent persistence."** Stopping preserves the existing container, but its writable layer disappears if that container is removed.
- **"`docker compose down` always deletes named volumes."** Named volumes are not removed by default; the `-v` option requests their removal.
- **"A named volume is the same as a backup."** A volume can persist beyond a container, but backups and tested restoration procedures are separate requirements.
- **"`.env` is a secure secrets manager."** `.env` supports configuration interpolation but may expose sensitive values if handled incorrectly.
- **"`.dockerignore` guarantees secrets cannot enter an image."** It can exclude matching files from the build context, but it must be correctly configured and does not replace proper secret-management mechanisms.
- **"All services start at exactly the same time."** Compose can follow dependency order, but startup order and readiness are different concepts.
- **"A Compose file automatically makes an application portable without review."** Compose provides a reusable application model, but paths, environment values, platform requirements, secrets, and external services may still vary.

## 12. Important Terminology

- **Compose file** — The YAML file describing the application's services, networks, volumes, and related configuration.
- **Service** — A definition for an application component that runs in one or more containers.
- **Image** — A packaged filesystem and configuration used to create containers.
- **Build context** — The collection of files available to a Docker image build.
- **Network** — A communication channel that connects services.
- **Service discovery** — The ability of services on a Compose network to locate one another using service names.
- **Volume** — Docker-managed persistent storage mounted into a container.
- **Interpolation** — Substitution of variables in the Compose configuration with values from the environment or associated environment files.
- **Health check** — A command or test used to assess whether a container is operating as expected.
- **`depends_on`** — A Compose service attribute used to express dependencies and control creation or startup order.
- **Compose Watch** — A development feature that reacts to source-file changes by synchronising content or rebuilding services according to its configuration.

## 13. Natural 30–60 Second Interview Answer

"Docker Compose is a tool for defining and running multi-container applications. Instead of starting each container individually with separate `docker run` commands, you describe your services, networks, and volumes in one YAML file — typically `compose.yaml` — and Compose reads that file to create and start everything together. Services can build from a local Dockerfile or pull an image from a registry, and by default they all join a shared network where they can reach each other by service name — so a web app can talk to a Redis service just by using the hostname `redis`. Compose also supports named volumes for data that needs to survive container recreation, and health checks so a dependent service can wait until another service is actually ready, not just started. It's worth being clear that `depends_on` on its own only controls startup order — it doesn't guarantee readiness unless it's paired with a health check and `condition: service_healthy`. Compose is really valuable for local development, integration testing, and CI, since it makes an application stack reproducible. That said, a working Compose file doesn't automatically mean an application is secure or production-ready — things like secrets management, backups, and resource limits still need separate attention."

## 14. Three Likely Interview Questions with Concise Model Answers

**Q1: What's the difference between a Dockerfile and a Compose file?**
A Dockerfile describes how to build a single image. A Compose file describes how multiple services — each possibly built from its own Dockerfile or pulled as an image — should run together, along with the networks and volumes they need.

**Q2: If service B depends on service A via `depends_on`, is service A guaranteed to be ready when B starts?**
No. `depends_on` by itself only affects container startup/creation order — it doesn't confirm the dependency is ready to accept connections. To wait for actual readiness, A needs a health check, and B's dependency should use `condition: service_healthy` so B waits for A's health check to pass, not just for A's container to start.

**Q3: If you run `docker compose down`, do you lose your database data stored in a named volume?**
Not by default — a plain `docker compose down` removes containers and networks but leaves named volumes intact. Data loss happens if you run `docker compose down -v`, which explicitly removes named volumes, or if the data was only ever stored in the container's writable layer rather than a named volume.

## 15. Human-Review Checklist

Before treating any of the following as confirmed, verify independently:

- [ ] Confirm the installed Docker Compose version.
- [ ] Verify support for `include`, merge, and other advanced Compose features.
- [ ] Run `docker compose config` to inspect variable interpolation and merged configuration.
- [ ] Test health-check commands and timing against the real application.
- [ ] Confirm whether dependent services correctly use `condition: service_healthy`.
- [ ] Verify all host paths, ports, and environment values.
- [ ] Confirm that named volumes contain only data intended to persist.
- [ ] Back up important volume data before using `docker compose down -v`.
- [ ] Review secrets handling using current Docker security guidance.
- [ ] Confirm that `.env` and other secret-bearing files are excluded from version control where appropriate.
- [ ] Review Dockerfile and `.dockerignore` behaviour using the real build context.
- [ ] Test the full application on the target operating system and environment.
- [ ] Do not describe the illustrative Flask/Redis example above as a completed personal implementation unless that is genuinely accurate for you.

---
*Source references: Docker Compose overview, Docker Compose Quickstart, Docker Compose file reference.*
