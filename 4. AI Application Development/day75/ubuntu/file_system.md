# Docker Ubuntu Django 개발 환경 메모

강사님 원본의 `file_system.md` 내용을 day75 실습 흐름에 맞게 보강한 문서다.

## 1. 리눅스 파일 시스템 구조

리눅스는 모든 파일과 디렉토리가 최상위 루트 디렉토리(`/`) 아래에 트리 구조로 배치된다.

| 경로 | 역할 |
|---|---|
| `/` | 파일 시스템의 최상위 루트 |
| `/bin` | 기본 실행 명령어가 위치하는 디렉토리 |
| `/etc` | 시스템과 서버 프로그램의 설정 파일 위치 |
| `/home` | 일반 사용자 계정의 홈 디렉토리 |
| `/root` | root 사용자의 홈 디렉토리 |
| `/tmp` | 임시 파일 저장 위치 |
| `/usr` | 사용자 프로그램과 라이브러리 위치 |
| `/var` | 로그, 캐시처럼 실행 중 계속 변하는 데이터 위치 |

Docker Ubuntu 컨테이너에 처음 접속하면 보통 `root@컨테이너ID:/#` 형태로 표시되며, 마지막의 `/`는 현재 위치가 루트 디렉토리라는 뜻이다.

## 2. 경로 이동과 탐색

현재 위치를 확인한다.

```bash
pwd
```

루트 디렉토리로 이동한다.

```bash
cd /
```

현재 디렉토리의 파일과 폴더를 확인한다.

```bash
ls
ls -la
```

절대 경로는 루트(`/`)를 기준으로 이동한다.

```bash
cd /etc
```

상대 경로는 현재 위치를 기준으로 이동한다. 한 단계 위로 이동할 때는 `cd..`가 아니라 `cd ..`처럼 띄어쓴다.

```bash
cd ..
```

## 3. 디렉토리 생성과 삭제

실습용 디렉토리를 생성한다.

```bash
mkdir /root/workspace
cd /root/workspace
```

빈 디렉토리를 삭제할 때는 `rmdir`을 사용한다.

```bash
mkdir temp_folder
rmdir temp_folder
```

`rmdir`은 폴더 안에 파일이 있으면 삭제하지 않는다. 파일이 들어 있는 폴더를 삭제할 때는 `rm -r`을 사용하지만, 복구가 어려우므로 경로를 꼭 확인한 뒤 실행해야 한다.

## 4. Windows 작업 폴더 준비

PowerShell에서 Django 프로젝트를 공유할 Windows 폴더를 준비한다.

```powershell
mkdir C:\DjangoProject
```

이미 폴더가 있으면 그대로 사용해도 된다.

## 5. Django 개발용 컨테이너 생성

```powershell
docker run -it --name django-dev -p 8000:8000 -v C:\DjangoProject:/workspace ubuntu:22.04 bash
```

옵션 의미:

| 옵션 | 의미 |
|---|---|
| `--name django-dev` | 컨테이너 이름을 `django-dev`로 지정 |
| `-p 8000:8000` | Windows 8000번 포트와 컨테이너 8000번 포트 연결 |
| `-v C:\DjangoProject:/workspace` | Windows 폴더를 컨테이너 `/workspace`에 연결 |
| `ubuntu:22.04` | Ubuntu 22.04 이미지 사용 |

## 6. Python과 Django 설치

컨테이너 안에서 실행한다. Ubuntu 최소 이미지에서는 패키지 목록을 먼저 갱신해야 한다.

```bash
apt update
apt install python3 python3-pip python3-venv -y
```

설치 확인:

```bash
python3 --version
pip3 --version
```

## 7. 작업 폴더 이동 및 가상환경 생성

```bash
cd /workspace
pwd
```

`/workspace` 안에서 만든 파일은 Windows의 `C:\DjangoProject`에서도 바로 확인할 수 있다.

Python 가상환경을 만든다.

```bash
python3 -m venv venv
```

가상환경을 활성화한다.

```bash
source venv/bin/activate
```

프롬프트 앞에 `(venv)`가 붙으면 가상환경이 활성화된 상태다.

가상환경 안에 Django를 설치한다.

```bash
pip install django
django-admin --version
```

