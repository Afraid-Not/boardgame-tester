# 보드게임 밸런스 테스터 — 디렉토리 구조 및 필요 사항

## 1. 디렉토리 구조

```
boardgame-tester/
├── frontend/                     # Next.js 프론트엔드
│   ├── public/                   # 정적 파일 (이미지, 아이콘)
│   ├── src/
│   │   ├── app/                  # Next.js App Router
│   │   │   ├── page.tsx          # 랜딩 페이지
│   │   │   ├── games/
│   │   │   │   ├── page.tsx      # 게임 목록
│   │   │   │   ├── new/
│   │   │   │   │   └── page.tsx  # 새 게임 생성 (규칙서 업로드)
│   │   │   │   └── [id]/
│   │   │   │       ├── page.tsx  # 게임 상세 (파싱 결과, 환경 코드)
│   │   │   │       ├── train/
│   │   │   │       │   └── page.tsx  # 학습 실행 + 진행률 모니터링
│   │   │   │       └── report/
│   │   │   │           └── page.tsx  # 밸런스 리포트 + 가이드라인
│   │   │   └── layout.tsx        # 공통 레이아웃 (사이드바, 헤더)
│   │   ├── components/           # 재사용 컴포넌트
│   │   │   ├── ui/               # 기본 UI (버튼, 카드, 모달 등)
│   │   │   ├── charts/           # 차트 컴포넌트 (승률 그래프, 히트맵)
│   │   │   ├── game/             # 게임 관련 (규칙 입력 폼, 파싱 결과 뷰어)
│   │   │   ├── training/         # 학습 관련 (진행률 바, 로그 뷰어)
│   │   │   └── report/           # 리포트 관련 (밸런스 스코어, 가이드라인 카드)
│   │   ├── hooks/                # 커스텀 훅
│   │   ├── lib/                  # 유틸리티, API 클라이언트, Supabase 클라이언트
│   │   ├── types/                # TypeScript 타입 정의
│   │   └── styles/               # 글로벌 스타일
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── backend/                      # FastAPI 백엔드
│   ├── app/
│   │   ├── main.py               # FastAPI 앱 엔트리포인트
│   │   ├── config.py             # 환경 변수, 설정
│   │   ├── api/                  # API 라우터
│   │   │   ├── games.py          # /api/games 엔드포인트
│   │   │   ├── training.py       # /api/training 엔드포인트
│   │   │   └── reports.py        # /api/reports 엔드포인트
│   │   ├── models/               # Pydantic 모델 (요청/응답 스키마)
│   │   │   ├── game.py
│   │   │   ├── training.py
│   │   │   └── report.py
│   │   ├── services/             # 비즈니스 로직
│   │   │   ├── game_service.py   # 게임 CRUD
│   │   │   ├── parse_service.py  # 규칙 파싱 (OpenAI API 호출)
│   │   │   ├── train_service.py  # 학습 작업 관리 + 로컬 실행
│   │   │   └── report_service.py # 리포트 생성
│   │   └── db/                   # Supabase 연동
│   │       ├── client.py         # Supabase 클라이언트 초기화
│   │       └── queries.py        # DB 쿼리 함수
│   ├── requirements.txt
│   └── Dockerfile
│
├── rl_engine/                    # 강화학습 엔진
│   ├── environments/             # 게임 환경
│   │   ├── base_env.py           # 공통 RL 환경 인터페이스 (Gymnasium 기반)
│   │   └── economic_board/       # 경제 보드 장르 (MVP)
│   │       ├── template.py       # 경제 보드 환경 템플릿
│   │       ├── components.py     # 맵, 칸, 자원 등 컴포넌트
│   │       └── examples/         # 예시 게임 환경
│   ├── agents/                   # RL 에이전트
│   │   ├── trainer.py            # 학습 실행기 (SB3 래퍼)
│   │   ├── self_play.py          # Self-play 로직
│   │   └── evaluator.py          # 학습된 모델 평가 (N판 추론)
│   ├── codegen/                  # 게임 환경 코드 자동 생성
│   │   ├── generator.py          # 파싱된 JSON → 환경 코드 생성
│   │   ├── validator.py          # 생성된 코드 검증 (자동 테스트)
│   │   └── templates/            # 코드 생성 템플릿
│   ├── checkpoints/              # 학습된 모델 저장
│   └── requirements.txt
│
├── ai_pipeline/                  # AI 파이프라인 (규칙 파싱 + RAG + 분석)
│   ├── parsing/                  # 규칙 파싱
│   │   ├── text_parser.py        # 텍스트 규칙 파싱 (OpenAI API)
│   │   ├── image_parser.py       # 이미지 규칙 파싱 (Claude Vision)
│   │   ├── prompts/              # 파싱용 프롬프트 템플릿
│   │   │   └── economic_board.py # 경제 보드 파싱 프롬프트
│   │   └── schemas/              # 파싱 결과 JSON 스키마
│   │       └── economic_board.json
│   ├── rag/                      # RAG 파이프라인
│   │   ├── embedder.py           # 텍스트 → 벡터 임베딩
│   │   ├── retriever.py          # 유사 게임 검색 (pgvector)
│   │   └── reference_loader.py   # 기존 게임 데이터 로드/저장
│   ├── analysis/                 # 밸런스 분석
│   │   ├── balance_analyzer.py   # 밸런스 점수 산출
│   │   ├── strategy_detector.py  # 지배 전략 탐지
│   │   ├── guideline_agent.py    # 개선 가이드라인 생성 (OpenAI API)
│   │   └── comparator.py         # Before/After 비교
│   └── requirements.txt
│
├── data/                         # 기존 게임 데이터 (RAG용)
│   ├── raw/                      # 원본 데이터
│   │   └── board_games/          # 보드게임 데이터
│   ├── processed/                # 전처리된 데이터
│   └── scripts/                  # 데이터 수집/전처리 스크립트
│       ├── collect.py            # 데이터 수집
│       └── preprocess.py         # 전처리 + 임베딩 생성
│
├── db/                           # Supabase 관련
│   ├── migrations/               # SQL 마이그레이션 파일
│   │   ├── 001_create_games.sql
│   │   ├── 002_create_training_jobs.sql
│   │   ├── 003_create_balance_reports.sql
│   │   ├── 004_create_game_references.sql
│   │   └── 005_enable_pgvector.sql
│   └── seed/                     # 초기 데이터 (테스트용)
│       └── seed_references.sql
│
├── tests/                        # 테스트
│   ├── backend/                  # API 테스트
│   ├── rl_engine/                # RL 환경/학습 테스트
│   ├── ai_pipeline/              # 파싱/RAG/분석 테스트
│   └── integration/              # 통합 테스트 (end-to-end)
│
├── .github/
│   └── workflows/                # GitHub Actions CI/CD
│       ├── ci.yml                # 린트 + 테스트
│       └── deploy.yml            # Vercel 배포 트리거
│
├── docker-compose.yml            # 로컬 개발 환경 (필요 시)
├── .gitignore
├── .env.example                  # 환경 변수 예시
├── PROJECT_PLAN_v2.md            # 프로젝트 기획서
└── CLAUDE.md                     # Claude Code 설정
```

