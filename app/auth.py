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
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token


# JWT 검증
def decode_jwt(token: str):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError as e:
        raise Exception("Invalid token")
