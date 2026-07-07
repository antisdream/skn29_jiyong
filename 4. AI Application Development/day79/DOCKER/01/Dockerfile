# FROM : 베이스가 되는 이미지를 지정, 이미지빌드의 시작점
# WORKDIR : 컨테이너 내부의 명령어가 실행될 작업 Directory
# COPY : 호스트의 파일이나 Directory를 컨테이너 내부로 복사
# RUN : 이미지를 빌드하는 과정에서 실행하는 명령어(패키지 설치 등)
# ENV : 컨테이너에서 사용할 환경 변수
# EXPOSE : 컨테이너가 런타임에 리스닝 할 포트
# CMD : 컨테이너가 시작될 때 실행 할 기본 명령어(한번만 정의)

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

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]