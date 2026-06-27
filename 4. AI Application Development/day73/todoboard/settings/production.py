# 운영환경(배포)
from .base import *

DEBUG=False

# 호스트목록
ALLOWED_HOSTS=env.list('ALLOWED_HOSTS', default=['localhost','127.0.0.1'])

# PostgreSQL 설정
# django-environ의 env.db() 함수는 DATABASE_URL 환경변수를 읽어서 자동으로 설정값을 빌드
DATABASES = {
    'default': env.db('DATABASE_URL')
}

# 운영환경용 정적 파일 수집 경로 설정
# collectstatic 실행 시 앱 내부 및 STATICFILES_DIRS 안의 파일들이 지정한 폴더로 모임
# python manange.py collectstatic --settings=todoboard.settings.production
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 로컬 개발 및 Nginx 프록시/HTTPS 연동 환경을 위한 CSRF 신뢰 오리진 추가
CSRF_TRUSTED_ORIGINS = [
    'http://127.0.0.1:8000',
    'http://localhost:8000',
    'http://127.0.0.1',
    'http://localhost',
    'https://127.0.0.1',
    'https://localhost',
]

# ==============================================================================
# 보안 강화 설정 (HTTPS 및 쿠키 보안)
# ==============================================================================

# Nginx 리버스 프록시로부터 전달받은 SSL 헤더 검증 설정
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HTTPS 접속이 아닐 경우 자동으로 HTTPS로 리다이렉션 수행
SECURE_SSL_REDIRECT = True

# 세션 및 CSRF 쿠키의 Secure 플래그 활성화 (HTTPS를 통해서만 전송되도록 강제)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTP Strict Transport Security (HSTS) 활성화
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# 브라우저 MIME Sniffing 방어 필터 적용
SECURE_CONTENT_TYPE_NOSNIFF = True
