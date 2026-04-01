# 보드게임 밸런스 테스터 — 프로젝트 기획서 v2

## 1. 프로젝트 개요

### 1.1 목표

보드게임 규칙서를 입력하면 AI가 자동으로 게임 환경을 생성하고, 강화학습(RL) 기반 시뮬레이션을 통해 밸런스를 분석하며, 구체적인 개선안을 제시하는 개인 SaaS 프로젝트.

### 1.2 지원 게임 장르

- **MVP: 경제 기반 보드게임** (부루마블, 모노폴리류) — 자원 관리, 주사위, 맵 기반
- **Phase 2: 카드 대전 게임** (하스스톤, 유희왕류) — 여유 되면 확장

### 1.3 핵심 기능

| 기능            | 설명                                                        |
| --------------- | ----------------------------------------------------------- |
| 규칙 파싱       | 규칙서 텍스트/이미지 업로드 → AI가 게임 구조 파싱           |
| 게임 환경 생성  | 파싱된 규칙 기반으로 RL 학습 가능한 코드 환경 자동 생성     |
| RL 시뮬레이션   | 에이전트끼리 수천~수만 판 자동 플레이                       |
| 밸런스 분석     | 선/후공 승률, 전략별 승률, 밸런스 비율 리포트               |
| 개선 가이드라인 | 불균형 감지 시 구체적 수치 조정 제안 (예: "통행료 300→200") |
| 재검증          | 가이드라인 적용 후 재시뮬레이션으로 개선 확인               |

---

## 2. 시스템 아키텍처

```
[사용자] → [Next.js 프론트엔드 (Vercel)]
               ↓
         [FastAPI 백엔드 (로컬 + ngrok)]
               ↓
    ┌──────────┼──────────┐
    ↓          ↓          ↓
[OpenAI API] [pgvector]  [로컬 RL 학습]
 규칙 파싱    RAG 참조    RTX 5070 Ti
    ↓                      ↓
[게임 환경 코드 생성]   [SB3 Self-play]
                           ↓
                     [밸런스 분석 Agent]
                           ↓
                    [리포트 + 가이드라인]
```

### 2.1 인프라 구조

```
[클라우드]                    [로컬 머신 (RTX 5070 Ti)]
 ├── Vercel → Frontend        ├── FastAPI 서버 (ngrok)
 ├── Supabase → DB + Auth     ├── RL 학습 (SB3 + PyTorch)
 │   + Storage + pgvector     └── 학습 결과 저장
 └── GitHub → 코드 관리
```

- Frontend: Vercel 배포
- Backend: 로컬 FastAPI + ngrok으로 외부 노출
- DB/Auth/Storage: Supabase (pgvector 포함)
- RL 학습: 로컬 단일 GPU 직접 실행 (BackgroundTasks)

---

## 3. 기술 스택

| 영역          | 기술                  | 선정 이유                              |
| ------------- | --------------------- | -------------------------------------- |
| Frontend      | Next.js (App Router)  | SSR/SSG, 대시보드 구축에 적합          |
| Frontend 배포 | Vercel                | Next.js 공식 배포, 무료 플랜           |
| Backend API   | FastAPI               | RL 파이프라인과 동일 언어, 비동기 지원 |
| Backend 배포  | ngrok (로컬)          | 개발/데모용                            |
| Database      | Supabase (PostgreSQL) | DB + Auth + Storage 올인원             |
| 벡터 DB       | pgvector (Supabase)   | RAG 구현                               |
| RL 프레임워크 | Stable-Baselines3     | Python 기반, 다양한 알고리즘           |
| AI 엔진       | OpenAI API            | 규칙 파싱, 코드 생성, 분석             |
| 상태 관리     | Zustand               | 경량 상태 관리                         |
| 차트          | Recharts              | 밸런스 리포트 시각화                   |

---

## 4. 개발 마일스톤

팀이 아닌 1인 개발이므로 주차별 대신 단계별 마일스톤으로 관리.

### M1: 프로젝트 세팅 + 기반 구축

- [ ] 모노레포 디렉토리 구조 생성
- [ ] Supabase 프로젝트 생성 + DB 스키마 (마이그레이션)
- [ ] FastAPI 기본 앱 + API 라우터 골격
- [ ] Next.js 프로젝트 세팅 + 기본 레이아웃
- [ ] .env 설정, Docker Compose (Redis 등 필요 시)
- [ ] CI/CD 기본 세팅 (GitHub Actions)

### M2: 규칙 파싱 + 게임 환경 생성

- [ ] OpenAI API 연동 (텍스트 파싱)
- [ ] 경제 보드게임 파싱 프롬프트 설계 + 구현
- [ ] 이미지 규칙서 파싱 (Claude Vision)
- [ ] 파싱 결과 → 구조화된 게임 JSON
- [ ] 게임 JSON → RL 환경 코드 자동 생성 (codegen)
- [ ] 생성된 환경 코드 자동 검증

