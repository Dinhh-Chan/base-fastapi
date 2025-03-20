#!/bin/sh

# Chờ database khởi động hoàn tất
echo "Waiting for PostgreSQL..."
sleep 5

# Kiểm tra kết nối đến PostgreSQL
echo "Checking PostgreSQL connection..."
python -c "
import psycopg2
import os
import time

# Số lần thử lại tối đa
max_retries = 5
retry_interval = 5

db_url = os.environ.get('SQL_DATABASE_URL') or 'postgresql://postgres:postgres@db:5432/app'
db_params = db_url.split('://')[-1].split('@')
user_pass = db_params[0].split(':')
host_db = db_params[1].split('/')

connection_params = {
    'user': user_pass[0],
    'password': user_pass[1],
    'host': host_db[0].split(':')[0],
    'port': host_db[0].split(':')[1] if ':' in host_db[0] else '5432',
    'database': host_db[1]
}

# Thử kết nối với số lần thử lại
for i in range(max_retries):
    try:
        conn = psycopg2.connect(**connection_params)
        conn.close()
        print('PostgreSQL connection successful!')
        break
    except Exception as e:
        print(f'Attempt {i+1}/{max_retries}: PostgreSQL connection failed: {e}')
        if i < max_retries - 1:
            print(f'Retrying in {retry_interval} seconds...')
            time.sleep(retry_interval)
        else:
            print('Could not connect to PostgreSQL after multiple attempts')
            exit(1)
"

# Tạo migrations ban đầu nếu cần
echo "Creating initial migrations if not exist..."
if [ ! -d "/app/alembic/versions" ] || [ -z "$(ls -A /app/alembic/versions)" ]; then
    alembic revision --autogenerate -m "Initial migration"
fi

# Chạy migrations
echo "Running database migrations..."
alembic upgrade head

# Khởi tạo dữ liệu ban đầu
echo "Initializing data..."
python -c "
from app.db.init_db import init_db
from app.db.session import SessionLocal
try:
    init_db(SessionLocal())
    print('Database initialized successfully!')
except Exception as e:
    print(f'Error initializing database: {e}')
"

# Khởi động ứng dụng
echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload