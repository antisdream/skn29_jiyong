# 프로세스 관리 및 포트 충돌 대응

## 1. 학습 목표

- 현재 실행 중인 프로세스를 확인한다.
- 포트가 어떤 프로세스에 의해 사용 중인지 찾는다.
- 포트 충돌이 발생했을 때 원인 프로세스를 종료한다.
- Docker에서 Django 서버를 실행할 때 `127.0.0.1`과 `0.0.0.0`의 차이를 이해한다.

## 2. 프로세스 기본 개념

프로세스는 실행 중인 프로그램이다. 같은 프로그램을 여러 번 실행하면 각각 다른 PID를 가진다.

| 용어 | 의미 |
|---|---|
| PID | 운영체제가 프로세스에 부여한 번호 |
| PPID | 부모 프로세스 ID |
| 포그라운드 | 현재 터미널을 점유하며 실행 중인 작업 |
| 백그라운드 | 터미널 뒤에서 실행되는 작업 |
| 데몬 | 항상 백그라운드에서 동작하는 서비스 |
| 좀비 프로세스 | 종료됐지만 부모가 회수하지 않아 남은 상태 |

## 3. 프로세스 조회

전체 프로세스를 확인한다.

```bash
ps aux
```

특정 프로세스만 찾는다.

```bash
ps aux | grep python
ps aux | grep nginx
```

CPU 사용량 순으로 본다.

```bash
ps aux --sort=-%cpu | head -20
```

메모리 사용량 순으로 본다.

```bash
ps aux --sort=-%mem | head -20
```

## 4. 포트 점유 확인

`lsof`가 없으면 먼저 설치한다.

```bash
apt update
apt install lsof -y
```

8000 포트를 누가 쓰는지 확인한다.

```bash
lsof -i :8000
```

예시:

```text
COMMAND PID USER FD TYPE DEVICE SIZE/OFF NODE NAME
python3 221 root 3u IPv4 99695 0t0 TCP localhost:8000 (LISTEN)
```

여기서 중요한 부분은 `localhost:8000`이다. 이 경우 컨테이너 내부에서만 듣고 있는 상태다.

Docker 밖의 Windows 브라우저에서 접속하려면 Django를 아래처럼 실행해야 한다.

```bash
python manage.py runserver 0.0.0.0:8000
```

정상적으로 외부 접속 가능하게 열리면 `lsof`에서 아래처럼 보인다.

```text
TCP *:8000 (LISTEN)
```

또는:

```text
TCP 0.0.0.0:8000 (LISTEN)
```

## 5. netstat과 ss

`netstat`은 Ubuntu 최소 이미지에 없을 수 있다.

```bash
netstat
# bash: netstat: command not found
```

필요하면 설치한다.

```bash
apt install net-tools -y
```

포트 확인:

```bash
netstat -tulpn | grep 8000
```

설치 없이 `ss`를 사용할 수도 있다. `ss`가 없다면 `iproute2`를 설치한다.

```bash
ss -ltnp | grep 8000
apt install iproute2 -y
```

## 6. 포트 충돌 대응 순서

포트가 이미 사용 중이면 보통 `Address already in use` 오류가 난다.

대응 흐름:

1. 어떤 포트가 문제인지 확인한다.
2. `lsof -i :포트번호`로 PID를 찾는다.
3. `ps aux | grep PID`로 어떤 프로세스인지 확인한다.
4. 종료해도 되는 프로세스인지 판단한다.
5. `kill PID`로 정상 종료한다.
6. 종료되지 않으면 `kill -9 PID`로 강제 종료한다.
7. 포트가 비었는지 다시 확인한다.

예시:

```bash
lsof -i :8000
ps aux | grep 221
kill 221
lsof -i :8000
```

강제 종료:

```bash
kill -9 221
```

## 7. Django 서버 포트 문제 해결

Docker 컨테이너 안에서 아래처럼 실행하면:

```bash
python manage.py runserver
```

서버가 컨테이너 내부의 `127.0.0.1:8000`에만 열린다.

```text
Starting development server at http://127.0.0.1:8000/
```

Windows 브라우저에서 접속하면 `ERR_EMPTY_RESPONSE`가 날 수 있다.

해결:

```bash
Ctrl + C
python manage.py runserver 0.0.0.0:8000
```

브라우저:

```text
http://127.0.0.1:8000/
```

## 8. 백그라운드 작업

명령어 뒤에 `&`를 붙이면 백그라운드로 실행된다.

```bash
sleep 300 &
sleep 400 &
```

현재 터미널의 백그라운드 작업 목록:

```bash
jobs
```

포그라운드로 가져오기:

```bash
fg %1
```

실행 중인 포그라운드 작업을 일시 정지:

```text
Ctrl + Z
```

일시 정지한 작업을 백그라운드에서 계속 실행:

```bash
bg %1
```

## 9. 프로세스 종료

일반 종료:

```bash
kill PID
```

강제 종료:

```bash
kill -9 PID
```

프로세스 이름으로 종료:

```bash
killall sleep
pkill -f "sleep 1000"
```

`kill -9`는 정리 작업 없이 즉시 종료하므로 먼저 `kill PID`를 시도하는 것이 좋다.

## 10. 실시간 모니터링

기본 내장 도구:

```bash
top
```

종료는 `q`를 누른다.

더 보기 좋은 모니터:

```bash
apt install htop -y
htop
```

종료는 `F10` 또는 `q`를 누른다.
