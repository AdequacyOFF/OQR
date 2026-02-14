#!/usr/bin/env python3
"""Initialize default admin user.

This script creates a default admin user if one doesn't exist.
Run this after the first deployment to set up the initial admin account.

Usage:
    python scripts/init_admin.py

Environment variables:
    ADMIN_EMAIL: Admin email (default: admin@olimpqr.local)
    ADMIN_PASSWORD: Admin password (required, no default for security)
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from uuid import uuid4
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from olimpqr.config import settings
from olimpqr.infrastructure.database.base import Base
from olimpqr.infrastructure.database.models import UserModel
from olimpqr.infrastructure.security import hash_password
from olimpqr.domain.value_objects import UserRole


async def create_admin_user():
    """Create default admin user if not exists."""
    # Get credentials from environment
    admin_email = os.getenv("ADMIN_EMAIL", "admin@admin.com")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_password:
        print("ERROR: ADMIN_PASSWORD environment variable is required")
        print("Example: ADMIN_PASSWORD=YourSecurePassword123 python scripts/init_admin.py")
        sys.exit(1)

    # Create async engine
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        # Check if admin already exists
        from sqlalchemy import select
        result = await session.execute(
            select(UserModel).where(
                UserModel.email == admin_email,
                UserModel.role == UserRole.ADMIN
            )
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print(f"Admin user already exists: {admin_email}")
            print("Skipping creation.")
            return

        # Create new admin user
        admin_user = UserModel(
            id=uuid4(),
            email=admin_email,
            password_hash=hash_password(admin_password),
            role=UserRole.ADMIN,
            is_active=True
        )

        session.add(admin_user)
        await session.commit()

        print("=" * 60)
        print("✓ Admin user created successfully!")
        print("=" * 60)
        print(f"Email:    {admin_email}")
        print(f"Password: {admin_password}")
        print("=" * 60)
        print("\nIMPORTANT: Save these credentials in a secure location!")
        print("You can now log in to the admin panel with these credentials.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
