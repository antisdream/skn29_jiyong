# Docker Desktop과 Ubuntu 컨테이너 실행 정리

## 문서 구성

- `basic_docker.md`: Docker 이미지, 컨테이너 생성, 실행, 접속, 삭제 등 기본 명령어 정리
- `file_system.md`: Ubuntu 파일 시스템 구조와 Docker 안에서 Django 개발 환경을 실행하는 흐름 정리
- `file_manipulation.md`: 표준입출력, 리다이렉션, 파일 생성/확인/복사/이동/삭제/검색, 실습 시나리오 정리
- `permission.md`: `ls -l`, `chmod`, `chown`, `run_server.sh` 실행 권한과 오류 해결 정리
- `package_manager.md`: `apt`, `venv`, `pip`, Django 프로젝트 생성 흐름 정리
- `process_port.md`: `ps`, `lsof`, `netstat`, `kill`, Django 포트 접속 문제 해결 정리

## 1. Docker Desktop 설치 전 필수 설정

관리자 권한으로 PowerShell을 실행한 뒤 WSL 기능과 가상 머신 플랫폼을 활성화한다.

```powershell
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
```

WSL 최신 커널과 기본 배포판 설치를 진행한다.

```powershell
wsl --install
```

설치 후에는 PC를 재부팅하고 Docker Desktop을 실행한다.

## 2. Docker 설치 확인

PowerShell에서 Docker가 정상 설치되었는지 확인한다.

```powershell
docker --version
```

Docker Desktop이 실행 중이어야 위 명령어가 정상 동작한다.

## 3. Ubuntu 공식 이미지 다운로드

```powershell
docker pull ubuntu:22.04
```

이미지는 컨테이너를 만들기 위한 원본 템플릿이다.

## 4. Ubuntu 학습용 컨테이너 생성 및 접속

```powershell
docker run -it --name ubuntu-study ubuntu:22.04 bash
```

옵션 의미:

| 옵션 | 의미 |
|---|---|
| `-i` | 표준 입력을 유지한다. |
| `-t` | 터미널 환경을 만든다. |
| `--name ubuntu-study` | 컨테이너 이름을 `ubuntu-study`로 지정한다. |
| `ubuntu:22.04` | 사용할 이미지 이름이다. |
| `bash` | 컨테이너 안에서 bash 쉘을 실행한다. |

프롬프트가 아래처럼 바뀌면 Ubuntu 컨테이너 안으로 들어온 것이다.

```bash
root@컨테이너ID:/#
```

## 5. 컨테이너에서 나가기

```bash
exit
```

`exit`를 입력하면 컨테이너에서 빠져나와 Windows PowerShell로 돌아온다.
대화형으로 실행한 컨테이너는 보통 `exit`와 함께 중지된다.

## 6. 기존 Ubuntu 컨테이너 다시 접속

이미 만들어 둔 컨테이너가 있는지 확인한다.

```powershell
docker ps -a
```

중지된 `ubuntu-study` 컨테이너를 다시 시작한다.

```powershell
docker start ubuntu-study
```

실행 중인 컨테이너에 bash로 접속한다.

```powershell
docker exec -it ubuntu-study bash
```

한 번에 실행하려면 다음처럼 입력할 수 있다.

```powershell
docker start ubuntu-study; docker exec -it ubuntu-study bash
```

또는 시작과 접속을 한 번에 처리할 수도 있다.

```powershell
docker start -ai ubuntu-study
```

## 7. 컨테이너 목록 확인

현재 실행 중인 컨테이너만 확인:

```powershell
docker ps
```

중지된 컨테이너까지 모두 확인:

```powershell
docker ps -a
```

## 8. 자주 만나는 오류

### No such container

```text
Error response from daemon: No such container: ubuntu-study
```

이 오류는 `ubuntu-study`라는 이름의 컨테이너가 아직 없다는 뜻이다.
처음에는 `docker start`가 아니라 `docker run`으로 컨테이너를 생성해야 한다.

```powershell
docker run -it --name ubuntu-study ubuntu:22.04 bash
```

### doker 오타

명령어는 `doker`가 아니라 `docker`가 맞다.

```powershell
docker ps
docker ps -a
```

### Ubuntu에서 cd.. 오류

Windows cmd에서는 `cd..`를 쓰는 경우가 있지만, Ubuntu bash에서는 띄어써야 한다.

```bash
cd ..
```

### apt install 전에 apt update 필요

Ubuntu 최소 이미지에서는 패키지 목록을 먼저 갱신해야 한다.

```bash
apt update
apt install python3 python3-pip python3-venv -y
```

## 9. Django 개발용 Ubuntu 컨테이너 예시

Windows의 `C:\DjangoProject` 폴더를 컨테이너의 `/workspace`와 연결하고, 8000 포트를 열어 Django 개발 서버를 실행할 수 있게 만든다.

```powershell
docker run -it --name django-dev -p 8000:8000 -v C:\DjangoProject:/workspace ubuntu:22.04 bash
```

컨테이너 안에서 Python, pip, venv 패키지를 설치한다.

```bash
apt update
apt install python3 python3-pip python3-venv -y
```

작업 폴더로 이동한 뒤 Python 가상환경을 만들고 활성화한다.

```bash
cd /workspace
python3 -m venv venv
source venv/bin/activate
```

가상환경이 활성화된 상태에서 Django를 설치한다.

```bash
pip install django
```

설치 확인:

```bash
python --version
pip --version
django-admin --version
```

## 10. Django 프로젝트 생성 및 DB 초기화

가상환경이 활성화된 상태에서 `/workspace`에 Django 프로젝트를 생성한다.

```bash
cd /workspace
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

Django 개발 서버를 컨테이너 외부에서 접속할 수 있게 실행한다.

```bash
python3 manage.py runserver 0.0.0.0:8000
```

Windows 브라우저에서 접속한다.

```text
http://127.0.0.1:8000/
```

## 11. 현재 실습 완료 상태

이번 실습에서는 `/workspace/venv` 가상환경을 활성화한 뒤 Django 설치까지 완료했다.

설치 완료 로그:

```text
Successfully installed asgiref-3.11.1 django-6.0.6 sqlparse-0.5.5
```

설치 후 확인 명령어:

```bash
python -m django --version
django-admin --version
```

나중에 다시 접속할 때는 PowerShell에서 다음 명령어를 사용한다.

```powershell
docker start django-dev
docker exec -it django-dev bash
```

다시 접속한 뒤 기존 가상환경을 사용하려면 컨테이너 안에서 다음 명령어를 실행한다.

```bash
cd /workspace
source venv/bin/activate
```
