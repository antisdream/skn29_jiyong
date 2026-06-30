# 패키지 매니저(apt)를 통한 관리

## 1. 학습 목표

- Ubuntu의 표준 패키지 관리자 `apt`의 역할을 이해한다.
- `apt update`, `apt install`, `apt upgrade`, `apt remove`, `apt purge`의 차이를 구분한다.
- 개발과 운영에서 자주 쓰는 도구(`curl`, `lsof`, `vim`, `net-tools`, `htop` 등)를 설치한다.
- 패키지 검색, 상세 정보 확인, 설치 여부 확인, 제거 흐름을 익힌다.
- Django 개발 환경 구성에 `apt`, `venv`, `pip`이 각각 어디에서 쓰이는지 정리한다.

## 2. 패키지 매니저란?

패키지 매니저는 운영체제 공식 저장소에서 프로그램을 내려받고, 필요한 의존성까지 자동으로 설치·업데이트·삭제해주는 도구다.

| 항목 | 직접 설치 | 패키지 매니저 |
|---|---|---|
| 의존성 처리 | 직접 해결 | 자동 해결 |
| 보안 검증 | 직접 확인 | 공식 저장소 서명 검증 |
| 업데이트 | 직접 재설치 | `apt upgrade` |
| 제거 | 파일 직접 삭제 | `apt remove`, `apt purge` |
| 추천 상황 | 공식 저장소에 없는 최신 도구 | 안정성이 중요한 일반 설치 |

## 3. apt 명령어 구조

```bash
apt [동작] [패키지명] [옵션]
```

| 명령 | 의미 |
|---|---|
| `apt update` | 원격 저장소의 패키지 목록을 최신으로 갱신 |
| `apt upgrade` | 설치된 패키지를 최신 버전으로 업그레이드 |
| `apt install 패키지명` | 패키지 설치 |
| `apt remove 패키지명` | 패키지 제거, 설정 파일은 일부 유지 |
| `apt purge 패키지명` | 패키지와 설정 파일까지 제거 |
| `apt autoremove` | 더 이상 필요 없는 의존성 제거 |
| `apt search 검색어` | 패키지 검색 |
| `apt show 패키지명` | 패키지 상세 정보 확인 |
| `apt list --installed` | 설치된 패키지 목록 확인 |

## 4. apt update와 apt upgrade 차이

`apt update`는 설치가 아니라 목록 갱신이다.

```bash
apt update
```

`apt upgrade`는 실제로 설치된 패키지를 새 버전으로 올린다.

```bash
apt upgrade
```

보통 새 컨테이너에서는 패키지 설치 전에 먼저 `apt update`를 실행한다.

```bash
apt update
apt install python3 python3-pip python3-venv -y
```

`apt update` 없이 설치하면 `Unable to locate package`가 나올 수 있다.

## 5. 자주 쓰는 실무 도구 패키지

| 패키지 | 용도 | 사용 예 |
|---|---|---|
| `curl` | URL 요청, API 테스트 | `curl http://localhost:8000` |
| `wget` | 파일 다운로드 | 배포 파일 다운로드 |
| `vim` | 터미널 편집기 | 서버 설정 파일 수정 |
| `nano` | 쉬운 터미널 편집기 | 간단한 파일 수정 |
| `lsof` | 열린 파일/포트 조회 | `lsof -i :8000` |
| `net-tools` | `netstat` 포함 | `netstat -tulpn` |
| `htop` | 프로세스 모니터 | CPU/메모리 확인 |
| `tree` | 디렉토리 구조 출력 | 프로젝트 구조 파악 |
| `unzip` | zip 압축 해제 | 배포 파일 압축 해제 |
| `git` | 버전 관리 | 소스 코드 clone |

한 번에 설치:

```bash
apt update
apt install -y curl wget vim nano lsof net-tools htop tree unzip git
```

설치 확인:

```bash
curl --version
lsof -v
netstat --version
vim --version | head -n 1
```

