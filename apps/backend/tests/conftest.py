import sys
from pathlib import Path

# Add apps/backend to PYTHONPATH so `import main` works even when pytest rootdir is repo root
BACKEND_DIR = Path(__file__).resolve().parents[1]  # .../apps/backend
sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture()
def client():
    return TestClient(app)
