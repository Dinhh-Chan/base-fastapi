# app/db/model_watcher.py
import asyncio
import logging
import os
import time
import hashlib
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.db.auto_migrate import check_and_update

# Thiết lập logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Đường dẫn đến thư mục models
MODELS_DIR = Path(__file__).parent.parent / "models"

class ModelsChangeHandler(FileSystemEventHandler):
    """Xử lý sự kiện thay đổi trong thư mục models"""
    
    def __init__(self):
        super().__init__()
        self.last_modified = 0
        self.debounce_seconds = 2  # Đợi 2 giây sau mỗi thay đổi
        self.processing = False
    
    async def on_any_event_async(self, event):
        """Xử lý bất kỳ thay đổi nào đối với files"""
        if event.is_directory:
            return
            
        # Chỉ quan tâm đến các file Python
        if not event.src_path.endswith(".py"):
            return
            
        # Tránh xử lý nhiều lần khi có nhiều file thay đổi cùng lúc
        current_time = time.time()
        if current_time - self.last_modified < self.debounce_seconds:
            return
            
        self.last_modified = current_time
        
        # Đợi một lúc để đảm bảo tất cả các thay đổi đã được lưu
        logger.info(f"Detected change in models: {event.src_path}")
        logger.info(f"Waiting {self.debounce_seconds} seconds before processing...")
        await asyncio.sleep(self.debounce_seconds)
        
        if self.processing:
            logger.info("Already processing changes, skipping...")
            return
            
        try:
            self.processing = True
            logger.info("Processing model changes...")
            await check_and_update()
        except Exception as e:
            logger.error(f"Error processing model changes: {e}")
        finally:
            self.processing = False
    
    def on_any_event(self, event):
        """Khởi chạy xử lý bất đồng bộ cho sự kiện"""
        asyncio.run(self.on_any_event_async(event))

async def watch_models():
    """Theo dõi thay đổi trong thư mục models"""
    logger.info(f"Starting model watcher on directory: {MODELS_DIR}")
    
    event_handler = ModelsChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, str(MODELS_DIR), recursive=True)
    observer.start()
    
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

if __name__ == "__main__":
    asyncio.run(watch_models())