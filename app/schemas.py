from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class ExampleRequestModel(BaseModel):
    """요청 데이터 구조를 정의하는 모델"""
    name: str = Field(..., description="사용자 이름")
    age: int = Field(..., gt=0, description="사용자 나이")
    email: str = Field(..., description="사용자 이메일")