"""Login user use case."""

from ....domain.repositories import UserRepository
from ....infrastructure.security import verify_password, create_access_token
from ...dto import LoginUserDTO, AuthResponseDTO


class LoginUserUseCase:
    """Use case for user login."""

    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, dto: LoginUserDTO) -> AuthResponseDTO:
        """Login user and return JWT token.

        Args:
            dto: Login credentials

        Returns:
            Authentication response with access token

        Raises:
            ValueError: If credentials are invalid or user is inactive
        """
        # Get user by email
        user = await self.user_repository.get_by_email(dto.email)
        if not user:
            raise ValueError("Неверный email или пароль")

        # Verify password
        if not verify_password(dto.password, user.password_hash):
            raise ValueError("Неверный email или пароль")

        # Check if user is active
        if not user.is_active:
            raise ValueError("Аккаунт пользователя неактивен")

        # Generate JWT token
        access_token = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role
        )

        return AuthResponseDTO(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            role=user.role
        )
