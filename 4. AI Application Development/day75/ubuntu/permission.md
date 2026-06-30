# 파일 권한(Permission) 체계 및 제어

## 1. 학습 목표

- 리눅스의 읽기, 쓰기, 실행 권한 구조를 이해한다.
- `ls -l` 결과에 나오는 `rw-r--r--`, `rwxr-xr-x` 같은 권한 표시를 읽는다.
- `chmod`로 파일 권한을 숫자 표기법과 기호 표기법으로 변경한다.
- `chown`으로 파일 소유자와 그룹을 변경하는 기본 형태를 익힌다.
- `Permission denied`, `command not found`, `No such file or directory` 오류의 차이를 구분한다.

## 2. 리눅스 소유권 구조

리눅스의 모든 파일과 디렉토리는 세 가지 대상에 대한 권한을 따로 관리한다.

| 대상 | 기호 | 설명 |
|---|---|---|
| 소유자 | `u` | 파일을 생성하거나 권한을 받은 사용자 |
| 그룹 | `g` | 소유자가 속한 사용자 그룹 |
| 기타 사용자 | `o` | 소유자와 그룹을 제외한 모든 사용자 |
| 전체 | `a` | `u + g + o` 전체 |

## 3. 권한의 종류

| 권한 | 기호 | 숫자값 | 파일에서 의미 | 디렉토리에서 의미 |
|---|---|---:|---|---|
| 읽기 | `r` | 4 | 파일 내용 확인 가능 | 목록 조회 가능 |
| 쓰기 | `w` | 2 | 파일 내용 수정 가능 | 하위 파일 생성/삭제 가능 |
| 실행 | `x` | 1 | 스크립트/프로그램 실행 가능 | `cd`로 진입 가능 |
| 없음 | `-` | 0 | 권한 없음 | 권한 없음 |

## 4. ls -l 권한 표시 읽기

```bash
ls -l
```

예시:

```text
-rwxr-xr-x 1 root root 40 Jun 30 14:35 run_server.sh
```

| 위치 | 예시 | 의미 |
|---|---|---|
| 1번째 | `-` | 일반 파일. 디렉토리는 `d`, 심볼릭 링크는 `l` |
| 2~4번째 | `rwx` | 소유자 권한 |
| 5~7번째 | `r-x` | 그룹 권한 |
| 8~10번째 | `r-x` | 기타 사용자 권한 |

자주 보는 권한:

```text
rwxr-xr-x = 755
rw-r--r-- = 644
rwx------ = 700
rwxrwxrwx = 777
```

## 5. 자주 쓰는 권한 값

| 권한 값 | 의미 | 사용 상황 |
|---|---|---|
| `755` | 소유자 rwx, 그룹/기타 r-x | 실행 스크립트, 웹 서버 디렉토리 |
| `644` | 소유자 rw-, 그룹/기타 r-- | 일반 설정 파일, HTML/CSS/JS 파일 |
| `600` | 소유자 rw-, 그룹/기타 권한 없음 | SSH 개인키, 비밀 파일 |
| `700` | 소유자 rwx, 그룹/기타 권한 없음 | 개인 실행 스크립트 |
| `777` | 모두 rwx | 임시 실습용. 실무에서는 거의 사용하지 않음 |
| `444` | 모두 r-- | 읽기 전용 문서 |

`chmod 777`은 모든 사용자가 읽기, 쓰기, 실행을 할 수 있게 만든다. 실습에서는 편하지만 운영 서버에서는 위험하다.

## 6. chmod 숫자 표기법

빈 파일을 만든 뒤 권한을 확인한다.

```bash
touch run_server.sh
ls -l run_server.sh
```

일반 파일은 보통 `644` 권한으로 생성된다.

```text
-rw-r--r-- 1 root root 0 Jun 30 14:35 run_server.sh
```

실행 스크립트 표준 권한으로 변경한다.

```bash
chmod 755 run_server.sh
ls -l run_server.sh
```

```text
-rwxr-xr-x 1 root root ... run_server.sh
```

모두에게 실행 권한까지 주는 실습용 권한:

