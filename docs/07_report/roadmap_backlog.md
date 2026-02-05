# 🗺️ ZIPSA Roadmap & Tasks (GitHub Issues)

본 문서는 프로젝트의 마일스톤(Roadmap)과 이를 달성하기 위한 구체적인 실행 계획(Tasks)을 통합 관리합니다.
**GitHub 이슈 등록 시, 각 항목의 제목을 이슈 제목으로 사용하세요.**

---

## 🚀 Phase 1: V3 안정화 및 버그 박멸 (Current)
> **목표**: 현재 구현된 기능(Dual-Model, V3 검색, 3-Node 에이전트)의 무결성 확보 및 데이터 신뢰도 향상.

- [x] **지역 코드 정합성 검증 및 중복 제거** (`region_codes.py`)
    - 이슈: `창원시` 등의 코드가 API에서 중복 반환되는 현상.
    - 결과: 데이터 중복 제거 및 무결성 확인 완료.
- [x] **스트리밍 토큰 필터링 및 보안 검증**
    - 이슈: `head_butler`의 라우팅용 JSON 토큰이 사용자에게 노출될 위험.
    - 결과: `astream_events` 핸들러 내 `router_classification` 태그 차단 검증 완료.
- [ ] **통합 테스트 시나리오 설계 및 실행**
    - **Plan**: 에이전트별 Happy/Bad Path, 멀티턴 대화 등을 포함한 상세 시나리오 문서(`test_plan.md`) 작성.
    - **Execution (필수 시나리오)**:
        - `Liaison` (유기묘):
        - **Tool**: 위치/상태 기반 유기묘 조회 결과 제시.
        - **RAG**: "입양 절차", "준비물" 등 가이드 정보 함께 제공 (Hybrid Response).
    - `Matchmaker` (품종): 사용자 성향 기반 매칭 및 정보 제공 로직 검증.
    - *Note*: 두 에이전트의 목적과 UX가 섞이지 않도록 엄격히 분리 테스트 수행.
- [ ] **공공데이터 품종 코드 매핑 테이블 구축**
    - 이슈: API의 `kindNm` 비표준 포맷(e.g., "[고양이] 한국 고양이") 대응.
    - 액션: `kindCd` -> 표준 품종명 변환 테이블 확보.
- [ ] **데이터셋 확장 및 V3 스키마 검증**
    - 액션: 보호소 상세 정보, 수의학적 기초 데이터 등 고품질 소스 발굴 및 통합.
    - **Critical**: V3 파이프라인 스키마 규격 엄수 (Schema Validation 필수).
    - **Discussion**: **멀티모달 데이터 수용**을 위한 **V4 스키마 설계 및 벡터 차원 호환성 팀 논의** 선행 필요.

---

## 🎨 Phase 2: UI/UX 고도화 & 개인화 (Next)
> **목표**: 현대적인 Frontend 기술(React/Vue) 도입 및 회원가입 기반의 개인화 서비스 구축.

### 2.1 Frontend Modernization
- [ ] **Next.js 프론트엔드 아키텍처 설계**
    - 검토: Streamlit 제거 후 **Next.js** 도입 시의 API 명세(FastAPI) 및 상태 관리 전략 수립.
    - **Decision**: 업계 표준인 **Next.js (React)** 로 확정. Vercel AI SDK 등 최신 AI 생태계와의 최적 호환성 고려.
    - 액션: Backend API(FastAPI/Django)와 Frontend 분리 아키텍처 수립.
- [ ] **카드형 UI 컴포넌트 개발 (유기묘/추천 결과)**
    - 목표: 텍스트 위주 정보를 시각적 카드(이미지, 핵심 태그, 요약) 형태로 변환.
    - 액션: `st.container` (단기) -> React Component (장기) 전환.
    - **Dependency**: 2.2의 **CatCard DTO 구조 개편**과 스키마 동기화 필수.

### 2.2 Auth & Personalization
- [ ] **회원가입/로그인 및 프로필 통합 시스템 구축**
    - **API & DTO**: `UserCreate` (가입 요청), `UserResponse` (응답) 등 요청/응답 스키마 분리.
    - **DB Schema**: MongoDB `users` 컬렉션 설계 (알레르기, 주거형태, 닉네임 등).
    - **Onboarding**: 기존 `onboarding.py` 로직을 가입 후 프로필 설정 단계로 이관.
