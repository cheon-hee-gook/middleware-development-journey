# 미들웨어 개발 스터디

### **실행 방법**
1. **Git 레포지토리 클론**:
   ```bash
   https://github.com/cheon-hee-gook/middleware-development-journey.git
   ```

2. **Python 환경 설정**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows에서는 venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **서버 실행**:
   ```bash
   uvicorn app.main:app --reload
   ```

## **1일차 - 요청 로깅 미들웨어**

### **구현된 미들웨어**
1. **기본 요청 로깅**: 요청 URL, 메서드, 헤더 정보를 로깅.
2. **요청 본문 로깅**: 요청 Body 데이터를 로깅.

### **테스트 방법**
1. **기본 요청 로깅**:
   1. **Postman**
      - Method: `GET`
      - URL: `http://127.0.0.1:8000/`
   2. **curl**
      ```bash
      curl -X GET http://127.0.0.1:8000/
      ```
   3. **기대 결과**:
        - 응답: `{"message": "Hello, Middleware!"}`
        - 터미널 로그:
        ```bash
        2025-01-10 11:49:27,445 Request URL: http://127.0.0.1:8000/
        2025-01-10 11:49:27,445 Request Method: GET
        2025-01-10 11:49:27,445 Request Headers: Headers({'user-agent': 'PostmanRuntime/7.37.3', 'accept': '*/*', 'postman-token': '69049fd3-fd8b-40bb-b74e-8818f3284824', 'host': '127.0.0.1:8000', 'accept-encoding': 'gzip, deflate, br', 'connection': 'keep-alive'})
        ```

2. **요청 본문 로깅**:
   1. **Postman**
      - Method: `POST`
      - URL: `http:127.0.0.1:8000`
      - Body: `{"key: "value"}` JSON 형식
   2. **curl**
   ```bash
   curl -X POST http://127.0.0.1:8000/ -H "Content-Type: application/json" -d '{"key": "value"}'
   ```
   3. **기대 결과**:
      - 응답: `{"message": "Hello, Middleware!"}`
      - 터미널 로그:
      ```bash
      2025-01-10 12:38:31,815 Request Body:{ 
         "key": "value" 
      }
      ```
