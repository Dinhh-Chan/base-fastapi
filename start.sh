#!/bin/sh
# Tạo file start.sh trong thư mục gốc

# Chờ database khởi động
echo "Chờ Postgres khởi động..."
sleep 5

# Chạy migrations
echo "Đang chạy database migrations..."
alembic upgrade head

# Khởi tạo dữ liệu ban đầu (nếu cần)
echo "Đang khởi tạo dữ liệu..."
python -c "from app.db.init_db import init_db; from app.db.session import SessionLocal; init_db(SessionLocal())"

# Khởi động ứng dụng với chế độ reload
echo "Khởi động ứng dụng..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload