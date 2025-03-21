# app/db/auto_migrate.py
import asyncio
import logging
import os
import time
import subprocess
from datetime import datetime

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_command(cmd):
    """Chạy lệnh shell và trả về kết quả"""
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    
    if process.returncode != 0:
        logger.error(f"Command failed: {cmd}")
        logger.error(f"Error: {stderr.decode()}")
        return False, stderr.decode()
    
    return True, stdout.decode()

async def create_migration():
    """Tạo migration mới từ thay đổi models"""
    logger.info("Creating new migration...")
    
    # Tạo tên migration dựa trên timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    migration_name = f"auto_migration_{timestamp}"
    
    # Chạy lệnh alembic tạo migration
    success, output = await run_command(f"alembic revision --autogenerate -m '{migration_name}'")
    
    if not success:
        logger.error("Failed to create migration")
        return False
    
    logger.info(f"Created migration: {migration_name}")
    return True

async def apply_migration():
    """Áp dụng migration mới nhất vào database"""
    logger.info("Applying migration...")
    
    # Chạy lệnh alembic upgrade
    success, output = await run_command("alembic upgrade head")
    
    if not success:
        logger.error("Failed to apply migration")
        return False
    
    logger.info("Migration applied successfully")
    return True

async def check_and_update():
    """Kiểm tra thay đổi và cập nhật database nếu cần"""
    try:
        # Tạo migration mới
        if await create_migration():
            # Nếu tạo thành công, áp dụng migration
            await apply_migration()
    except Exception as e:
        logger.error(f"Error during migration process: {e}")

async def auto_migrate():
    """Tự động migrate khi khởi động và sau khi có thay đổi"""
    # Đợi database khởi động
    logger.info("Waiting for database to be ready...")
    await asyncio.sleep(5)
    
    # Khởi tạo migration đầu tiên khi khởi động
    logger.info("Running initial migration check...")
    await check_and_update()
    
    logger.info("Auto-migration process completed!")

if __name__ == "__main__":
    asyncio.run(auto_migrate())