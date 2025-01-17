# 미들웨어 스터디

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

## **사용자 권한 관리 미들웨어**

### **구현된 미들웨어**
1. **사용자 권한 관리**:
    - JWT 인증 미들웨어에서 설정한 scope["state"]["user"] 정보를 활용하여 역할(Role) 기반의 접근 제어를 처리
    - 특정 역할(예: admin)만 접근 가능한 경로에 대해 권한을 확인
    - 요구되는 역할(required_roles)에 사용자의 역할이 포함되지 않은 경우, HTTP 403 응답 반환
    - 사용자 정보가 누락된 경우, HTTP 401 응답 반환
    - 관리자 전용 리소스(/admin)와 같이, 접근이 제한된 경로를 보호
    - 미들웨어 실행 순서를 보장하기 위해, JWT 인증 미들웨어 이후에 실행되도록 등록

### **삽질과 문제 해결 과정**
1. BaseHTTPMiddleware를 사용한 초기 접근
    - **초기 구현**:
      - BaseHTTPMiddleware를 사용하여 JWT 인증과 사용자 권한 관리를 각각의 미들웨어로 구현
      - request.state를 사용해 JWT 인증 미들웨어에서 사용자 정보를 저장하고, 권한 관리 미들웨어에서 이를 참조하려고 시도
    - **발생한 문제**:
      - request.state가 공유되지 않음
        - BaseHTTPMiddleware는 요청 객체를 새로 생성하므로, JWT 인증 미들웨어에서 설정한 request.state 값이 권한 관리 미들웨어에서 참조되지 않음
        - 각 미들웨어에서의 request가 서로 다른 객체로 동작
    - **결과**:
      - 권한 관리 미들웨어에서 항상 request.state가 비어 있는 상태로 동작
      - 권한 확인이 제대로 이루어지지 않음
      
2. Starlette 기반 미들웨어로 전환
    - **이유**:
      - Starlette 미들웨어는 scope 객체를 공유하므로, JWT 인증 미들웨어에서 설정한 데이터를 권한 관리 미들웨어에서 참조 가능
      - FastAPI의 BaseHTTPMiddleware와 달리, 요청-응답 흐름을 직접 관리하며 유연하게 처리 가능
    - **Starlette 기반 미들웨어로 변경 후 개선된 점**:
      - scope["state"]를 통해 미들웨어 간 데이터를 안전하게 공유 가능
      - 실행 순서를 명확히 관리할 수 있어, JWT 인증 미들웨어가 항상 권한 관리 미들웨어보다 먼저 실행되도록 설정 가능

3. lifespan 이벤트 처리
    - 문제:
      - Starlette 기반 미들웨어를 작성할 때, lifespan 이벤트를 처리하지 않으면 애플리케이션이 시작하거나 종료될 때 오류가 발생
      - 이는 lifespan 이벤트를 처리해야 하는 Starlette/ASGI 스펙 때문이라고 함
    - 해결:
      - 모든 미들웨어에서 scope["type"] == "lifespan" 조건을 추가하여, 애플리케이션 시작 및 종료 이벤트를 정상적으로 처리하도록 수정 
      - 이를 통해 서버 시작/종료 시 정상동작하지 않던 문제를 해결

4. 삽질과 배운 점
   - BaseHTTPMiddleware의 한계와 Starlette 기반 미들웨어의 필요성 
     - BaseHTTPMiddleware는 요청 객체를 새로 생성하여 미들웨어 간 데이터를 공유하지 못했음 
     - Starlette 기반 미들웨어로 전환하여 scope["state"]를 통해 데이터를 안전하게 공유 가능
   - Starlette 미들웨어 실행 순서 문제 
     - Starlette는 미들웨어를 스택 구조로 관리하며, 마지막에 등록된 미들웨어가 먼저 실행
     - 초기에는 순서를 잘못 설정하여, 권한 관리 미들웨어가 인증 미들웨어보다 먼저 실행되는 문제가 발생 
     - 이를 해결하기 위해 실행 순서를 재조정
   - lifespan 이벤트 처리의 중요성 
     - lifespan 이벤트를 처리하지 않아, 애플리케이션 시작 및 종료 단계에서 에러가 발생
     - 미들웨어에 if scope["type"] == "lifespan": 처리를 추가하여 문제를 해결
   - 인증과 권한 관리를 더 쉽게 처리하는 방법 
     - FastAPI의 Depends 사용:
       - 인증과 권한 관리는 미들웨어를 통해 구현할 수도 있지만, FastAPI의 Depends를 활용하면 더 직관적이고 간단하게 처리 가능
       - 이 방식은 경로별로 인증과 권한 검사를 유연하게 설정할 수 있어 더욱 적합할 수 있음
       - 하지만, 미들웨어는 요청 흐름 전반에 대해 동일한 처리가 필요한 경우 유용

## **학습 포인트**
1. BaseHTTPMiddleware의 한계
    - 요청 객체를 새로 생성하여 미들Middleware 간 데이터를 공유하지 못함
    - Starlette 기반 미들Middleware로 전환하면서 이러한 한계를 극복
2. Starlette 미들웨어의 실행 순서
   - Starlette는 스택 구조로 미들Middleware를 관리하므로, 마지막에 등록된 미들웨어가 먼저 실행
   - 이를 통해 실행 순서를 명확히 이해하고, 필요한 경우 미들Middleware 등록 순서를 조정하여 문제를 해결
3. lifespan 이벤트의 중요성
   - ASGI 애플리케이션의 정상적인 시작과 종료를 보장하기 위해 모든 미들Middleware에서 lifespan 이벤트를 적절히 처리해야 함
   - ``` python
     if scope["type"] == "lifespan": 
        return await self.app(scope, receive, send)
     ```
     를 추가하여 이 문제를 해결
