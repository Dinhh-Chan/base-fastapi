# FastAPI Base - API Documentation

## Giới thiệu

FastAPI Base là một dự án khung hoàn chỉnh sử dụng FastAPI framework, giúp xây dựng REST API hiệu suất cao với các tính năng đầy đủ như:

- Xác thực người dùng (JWT và API Key)
- Phân quyền
- CRUD operations
- Migration cơ sở dữ liệu
- Docker support

## Cài đặt và Chạy

### Yêu cầu

- Docker và Docker Compose
- Python 3.10+ (nếu chạy không dùng Docker)

### Chạy với Docker

```bash
# Clone repository
git clone https://github.com/yourusername/fastapi-base.git
cd fastapi-base

# Copy file .env.example thành .env và cấu hình
cp .env.example .env

# Khởi động ứng dụng với Docker
docker-compose up -d
```

### Chạy trực tiếp

```bash
# Tạo môi trường ảo
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy migrations
alembic upgrade head

# Khởi động ứng dụng
uvicorn app.main:app --reload
```