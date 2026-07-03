## 1. [초기 환경 구축] AWS 클라우드 자원 생성 가이드

가상 인프라 구축을 위해 AWS 웹 콘솔에 로그인한 뒤, 아래 순서대로 인프라 자원을 먼저 생성합니다.

### ① IAM 역할 (Role) 생성 (S3 접근 권한 부여)
액세스 키를 코드에 하드코딩하지 않고 EC2 서버 자체가 S3 버킷에 안전하게 접근할 수 있도록 IAM 역할을 부여합니다.

1. AWS 콘솔에서 **IAM** 검색 ➡️ 왼쪽 메뉴 **역할(Roles)** 클릭 ➡️ **역할 만들기** 클릭
2. 신뢰할 수 있는 엔터티 유형: **AWS 서비스** 선택
3. 서비스 또는 사례: **EC2** 선택 ➡️ 하단의 EC2 라디오 버튼 체크 후 **다음** 클릭
4. 권한 정책 추가: 검색창에 **`AmazonS3FullAccess`** 검색 후 체크 ➡️ **다음** 클릭
5. 역할 이름: **`skn29-ec2-s3-role`** 입력 ➡️ **역할 생성** 클릭

---

### ② 보안 그룹 (Security Group) 생성
네트워크 방화벽 역할을 하는 보안 그룹을 웹서버용과 DB용으로 각각 생성합니다.

#### 1. 웹서버 보안 그룹 (`skn29-django-sg`)
1. AWS 콘솔에서 **VPC** 또는 **EC2** 검색 ➡️ 왼쪽 메뉴 **보안 그룹** ➡️ **보안 그룹 생성** 클릭
2. 보안 그룹 이름: **`skn29-django-sg`**
3. 설명: `Django Web Server Security Group`
4. **인바운드 규칙(Inbound Rules) 추가**:
   * **규칙 1**: 유형 `SSH` (22 포트) / 소스 `내 IP` (보안상 내 컴퓨터에서만 접속 허용)
   * **규칙 2**: 유형 `HTTP` (80 포트) / 소스 `Anywhere-IPv4` (`0.0.0.0/0`)
   * **규칙 3**: 유형 `HTTPS` (443 포트) / 소스 `Anywhere-IPv4` (`0.0.0.0/0`)
5. **보안 그룹 생성** 클릭

#### 2. 데이터베이스 보안 그룹 (`skn29-rds-sg`)
1. 동일하게 **보안 그룹 생성** 클릭
2. 보안 그룹 이름: **`skn29-rds-sg`**
3. 설명: `PostgreSQL RDS Security Group`
4. **인바운드 규칙 추가**:
   * 유형: **`PostgreSQL`** (5432 포트 자동 지정)
   * 소스: 사용자 지정 선택 후, 우측 검색 칸을 눌러 위에서 만든 **`skn29-django-sg`** 선택 (EC2 웹서버에서만 DB에 들어올 수 있도록 차단 설정)
5. **보안 그룹 생성** 클릭

---

### ③ EC2 인스턴스 생성 및 탄력적 IP 연결

#### 1. EC2 인스턴스 생성
1. AWS 콘솔에서 **EC2** 검색 ➡️ **인스턴스 시작** 클릭
2. 이름: **`skn29-django-server`**
3. AMI(운영체제): **Ubuntu Server 26.04 LTS** (또는 최신 LTS 버전)
4. 인스턴스 유형: **`t3.micro`** (프리티어 대상)
5. 키 페어: 새 키 페어 생성 클릭 ➡️ 이름 **`skn29-key`**, 형식 **`.pem`** ➡️ 키 페어 생성 및 다운로드 (다운로드한 `.pem` 파일은 절대 잃어버리지 않도록 안전한 폴더에 보관)
6. 네트워크 설정 ➡️ **기존 보안 그룹 선택** 체크 ➡️ **`skn29-django-sg`** 보안 그룹 체크
7. 스토리지 구성: 기본 8GB를 프리티어 최대 사양인 **`20GB gp3`**로 변경
8. 인스턴스 시작 클릭

#### 2. 탄력적 IP (Elastic IP) 할당 및 연결 (서버 고정 IP 확보)
*서버를 껐다 켜도 IP 주소가 바뀌지 않도록 고정 IP를 매핑합니다.*
1. EC2 콘솔 왼쪽 메뉴 ➡️ **탄력적 IP** ➡️ **탄력적 IP 주소 할당** 클릭 ➡️ 하단 **할당** 클릭
2. 생성된 탄력적 IP 선택 ➡️ 우측 상단 **작업** ➡️ **탄력적 IP 주소 연결** 클릭
3. 리소스 유형: 인스턴스 ➡️ 인스턴스 검색 칸에서 `skn29-django-server` 선택 ➡️ 하단 **연결** 클릭

---

