# 데이터 전처리 결과 보고서 (Data Preprocessing Report)

`bemypet_catlab.json` 및 `youtube_extract.md` 데이터셋에 대한 전처리와 RAG 최적화 작업을 완료했습니다.

## ✅ 주요 성과
- **전체 항목 처리**: 1,153개(비마이펫) + 8개(유튜브) 아티클 전체에 대해 상세 메타데이터 생성 완료
- **완벽한 한국어 지원**: 모든 요약, 키워드, 예상 질문, 엔터티 등이 한국어로 생성됨
- **성능 최적화**: 비동기 병렬 처리(`asyncio`)를 통해 작업 시간을 18분 이내로 단축 (기존 대비 약 10배 개선)
- **데이터 무결성**: 고유 ID(`uid`)를 부여하여 중복 및 누락 방지

## 📊 지식 Taxonomy 버전 관리 (Versioning)

### [v1] 단일 레이어 분류 (Legacy)
- **방식**: 가장 적합한 카테고리 1개만 선택 (Single-label)
- **한계**: 복합 주제(예: 건강+행동)에 대한 정보 누락 발생

### [v2] 2-계층 다중 레이어 설계 (Current)
효율적인 RAG 검색과 전문가 페르소나 매칭을 위해 설계된 새로운 표준입니다.

#### Layer 1: 토픽 카테고리 (What)
- 정보 손실을 막기 위한 **다중 라벨(Multi-label)** 방식.
- **범주**: 건강, 영양, 행동, 양육, 생활/환경, 제품, 법률/사회, 이별/상실, 상식

### Layer 2: 전담 전문가 태그 (Who)
- 각 아티클을 답변하기에 가장 적합한 **4대 전문가 페르소나**를 매핑합니다.
- **Matchmaker**: 품종 추천 및 입양 상담 전문가
- **Liaison**: 보호소/구조 및 사회적 이슈 법률 전문가
- **Peacekeeper**: 다묘 갈등 및 행동 교정 전문 교관
- **Physician**: 질병 예방 및 영양 관리 전문 주치의

## 🔍 생성된 RAG 메타데이터 (스키마)
각 데이터 포인트는 다음의 필드를 포함하고 있습니다:
- `uid`: 고유 식별자 (`doc_0` ~ `doc_1152`, `md_0` ~ `md_7`)
- `categories`: 다중 선택된 토픽 레이어 (List[str])
- `specialists`: 매핑된 전문가 페르소나 레이어 (List[str])
- `keywords`: 3~5개의 검색용 핵심 키워드
- `summary`: 1~2문장의 벡터 임베딩용 요약
- `potential_questions`: 사용자 예상 질문 (QA 매칭용)
- `target_audience`: 대상 독자 (초보 집사, 노령묘 집사 등)
- `entities`: 언급된 주요 개체 (품종, 성분, 질병 등)

## 📊 MongoDB Atlas Index Configuration

### [v1] Legacy Index (MONGO_V1_URI)
- **Vector Index (`vector_index`)**:
```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "category",
      "type": "filter"
    }
  ]
}
```
- **Keyword Index (`keyword_index`)**:
```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "tokenized_text": {
        "type": "string"
      }
    }
  }
}
```

### [v2] Specialist-Centric Index (MONGO_V2_URI)
- **Vector Index (`vector_index`)**:
```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "categories",
      "type": "filter"
    },
    {
      "path": "specialists",
      "type": "filter"
    }
  ]
}
```
- **Keyword Index (`keyword_index`)**:
```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "tokenized_text": {
        "type": "string"
      },
      "specialists": {
        "type": "string"
      }
    }
  }
}
```

## 🛠️ 리팩토링된 정책 기반 구조 (Policy-Based Architecture)

핵심 원칙: **구조 기반 분리가 아닌, 정책(Strategy) 기반 기능 선택**

### 1. 전처리 및 분류 도메인 (`src/domain/`)
- **[src/domain/classifier.py](file:///Users/leemdo/Workspaces/SKN22-3rd-3Team/src/domain/classifier.py)**: V1(Legacy)과 V2(Pro) 분류 전략을 통합 관리하는 엔진
- **[src/domain/schemas.py](file:///Users/leemdo/Workspaces/SKN22-3rd-3Team/src/domain/schemas.py)**: Pydantic 기반의 버전별 데이터 모델 정의

### 2. 통합 실행 스크립트 (`scripts/`)
사용자가 직접 실행하는 진입점입니다.
- **[scripts/classify.py](file:///Users/leemdo/Workspaces/SKN22-3rd-3Team/scripts/classify.py)**: `--version` 인자를 통해 V1/V2 분류를 선택 실행
- **[scripts/ingest.py](file:///Users/leemdo/Workspaces/SKN22-3rd-3Team/scripts/ingest.py)**: `--version` 인자를 통해 V1/V2 데이터 적재를 선택 실행

### 3. 데이터 및 핵심 설정
- **[src/core/config.py](file:///Users/leemdo/Workspaces/SKN22-3rd-3Team/src/core/config.py)**: **[중요]** 각 버전의 DB 이름, 파일 경로, 카테고리 정책을 중앙 관리
- **[data/v1/](file:///Users/leemdo/Workspaces/SKN22-3rd-3Team/data/v1/)**, **[data/v2/](file:///Users/leemdo/Workspaces/SKN22-3rd-3Team/data/v2/)**: 각 정책 실행 결과물이 저장되는 독립 공간

---
**CatFit** 프로젝트는 이제 정책 기반의 유연한 구조를 통해 V3, V4가 추가되어도 폴더 구조 변경 없이 대응할 수 있는 확장성을 확보했습니다! 🐾✨
