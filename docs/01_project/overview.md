# 🏰 ZIPSA: AI-Powered Cat Head Butler Service
> **"Every Butler Needs a Head Butler."**
> **Agentic RAG-based Lifestyle Matching & Comprehensive Care System**

---

## 1. Project Vision (비전)
**ZIPSA(집사)**는 초보 및 예비 '집사(고양이 반려인)'를 위한 **AI 수석 집사 서비스**입니다.
사용자의 라이프스타일을 심층 분석하여 가장 적합한 묘종을 추천하고(Matching), 입양 절차를 안내하며(Liaison), 입양 후에는 다중묘 갈등 조정부터 건강 관리까지(Care) 전방위로 지원하는 **'Agentic RAG' 기반의 코칭 시스템**입니다. 단순한 챗봇을 넘어, 전문성을 가진 **전문가 팀(Specialist Agents)**이 협업하여 사용자의 고민을 해결합니다.

---

## 2. Core Features (핵심 기능)

### 🧩 1. Lifestyle Matching (맞춤형 매칭)
- **사용자 분석**: 주거 환경(아파트/주택), 가족 구성원, 알러지 유무, 활동량 등을 고려한 정밀 분석.
- **RAG 기반 추천**: 67종의 고양이 품종 데이터와 수천 건의 양육 가이드를 기반으로 최적의 묘종 매칭.
- **Breed Filtering Policy**: "털 빠짐", "활동량" 등 사용자의 구체적인 요구사항을 데이터 수치와 매칭하는 엄격한 필터링 정책(`breed_criteria.py`) 적용.
- **파양 방지**: 단순 외모가 아닌, '함께 살 수 있는' 반려묘를 추천하여 파양률을 낮춥니다.

### 🔭 2. Ethical Adoption (입양/구조 연계)
- **입양 안내**: 입양 절차, 서류, 비용, 준비물 등 일반 입양 정보를 RAG 기반으로 제공.
- **구조동물 조회**: 국가동물보호정보시스템 API를 통해 보호 중인 고양이 정보를 실시간 조회.
- **보호소 연계**: 지역별 보호소 정보 및 연락처 안내.

### ⚖️ 3. Conflict Resolution (다묘 갈등 조정)
- **성향 분석**: 기존 반려묘와 새로운 반려묘의 MBTI(성격 유형) 분석.
- **합사 솔루션**: 단계별 합사 스케줄링 및 긴장 완화(Peacekeeping) 프로토콜 제공.

### 🩺 4. Lifecycle Care (생애주기 케어)
- **건강 모니터링**: 구토, 배변 등 이상 징후 발생 시 초기 대응 가이드(Triage) 제공.
- **영양 관리**: 연령별/묘종별 사료 및 영양학적 조언.

---

## 3. Agent Structure (AI 에이전트 구조)
ZIPSA 시스템은 **수석 집사(Head Butler)**를 중심으로 4개의 전문가 노드로 구성되어 있습니다.
Head Butler가 유일한 Exit Point이며, 전문가 노드는 구조화 JSON(`specialist_result`)으로 결과를 반환하고 반드시 Head Butler로 복귀합니다.

### 🎩 Head Butler (수석 집사 / Router & Exit Point)
- **역할**: 사용자 의도를 LLM Structured Output으로 분류(`matchmaker`, `liaison`, `care`, `general`)하여 라우팅. 일반 질문은 직접 응답. 전문가 복귀 시 specialist_result를 후처리하여 최종 응답 생성.
- **위치**: `src/agents/head_butler.py`

### 🧩 Matchmaker (품종 추천 전문가)
- **역할**: 라이프스타일 기반 품종 추천 (RAG: `specialist="Matchmaker"`, `categories="Breeds"` 필터).
- **위치**: `src/agents/matchmaker.py`

### 🔭 Liaison (입양/구조 전문가)
- **역할**: 입양 절차/서류/비용 안내 (RAG: `specialist="Liaison"`), 구조동물 조회 (Tool).
- **Tool**: `search_abandoned_animals` — 국가동물보호정보시스템 유기동물 조회 API (`src/agents/tools/animal_protection.py`)
- **위치**: `src/agents/liaison.py`

### 🏥 Care Team (건강 & 행동 통합 전문가)
- **역할**: LLM 분류로 Physician(의료) / Peacekeeper(행동)을 내부 판단 후 해당 specialist 태그로 RAG 검색. 페르소나 프롬프트 기반 응답 생성.
- **위치**: `src/agents/care_team.py`

> [!TIP]
> 각 페르소나의 상세 역할과 동작 방식은 **[personas.md](./personas.md)** 문서를 참조하세요.

---

## 4. Technical Architecture (아키텍처)
본 프로젝트는 **LangGraph 기반 4-Node Agent System** 패턴을 채택했습니다.

- **Orchestration**: `LangGraph`를 이용한 상태 관리(Stateful) 및 에이전트 라우팅. Head Butler가 유일한 Exit Point.
- **Knowledge Base (RAG)**:
    - **Vector Store**: MongoDB Atlas Vector Search (`cat_library`).
    - **Retrieval**: Hybrid Search (Vector + Keyword/BM25 + RRF Re-ranking + Dynamic Metadata Filtering).
    - **Data Source**: TheCatAPI(품종), Wikipedia(상세), BemyPet(케어 가이드).
- **Interface**: Streamlit 기반의 인터랙티브 채팅 UI.
- **Environment**: Python 3.11+ (Conda `skn-third-proj`).
- **Data Pipeline**:
  - **V3 Pipeline**: `src/pipelines/v3/` (Decoupled 3-Stage Process)
    1. **Preprocessor**: Text Cleaning & Tokenization -> `processed.json`
    2. **Embedder**: OpenAI Embedding Generation -> `embedded.pkl`
    3. **Loader**: MongoDB Ingestion (`cat_library`)

> [!IMPORTANT]
> 시스템의 시각적 구조도와 데이터 흐름은 **[architecture_graph.md](./architecture_graph.md)**를 확인하세요.

---

## 5. Directory Structure
```
skn-third-proj/
├── data/               # Raw & Processed Data
├── docs/               # Documentation
├── scripts/            # Execution Scripts
│   ├── v3/             # Article Pipeline (run_preprocess, run_embed, run_load)
│   └── process_breeds_v3.py  # Breed Data Pipeline (Policy-based)
├── src/
│   ├── agents/         # LangGraph Agents & Routing Logic
│   │   ├── filters/    # Metadata Filter Extraction (breed_criteria.py)
│   │   └── tools/      # Agent Tools (animal_protection.py)
│   ├── core/           # Standardized Core (Prompts, DTOs, Tokenizer Config)
│   ├── pipelines/      # Data Pipelines (ETL)
│   ├── retrieval/      # RAG & Search Logic (hybrid_search.py)
│   └── utils/          # Generic Utilities
└── .env                # Environment Variables
```
