#!/usr/bin/env python3
"""Seed test data: multiple olympiads and participant accounts."""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4
from datetime import date, datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from olimpqr.config import settings
from olimpqr.infrastructure.database.models import (
    UserModel,
    ParticipantModel,
    CompetitionModel,
)
from olimpqr.infrastructure.security import hash_password
from olimpqr.domain.value_objects import UserRole, CompetitionStatus


async def seed():
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # ── Find admin user for created_by ──
        result = await session.execute(
            select(UserModel).where(UserModel.role == UserRole.ADMIN)
        )
        admin = result.scalar_one_or_none()
        if not admin:
            print("ERROR: No admin user found. Run create_admin.bat first.")
            return
        admin_id = admin.id
        print(f"  Using admin: {admin.email} ({admin_id})")

        # ── Create participant accounts: test11@mail.ru .. test20@mail.ru ──
        passwords = ["12345678", "22222222", "33333333", "44444444",
                      "55555555", "66666666", "77777777", "88888888",
                      "12345678", "12345678"]

        for i in range(11, 21):
            email = f"test{i}@mail.ru"
            # Check if already exists
            result = await session.execute(
                select(UserModel).where(UserModel.email == email)
            )
            if result.scalar_one_or_none():
                print(f"  User {email} already exists, skipping")
                continue

            pwd = passwords[i - 11]
            user_id = uuid4()
            user = UserModel(
                id=user_id,
                email=email,
                password_hash=hash_password(pwd),
                role=UserRole.PARTICIPANT,
                is_active=True,
            )
            session.add(user)

            participant = ParticipantModel(
                id=uuid4(),
                user_id=user_id,
                full_name=f"Участник {i}",
                school=f"Школа №{i}",
                grade=min(11, max(5, (i - 11) + 5)),
            )
            session.add(participant)
            print(f"  Created {email}  password={pwd}")

        # ── Create olympiads ──
        olympiads = [
            {
                "name": "Математическая олимпиада 2026",
                "date": date(2026, 3, 15),
                "reg_start": datetime(2026, 2, 1),
                "reg_end": datetime(2026, 3, 10, 23, 59, 59),
                "variants": 4,
                "max_score": 100,
            },
            {
                "name": "Олимпиада по физике 2026",
                "date": date(2026, 4, 10),
                "reg_start": datetime(2026, 2, 15),
                "reg_end": datetime(2026, 4, 5, 23, 59, 59),
                "variants": 3,
                "max_score": 80,
            },
            {
                "name": "Олимпиада по информатике 2026",
                "date": date(2026, 5, 20),
                "reg_start": datetime(2026, 3, 1),
                "reg_end": datetime(2026, 5, 15, 23, 59, 59),
                "variants": 5,
                "max_score": 120,
            },
            {
                "name": "Олимпиада по химии 2026",
                "date": date(2026, 4, 25),
                "reg_start": datetime(2026, 2, 20),
                "reg_end": datetime(2026, 4, 20, 23, 59, 59),
                "variants": 4,
                "max_score": 90,
            },
            {
                "name": "Олимпиада по биологии 2026",
                "date": date(2026, 5, 5),
                "reg_start": datetime(2026, 3, 10),
                "reg_end": datetime(2026, 4, 30, 23, 59, 59),
                "variants": 3,
                "max_score": 75,
            },
        ]

        for o in olympiads:
            # Check by name
            result = await session.execute(
                select(CompetitionModel).where(CompetitionModel.name == o["name"])
            )
            if result.scalar_one_or_none():
                print(f"  Competition '{o['name']}' already exists, skipping")
                continue

            comp = CompetitionModel(
                id=uuid4(),
                name=o["name"],
                date=o["date"],
                registration_start=o["reg_start"],
                registration_end=o["reg_end"],
                variants_count=o["variants"],
                max_score=o["max_score"],
                status=CompetitionStatus.REGISTRATION_OPEN,
                created_by=admin_id,
            )
            session.add(comp)
            print(f"  Created competition: {o['name']}")

        await session.commit()

    await engine.dispose()
    print("\nDone! All test data seeded.")


if __name__ == "__main__":
    asyncio.run(seed())
