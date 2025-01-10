from fastapi import FastAPI, HTTPException
from starlette.responses import Response

from app.middleware import BasicRequestLoggingMiddleware, RequestBodyLoggingMiddleware, ResponseLoggingMiddleware, \
    ProcessingTimeLoggingMiddleware

app = FastAPI()

# 요청 로깅 미들웨어 등록
# app.add_middleware(BasicRequestLoggingMiddleware)

# 요청 본문 로깅 미들웨어 등록
# app.add_middleware(RequestBodyLoggingMiddleware)

# 응답 로깅 미들웨어 등록
# app.add_middleware(ResponseLoggingMiddleware)

# 처리 시간 로깅 미들웨어 등록
app.add_middleware(ProcessingTimeLoggingMiddleware)


@app.get("/")
async def root():
    return {"message": "Hello, Middleware!"}


@app.post("/data")
async def receive_data(payload: dict):
    if "key" not in payload:
        raise HTTPException(status_code=400, detail="Missing 'key' in payload")
    return {"received_key": payload["key"]}

@app.get("/data")
async def get_data():
    from faker import Faker
    import time
    fake = Faker("ko_KR")
    Faker.seed(42)

    email = { str(i+1): fake.unique.free_email() for i in range(10)}
    time.sleep(3)
    return email
