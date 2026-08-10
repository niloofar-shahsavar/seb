from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.pipeline import run_daily_monitoring

app = FastAPI(title="Portfolio Bond Compliance Monitoring")

# The React dev server runs on a different port, so the browser needs this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/daily-run")
def daily_run(run_date: str | None = None):
    """Return the complete result of one daily monitoring run."""
    try:
        return run_daily_monitoring(run_date)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

@app.get("/")
def root():
    return {
        "service": "Portfolio Bond Compliance Monitoring",
        "endpoints": ["/api/health", "/api/daily-run", "/docs"],
    }