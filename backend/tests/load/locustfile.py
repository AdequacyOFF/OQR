"""Locust load testing script for OlimpQR API.

Usage:
    pip install locust
    locust -f tests/load/locustfile.py --host http://localhost:8000

Open http://localhost:8089 to start the test.
"""

import random
import string
from locust import HttpUser, task, between, tag


def random_email():
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"load_{suffix}@test.com"


class PublicUser(HttpUser):
    """Simulates unauthenticated users browsing public endpoints."""

    weight = 3
    wait_time = between(1, 3)

    @tag("public")
    @task(5)
    def health_check(self):
        self.client.get("/health")

    @tag("public")
    @task(10)
    def list_competitions(self):
        self.client.get("/api/v1/competitions")

    @tag("public")
    @task(3)
    def view_results(self):
        # Attempt to view results for a random competition UUID
        # Will return 404 or 403, which is expected
        self.client.get(
            "/api/v1/results/00000000-0000-0000-0000-000000000001",
            name="/api/v1/results/[id]",
        )


class ParticipantUser(HttpUser):
    """Simulates participant registration and browsing."""

    weight = 5
    wait_time = between(2, 5)

    def on_start(self):
        """Register a new participant on start."""
        email = random_email()
        resp = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "loadtest123",
                "role": "participant",
                "full_name": "Load Test User",
                "school": "Load Test School",
                "grade": random.randint(8, 11),
            },
        )
        if resp.status_code == 201:
            self.token = resp.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @tag("participant")
    @task(5)
    def list_competitions(self):
        self.client.get("/api/v1/competitions")

    @tag("participant")
    @task(3)
    def get_me(self):
        if self.token:
            self.client.get("/api/v1/auth/me", headers=self.headers)

    @tag("participant")
    @task(1)
    def register_for_competition(self):
        """Try to register for a competition (may fail if none exist)."""
        if not self.token:
            return
        # Get competitions first
        resp = self.client.get("/api/v1/competitions")
        if resp.status_code == 200:
            competitions = resp.json().get("competitions", [])
            open_comps = [c for c in competitions if c["status"] == "registration_open"]
            if open_comps:
                comp = random.choice(open_comps)
                self.client.post(
                    "/api/v1/registrations",
                    json={"competition_id": comp["id"]},
                    headers=self.headers,
                    name="/api/v1/registrations",
                )


class AdminUser(HttpUser):
    """Simulates admin operations."""

    weight = 1
    wait_time = between(3, 8)

    def on_start(self):
        """Register admin user."""
        email = random_email()
        resp = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "adminload123",
                "role": "admin",
            },
        )
        if resp.status_code == 201:
            self.token = resp.json().get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
        else:
            self.token = None
            self.headers = {}

    @tag("admin")
    @task(3)
    def list_users(self):
        if self.token:
            self.client.get("/api/v1/admin/users", headers=self.headers)

    @tag("admin")
    @task(2)
    def list_competitions(self):
        self.client.get("/api/v1/competitions", headers=self.headers)

    @tag("admin")
    @task(1)
    def create_competition(self):
        if not self.token:
            return
        self.client.post(
            "/api/v1/competitions",
            json={
                "name": f"Load Test Competition {random.randint(1, 10000)}",
                "date": "2026-06-15",
                "registration_start": "2026-01-01T00:00:00",
                "registration_end": "2026-06-10T23:59:59",
                "variants_count": random.randint(2, 4),
                "max_score": 100,
            },
            headers=self.headers,
        )

    @tag("admin")
    @task(1)
    def view_audit_log(self):
        if self.token:
            self.client.get("/api/v1/admin/audit-log", headers=self.headers)


class LoginUser(HttpUser):
    """Simulates login flow — register once, then repeatedly login."""

    weight = 2
    wait_time = between(2, 5)

    def on_start(self):
        self.email = random_email()
        self.password = "logintest123"
        self.client.post(
            "/api/v1/auth/register",
            json={
                "email": self.email,
                "password": self.password,
                "role": "admin",
            },
        )

    @tag("auth")
    @task
    def login(self):
        self.client.post(
            "/api/v1/auth/login",
            json={
                "email": self.email,
                "password": self.password,
            },
        )
