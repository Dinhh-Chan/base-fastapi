# FastAPI Base Project

Dự án nền tảng FastAPI được thiết kế để giúp bạn xây dựng API nhanh chóng, có cấu trúc rõ ràng và dễ mở rộng.

## 🌟 Tính năng

- **Kiến trúc module hóa**: Cấu trúc thư mục rõ ràng, phân tách trách nhiệm
- **RESTful API**: Endpoints được thiết kế theo chuẩn RESTful
- **Xác thực & Phân quyền**: JWT token authentication
- **ORM**: SQLAlchemy với hỗ trợ async
- **Database Migrations**: Quản lý schema với Alembic
- **Validation**: Pydantic cho việc xác thực dữ liệu đầu vào
- **Docker**: Docker Compose setup cho phát triển và triển khai
- **Auto-migration**: Tự động cập nhật database khi models thay đổi
- **CRUD Base**: Lớp cơ sở tái sử dụng cho các thao tác CRUD

## 🚀 Bắt đầu

### Sử dụng Docker

1. Clone repository:
   ```bash
   git clone <repository_url>
   cd base-fastapi
   ```

2. Khởi động với Docker Compose:
   ```bash
   docker-compose up -d
   ```

3. API có thể truy cập tại: http://localhost:8000

### Sử dụng môi trường ảo (venv)

1. Tạo và kích hoạt môi trường ảo:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # hoặc
   venv\Scripts\activate  # Windows
   ```

2. Cài đặt dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Khởi động ứng dụng:
   ```bash
   uvicorn app.main:app --reload
   ```

## 📁 Cấu trúc dự án

```
base-fastapi/
├── alembic/                 # Database migrations
├── app/
│   ├── api/                 # API endpoints
│   │   └── v1/              # API phiên bản 1
│   │       ├── endpoints/   # Các module API
│   │       └── api.py       # Router tổng hợp
│   ├── background/          # Tác vụ nền
│   ├── cache/               # Cache utilities
│   ├── core/                # Core functionality
│   │   └── config.py        # Cấu hình ứng dụng
│   ├── db/                  # Database
│   │   ├── base_class.py    # Base model class
│   │   ├── init_db.py       # Khởi tạo dữ liệu ban đầu
│   │   └── session.py       # DB session management
│   ├── dependencies/        # FastAPI dependencies
│   ├── dto/                 # Data Transfer Objects
│   ├── models/              # SQLAlchemy models
│   ├── services/            # Business logic
│   │   ├── base.py          # Base CRUD service
│   │   └── user.py          # User service
│   ├── utils/               # Utilities
│   │   └── security.py      # Security utilities
│   └── main.py              # Entry point
├── docker-compose.yml       # Docker Compose
├── Dockerfile               # Docker config
└── requirements.txt         # Dependencies
```

## 🔑 Xác thực API

### Đăng ký người dùng mới
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "Example User"
  }'
```

### Đăng nhập
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

### Sử dụng endpoints được bảo vệ
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🛠️ Sử dụng Base CRUD Service

Dự án cung cấp service cơ sở cho các thao tác CRUD, hỗ trợ:

- Phân trang nâng cao
- Tìm kiếm và lọc
- Sắp xếp
- Bulk operations
- Update/create tự động (upsert)

### Ví dụ tạo service mới:
```python
from app.services.base import CRUDBase
from app.models.product import Product
from app.dto.product import ProductCreate, ProductUpdate

class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    # Thêm các phương thức đặc thù nếu cần
    pass

product_service = CRUDProduct(Product)
```

## 📋 Môi trường và Cấu hình

Các biến môi trường có thể được cấu hình trong file `.env` hoặc thông qua Docker Compose:

- `SQL_DATABASE_URL`: Database connection string
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Thời gian hết hạn token
- `FIRST_SUPERUSER_EMAIL`: Email của superuser
- `FIRST_SUPERUSER_PASSWORD`: Mật khẩu superuser
- `AUTO_MIGRATE`: Tự động cập nhật database

## 📚 API Documentation

Sau khi khởi động, bạn có thể truy cập:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🔄 Quản lý Database

### Tạo migration mới:
```bash
alembic revision --autogenerate -m "Migration description"
```

### Áp dụng migrations:
```bash
alembic upgrade head
```

### Reset database:
```bash
docker-compose down -v
docker-compose up -d
```

## 🤝 Đóng góp

Đóng góp và đề xuất cải tiến luôn được chào đón!

## 📝 License

MIT