### ④ RDS (PostgreSQL) 데이터베이스 생성
1. AWS 콘솔에서 **RDS** 검색 ➡️ 왼쪽 메뉴 **데이터베이스** ➡️ **데이터베이스 생성** 클릭
2. 생성 방식: **표준 생성** ➡️ 엔진 옵션: **PostgreSQL** 선택
3. 템플릿: **프리 티어** 선택
4. 설정:
   * DB 인스턴스 식별자: **`skn29-django-db`**
   * 마스터 사용자 이름: **`postgres`**
   * 마스터 암호: 본인이 사용할 **보안성 높은 암호 입력 및 별도 기록**
5. 인스턴스 구성: **`db.t3.micro`** 또는 **`db.t4g.micro`**
6. 스토리지: **`gp3`**, 할당된 스토리지 **`20GB`** (스토리지 자동 조정 활성화는 비용 절감을 위해 체크 해제 권장)
7. 연결:
   * **퍼블릭 액세스**: **아니요** (보안 표준: 외부에서는 접속 불가하게 막고 VPC 내부의 EC2만 우회 연결하도록 설정)
   * VPC 보안 그룹: **기존 항목 선택** ➡️ 기본 지정된 default 그룹 해제 후, 위에서 만든 **`skn29-rds-sg`** 선택
8. **추가 구성** (맨 아래 아코디언 메뉴 클릭하여 펼치기):
   * **초기 데이터베이스 이름**: **`chatbotdb`** 입력 (이 값을 입력해 두어야 장고가 바로 연결하여 테이블을 생성할 수 있는 최초의 공간이 마련됩니다)
9. 맨 아래 **데이터베이스 생성** 클릭 (구축 완료 및 상태가 '사용 가능'으로 변할 때까지 약 5~10분 소요됩니다)

---

### ⑤ S3 버킷 생성 및 버킷 정책 설정
웹 화면을 그리는 정적 리소스(CSS/JS)를 브라우저에 뿌려주기 위해 S3 버킷을 열고 퍼블릭 읽기 권한을 부여합니다.

1. AWS 콘솔에서 **S3** 검색 ➡️ **버킷 만들기** 클릭
2. 버킷 이름: **`skn29-django-static-<본인 고유 식별값>`** 입력 (S3 이름은 전 세계 유일해야 하므로 본인 영문 이름 이니셜 등을 뒤에 붙입니다)
3. 객체 소유권: **ACL 비활성화됨(권장)** 선택
4. **이 버킷의 퍼블릭 액세스 차단 설정**:
   * **`모든 퍼블릭 액세스 차단` 체크 해제**
   * 하단에 나타나는 '현재 설정으로 인해... 알고 있습니다' 체크박스 체크 (사용자의 브라우저가 정적 디자인 파일들을 무리 없이 다운로드해 갈 수 있도록 퍼블릭 읽기 권한의 통로를 열어두는 과정입니다)
5. 맨 아래 **버킷 만들기** 클릭
6. 생성된 버킷 이름을 클릭해 들어간 뒤, 상단 **권한 (Permissions)** 탭 클릭
7. 스크롤을 내려 **버킷 정책 (Bucket policy)** 우측의 **편집(Edit)** 클릭 ➡️ 아래 JSON 복사/붙여넣기:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Sid": "PublicReadGetObject",
               "Effect": "Allow",
               "Principal": "*",
               "Action": "s3:GetObject",
               "Resource": "arn:aws:s3:::<자신의_버킷_이름>/*"
           }
       ]
   }
   ```
   * *주의: `<자신의_버킷_이름>` 부분을 실제 본인이 생성한 버킷 명칭으로 수정해야 합니다.*
8. **변경 사항 저장** 클릭

---

## 2. 개발 프로세스 설계 및 데이터 흐름

모든 클라우드 자원의 셋팅이 끝났습니다. 이제 이 자원들을 유기적으로 결합하여 코딩하기 위해 구축할 개발 자동화 아키텍처와 요청 처리 순서는 다음과 같습니다.

### 🔄 개발 작업 흐름 (Workflow)
```
[로컬 PC에서 수정] ──(git push)──> [GitHub Repository] ──(자동 배포)──> [GitHub Actions]
                                                                               │ (SSH 원격 제어)
                                                                               ▼
                                                                        [AWS EC2 서버]
                                                                  (배포 스크립트 실행 및 반영)
```

### 🖥️ 시스템 아키텍처 및 데이터 흐름
```
[사용자 브라우저]
       ↓ (HTTP 요청)
    [Nginx] (리버스 프록시 / 정적 파일 서빙)
       ↓ (유닉스 소켓: gunicorn.sock)
   [Gunicorn] (WSGI 미들웨어 서버)
       ↓ (장고 앱 구동)
   [Django]
      ├── [RDS (PostgreSQL)]  ← (데이터베이스 연동)
      ├── [S3 (Bucket)]       ← (정적/미디어 파일 위임)
      └── [OpenAI API]        ← (gpt-5-nano 실시간 추론)
