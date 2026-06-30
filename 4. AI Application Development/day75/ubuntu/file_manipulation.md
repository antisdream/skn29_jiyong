# 파일 조작 및 텍스트 리다이렉션

## 1. 학습 목표

- 터미널에서 파일을 새로 만들고 텍스트를 입력하는 방법을 익힌다.
- 리다이렉션(`>`, `>>`, `2>`)으로 정상 출력과 에러 출력을 파일에 저장한다.
- 파일 생성, 확인, 복사, 이동, 삭제, 검색 명령어를 실습한다.
- 실무에서 자주 사용하는 백업, 로그 확인, 임시 파일 정리 흐름을 이해한다.

## 2. 표준 입출력 스트림

리눅스의 모든 프로세스는 기본적으로 3가지 입출력 채널을 가진다.

| 스트림 | 번호 | 설명 | 기본 연결 장치 |
|---|---:|---|---|
| 표준 입력(stdin) | `0` | 데이터를 읽어오는 채널 | 키보드 |
| 표준 출력(stdout) | `1` | 정상 결과를 출력하는 채널 | 터미널 화면 |
| 표준 에러(stderr) | `2` | 에러 메시지를 출력하는 채널 | 터미널 화면 |

리다이렉션은 이 채널의 연결 대상을 터미널 화면이 아니라 파일로 바꾸는 기능이다.

## 3. 리다이렉션 종류

| 기호 | 이름 | 동작 | 주의 |
|---|---|---|---|
| `>` | 출력 리다이렉션 | 정상 출력을 파일에 저장하고 기존 내용을 덮어씀 | 기존 파일 내용 삭제 |
| `>>` | 출력 추가 리다이렉션 | 정상 출력을 파일 끝에 추가 | 파일이 없으면 새로 생성 |
| `2>` | 에러 리다이렉션 | 에러 출력만 파일에 저장 | 정상 출력은 화면에 표시 |
| `2>>` | 에러 추가 리다이렉션 | 에러 출력을 파일 끝에 추가 | 에러 로그 누적에 사용 |
| `&>` | 전체 리다이렉션 | 정상 출력과 에러 출력을 한 파일에 저장 | bash에서 사용 |

에러 로그만 저장한다.

```bash
python3 app.py 2> error.log
```

정상 출력만 저장한다.

```bash
python3 app.py > output.log
```

정상 출력과 에러 출력을 각각 다른 파일에 저장한다.

```bash
python3 app.py > output.log 2> error.log
```

정상 출력과 에러 출력을 한 파일에 같이 저장한다.

```bash
python3 app.py > output.log 2>&1
```

## 4. Django manage.py 출력 저장 예시

`python3 manage.py`를 하위 명령 없이 실행하면 에러가 아니라 도움말이 정상 출력(stdout)으로 나온다.

```bash
python3 manage.py 2> error.log
```

위 명령은 에러 출력만 `error.log`로 보내기 때문에, 도움말은 화면에 보이고 `error.log`는 비어 있을 수 있다.
`output.log`는 만든 적이 없으므로 `cat output.log`를 실행하면 `No such file or directory`가 나온다.

도움말을 파일로 저장하려면 정상 출력을 저장해야 한다.

```bash
python3 manage.py > output.log
```

정상 출력과 에러 출력을 모두 저장하고 싶다면 다음처럼 실행한다.

```bash
python3 manage.py > output.log 2> error.log
```

## 5. 파일 생성

빈 파일을 만든다.

```bash
touch app.log
```

문자열을 파일에 저장한다.

```bash
echo "초기 설정값" > config.txt
```

기존 파일 뒤에 내용을 추가한다.

```bash
echo "추가 설정값" >> config.txt
```

여러 줄을 입력해서 파일을 만든다. 입력을 마칠 때는 `Ctrl + D`를 누른다.

```bash
cat > memo.txt
첫 번째 줄
두 번째 줄
```

## 6. 파일 내용 확인

| 명령어 | 특징 | 적합한 상황 |
|---|---|---|
| `cat` | 파일 전체 내용을 한 번에 출력 | 짧은 설정 파일 확인 |
| `head -n N` | 파일 앞 N줄만 출력 | 로그 시작 부분 확인 |
| `tail -n N` | 파일 끝 N줄만 출력 | 최근 로그 확인 |
| `less` | 페이지 단위로 파일 탐색 | 긴 파일 확인 |
| `wc -l` | 파일 줄 수 계산 | 로그 건수, 데이터 행 수 확인 |

```bash
cat config.txt
head -n 5 config.txt
tail -n 5 config.txt
wc -l config.txt
```

대용량 로그는 `less`로 열어 확인할 수 있다. `q`를 누르면 종료하고, `/검색어`로 검색한다.

```bash
less /var/log/syslog
```

Ubuntu 최소 이미지에서 `less`가 없으면 먼저 설치한다.

```bash
apt update
apt install less -y
```

## 7. 파일 복사, 이동, 삭제

### cp

파일을 복사한다.

```bash
cp config.txt config_backup.txt
```

디렉토리 전체를 복사한다.

```bash
cp -r /app/config /app/config_backup
```