## 8. Django 프로젝트 생성 예시

```bash
django-admin startproject config .
```

초기 데이터베이스 테이블을 생성한다.

```bash
python3 manage.py migrate
```

관리자 계정을 생성한다.

```bash
python3 manage.py createsuperuser
```

Django 개발 서버를 실행한다.

```bash
python3 manage.py runserver 0.0.0.0:8000
```

브라우저에서 접속:

```text
http://127.0.0.1:8000/
```

현재 실습에서는 Django 설치까지 완료했다.

```text
Successfully installed asgiref-3.11.1 django-6.0.6 sqlparse-0.5.5
```

설치 확인:

```bash
python -m django --version
django-admin --version
```

## 9. 컨테이너에서 나간 뒤 다시 접속

컨테이너 안에서 나가기:

```bash
exit
```

PowerShell에서 다시 시작하고 접속:

```powershell
docker start django-dev
docker exec -it django-dev bash
```

다시 접속한 뒤 기존 가상환경을 사용하려면 컨테이너 안에서 다음을 실행한다.

```bash
cd /workspace
source venv/bin/activate
```

## 10. 컨테이너가 이미 존재한다는 오류

같은 이름의 컨테이너가 이미 있으면 `docker run --name django-dev`는 다시 실행할 수 없다.

```text
Conflict. The container name "/django-dev" is already in use
```

이 경우 새로 만들지 말고 기존 컨테이너에 다시 접속한다.

```powershell
docker start django-dev
docker exec -it django-dev bash
```

완전히 지우고 다시 만들 때만 삭제한다.

```powershell
docker rm -f django-dev
```

## 11. 프로젝트 구조 확인

Windows의 `C:\DjangoProject`와 Docker Ubuntu의 `/workspace`는 볼륨으로 연결되어 있다.

```text
Windows

C:\DjangoProject
        |
        | Volume
        v
Docker Ubuntu

/workspace
        |
        |-- manage.py
        |-- db.sqlite3
        `-- config
            |-- settings.py
            |-- urls.py
            |-- asgi.py
            `-- wsgi.py
```

Windows에서 파일을 수정하면 컨테이너의 `/workspace`에도 바로 반영되고, 컨테이너에서 만든 파일도 Windows의 `C:\DjangoProject`에서 확인할 수 있다.

## 12. 전체 명령어 순서

처음부터 Django 개발 환경을 만드는 흐름은 다음과 같다.

```powershell
docker run -it --name django-dev -p 8000:8000 -v C:\DjangoProject:/workspace ubuntu:22.04 bash
```

컨테이너 안에서 실행한다.

```bash
apt update
apt install python3 python3-pip python3-venv -y

cd /workspace
python3 -m venv venv
source venv/bin/activate

pip install django

django-admin startproject config .
python3 manage.py migrate
python3 manage.py createsuperuser
python3 manage.py runserver 0.0.0.0:8000
```

## 13. 브라우저 접속 주소

Django 개발 서버를 `0.0.0.0:8000`으로 실행했다면 Windows 브라우저에서 접속할 수 있다.

```text
http://localhost:8000
http://127.0.0.1:8000
```

관리자 페이지는 다음 주소로 접속한다.

```text
http://localhost:8000/admin
```

## 14. 개발 중 자주 쓰는 명령

컨테이너 재접속:

```powershell
docker start django-dev
docker exec -it django-dev bash
```

프로젝트 폴더 이동 및 가상환경 활성화:

```bash
cd /workspace
source venv/bin/activate
```

Django 개발 명령:

```bash
python3 manage.py runserver 0.0.0.0:8000
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py createsuperuser
```

## 15. 참고 사항

이 방식은 Docker 학습을 위한 가장 단순한 Django 개발 환경이다. 실무에서는 보통 다음 구성을 함께 사용한다.

- Python 공식 이미지(`python:3.12-slim`) 기반 컨테이너
- `requirements.txt`로 패키지 관리
- `Dockerfile`을 사용한 이미지 빌드
- `docker compose`를 이용한 Django, PostgreSQL, Redis 등 멀티 컨테이너 구성
- 개발 서버 대신 Gunicorn, Nginx를 사용한 운영 환경 구성
