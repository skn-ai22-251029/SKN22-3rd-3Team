# [Project] Zipsa: AI-Powered Cat Head Butler Helper Service
**Agentic RAG-based Lifestyle Matching & Care System**

## 1. 프로젝트 개요 (Project Overview)
본 프로젝트는 **LLM과 LangGraph를 활용한 Agentic RAG 시스템**을 기반으로, 사용자의 라이프스타일에 맞는 반려묘 추천, 다중묘 가정의 갈등 해결, 그리고 유기묘 입양 연계 서비스를 제공하는 **종합 캣 코칭 AI 서비스**입니다.

---

## 2. 주요 페르소나 및 서비스 (Personas)
**Concept: The AI Head Butler (AI 수석 집사)**
집사Helper는 사용자의 라이프스타일에 맞춘 4가지 전문 페르소나를 통해 종합 케어를 제공합니다.

- **Matchmaker (인사 담당)**: 라이프스타일 매칭 및 품종 추천
- **Liaison (대외 협력)**: 유기묘 구조 및 보호소 연계
- **Peacekeeper (평화 유지군)**: 다묘 갈등 및 행동 조정
- **Physician (주치의)**: 건강 관리 및 영양 가이드

> [!TIP]
> 상세한 페르소나 정의 및 역할은 **[personas.md](./personas.md)** 문서를 참조하세요.

---

## 3. 시스템 아키텍처 (Technical Architecture)
**Hierarchical LangGraph (Multi-Agent Teams)** 구조로 설계되어 사용자 의도에 따라 팀 단위로 협업합니다.

- **Team: New Family**: 입양 전략 수립 및 매칭 (Sequential)
- **Team: Daily Life**: 건강 및 행동 케어 조정 (Collaborative)

> [!IMPORTANT]
> 상세한 그래프 구조 및 워크플로우 로직은 **[architecture.md](../02_design/architecture.md)** 문서를 참조하세요.

---

## 4. 데이터 전략 (Data Strategy)
신뢰성 있는 데이터 확보를 위해 내부 데이터 구축과 외부 API를 병행합니다.

### 📚 Internal Knowledge Base (RAG)
- **Integrated Breed Data (`cat_breeds_integrated.json`):**
    - **Sources:** TheCatAPI (기본 스펙) + Wikipedia (상세 정보/배경) 통합.
    - **Content:** 품종별 원산지, 크기, 수명, 성격, 특징 등 67개 주요 묘종 데이터 구축.
- **Preprocessed Care Guide (`bemypet_catlab_preprocessed.json`):**
    - **Sources:** BemyPet Catlab (1,153개 아티클).
    - **Taxonomy v2 (Specialist-Centric Design):** 
        - **Layer 1 (Topic):** 다중 카테고리 분류 (v2 확장 범주 적용).
        - **Layer 2 (Expert):** 전담 페르소나 매핑 (Matchmaker, Liaison, Peacekeeper, Physician).
    - **RAG 최적화:** v2 메타데이터를 활용한 Pre-filtering으로 검색 정확도 고도화.

### 🌐 External APIs (Real-time)
- **보호소 데이터:** 농림축산식품부 국가동물보호정보시스템 (OpenAPI)
- **추가 정보 검색:** Web Search API (필요 시 Fallback)

---

## 5. 로드맵 및 진행 현황 (Roadmap & Status)
**Phase 1: 기획 및 데이터 구축**
- [x] 페르소나별 시나리오 및 서비스 컨셉 구체화 (Zipsa, The Head Butler)
- [x] 고양이 품종/케어 데이터셋 확보 및 통합 (TheCatAPI, Wikipedia, BemyPet)
- [x] 전처리 정책 수립 (v1 Legacy / v2 Pro Specialist-Centric Taxonomy)
- [x] LangGraph 설계 및 State 정의 (Hierarchical Supervisor Architecture)
- [x] 프로젝트 구조 리팩토링 (Policy-Based Architecture 도입)

**Phase 2: MVP 개발 (Agentic RAG)**
- [x] **MongoDB Atlas Vector Search 구축** (v1 및 v2 멀티 클러스터 환경 자립)
- [x] **Hybrid Search 구현** (BM25 + Vector Retrieval + RRF 결합)
    - [x] Kiwi (Kiwipiepy) 형태소 분석 기반 한국어 토큰화 적용
- [x] **User Onboarding Form 구현:**
    - [x] 집사 성향 진단 및 프로필 수집 프로토타입 (Streamlit)
- [x] **에이전트 워크플로우 구현 (LangGraph 1.0.7):**
    - [x] Supervisor 및 전문가 노드 (Physician, Peacekeeper, Matchmaker) 구현
- [ ] 외부 API (실시간 유이묘 구조 정보) 연동 및 테스트

**Phase 3: 고도화 및 품질 검증**
- [/] **지식 베이스 품질 강화 (v2 Pro):**
    - [x] 2계층 다중 라벨링 엔진 고도화
    - [x] 전문가 페르소나 매핑 자동화
    - [/] 전체 아티클 재분류 및 데이터 적재 진행 중
- [ ] 에이전트 답변 정합성 테스트 (Evaluation)
- [x] Streamlit UI 고도화 (Premium Chat Interface & Onboarding)

## 6. Backlog (Future Work)
- [ ] CI/CD 파이프라인 구축
- [ ] 실제 서비스 배포 (AWS/GCP)
- [ ] 고양이 용품 추천 수익화 모델 (Affiliate)
- [ ] 멀티모달 기능 추가 (고양이 사진으로 품종/감정 분석)

