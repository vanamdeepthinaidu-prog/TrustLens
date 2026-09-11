import os
import sys
from pathlib import Path

# Ensure root directory and backend directory are in sys.path
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
    
    print(f"[*] VisionTrust AI starting on 0.0.0.0:{port}...")
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, app_dir=str(BACKEND_DIR))
