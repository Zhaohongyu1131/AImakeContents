"""
Security Module
安全功能模块 - [security]
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
import secrets

from app.config.settings import app_config_get_settings

settings = app_config_get_settings()

# 密码加密上下文
security_password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def security_password_hash_create(password: str) -> str:
    """
    创建密码哈希
    [security][password][hash_create]
    """
    return security_password_context.hash(password)

def security_password_verify(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码
    [security][password][verify]
    """
    return security_password_context.verify(plain_password, hashed_password)

def security_jwt_token_create(
    data: dict, 
    expires_delta: Optional[timedelta] = None,
    token_type: str = "access"
) -> str:
    """
    创建JWT令牌
    [security][jwt][token_create]
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        if token_type == "access":
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        else:  # refresh token
            expire = datetime.utcnow() + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": token_type
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

def security_jwt_token_decode(token: str) -> dict:
    """
    解码JWT令牌
    [security][jwt][token_decode]
    """
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )

def security_jwt_token_verify(token: str, token_type: str = "access") -> dict:
    """
    验证JWT令牌
    [security][jwt][token_verify]
    """
    payload = security_jwt_token_decode(token)
    
    if payload.get("type") != token_type:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌类型错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload

def security_random_string_generate(length: int = 32) -> str:
    """
    生成随机字符串
    [security][random_string][generate]
    """
    return secrets.token_urlsafe(length)

def security_api_key_generate() -> str:
    """
    生成API密钥
    [security][api_key][generate]
    """
    return f"ds_{security_random_string_generate(32)}"