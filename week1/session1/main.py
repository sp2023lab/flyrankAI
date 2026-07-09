from fastapi import FastAPI

app = FastAPI(title="FlyRank BE-01 API")


@app.get("/")
def home():
    return {
        "message": "Hello FlyRank!",
        "assignment": "BE-01",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "flyrank-be-01"
    }