- [ ] **CatCard DTO 구조 개편 및 상속 설계**
    - 목표: 유기동물(`Abandoned`), 품종추천(`Recommend`), **사용자 반려묘(`UserCat`)** 의 공통 속성 통합.
    - 구조: `BaseCatCard` (공통) -> `RecommendCard` / `AbandonedCard` / **`UserCatCard`** 상속.
    - **One-to-Many**: 사용자 1명이 N마리의 고양이를 등록/관리할 수 있는 스키마 및 UI 설계.
    - 기능: **Interactive Text** (LLM 응답 내 고양이 이름 호버 시 카드 팝오버 노출).

### 2.3 Search Logic Enhancement
- [ ] **자연어 필터링 정책 고도화 (Breed Filtering Policy)**
    - 목표: 사용자의 자연어 표현을 숫자로 된 데이터 필터로 정확히 변환.
    - **Draft Policy (예시)**:
        - *Shedding*: "털 안 빠지는" -> `shedding_level <= 2`
        - *Energy*: "얌전한/아파트용" -> `energy_level <= 2`, "활발한" -> `energy_level >= 4`
        - *Friendly*: "초보/아이 있는 집" -> `child_friendly >= 4`

---

## 🏗️ Phase 3: 확장 및 자동화 (Future)
> **목표**: 운영 효율성 증대, 인프라 안정화(DevOps) 및 AI 기능 확장.

### 3.1 Backend & Infrastructure
- [ ] **FastAPI 기반 백엔드 서버 구축**
    - `LangServe`를 활용하여 에이전트 그래프(`graph.py`)를 REST API로 서빙.
    - **Context Management**: 턴당/세션당 최대 토큰 제한(`max_tokens`) 및 대화 히스토리 Trimming 로직 구현 (안정성 확보).
- [ ] **도커(Docker) 컨테이너 환경 구축**
    - App + DB + Redis 구성을 `docker-compose`로 컨테이너화하여 환경 일관성 보장.
- [ ] **GitHub Actions 기반 CI/CD 파이프라인 구축**
    - GitHub Actions: PR 시 테스트(`pytest`) -> Main 병합 시 자동 배포.
- [ ] **클라우드 배포 (AWS/GCP)**
    - AWS/GCP 인스턴스 프로비저닝 및 실서버 배포.

### 3.2 Data & AI Ops
- [ ] **LangSmith 기반 KPI 자동 측정 시스템 도입**
    - 답변 정확도, 응답 속도 등 품질 지표 모니터링 대시보드 구축.
- [ ] **Redis 캐싱 시스템 도입**
    - 반복되는 쿼리에 대한 응답 속도 개선.
- [ ] **멀티모달 (Vision) 확장 기능 구현**
    - 사용자가 업로드한 고양이 사진을 분석하여 품종 판별 및 상담.
    - **Prerequisite**: Phase 1의 **V4 스키마 설계 및 벡터 차원 호환성** 논의 완료 필수.
    - **인프라 고려사항**: 이미지 저장 및 벡터 검색을 위한 별도 스토리지 및 인덱싱 전략 필요.

### 3.3 Security & Ops (New)
- [ ] **개인정보 보호(PII) 마스킹 처리 구현**
    - **PII Masking**: LangSmith 전송 전 민감정보(전화번호, 주소 등) 마스킹 처리 (Privacy).
- [ ] **트래픽 관리 및 레이트 리미팅(Rate Limiting) 적용**
    - **Rate Limiting**: FastAPI `slowapi` 및 Cloudflare WAF 설정을 통한 DDoS/Abuse 방지.
- [ ] **장애 대응 및 자동 복구(Fallback) 로직 구현**
    - **Graceful Fallback**: LLM/검색 API 장애 시 "기본 응답 모드" 자동 전환 로직 구현.
- [ ] **사용자 피드백 루프 및 개선 프로세스 정립**
    - 주간 리뷰: 하위 평점(👎) 답변 분석 -> 프롬프트 개선 -> 재배포 프로세스 정립.

---

## 🛠️ Continuous Improvement (기술 부채)
- [ ] **단위 테스트(Unit Test) 작성 및 커버리지 확보**
- [ ] **RAG 태그 정합성 전수 조사 및 검증**
    - DB 태그와 에이전트 라우팅 키워드(`care_team.py`) 일치 여부 전수 조사.

---
**Last Updated**: 2026-02-05
