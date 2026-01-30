# 💻 Source Code (`src/`)

에이전틱 RAG(Retrieval-Augmented Generation) 시스템의 핵심 로직과 엔진 아키텍처가 구현되어 있습니다.

---

## 📂 모듈별 상세 아키텍처

### 1. [agents/](./agents) (지능형 에이전트 시스템)
LangGraph를 이용한 계층형 전문가 조직을 정의합니다.
- **`graph.py`**: 서비스 내 모든 대화 흐름의 토폴로지 및 상태 전이 로직 정의.
- **`head_butler.py`**: 사용자 의도 분석 및 최적 전문가 팀(`adoption`, `care`) 배정.
- **`adoption_team.py`**: `matchmaker`(추천), `liaison`(연계) 전문가 노드 구현.
- **`care_team.py`**: `physician`(건강), `peacekeeper`(행동) 전문가 노드 구현.
- **`state.py`**: 전체 그래프에서 공유되는 `AgentState` 데이터 구조 정의.

### 2. [pipelines/](./pipelines) (데이터 제조 공정)
V1, V2, V3 각 파이프라인 세대별로 독립적인 5모듈 구조를 갖습니다.
- **구조**: `classifier.py`, `embedder.py`, `loader.py`, `preprocessor.py`, `schemas.py`
- **v3**: 현재 서비스 공정으로, 비동기 병렬 처리 및 구조적 임베딩을 통한 고속 적재 수행.

### 3. [retrieval/](./retrieval) (지능형 검색 엔진)
- **`hybrid_search.py`**: **RRF(Reciprocal Rank Fusion)** 알고리즘을 구현하여 벡터 검색 유사도와 BM25 키워드 정합성을 통합 산출하는 엔진.

### 4. [core/](./core) (핵심 자산 및 설정)
- **`config.py`**: 정책 기반 환경 설정(ZipsaPolicy) 및 DB/모델 관리.
- **`prompts.yaml`**: 중앙 집중식 전문가 페르소나 및 시스템 프롬프트 관리.
- **`prompt_manager.py`**: 프롬프트의 동적 로딩 및 버전 관리 엔진.
- **`domain_dictionary.txt`**: Kiwi 형태소 분석기용 사용자 사전 (**1,602개 핵심 용어**).
- **`extra_nouns.txt`**: 사전 빌드 시 참조하는 추가 명사 소스.
- **`synonyms.json`**: 묘종 명칭 및 특성어 확장을 위한 동의어 정규화 사전.
- **`stopwords.txt`**: 한국어 검색 제외어 리스트.

### 5. [ui/](./ui) (사용자 인터페이스)
Streamlit 기반의 다중 페이지 애플리케이션 구조입니다.
- **`app.py`**: 메인 엔트리포인트 및 사이드바 내비게이션.
- **`pages/`**: `chat.py`(채팅화면), `onboarding.py`(사용자 분석), `04_Prompt_Editor.py`(개발자용).
- **`components/`**: `header.py` 등 재사용 가능한 UI 컴포넌트.
- **`style.css`**: Glassmorphism 테마 및 프로젝트 통합 스타일 시트.

### 6. [utils/](./utils) (공통 유틸리티)
- **`text.py`**: Kiwi 형태소 분석기를 이용한 도메인 사전 기반 토큰화 및 클리닝.
- **`mongodb.py`**: v1, v2, v3 클러스터별 비동기 DB 매니저.

### 7. [notebooks/](./notebooks) (실험실)
- 토크나이저 최적화, 검색 성능 벤치마킹, 에이전트 프롬프트 실험용 Jupyter Notebook 보관.
