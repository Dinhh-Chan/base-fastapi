import logging
from sqlalchemy.orm import Session
from app.core.settings import settings
from app.crud.user import crud_user
from app.schemas.user import UserCreate

logger = logging.getLogger(__name__)

def init_db(db: Session) -> None:
    """
    Khởi tạo database với dữ liệu cần thiết.
    """
    # Tạo superuser nếu chưa có
    user = crud_user.get_by_email(db, email=settings.FIRST_SUPERUSER_EMAIL)
    if not user:
        logger.info("Creating first superuser")
        user_in = UserCreate(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username=settings.FIRST_SUPERUSER_USERNAME,
            password=settings.FIRST_SUPERUSER_PASSWORD,
            is_superuser=True,
            is_active=True,
        )
        crud_user.create(db, obj_in=user_in)
        logger.info("First superuser created")
    else:
        logger.info("First superuser already exists")