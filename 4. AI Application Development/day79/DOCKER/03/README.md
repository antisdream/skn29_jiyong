### Django, PostgreSQL 컨테이너 통합
- 두 앱은 독립된 컨테이너에서 격리되어 실행
- 호스트와 공유하는 볼륨을 설계
- Django가 데이터베이스를 찾아가려면 호스트 정보로 데이터베이스 별칭을 사용하도록 구성, 사용자 브릿지 망에 소속된 장고 컨테이너가 내장 DNS 기능을 통해서 db-container라는 이름을 PostgreSQL의 내부 ip주소로 변환해서 연결

1. 전용 backend bridge network 생성
```
docker network create app-bridge-net
```
2. PostgreSQL 데이터 볼륨 생성, 데이터베이스 컨테이너 가동
```
docker volume create pg-data-vol
docker run -d --name db-container --network app-bridge-net -e POSTGRES_DB=django_db -e POSTGRES_USER=django_user -e POSTGRES_PASSWORD=django-pwd -v pg-data-vol:/var/lib/postgresql/data postgres:16-alpine
```
3. Django 웹 컨테이너를 데이터베이스 정보와 함께 가동
```
docker run -d --name web-container --network app-bridge-net -p 8000:8000 -v "${PWD}:/app" -e SQL_DATABASE=django_db -e SQL_USER=django_user -e SQL_PASSWORD=django-pwd -e SQL_HOST=db-container -e SQL_PORT=5432 my-django-app:1.0
```
