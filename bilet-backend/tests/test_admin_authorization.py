import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI
from fastapi.testclient import TestClient

from database import get_db
from routers import auth, events


EVENT = {
    "title": "Konser",
    "date": "2026-10-01",
    "location": "Salon",
    "price": "100",
    "description": "Test",
    "city": "İstanbul",
    "category": "Konser",
    "capacity": 10,
    "time": "20:00",
}


class AdminAuthorizationTest(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(auth.router)
        app.include_router(events.router)
        app.dependency_overrides[get_db] = lambda: object()
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()

    def test_event_creation_requires_admin(self):
        with patch.object(events.event_service, "create_event", return_value={"mesaj": "ok"}) as create:
            response = self.client.post("/api/events/", json=EVENT)
            self.assertEqual(response.status_code, 401)

            with patch.object(auth.auth_service, "get_user_from_token", return_value=SimpleNamespace(is_admin=False)):
                response = self.client.post("/api/events/", json=EVENT, headers={"Authorization": "Bearer regular"})
            self.assertEqual(response.status_code, 403)
            create.assert_not_called()

            with patch.object(auth.auth_service, "get_user_from_token", return_value=SimpleNamespace(is_admin=True)):
                response = self.client.post("/api/events/", json=EVENT, headers={"Authorization": "Bearer admin"})
            self.assertEqual(response.status_code, 200)
            create.assert_called_once()

    def test_admin_promotion_requires_admin(self):
        with patch.object(auth.auth_service, "make_admin", return_value={"mesaj": "ok"}) as promote:
            response = self.client.get("/api/auth/make-admin/user@example.com")
            self.assertEqual(response.status_code, 405)

            response = self.client.post("/api/auth/make-admin/user@example.com")
            self.assertEqual(response.status_code, 401)

            with patch.object(auth.auth_service, "get_user_from_token", return_value=SimpleNamespace(is_admin=False)):
                response = self.client.post("/api/auth/make-admin/user@example.com", headers={"Authorization": "Bearer regular"})
            self.assertEqual(response.status_code, 403)
            promote.assert_not_called()

            with patch.object(auth.auth_service, "get_user_from_token", return_value=SimpleNamespace(is_admin=True)):
                response = self.client.post("/api/auth/make-admin/user@example.com", headers={"Authorization": "Bearer admin"})
            self.assertEqual(response.status_code, 200)
            promote.assert_called_once()