---

## 2. 필요 사항

### 2.1 계정 및 서비스

| 서비스       | 용도                           | 플랜              |
| ------------ | ------------------------------ | ----------------- |
| **Supabase** | DB + Auth + Storage + pgvector | Free 플랜         |
| **Vercel**   | Next.js 프론트엔드 배포        | Hobby 플랜 (무료) |
| **GitHub**   | 코드 관리, CI/CD               | Free 플랜         |
| **OpenAI**   | OpenAI API (파싱, 가이드라인)  | API 키 (유료)     |
| **ngrok**    | 로컬 백엔드 외부 노출          | Free 플랜         |

### 2.2 환경 변수 (.env)

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# OpenAI API
OPENAI_API_KEY=your-api-key

# ngrok
NGROK_AUTH_TOKEN=your-ngrok-token
```

### 2.3 로컬 개발 환경

| 도구        | 버전   | 용도                       |
| ----------- | ------ | -------------------------- |
| **Python**  | 3.10+  | Backend, RL, AI 파이프라인 |
| **Node.js** | 18+    | Frontend (Next.js)         |
| **CUDA**    | 12.x   | GPU 학습 (RTX 5070 Ti)     |
| **conda**   | latest | Python 가상환경            |
| **Git**     | latest | 버전 관리                  |

### 2.4 Python 패키지 (주요)

```
# Backend
fastapi
uvicorn
supabase
python-multipart          # 파일 업로드

# RL Engine
stable-baselines3
gymnasium
torch                     # PyTorch (CUDA)
numpy

# AI Pipeline
openai                 # OpenAI API
sentence-transformers     # 임베딩 생성

# 공통
pydantic
python-dotenv
pytest
```

### 2.5 Node.js 패키지 (주요)

```
# Frontend
next
react
typescript
tailwindcss
@supabase/supabase-js    # Supabase 클라이언트
recharts                  # 차트 라이브러리
lucide-react              # 아이콘
zustand                   # 상태 관리
```

### 2.6 하드웨어

| 장비               | 수량 | 용도                    |
| ------------------ | ---- | ----------------------- |
| **RTX 5070 Ti PC** | 1대  | 개발 + RL 학습 + 백엔드 |
