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

if __name__ == "__main__":
    port_str = os.environ.get("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
    
    print(f"[*] VisionTrust AI initializing on 0.0.0.0:{port}...", flush=True)
    try:
        from app.main import app
        import uvicorn
        print("[*] FastAPI app loaded successfully. Starting Uvicorn...", flush=True)
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"[!] FATAL STARTUP ERROR: {e}", file=sys.stderr, flush=True)
        traceback.print_exc()
        sys.exit(1)
