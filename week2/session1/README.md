# FlyRank Backend AI Engineering - BE-04

## Containerize Your Stack

This project completes the FlyRank **BE-04** assignment by containerizing a FastAPI backend with PostgreSQL using Docker Compose. The previous in-memory repository has been replaced with a PostgreSQL repository while keeping the service and route layers unchanged.

---

# Technologies

- Python 3.12
- FastAPI
- PostgreSQL
- Docker
- Docker Compose
- psycopg3
- Pydantic

---

# Project Structure

```
week2/session1/
│
├── app/
│   ├── repositories/
│   │   ├── interface.py
│   │   ├── memory_repository.py
│   │   └── postgres_repository.py
│   ├── dependencies.py
│   ├── main.py
│   ├── models.py
│   ├── routes.py
│   └── service.py
│
├── db/
│   └── init.sql
│
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# Architecture

The project follows a layered architecture:

```
Routes
   ↓
Service
   ↓
Repository Interface
   ↓
Postgres Repository
```

The service layer communicates only with the repository interface.

For this assignment, the **only architectural change** required was swapping the repository implementation from the previous in-memory repository to the PostgreSQL repository.

No changes were made to the API routes or service logic.

---

# Environment Variables

Create a `.env` file from `.env.example`.

Example:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=flyrank_be04
DATABASE_URL=postgresql://postgres:postgres@db:5432/flyrank_be04
```

---

# Running the Project

Start the application and database:

```bash
docker compose up --build
```

The API will be available at:

```
http://localhost:8000
```

Swagger documentation:

```
http://localhost:8000/docs
```

---

# API Endpoints

## Health Check

```
GET /health
```

---

## Create Item

```
POST /items
```

---

## List Items

```
GET /items
```

---

## Get Item

```
GET /items/{id}
```

---

## Update Item

```
PATCH /items/{id}
```

---

## Delete Item

```
DELETE /items/{id}
```

---

# Database

The PostgreSQL database is started using Docker Compose.

A Docker volume is used to persist data between container restarts.

The database schema is created automatically from:

```
db/init.sql
```

---

# Persistence

The project is configured so that PostgreSQL data is stored within a Docker volume, allowing data to persist across container restarts.

The intended verification process is:

1. Start the application with Docker Compose.
2. Create one or more records through the API.
3. Restart the application and PostgreSQL containers.
4. Retrieve the records again to verify they remain in the database.

---

# Notes

The application has been implemented according to the BE-04 architecture requirements.

- Docker Compose configuration included
- PostgreSQL repository implemented
- Environment variables stored in `.env`
- `.env.example` provided
- SQL initialization script included
- Service and routes remain unchanged from the previous architecture
- Storage implementation swapped from in-memory to PostgreSQL

At the time of writing, Docker Desktop was experiencing issues pulling public images from Docker Hub (`hello-world` and `postgres`) on the local development machine, preventing a full runtime verification. The project structure and implementation have been completed, and the intended persistence verification process is documented above.

---

# Assignment Requirements Checklist

- PostgreSQL configured with Docker
- Docker Compose configuration
- Persistent Docker volume configured
- `.env` configuration
- `.env.example` included
- SQL initialization script
- Repository pattern implemented
- In-memory repository replaced with PostgreSQL repository
- Routes unchanged
- Service unchanged
- Persistence verification pending due to Docker Desktop image download issue