## 6. 패키지 검색과 정보 확인

패키지 이름을 검색한다.

```bash
apt search tree
```

패키지 상세 정보를 본다.

```bash
apt show curl
```

현재 설치된 패키지 목록을 본다.

```bash
apt list --installed
```

특정 패키지가 설치됐는지 확인한다.

```bash
apt list --installed | grep curl
```

명령어 위치를 확인한다.

```bash
which curl
which lsof
which netstat
```

## 7. vim 기본 사용법

파일 열기:

```bash
vim /root/workspace/test_edit.txt
```

기본 흐름:

```text
i      입력 모드 진입
Esc    일반 모드로 복귀
:w     저장
:q     종료
:wq    저장 후 종료
:q!    저장하지 않고 종료
/검색어 검색
dd     현재 줄 삭제
yy     현재 줄 복사
p      붙여넣기
```

저장 후 확인:

```bash
cat /root/workspace/test_edit.txt
```

## 8. 패키지 제거

패키지만 제거하고 설정 파일은 일부 남긴다.

```bash
apt remove curl -y
```

설정 파일까지 제거한다.

```bash
apt purge curl -y
```

더 이상 필요 없는 의존성을 정리한다.

```bash
apt autoremove -y
```

## 9. 자주 발생하는 오류와 해결

| 오류 메시지 | 원인 | 해결 |
|---|---|---|
| `Unable to locate package` | 패키지 목록 미갱신 또는 패키지명 오류 | `apt update` 후 재시도 |
| `E: Could not get lock` | 다른 apt 프로세스 실행 중 | 잠시 기다린 뒤 재시도 |
| 설치 후 명령어 없음 | 패키지 미설치 또는 경로 갱신 문제 | `which 명령어`, `hash -r` 확인 |
| 의존성 충돌 | 패키지 버전 충돌 | `apt -f install` 시도 |

## 10. Django 개발 환경 구성에 적용

PowerShell에서 Windows 작업 폴더를 준비한다.

```powershell
mkdir C:\DjangoProject
```

`C:\DjangoProject`를 Ubuntu 컨테이너의 `/workspace`와 연결한다.

```powershell
docker run -it --name django-dev -p 8000:8000 -v C:\DjangoProject:/workspace ubuntu:22.04 bash
```

이미 `django-dev` 컨테이너가 있으면 새로 만들지 않고 다시 접속한다.

```powershell
docker start django-dev
docker exec -it django-dev bash
```

컨테이너 안에서 Python과 venv를 설치한다.

```bash
apt update
apt install python3 python3-pip python3-venv -y
```

작업 폴더로 이동한다.

```bash
cd /workspace
```

가상환경을 생성하고 활성화한다.

```bash
python3 -m venv venv
source venv/bin/activate
```

Django를 설치한다.

```bash
pip install django
django-admin --version
```

Django 프로젝트를 생성한다. 마지막의 `.`을 붙이면 `/workspace` 바로 아래에 `manage.py`가 생긴다.

```bash
django-admin startproject config .
```

DB 초기화와 상태 확인:

```bash
python manage.py migrate
python manage.py check
```

Docker 외부 Windows 브라우저에서 접속하려면 `0.0.0.0:8000`으로 실행한다.

```bash
python manage.py runserver 0.0.0.0:8000
```

브라우저 접속:

```text
http://127.0.0.1:8000/
```

## 11. 운영 관점 예시

이미지 처리 라이브러리 누락:

```bash
apt update
apt install -y libpng-dev
pip install Pillow
```

서버에서 설정 파일 직접 수정:

```bash
vim /etc/nginx/nginx.conf
nginx -t
nginx -s reload
```

Dockerfile에서 패키지 설치:

```dockerfile
FROM ubuntu:22.04

RUN apt update && apt install -y \
    curl \
    vim \
    git \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*
```

Dockerfile에서는 `apt update`와 `apt install`을 같은 `RUN`에 묶는 것이 좋다.
