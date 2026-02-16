"""Script to create test data: competitions and participant accounts."""

import asyncio
from uuid import uuid4
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.olimpqr.config import settings
from src.olimpqr.infrastructure.repositories import (
    UserRepositoryImpl,
    ParticipantRepositoryImpl,
    CompetitionRepositoryImpl,
)
from src.olimpqr.infrastructure.security import hash_password
from src.olimpqr.domain.entities import User, Participant, Competition
from src.olimpqr.domain.value_objects import UserRole, CompetitionStatus


async def create_test_data():
    """Create test competitions and participant accounts."""

    # Create async engine and session
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session() as session:
        user_repo = UserRepositoryImpl(session)
        participant_repo = ParticipantRepositoryImpl(session)
        competition_repo = CompetitionRepositoryImpl(session)

        # Use existing admin user ID (admin@admin.com)
        admin_user_id = uuid4()  # Will be replaced with actual admin ID
        try:
            # Try to find admin user by email
            from sqlalchemy import select
            from src.olimpqr.infrastructure.database.models import UserModel
            result = await session.execute(
                select(UserModel).where(UserModel.email == "admin@admin.com")
            )
            admin_model = result.scalar_one_or_none()
            if admin_model:
                admin_user_id = admin_model.id
                print(f"Using admin user: {admin_model.email}")
        except Exception as e:
            print(f"Could not find admin user, using placeholder ID: {e}")

        print("\n=== Creating Test Competitions ===")

        competitions_data = [
            {"name": "Математическая олимпиада", "variants": 3, "max_score": 100},
            {"name": "Физическая олимпиада", "variants": 4, "max_score": 120},
            {"name": "Олимпиада по информатике", "variants": 2, "max_score": 150},
            {"name": "Химическая олимпиада", "variants": 3, "max_score": 100},
            {"name": "Биологическая олимпиада", "variants": 2, "max_score": 90},
        ]

        created_competitions = []
        for comp_data in competitions_data:
            competition = Competition(
                name=comp_data["name"],
                date=(datetime.now() + timedelta(days=7)).date(),
                registration_start=datetime.now(),
                registration_end=datetime.now() + timedelta(days=5),
                variants_count=comp_data["variants"],
                max_score=comp_data["max_score"],
                created_by=admin_user_id,
            )
            # Open registration
            competition.open_registration()

            created_comp = await competition_repo.create(competition)
            created_competitions.append(created_comp)
            print(f"✓ Created competition: {created_comp.name}")

        await session.commit()

        print("\n=== Creating Test Participant Accounts ===")

        schools = [
            "Гимназия №1",
            "Лицей №5",
            "Школа №12",
            "Гимназия №7",
            "Лицей №3",
        ]

        for i in range(1, 11):
            email = f"test{i}@mail.ru"
            password = "12345678"

            # Check if user already exists
            if await user_repo.exists_by_email(email):
                print(f"⊘ User {email} already exists, skipping...")
                continue

            # Create user
            user = User(
                id=uuid4(),
                email=email,
                password_hash=hash_password(password),
                role=UserRole.PARTICIPANT,
            )
            created_user = await user_repo.create(user)

            # Create participant profile
            participant = Participant(
                id=uuid4(),
                user_id=created_user.id,
                full_name=f"Тестовый Участник {i}",
                school=schools[i % len(schools)],
                grade=7 + (i % 5),  # Grades 7-11
            )
            await participant_repo.create(participant)

            print(f"✓ Created participant: {email} (password: {password})")

        await session.commit()

        print("\n=== Summary ===")
        print(f"Competitions created: {len(created_competitions)}")
        print(f"Participant accounts: test1@mail.ru - test10@mail.ru")
        print(f"Password for all accounts: 12345678")
        print("\nTest data created successfully!")


if __name__ == "__main__":
    asyncio.run(create_test_data())
