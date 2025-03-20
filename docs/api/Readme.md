## Endpoints API

### Authentication

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|--------------|
| `/api/v1/auth/token` | POST | Lấy JWT token | No |
| `/api/v1/auth/test-token` | POST | Kiểm tra token hợp lệ | Yes (JWT) |

### Users

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|--------------|
| `/api/v1/users/` | GET | Lấy danh sách người dùng | Yes (Superuser) |
| `/api/v1/users/` | POST | Tạo người dùng mới | Yes (Superuser) |
| `/api/v1/users/me` | GET | Lấy thông tin người dùng hiện tại | Yes (JWT) |
| `/api/v1/users/me` | PUT | Cập nhật thông tin người dùng hiện tại | Yes (JWT) |
| `/api/v1/users/{user_id}` | GET | Lấy thông tin người dùng cụ thể | Yes (JWT/Superuser) |
| `/api/v1/users/{user_id}` | PUT | Cập nhật người dùng | Yes (Superuser) |

### API Keys

| Endpoint | Method | Description | Auth Required |
|----------|--------|-------------|--------------|
| `/api/v1/api-keys/` | GET | Lấy danh sách API key | Yes (JWT) |
| `/api/v1/api-keys/` | POST | Tạo API key mới | Yes (JWT) |
| `/api/v1/api-keys/with-expiry` | POST | Tạo API key có thời hạn | Yes (JWT) |
| `/api/v1/api-keys/{api_key_id}` | GET | Lấy thông tin API key | Yes (JWT) |
| `/api/v1/api-keys/{api_key_id}` | PUT | Cập nhật API key | Yes (JWT) |
| `/api/v1/api-keys/{api_key_id}` | DELETE | Xóa API key | Yes (JWT) |

## Chi tiết xác thực

### JWT Authentication

API sử dụng JWT (JSON Web Tokens) cho xác thực người dùng. Flow xác thực:

1. Đăng nhập qua endpoint `/api/v1/auth/token`
2. Nhận JWT token
3. Sử dụng token trong header `Authorization: Bearer {token}` cho các request tiếp theo

**Ví dụ đăng nhập:**

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin"
```

**Phản hồi:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### API Key Authentication

Hệ thống cũng hỗ trợ xác thực qua API Key, phù hợp cho việc tích hợp hệ thống hoặc ứng dụng máy chủ:

1. Tạo API key qua endpoint `/api/v1/api-keys/`
2. Sử dụng API key trong header `X-API-Key: {api_key}` cho các request

**Ví dụ tạo API key:**

```bash
curl -X POST "http://localhost:8000/api/v1/api-keys/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Service Integration"}'
```

## Quản lý người dùng

### Tạo người dùng mới (Superuser)

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "username": "newuser",
    "password": "password123",
    "full_name": "New User",
    "is_active": true,
    "is_superuser": false
  }'
```

### Lấy thông tin người dùng hiện tại

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Cập nhật thông tin người dùng

```bash
curl -X PUT "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Name"
  }'
```

## Quản lý API Keys

### Tạo API Key mới

```bash
curl -X POST "http://localhost:8000/api/v1/api-keys/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Service Integration",
    "is_active": true
  }'
```

### Tạo API Key có thời hạn

```bash
curl -X POST "http://localhost:8000/api/v1/api-keys/with-expiry?days_valid=30" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Temporary Integration",
    "is_active": true
  }'
```

### Lấy danh sách API Key

```bash
curl -X GET "http://localhost:8000/api/v1/api-keys/" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Vô hiệu hóa API Key

```bash
curl -X PUT "http://localhost:8000/api/v1/api-keys/{api_key_id}" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

## Mã lỗi API

| Mã lỗi | Mô tả |
|--------|-------|
| 400 | Bad Request - Thông tin gửi lên không hợp lệ |
| 401 | Unauthorized - Chưa xác thực hoặc token/API key không hợp lệ |
| 403 | Forbidden - Không có quyền truy cập |
| 404 | Not Found - Không tìm thấy tài nguyên |
| 422 | Unprocessable Entity - Dữ liệu không thể xử lý |
| 500 | Internal Server Error - Lỗi máy chủ |

## Mẹo và Lưu ý

### Đặt biến môi trường

Tất cả cấu hình có thể được đặt qua biến môi trường hoặc file `.env`:

- **POSTGRES_SERVER**: Địa chỉ máy chủ PostgreSQL
- **POSTGRES_USER**: Tên người dùng PostgreSQL
- **POSTGRES_PASSWORD**: Mật khẩu PostgreSQL
- **POSTGRES_DB**: Tên database
- **SQL_DATABASE_URL**: URL kết nối đầy đủ đến database
- **SECRET_KEY**: Khóa bí mật sử dụng để tạo JWT
- **ACCESS_TOKEN_EXPIRE_MINUTES**: Thời gian hết hạn của JWT token (phút)

### Tạo admin user từ command line

Để tạo admin user mới:

```bash
docker-compose exec api python -c "from app.db.init_db import init_db; from app.db.session import SessionLocal; init_db(SessionLocal())"
```

### API Documentation

Swagger UI đã được cài đặt và có thể truy cập tại:

- `/api/v1/docs` - Swagger UI
- `/api/v1/redoc` - ReDoc

## Phát triển và Mở rộng

### Thêm endpoint mới

1. Tạo file mới trong `app/api/v1/endpoints/`
2. Thêm router vào file `app/api/v1/api.py`

### Thêm model mới

1. Tạo model SQLAlchemy trong `app/models/`
2. Tạo schema Pydantic trong `app/schemas/`
3. Tạo CRUD operations trong `app/crud/`
4. Tạo endpoints trong `app/api/v1/endpoints/`
5. Chạy migration: `alembic revision --autogenerate -m "Add new model"`

## License

MIT