```bash
chmod 777 run_server.sh
ls -l run_server.sh
```

```text
-rwxrwxrwx 1 root root ... run_server.sh
```

## 7. chmod 기호 표기법

소유자에게 실행 권한을 추가한다.

```bash
chmod u+x run_server.sh
```

전체 사용자에게 실행 권한을 추가한다.

```bash
chmod +x run_server.sh
```

기타 사용자의 읽기/쓰기 권한을 제거한다.

```bash
chmod o-rw run_server.sh
```

그룹에게 쓰기 권한을 추가한다.

```bash
chmod g+w run_server.sh
```

## 8. run_server.sh 생성과 실행

Django 개발 서버를 실행하는 스크립트를 만든다.

```bash
echo "python manage.py runserver 0.0.0.0:8000" > run_server.sh
```

또는 `cat`으로 직접 입력할 수 있다.

```bash
cat > run_server.sh
python manage.py runserver 0.0.0.0:8000
```

`cat > run_server.sh`는 멈춘 것이 아니라 입력을 기다리는 상태다. 내용을 입력한 뒤 `Ctrl + D`를 누르면 저장하고 종료된다.

실행 권한을 준다.

```bash
chmod 755 run_server.sh
```

현재 폴더의 스크립트는 파일명만으로 실행하지 않고 앞에 `./`를 붙인다.

```bash
./run_server.sh
```

아래처럼 실행하면 현재 폴더를 검색하지 않기 때문에 실패할 수 있다.

```bash
run_server.sh
```

오류 예시:

```text
bash: run_server.sh: command not found
```

## 9. 실행 권한 오류 확인과 해결

실행 권한을 제거한다.

```bash
chmod 644 run_server.sh
```

실행을 시도한다.

```bash
./run_server.sh
```

오류:

```text
bash: ./run_server.sh: Permission denied
```

해결:

```bash
chmod +x run_server.sh
./run_server.sh
```

## 10. 디렉토리 권한

디렉토리를 만들고 권한을 확인한다.

```bash
mkdir mydir
ls -ld mydir
```

디렉토리에 실행 권한(`x`)이 없으면 `cd`로 들어갈 수 없다.

```bash
chmod 644 mydir
cd mydir
```

오류:

```text
bash: cd: mydir: Permission denied
```

원복:

```bash
chmod 755 mydir
```

## 11. chown 소유자 변경

파일의 소유자를 변경한다.

```bash
chown 새소유자 파일명
```

소유자와 그룹을 함께 변경한다.

```bash
chown 사용자:그룹 파일명
```

디렉토리 전체를 재귀적으로 변경한다.

```bash
chown -R www-data:www-data /var/www/html
```

## 12. 자주 만나는 오류

| 오류 메시지 | 원인 | 해결 |
|---|---|---|
| `chmode: command not found` | 명령어 오타 | `chmod`로 입력 |
| `chmod: cannot access 'run_server.sh'` | 파일이 아직 없음 | 먼저 파일 생성 |
| `bash: run_server.sh: command not found` | 현재 폴더 실행 표시가 없음 | `./run_server.sh`로 실행 |
| `Permission denied` | 실행/쓰기/진입 권한 없음 | `chmod +x`, `chmod u+w`, `chmod 755` 등으로 수정 |
| `No such file or directory` | 경로 또는 파일 없음 | `pwd`, `ls -l`로 위치 확인 |

## 13. 서버 운영 관점의 예시

배포 스크립트 실행 권한 문제:

```bash
./deploy.sh
# bash: ./deploy.sh: Permission denied

ls -l deploy.sh
# -rw-r--r-- root root ...

chmod +x deploy.sh
./deploy.sh
```

웹 서버 정적 파일 권한 설정:

```bash
chown -R www-data:www-data /var/www/html
find /var/www/html -type f -exec chmod 644 {} \;
find /var/www/html -type d -exec chmod 755 {} \;
```

SSH 인증키 권한 문제 해결:

```bash
chmod 600 ~/.ssh/id_rsa
chmod 700 ~/.ssh
```
