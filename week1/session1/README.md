# FlyRank BE-01 - Build Your First API Endpoint

This is my Week 1 Session 1 backend assignment for the FlyRank AI Internship.

## Goal

Build a minimal backend server with two JSON endpoints.

## Tech Stack

- Python
- FastAPI
- Uvicorn

## Endpoints

### GET /

Returns a welcome response.

### GET /health

Returns a health-check response.

## Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8080