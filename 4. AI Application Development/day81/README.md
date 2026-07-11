# 81일차 (2026-07-08)

## 학습 주제

관리자 운영 기능, 작명 이력 관리, 실데이터 연동과 배포 안정화 작업을 정리했다.

## 핵심 작업

### 1. 관리자 페이지와 관리자 API

- Django Ninja 기반 관리자 API를 구성하고 관리자 전용 세션과 역할별 권한을 적용했다.
- 관리자 로그인, 로그아웃, 비밀번호 변경, 회원 목록·상세·상태 변경·삭제 기능을 연결했다.
- 공지사항, FAQ, 1:1 문의, 답변, 관리자 계정, 감사 로그 관리 API를 구성했다.
- 대시보드 통계, 시스템 상태, 점검 모드, API 사용량 조회를 관리자 화면과 연결했다.
- React 관리자 SPA를 별도 진입점과 라우팅으로 분리하고 화면별 Hook과 API 모듈을 정리했다.

### 2. 회원·작명 데이터 정합성 보완

- 이메일 중복 방지와 회원 상태 및 승인 상태 검증을 보완했다.
- 관리자 계정 삭제가 실제 완전 삭제로 동작하도록 Mutation과 안내 문구를 수정했다.
- 작명 이력과 결과 모델을 정리하고 관련 마이그레이션을 통합했다.
- 일별 통계와 트렌드 데이터 집계 구조를 추가했다.

### 3. 작명 결과와 이력 화면 개선

- 작명 결과를 생성 직후 자동 저장하도록 연결했다.
- 작명 기록에서 결과를 다시 생성하지 않고 저장된 결과를 그대로 확인하도록 상세 화면과 API를 추가했다.
- 동작하지 않던 북마크 버튼을 제거하고 저장·상세 이동 UI를 정리했다.
- 81수리·4격 요약, 한자 칩, 출처 표시, 검증 배지와 반응형 배치를 개선했다.
- 순우리말 이름 유형을 지원하고 인증서 PDF가 1페이지로 출력되도록 수정했다.

### 4. API와 배포 문제 수정

- 로그인·회원가입 요청에서 `API_BASE`가 빈 문자열로 처리되어 발생하던 405 오류를 수정했다.
- 관리자 화면이 Mock 데이터를 표시하던 문제를 실제 API 사용 설정으로 변경했다.
- GitHub Actions 자동 배포 과정에서 Django 마이그레이션이 실행되도록 배포 단계를 추가했다.
- Docker 새로고침 후 로컬 Chroma 인덱스가 갱신되는 흐름을 확인했다.

## 원본 구현 위치

- 관리자 API: `webapp/naming/api.py`, `webapp/naming/schemas.py`, `webapp/naming/auth.py`
- 관리자 프론트엔드: `frontend/src/app/AdminApp.tsx`, `frontend/src/app/screens/Admin*.tsx`, `frontend/src/api/admin.ts`
- 작명 이력: `frontend/src/app/screens/HistoryScreen.tsx`, `frontend/src/app/screens/HistoryDetailScreen.tsx`, `webapp/naming/views.py`
- 데이터 정합성: `webapp/naming/models.py`, `webapp/naming/migrations/`, `webapp/naming/tests.py`
- 배포 설정: `.github/workflows/deploy-4th.yml`, `docker-compose.4th.yml`

## 공개 정리 기준

관리자 화면 전체 코드, 환경 파일, Mock 계정 비밀번호, ChromaDB와 대용량 데이터는 Daily에 복사하지 않는다. 구현 내용과 학습 포인트만 기록하고 실제 프로젝트 코드는 별도 프로젝트 저장소에서 관리한다.

## 한 줄 요약

사용자 기능을 넘어 관리자 운영 기능과 작명 이력·실데이터 흐름을 연결하고, API 및 자동 배포 문제를 보완한 날이다.
