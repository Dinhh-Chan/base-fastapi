# app/db/init_db.py
import logging
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.user import User
from app.utils.security import get_password_hash


logger = logging.getLogger(__name__)


async def init_db(db: AsyncSession) -> None:
    """
    Initialize the database with initial data.
    """
    # Tạo superuser đầu tiên nếu chưa có
    try:
        result = await db.execute(
            User.__table__.select().where(User.email == settings.FIRST_SUPERUSER_EMAIL)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user_obj = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                full_name=settings.FIRST_SUPERUSER_USERNAME,
                is_superuser=True,
                is_active=True,
            )
            db.add(user_obj)
            await db.commit()
            logger.info(f"Created first superuser: {settings.FIRST_SUPERUSER_EMAIL}")
        else:
            logger.info(f"Superuser already exists: {settings.FIRST_SUPERUSER_EMAIL}")
    
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        await db.rollback()
        raise