### M3: RAG 파이프라인

- [ ] 기존 보드게임 데이터 수집 + 전처리
- [ ] 임베딩 파이프라인 (텍스트 → 벡터)
- [ ] pgvector 세팅 + 유사 게임 검색 로직
- [ ] 파싱 시 RAG 참조하여 품질 향상

### M4: RL 학습 파이프라인

- [ ] 경제 보드게임 RL 환경 템플릿 (Gymnasium)
- [ ] SB3 학습 로직 (PPO 기반)
- [ ] Self-play 구현 (에이전트 vs 에이전트)
- [ ] 학습 진행률 추적 + 상태 관리
- [ ] 학습을 BackgroundTasks로 비동기 실행

### M5: 밸런스 분석 + 가이드라인

- [ ] 학습된 모델로 평가 게임 N판 실행
- [ ] 승률 계산 (선/후공별, 전략별)
- [ ] 밸런스 점수 산출 (0~100)
- [ ] 지배 전략 탐지
- [ ] OpenAI API 기반 개선 가이드라인 생성
- [ ] 가이드라인 적용 → 재시뮬레이션 → Before/After 비교

### M6: 프론트엔드 대시보드

- [ ] 규칙 입력 페이지 (텍스트 + 파일 업로드)
- [ ] 파싱 결과 확인/수정 UI
- [ ] 학습 진행 모니터링 페이지
- [ ] 밸런스 리포트 시각화 (차트, 그래프)
- [ ] 가이드라인 표시 + 재검증 결과 비교 UI
- [ ] Vercel 배포

### M7 (Phase 2): 카드 대전 게임 확장

- [ ] 카드 대전 파싱 프롬프트 + JSON 스키마
- [ ] 카드 대전 RL 환경 템플릿
- [ ] 카드별 승률 기여도 분석
- [ ] 프론트엔드 장르 선택 UI

---

## 5. 주요 데이터 모델

### 5.1 Game (게임 정보)

```
Game
├── id
├── name (게임 이름)
├── genre (economic_board | card_battle)
├── rules_text (파싱된 규칙 텍스트)
├── rules_raw (원본 규칙서 파일 경로)
├── parsed_structure (JSON - 파싱된 게임 구조)
├── environment_code (생성된 RL 환경 코드)
├── status (parsing | ready | training | completed)
├── created_at
└── updated_at
```

### 5.2 TrainingJob (학습 작업)

```
TrainingJob
├── id
├── game_id (FK → Game)
├── algorithm (PPO | DQN | A2C)
├── hyperparameters (JSON)
├── status (queued | running | completed | failed)
├── progress (0~100%)
├── total_episodes
├── started_at
└── completed_at
```

### 5.3 BalanceReport (밸런스 리포트)

```
BalanceReport
├── id
├── training_job_id (FK → TrainingJob)
├── win_rates (JSON - 선/후공별, 전략별 승률)
├── balance_score (0~100, 50이 완벽한 밸런스)
├── dominant_strategies (JSON - 지배 전략 목록)
├── severity (good | warning | critical)
├── guidelines (JSON - 개선 제안 목록)
├── created_at
```

### 5.4 GameReference (기존 게임 데이터 - RAG용)

```
GameReference
├── id
├── name (게임 이름)
├── genre
├── rules_summary
├── balance_data (JSON - 알려진 밸런스 정보)
├── strategies (JSON - 유효 전략 목록)
├── embedding (벡터 - pgvector)
└── source (데이터 출처)
```

---

## 6. API 엔드포인트

### 게임 관리

| Method | Endpoint                      | 설명                         |
| ------ | ----------------------------- | ---------------------------- |
| POST   | `/api/games`                  | 새 게임 생성 (규칙서 업로드) |
| GET    | `/api/games/{id}`             | 게임 정보 조회               |
| GET    | `/api/games`                  | 게임 목록 조회               |
| POST   | `/api/games/{id}/parse`       | 규칙 파싱 실행               |
| GET    | `/api/games/{id}/environment` | 생성된 게임 환경 코드 조회   |

### 학습

| Method | Endpoint                          | 설명                |
| ------ | --------------------------------- | ------------------- |
| POST   | `/api/games/{id}/train`           | 학습 작업 생성      |
| GET    | `/api/training/{job_id}`          | 학습 상태 조회      |
| GET    | `/api/training/{job_id}/progress` | 실시간 진행률 (SSE) |
| POST   | `/api/training/{job_id}/stop`     | 학습 중지           |

### 분석

| Method | Endpoint                           | 설명                      |
| ------ | ---------------------------------- | ------------------------- |
| GET    | `/api/reports/{job_id}`            | 밸런스 리포트 조회        |
| GET    | `/api/reports/{job_id}/guidelines` | 개선 가이드라인 조회      |
| POST   | `/api/reports/{job_id}/revalidate` | 가이드라인 적용 후 재검증 |

