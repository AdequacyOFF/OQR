"""E2E test fixtures - reuses integration test infrastructure."""

# Re-export all fixtures from integration tests
# E2E tests use the same in-memory SQLite setup for speed
from tests.integration.conftest import (
    setup_database,
    client,
    db_session,
    admin_user,
    participant_user,
    invigilator_user,
    institution,
    make_auth_header,
)

__all__ = [
    "setup_database",
    "client",
    "db_session",
    "admin_user",
    "participant_user",
    "invigilator_user",
    "institution",
    "make_auth_header",
]