권한과 수정 시간을 보존하며 복사한다.

```bash
cp -p deploy.sh deploy.sh.bak
```

덮어쓰기 전 확인을 받는다.

```bash
cp -i new_config.txt /etc/myapp/config.txt
```

### mv

파일 이름을 변경한다.

```bash
mv old_name.txt new_name.txt
```

파일을 다른 디렉토리로 이동한다.

```bash
mv app.log /var/log/myapp/
```

여러 파일을 한 디렉토리로 이동한다.

```bash
mv file1.txt file2.txt file3.txt /backup/
```

### rm

파일을 삭제한다.

```bash
rm config_old.txt
```

삭제 전 확인을 받는다.

```bash
rm -i important.txt
```

디렉토리와 내부 파일을 함께 삭제할 때는 `-r` 옵션을 사용한다.

```bash
rm -r sample_folder
```

강제 삭제는 매우 조심해서 사용한다.

```bash
rm -rf /tmp/test_build
```

아래 명령은 절대 실행하지 않는다.

```bash
# rm -rf /
# rm -rf /*
```

삭제 전에는 현재 위치와 삭제 대상을 먼저 확인한다.

```bash
pwd
ls -la
```

운영 환경에서는 삭제 대상을 변수에 담고 `echo`로 먼저 확인하는 습관을 들인다.

```bash
TARGET="/tmp/old_logs"
echo "삭제 대상: $TARGET"
rm -rf "$TARGET"
```

## 8. 파일과 디렉토리 탐색

현재 위치를 확인한다.

```bash
pwd
```

경로를 이동한다.

```bash
cd /var/log
cd ../config
cd ~
cd -
```

파일 목록을 확인한다.

```bash
ls -al
ls -lh
ls -lt
```

파일 이름을 기준으로 찾는다.

```bash
find /var/log -name "*.log"
find /app -name "config*" -type f
find /tmp -mtime +7
find / -size +100M
```

현재 위치 아래에서 찾을 때는 `.`을 사용한다.

```bash
find . -name "config.txt"
```

파일 내용에서 특정 문자열을 찾는다.

```bash
grep "초기" config.txt
```

## 9. 실습 명령어

### 실습 1: 빈 파일 생성 및 초기 내용 입력

```bash
cd /root/workspace
touch server_test.txt
echo "Server Started" > server_test.txt
cat server_test.txt
```

### 실습 2: 덧붙이기와 덮어쓰기 차이 확인

```bash
echo "Connection Open" >> server_test.txt
echo "User Login: admin" >> server_test.txt
cat server_test.txt
```

`>>`는 기존 내용을 유지하고 뒤에 추가한다.

```bash
echo "Database Disconnected" > server_test.txt
cat server_test.txt
```

`>`는 기존 내용을 모두 지우고 새 내용으로 덮어쓴다.

### 실습 3: 에러 로그 분리 수집

존재하지 않는 파일을 읽으면 에러가 발생한다.

```bash
cat /nonexistent_file 2> error.log
cat error.log
```

### 실습 4: 파일 내용 확인 도구 비교

```bash
for i in $(seq 1 30); do echo "Line $i: Event occurred"; done > sample.log

cat sample.log
head -n 5 sample.log
tail -n 5 sample.log
wc -l sample.log
```

### 실습 5: 파일 복사 및 백업

```bash
cp server_test.txt server_test.txt.bak

mkdir -p backup_storage/2024
mv server_test.txt.bak backup_storage/2024/
ls -l backup_storage/2024/
```

### 실습 6: find로 파일 탐색

```bash
find /root/workspace -name "*.txt"
find /root/workspace -mmin -10
```

### 실습 7: 실습 파일 정리

```bash
rm server_test.txt
rm sample.log
rm error.log
rm -rf backup_storage
```

## 10. 자주 겪는 실수와 주의사항

| 실수 유형 | 발생 상황 | 예방법 |
|---|---|---|
| `>`로 덮어쓰기 | `>>` 대신 `>` 입력 | 중요 파일은 먼저 `cp`로 백업 |
| `rm -rf` 경로 실수 | 변수 오타, 공백 경로 | 삭제 전 `echo $TARGET`으로 확인 |
| 원본 파일 직접 수정 | 백업 없이 설정 파일 편집 | `.bak` 백업 후 수정 |
| find 결과 없음 | 경로 오타, 권한 부족 | 경로와 옵션을 줄여서 다시 확인 |

## 11. 서버 운영 관점의 예시

### 웹서버 점검 페이지로 임시 전환

```bash
cp /var/www/html/index.html /var/www/html/index.html.bak
echo "<h1>서비스 점검 중입니다. 잠시 후 다시 접속해 주세요.</h1>" > /var/www/html/index.html
cp /var/www/html/index.html.bak /var/www/html/index.html
```

### 설정 파일 변경 전 백업

```bash
DATE=$(date +%Y%m%d_%H%M%S)
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.$DATE.bak
ls -lt /etc/nginx/*.bak
```

### 오래된 임시 파일 정리

```bash
find /tmp -mtime +7 -type f
find /tmp -mtime +7 -type f -delete
```
