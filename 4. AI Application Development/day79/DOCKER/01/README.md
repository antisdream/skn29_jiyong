### 1. 로컬에 장고 프로젝트 생성
```
django-admin startproject config .
```
requriements.txt
```
Django>=5.0,<6.0
psycopg>=3.1.18,<4.0
openai>=1.0.0
```


### 2. Dockerfile
```
FROM: 베이스가 되는 이미지를 지정합니다. 이미지 빌드의 시작점입니다.
WORKDIR: 컨테이너 내부에서 명령어가 실행될 작업 디렉토리를 정의합니다.
COPY: 호스트의 파일이나 디렉토리를 컨테이너 내부로 복사합니다.
RUN: 이미지 빌드 과정에서 실행할 명령어(패키지 설치 등)를 지정하여 새 레이어를 만듭니다.
ENV: 컨테이너 환경 변수를 정의합니다.
EXPOSE: 컨테이너가 런타임에 리스닝할 포트를 명시합니다.
CMD: 컨테이너가 시작될 때 실행할 기본 명령을 지정합니다. (단 한 번만 정의 가능)
```
```
# FROM  : 베이스가 되는 이미지를 지정, 이미지빌드의 시작점
# WORKDIR : 컨테이너 내부의 명령어가 실행될 작업 Directory
# COPY : 호스트의 파일이나 directory를 컨테이너 내부로 복사
# RUN : 이미지를 빌드하는 과정에서 실행하는 명령어(패키지설치등)
# ENV : 컨테이너에서 사용할 환경변수
# EXPOSE : 컨터이너가 런타임에 리스닝할 포트
# CMD : 컨테이너가 시작될때 실행할 기본 명령어(한번만 정의)

FROM python:3.11-slim

# PYTHON DONT WRITE BYTECODE=1
ENV PYTHONDONTWRITEBYTECODE=1
# PYTHON UNBUFFERED=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["python","manage.py", "runserver","0.0.0.0:8000"]
```
### 3. 도커 이미지 빌드 (Dockerfile의 내용을 실행)
```
docker build -t my-django-app:1.0 .
```
### 4. 빌드된 이미지로 부터 컨테이너를 실행
```
docker run -d -p 8000:8000 --name my-django-container my-django-app:1.0
```

### 5 컨터이너 접속
```
docker exec -it my-django-container bash
```
중지되면 재시작 또는 시작
```
docker start my-django-container
docker restart my-django-container
```


### 6. 컨터이너 가동중에 실시간 로그 확인
```
docker log -f my-django-container
```

### 7. 리소스 정리(도커 데스크탑이용 또는)
```
docker stop my-django-container
docker rm my-django-container
```
