from fastapi import FastAPI, Depends, HTTPException, status, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import os
from typing import Optional

app = FastAPI(title="JWT Auth API")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:10000", "http://122.51.223.247:10000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 90

# 数据模型
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class UserResponse(BaseModel):
    username: str

# 工具函数
def hash_password(password: str) -> str:
    """哈希密码"""
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    pwd_bytes = plain_password.encode('utf-8')[:72]
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问token (短期)"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """创建刷新token (长期)"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str, token_type: str):
    """验证token并返回用户名"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type_payload: str = payload.get("type")

        if username is None:
            return None

        # 检查token类型
        if token_type_payload != token_type:
            return None

        return username
    except JWTError:
        return None

def authenticate_user(username: str, password: str):
    """认证用户"""
    user = fake_users_db.get(username)
    if not user:
        return False
    if not verify_password(password, user["password_hash"]):
        return False
    return user

# 模拟用户数据库（实际应用中应使用真实数据库）
fake_users_db = {
    "admin": {
        "username": "admin",
        "password_hash": hash_password("admin123")  # 默认密码: admin123
    }
}

@app.get("/")
async def root():
    return {
        "message": "JWT Auth API is running",
        "features": {
            "access_token_expire": f"{ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
            "refresh_token_expire": f"{REFRESH_TOKEN_EXPIRE_DAYS} days",
            "auto_refresh": "supported"
        }
    }

@app.post("/login", response_model=Token)
async def login(user: User):
    """用户登录 - 返回访问token和刷新token"""
    authenticated_user = authenticate_user(user.username, user.password)
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问token (短期，30分钟)
    access_token = create_access_token(
        data={"sub": authenticated_user["username"]},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # 创建刷新token (长期，7天)
    refresh_token = create_refresh_token(
        data={"sub": authenticated_user["username"]}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@app.post("/refresh", response_model=Token)
async def refresh_token(authorization: str = Header(None)):
    """使用refresh_token获取新的access_token"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供刷新token",
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证格式错误",
        )

    refresh_token = authorization.split(" ")[1]

    # 验证refresh token
    username = verify_token(refresh_token, "refresh")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的刷新token",
        )

    # 获取用户信息
    user = fake_users_db.get(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    # 生成新的access token和refresh token
    new_access_token = create_access_token(
        data={"sub": username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    new_refresh_token = create_refresh_token(
        data={"sub": username}
    )

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(authorization: str = Header(None)):
    """获取当前用户信息"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供认证信息",
        )

    # 提取Bearer token
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="认证格式错误",
        )

    token = authorization.split(" ")[1]

    # 验证access token
    username = verify_token(token, "access")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或过期的访问token",
        )

    user = fake_users_db.get(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
        )

    return {"username": user["username"]}

@app.post("/logout")
async def logout(authorization: str = Header(None)):
    """用户登出 - 前端需要清除token"""
    # 在实际应用中，这里应该将refresh_token加入黑名单
    # 当前版本仅返回成功消息，实际清除由前端处理
    return {"message": "登出成功"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
