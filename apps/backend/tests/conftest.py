import sys
from pathlib import Path

# Add apps/backend to PYTHONPATH so `import main` works even when pytest rootdir is repo root
BACKEND_DIR = Path(__file__).resolve().parents[1]  # .../apps/backend
sys.path.insert(0, str(BACKEND_DIR))

import pytest
from fastapi.testclient import TestClient
from deps import get_current_user, get_optional_current_user
from main import app
from services import db


@pytest.fixture()
def client():
    db.init_db()
    with db._conn() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO users(id, email, password_hash, email_verified)
            VALUES (1, 'pytest@example.com', 'test-hash', 1)
            """
        )

    test_user = {
        "id": 1,
        "email": "pytest@example.com",
    }
    app.dependency_overrides[get_current_user] = lambda: test_user
    app.dependency_overrides[get_optional_current_user] = lambda: test_user
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
