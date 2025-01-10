# 미들웨어 개발 스터디

## **1주차 - 요청 로깅 미들웨어**

### **구현된 미들웨어**
1. **기본 요청 로깅**:
   - 요청 URL, 메서드, 헤더 정보를 로깅.

### **테스트 방법**
1. **GET 요청**:
   - URL: `http://127.0.0.1:8000/`
   - 테스트 도구: Postman 또는 curl 사용.
   - 기대 결과:
     - 응답: `{"message": "Hello, Middleware!"}`
     - 터미널 로그: 
     ```bash
     2025-01-10 11:49:27,445 Request URL: http://127.0.0.1:8000/
     2025-01-10 11:49:27,445 Request Method: GET
     2025-01-10 11:49:27,445 Request Headers: Headers({'user-agent': 'PostmanRuntime/7.37.3', 'accept': '*/*', 'postman-token': '69049fd3-fd8b-40bb-b74e-8818f3284824', 'host': '127.0.0.1:8000', 'accept-encoding': 'gzip, deflate, br', 'connection': 'keep-alive'})

### **실행 방법**
1. **Git 레포지토리 클론**:
   ```bash
   https://github.com/cheon-hee-gook/middleware-development-journey.git

2. **Python 환경 설정**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows에서는 venv\Scripts\activate
   pip install fastapi uvicorn

3. **서버 실행**:
   ```bash
   uvicorn app.main:app --reload

### **학습 포인트**
1. HTTP 요청 데이터를 로깅하는 기본 원리
2. FastAPI에서 미들웨어 구현 및 적용 방법
