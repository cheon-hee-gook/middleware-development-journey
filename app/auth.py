import jwt
from datetime import datetime, timedelta

SECRET_KEY = "secret_key"
ALGORITHM = "HS256"


# JWT 생성
def create_jwt(user_id: str, role: str):
    payload = {
        "sub": user_id,
        "role": role,
        "exp": datetime.now() + timedelta(hours=1)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# JWT 검증
def decode_jwt(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise Exception("Token is expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