---

## 7. 핵심 파이프라인 상세

### 7.1 규칙 파싱 파이프라인

```
[규칙서 입력 (텍스트/이미지)]
    ↓
[OpenAI API - Vision + Text]
    ↓
[RAG: pgvector에서 유사 게임 검색]
    ↓
[유사 게임 참조하여 구조화된 게임 JSON 생성]
    ↓
[게임 JSON → RL 환경 코드 자동 생성]
    ↓
[코드 검증 (자동 테스트)]
    ↓
[저장]
```

**게임 JSON 구조 예시 (경제 보드게임):**

```json
{
  "type": "economic_board",
  "players": { "min": 2, "max": 4 },
  "turn_based": true,
  "components": {
    "board": {
      "total_spaces": 40,
      "spaces": [
        { "index": 0, "type": "start", "name": "출발" },
        {
          "index": 1,
          "type": "property",
          "name": "지중해",
          "price": 60,
          "rent": [2, 10, 30, 90, 160, 250]
        },
        { "index": 5, "type": "railroad", "name": "철도역", "price": 200 }
      ]
    },
    "dice": { "count": 2, "sides": 6 },
    "starting_money": 1500,
    "currency_unit": "원"
  },
  "phases": ["roll_dice", "move", "action", "end_turn"],
  "win_condition": "last_player_standing"
}
```

### 7.2 RL 학습 파이프라인

```
[게임 환경 코드 로드]
    ↓
[FastAPI BackgroundTasks로 학습 실행]
    ↓
[Stable-Baselines3 학습 (RTX 5070 Ti)]
  ├── Self-play (에이전트 vs 에이전트)
  ├── 전략 탐색 (다양한 정책 학습)
  └── 선/후공 교대 학습
    ↓
[학습 결과 저장 (모델 + 로그)]
    ↓
[분석 파이프라인으로 전달]
```

### 7.3 밸런스 분석 파이프라인

```
[학습된 모델로 평가 게임 N판 실행]
    ↓
[통계 수집]
  ├── 선/후공 승률
  ├── 전략별 승률 분포
  ├── 게임 길이 분포
  └── 칸/자산별 가성비 분석
    ↓
[밸런스 점수 산출 (0~100)]
    ↓
[불균형 감지 시 → OpenAI API로 개선 가이드라인 생성]
  ├── 구체적 수치 조정 제안
  ├── 규칙 변경 제안
  └── 예상 개선 효과
    ↓
[가이드라인 적용 → 환경 수정 → 재학습 → 재분석]
    ↓
[Before/After 비교 리포트 생성]
```

---

## 8. 고도화 로드맵

### Phase 2: 카드 대전 게임 확장

- 카드 대전 파싱/환경/분석 추가
- 카드별 승률 기여도, 덱 다양성 분석

### Phase 3: 고도화

| Task                     | 설명                                                  |
| ------------------------ | ----------------------------------------------------- |
| **백엔드 클라우드 배포** | ngrok → Railway/Fly.io로 이전                         |
| **게임 장르 확장**       | 주사위 전략, 타일 배치 등 추가 장르                   |
| **규칙 파싱 고도화**     | 복잡한 규칙서 (예외 조항, 특수 능력) 파싱 정확도 향상 |
| **노코드 게임 에디터**   | GUI로 보드/카드 직접 편집, 실시간 밸런스 미리보기     |
| **리플레이 시각화**      | AI 게임 플레이를 시각적으로 재생                      |
| **A/B 테스트**           | 규칙 변형 2가지를 동시에 학습/비교                    |

---

## 9. 리스크 및 대응

| 리스크                     | 영향                  | 대응                                                           |
| -------------------------- | --------------------- | -------------------------------------------------------------- |
| 규칙 파싱 정확도 부족      | 잘못된 게임 환경 생성 | 파싱 결과 검토/수정 UI 제공, RAG로 품질 보완                   |
| RL 학습 시간 과다          | 대기 시간 증가        | 단순한 게임부터 테스트, 진행률 실시간 표시, 체크포인트 저장    |
| OpenAI API 비용            | 운영 비용 증가        | 파싱 결과 캐싱, 유사 게임은 기존 결과 재활용                   |
| 복잡한 게임 환경 생성 실패 | 지원 불가 게임 발생   | 경제 보드게임 템플릿 기반 생성, 실패 시 수동 수정 가이드 제공  |
| 1인 개발 병목              | 진행 지연             | 마일스톤별 순차 진행, MVP 스코프 최소화, Claude Code 적극 활용 |

---

## 10. 환경 변수

`.env`에 필요한 값:

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

---

## 11. 코드 스타일

- Python: Black + isort
- TypeScript: ESLint + Prettier
- TypeScript에서 항상 arrow function 사용
- Python 3.10+, Node.js 18+
