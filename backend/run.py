import sys
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)
for _venv_sp in (
    os.path.join(backend_dir, ".venv", "Lib", "site-packages"),
    os.path.join(backend_dir, "venv", "Lib", "site-packages"),
):
    if os.path.isdir(_venv_sp) and _venv_sp not in sys.path:
        sys.path.insert(0, _venv_sp)

import uvicorn
from app.config.settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
