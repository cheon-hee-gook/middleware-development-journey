# 미들웨어 개발 스터디

### **실행 방법**
1. **Git 레포지토리 클론**:
   ```
   https://github.com/cheon-hee-gook/middleware-development-journey.git
   ```

2. **Python 환경 설정**:
   ```
   python3 -m venv venv
   source venv/bin/activate  # Windows에서는 venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **서버 실행**:
   ```
   uvicorn app.main:app --reload
   ```

## **요청 로깅 미들웨어**

### **구현된 미들웨어**
1. **기본 요청 로깅**: 요청 URL, 메서드, 헤더 정보를 로깅
2. **요청 본문 로깅**: 요청 Body 데이터를 로깅
3. **응답 로깅**: 응답 상태 코드와 본문 데이터를 로깅
4. **요청 처리 시간 로깅**: 요청 처리 시간을 측정하여 로깅

### **테스트 방법**
1. **기본 요청 로깅**:
   - **Postman**
      - Method: `GET`
      - URL: `http://127.0.0.1:8000/`
   - **curl**
      ```
      curl -X GET http://127.0.0.1:8000/
      ```
   - **기대 결과**:
        - 응답: `{"message": "Hello, Middleware!"}`
        - 터미널 로그:
        ```
        2025-01-10 11:49:27,445 Request URL: http://127.0.0.1:8000/
        2025-01-10 11:49:27,445 Request Method: GET
        2025-01-10 11:49:27,445 Request Headers: Headers({'user-agent': 'PostmanRuntime/7.37.3', 'accept': '*/*', 'postman-token': '69049fd3-fd8b-40bb-b74e-8818f3284824', 'host': '127.0.0.1:8000', 'accept-encoding': 'gzip, deflate, br', 'connection': 'keep-alive'})
        ```

2. **요청 본문 로깅**:
   - **Postman**
      - Method: `POST`
      - URL: `http://127.0.0.1:8000/data`
      - Body: `{"key: "value"}` JSON 형식
   - **curl**
   ```
   curl -X POST http://127.0.0.1:8000/data -H "Content-Type: application/json" -d '{"key": "value"}'
   ```
   - **기대 결과**:
      - 응답: `{"message": "Hello, Middleware!"}`
      - 터미널 로그:
      ```
      2025-01-10 12:38:31,815 Request Body:{ 
         "key": "value" 
      }
      ```

3. **응답 로깅**:
   - **Postman**
      - Method: `GET`
      - URL: `http://127.0.0.1:8000`
   - **curl**
   ```
   curl -X GET http://127.0.0.1:8000/
   ```
   - **기대 결과**:
      - 응답: `{"message": "Hello, Middleware!"}`
      - 터미널 로그:
      ```
      2025-01-10 13:01:21,826 Response Status Code: 200
      2025-01-10 13:01:21,826 Response Body: {"message":"Hello, Middleware!"}
      ```

4. **요청 처리 시간 로깅**:
   - **Postman**
      - Method: `GET`
      - URL: `http://127.0.0.1:8000/data`
   - **curl**
   ```
   curl -X GET http://127.0.0.1:8000/data
   ```
   - **기대 결과**:
      - 응답: `{"1": "abc@abc", ...}`
      - 터미널 로그:
      ```
      2025-01-10 13:15:00,349 Processing Time: 3.0949 seconds
      ```

## **학습 포인트**
1. FastAPI 미들웨어 구현 원리
2. 스트리밍 응답 로깅 문제 해결
3. 요청 처리 시간 측정 및 로깅

## **JWT 인증 미들웨어**

### **구현된 미들웨어**
1. **JWT 인증 처리**:
   - 요청 헤더에서 JWT를 추출하고 디코딩하여 사용자 인증을 처리
   - 인증 제외 경로(/, /token)를 설정하여 특정 경로는 인증을 우회 
   - 잘못된 입력(토큰 누락, 잘못된 토큰, 만료된 토큰)에 대해 적절한 HTTP 401 응답을 반환 
   - 인증 성공 시 사용자 정보를 request.state.user에 저장

### **테스트 방법**
1. **JWT 인증 처리**:
   - **Postman**
      - Method: `POST`
      - URL: `http://127.0.0.1:8000/token`
      - Body: `{ "username": "user1", "password": "password1"}` JSON 형식
   - **curl**
      ```
      curl -X POST http://127.0.0.1:8000/token \
     -H "Content-Type: application/json" \
     -d '{"username": "user1", "password": "password1"}'
      ```
   - **기대 결과**:
        - 응답:
        ```
        {
           "access_token": "<jwt_token>",
           "token_type": "Bearer"
        }
        ```
        - 터미널 로그:
        ```
        INFO:     127.0.0.1:65277 - "POST /token HTTP/1.1" 200 OK
        ```

2. **보호된 경로 요청**:
   - **Postman**
      - Method: `GET`
      - URL: `http://127.0.0.1:8000/protected`
      - Header: `Authorization: Bearer <jwt_token>`
   - **curl**
      ```
      curl -X GET http://127.0.0.1:8000/protected \
      -H "Authorization: Bearer <jwt_token>"
      ```
   - **기대 결과**:
        - 응답:
           ```
           {
              "message": "Hello, user1!"
           }
           ```
        - 터미널 로그:
           ```
           INFO:     127.0.0.1:65337 - "GET /protected HTTP/1.1" 200 OK
           ```
3. **인증 실패 테스트**:
   1. 토큰 없음
      - **요청**: GET /protected (헤더에 Authorization 없음)
      - **기대 결과**:
         ```
        {
           "message": "Unauthorized: No token provided"
        }
         ```
   2. 잘못된 토큰
      - **요청**: GET /protected (헤더에 잘못된 토큰 전달)
         ```
         curl -X GET http://127.0.0.1:8000/protected \
         -H "Authorization: Bearer invalid_token"
         ```
      - **기대 결과**:
         ```
        {
           "message": "Unauthorized: Invalid or expired token"
        }
         ```
## **학습 포인트**
1. JWT 인증 미들웨어 구현 원리: BaseHTTPMiddleware를 사용해 요청 헤더에서 JWT를 추출하고 검증
2. 인증 제외 경로 설정: 인증이 필요하지 않은 경로(/, /token)는 우회 처리
3. 요청 상태에 사용자 정보 저장: 인증된 사용자 정보를 request.state.user에 저장하여 이후 경로에서 활용