4. Depends 사용: 경로별로 인증과 권한 검사가 다르게 적용될 때 적합
5. 미들웨어 사용: 모든 요청에 동일한 처리가 필요할 때 적합 (예: 로깅, 공통 인증)

## **요청 데이터 암호화 및 복호화 미들웨어**

### **구현된 미들웨어**
1. **요청 데이터 암호화 미들웨어**:
    - 클라이언트에서 요청한 데이터를 암호화하여 서버에 전송
    - 서버는 암호화된 데이터를 그대로 응답

2. **요청 데이터 복호화 미들웨어**:
    - 클라이언트에서 암호화된 데이터를 전송하면 서버는 이를 복호화
    - 복호화된 데이터를 JSON으로 변환하여 클라이언트에 반환

### **테스트 방법**
1. **요청 데이터를 암호화하여 반환**:
   - **Postman**
      - Method: `POST`
      - URL: `http://127.0.0.1:8000/secure-data`
      - Body: ` { "key": "value" }` JSON 형식
   - **기대 결과**:
        - 응답
        - Body:
        ```
        gAAAAABniJ-fHHVjhfvDr8mEo8TlZZjw8kj_12VIY6VtnxQWj9jChCAizPiGXsqTAUWrP0_faYf1AALXEHyFvU69pU-rlqpUQq1Hv2UhxxoHGLra-uT1aHw=
        ```
        - Headers:
        ```
        application/octet-stream
        ```

2. **암호화된 요청 데이터를 복호화하여 반환**:
   - **Postman**
      - Method: `POST`
      - URL: `http://127.0.0.1:8000/secure-data`
      - Headers: `Content-Type: application/octet-stream`
      - Body: ` gAAAAABniJ-fHHVjhfvDr8mEo8TlZZjw8kj_12VIY6VtnxQWj9jChCAizPiGXsqTAUWrP0_faYf1AALXEHyFvU69pU-rlqpUQq1Hv2UhxxoHGLra-uT1aHw= ` raw TEXT 형식
   - **기대 결과**:
        - 응답
        - Body:
        ```
        {
          "received": {
            "key": "value"
            }
        }
        ```
        - Headers:
        ```
        application/json
        ```

### **학습 포인트**
1. 암호화와 복호화의 분리: 요청 데이터를 암호화/복호화하는 미들웨어를 별도로 분리하여 관리
2. FastAPI의 요청 데이터 처리: request.body()를 사용하여 요청 데이터를 수동으로 처리
3. Postman을 활용한 테스트: Content-Type 설정을 통해 암호화된 데이터를 전송하고 복호화된 데이터를 검증

## **요청 데이터 검증 미들웨어**

### **구현된 미들웨어**
1. **요청 데이터 검증**:
    - 요청 본문 데이터를 Pydantic 모델과 비교하여 검증
    - 잘못된 데이터는 처리하지 않고, 상세한 오류 메시지와 함께 응답
    - POST, PUT, PATCH 요청에 대해서만 검증 수행
    - 유효성 검증 로직:
      - 필수 필드 확인
      - 데이터 유형 체크
      - 값의 범위 및 포맷 검증

### **테스트 방법**
1. **올바른 요청 데이터 전송**:
   - **Postman**
      - Method: `POST`
      - URL: `http://127.0.0.1:8000/validate-data`
      - Headers: `Content-Type`:`application/json`
      - Body: 
        ```
        {
           "name": "Hui Guk",
           "age": 30,
           "email": "test@example.com"
        }
        ```
   - **기대 결과**:
        - 응답
        - Body:
          ```
          {
             "message": "Valid data received"
          }
          ```
2. **잘못된 데이터 전송**:
   - **Postman**
      - Method: `POST`
      - URL: `http://127.0.0.1:8000/validate-data`
      - Headers: `Content-Type`:`application/json`
      - Body: 
        ```
        {
           "name": "Hui Guk"
        }
        ```
   - **기대 결과**:
        - 응답
        - Body:
          ```
          {
             "message": "Invalid request data",
             "errors": [
               {
                 "loc": ["age"],
                 "msg": "field required",
                 "type": "value_error.missing"
               },
               {
                 "loc": ["email"],
                 "msg": "field required",
                 "type": "value_error.missing"
               }
              ]
          }
          ```

3. **유효하지 않은 값**:
   - **Postman**
      - Method: `POST`
      - URL: `http://127.0.0.1:8000/validate-data`
      - Headers: `Content-Type`:`application/json`
      - Body: 
        ```
        {
           "name": "Hui Guk",
           "age": -5,
           "email": "not-an-email"
        }
        ```
   - **기대 결과**:
        - 응답
        - Body:
          ```
          {
             "message": "Invalid request data",
             "errors": [
               {
                  "loc": ["age"],
                  "msg": "ensure this value is greater than 0",
                  "type": "value_error.number.not_gt",
                  "ctx": {"limit_value": 0}
               },
               {
                  "loc": ["email"],
                  "msg": "value is not a valid email address",
                  "type": "value_error.email"
               }
              ]
          }
          ```

### **학습 포인트**
1. Pydantic의 강력한 유효성 검증 기능:
   - 데이터 유형, 필수 필드, 값의 범위 등을 유연하게 검증 가능
   - 상세한 오류 메시지 제공
2. 미들웨어와 유효성 검증의 결합:
   - 데이터를 사전에 검증하여 불필요한 리소스 낭비를 방지
3. Postman을 활용한 테스트: 
   - 다양한 테스트 시나리오를 통해 미들웨어의 동작 검증
