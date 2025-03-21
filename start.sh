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
connected = False
for i in range(max_retries):
    try:
        conn = psycopg2.connect(**connection_params)
        conn.close()
        print('PostgreSQL connection successful!')
        connected = True
        break
    except Exception as e:
        print(f'Attempt {i+1}/{max_retries}: PostgreSQL connection failed: {e}')
        if i < max_retries - 1:
            print(f'Retrying in {retry_interval} seconds...')
            time.sleep(retry_interval)
        else:
            print('Could not connect to PostgreSQL after multiple attempts')
            exit(1)

# Kiểm tra biến môi trường để xác định có reset database hay không
if connected and os.environ.get('RESET_DB', '').lower() == 'true':
    print('RESET_DB is set to true, dropping all tables...')
    try:
        conn = psycopg2.connect(**connection_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Xóa tất cả các bảng trong database
        cursor.execute(\"\"\"
        DO $$ DECLARE
            r RECORD;
        BEGIN
            FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
            END LOOP;
        END $$;
        \"\"\")
        
        # Xóa alembic_version table nếu tồn tại
        cursor.execute('DROP TABLE IF EXISTS alembic_version;')
        
        conn.close()
        print('All tables dropped successfully!')
        
        # Xóa các file migration cũ
        if os.path.exists('/app/alembic/versions'):
            import shutil
            shutil.rmtree('/app/alembic/versions')
            os.makedirs('/app/alembic/versions')
            print('Removed old migration files')
    except Exception as e:
        print(f'Error resetting database: {e}')
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
import asyncio
from app.db.init_db import init_db
from app.db.session import AsyncSessionLocal

async def run_init_db():
    async with AsyncSessionLocal() as session:
        await init_db(session)
    print('Database initialized successfully!')

try:
    asyncio.run(run_init_db())
except Exception as e:
    print(f'Error initializing database: {e}')
"

# Chạy auto_migrate để thiết lập theo dõi thay đổi models
echo "Setting up automatic database migration..."
python -m app.db.auto_migrate &

# Khởi động ứng dụng
echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload