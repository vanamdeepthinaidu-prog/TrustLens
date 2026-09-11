import os
import sys
import traceback
from pathlib import Path

# Force unbuffered output so logs appear instantly on Render
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(line_buffering=True)

ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"

for p in (str(ROOT_DIR), str(BACKEND_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

# Prevent Uvicorn multi-process warning from Render's WEB_CONCURRENCY
os.environ.pop("WEB_CONCURRENCY", None)

if __name__ == "__main__":
    port_str = os.environ.get("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
    
    print(f"[*] VisionTrust AI initializing on 0.0.0.0:{port}...", flush=True)
    try:
        # Pre-create database schema before any module initializes
        from app.core.database import engine, Base
        import app.models.orm_models
        Base.metadata.create_all(bind=engine)
        print("[*] Database schema verified and initialized successfully.", flush=True)

        # Pre-verify imports
        import app.main
        print("[*] FastAPI application and routers imported successfully.", flush=True)
        import uvicorn
        print(f"[*] Starting Uvicorn on 0.0.0.0:{port}...", flush=True)
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=port,
            app_dir=str(BACKEND_DIR),
            log_level="info",
            workers=1
        )
    except BaseException as e:
        print(f"[!] FATAL STARTUP ERROR: {type(e).__name__}: {e}", flush=True)
        traceback.print_exc()
        sys.exit(1)
