### 도커네트웍 컨테이너 통신
- Bridge : 도커의 기본 네트워크, 가상의 스위치 역할, 동일한 브릿지에 속한 컨테이너들은 가상 ip주소를 할당받아서 서로 직접 통신
- Host : 호스트 os의 네트워크 환경을 그대로 공유
- None : 컨테이너의 네트워크 스택을 비활성화해서 외부 및 컨테이너간의 네트워크를 원천 차단

### 사용자 정의 브릿지 네트워크의 장점
default bridge에서는 컨테이너통신이 ip주소로만 접근이 가능, 사용자 브릿지를 사용하면 도커의 내장 DNS서버가 동작을해서 컨테이너 이름으로 상대 컨테이너를 찾아가는 서비스 디스커버리 기능을 제공, 보안기능(불필요한 컨테이너 접근을 차단)

### 네트워크 내 컨테이너 가동(호스트 80포트 연동)
```
docker network create app-bridge-net
docker run -d --name test-backend --network app-bridge-net -p 80:80 nginx:alpine
```

### 확인 방법
### web에서는 http://127.0.0.1:80 OR http://127.0.0.1
### 컨테이너 내부   nginx 화면이 http로 리턴되는 것을 확인
```
docker run --rm --network app-bridge-net curlimages/curl -s http://test-backend
```
### 리소스 정리
```
docker stop test-backend
docker rm test-backend
docker network rm app-bridge-net
```