```

---

## 3. [서버 최초 1회] EC2 기본 뼈대 초기 설정

자동 배포 스크립트가 EC2에서 정상적으로 명령을 수행하려면, 최초 1회 서버 디렉토리 구조와 Gunicorn/Nginx의 기본 뼈대가 만들어져 있어야 합니다.

### ① 서버 패키지 설치 및 디렉토리 구성
탄력적 IP(EIP) 주소를 복사한 뒤, 다운로드해 둔 `.pem` 키를 사용해 터미널 또는 MobaXterm으로 EC2 서버에 SSH 접속을 진행합니다.


```
# 서버 패키지 업데이트 및 빌드 도구 설치
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv python3-dev git build-essential libpq-dev nginx

# 프로젝트 디렉토리 생성 및 가상환경 활성화
mkdir ~/myproject && cd ~/myproject
python3 -m venv venv
source venv/bin/activate

# 필수 패키지 임시 설치 및 최초 프로젝트 생성
pip install django gunicorn
django-admin startproject config .
python manage.py migrate

# settings.py의 ALLOWED_HOSTS에 EC2 퍼블릭 IP 등록 (최초 1회 편집)
nano config/settings.py
# ALLOWED_HOSTS = ['<EC2 퍼블릭 IP>', 'localhost', '127.0.0.1']
```

### Gunicorn 서비스 생성 (/etc/systemd/system/gunicorn.service)
```
sudo nano /etc/systemd/system/gunicorn.service
```
아래 내용 입력
```
[Unit]
Description=gunicorn daemon for Django Chatbot
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/myproject
ExecStart=/home/ubuntu/myproject/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/home/ubuntu/myproject/gunicorn.sock \
          --timeout 120 \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
```
### Nginx 리버스 프록시 설정 (/etc/nginx/sites-available/myproject)
```
sudo nano /etc/nginx/sites-available/myproject
```
아래 설정을 입력 포트80(HTTP) 요청을 Gunicorn 소켁으로 흐르게 처리
```
server {
    listen 80;
    server_name <EC2 퍼블릭 IP 또는 도메인>;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /home/ubuntu/myproject/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/myproject/gunicorn.sock;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }
}
```
### 반영 및 서비스 활성화
```
sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo chmod 755 /home/ubuntu
sudo systemctl daemon-reload
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl restart nginx
```
### CI/CD 구축 Gihub Actions 자동 배포
### git 초기화 및 최초 push
```
# EC2 터미널에서 실행
cd ~/myproject
git init
git remote add origin https://github.com/<본인_GitHub_ID>/django-chatbot-preview.git

# requirements.txt 파일 생성
pip freeze > requirements.txt

# 민감 정보 보호를 위해 .gitignore 작성
echo ".env" >> .gitignore
echo "venv/" >> .gitignore
echo "__pycache__/" >> .gitignore

# 커밋 및 최초 푸시
git add .
git commit -m "Initial skeleton setup"
git push -u origin main
```
### Github Secrets 등록
github-settings - Secrets and variables - actions - new repository secret 접속
```
EC2_HOST: EC2 퍼블릭 IP 주소
EC2_USER: ubuntu
EC2_SSH_KEY: EC2 접속 시 사용하는 .pem 키 내용 전체 복사 (메모장으로 열어 첫 줄부터 끝 줄까지 그대로 복사)
```
### 로컬pc로 프로젝트 복사(clone)

### 배포 워크플로우 파일 생성
로컬(원격) pc 프로젝트 루트 .github/workflows/deploy.yml 파일생성
```
name: Deploy Chatbot to EC2

on:
  push:
    branches: [ main ] # main 브랜치로 push 발생 시 배포 구동

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: SSH Connection and Auto Deploy
        uses: appleboy/ssh-action@v1.2.2
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ${{ secrets.EC2_USER }}
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd ~/myproject
            source venv/bin/activate
            git pull origin main
            pip install -r requirements.txt
            python manage.py migrate --noinput
            python manage.py collectstatic --noinput
            sudo systemctl restart gunicorn
```
첫번째 자동 배포 테스트
```
git add .
git commit -m "add actions first"
git push origin main
```
github의 actions탭에서 초록색 체크마크 확인
### 로컬작업에서 RDS 연동(PostgreSQL)
로컬 터미널에서
```
pip install psycopg2-binary python-dotenv
pip freeze > requirements.txt
```
### 로컬 .env 파일 설정
```
DB_NAME=skn29db
DB_USER=postgres
DB_PASSWORD=<비번>
DB_HOST=skn29-db2.------rds.amazonaws.com  <RDS의 엔드포인트>
DB_PORT=5432
```
config/settings.py 수정
```
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
```
### git 배포 ( 자동 배포)
