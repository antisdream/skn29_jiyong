### SKN29-4th-4Team Docker 구성

- 원본 위치: `C:\python-src\4rd_PROJECT\SKN29-4th-4Team`
- 기준 커밋: `f08edc6`
- 포함: Docker Compose 파일, Django/FastAPI/Nginx/Frontend 구성, GitHub Actions 배포 워크플로, 통합 문서, 실행에 필요한 소스와 작은 참조 데이터
- 제외: `.env.local`, `.env`, `data/chroma`

로컬 실행 전에는 `.env.local.example`을 복사해서 `.env.local`을 만든 뒤 값을 확인한다.

```
docker compose --env-file .env.local -f docker-compose.local.yml up --build
```
